"""Temple con h(Ts): conducción radial no lineal (esfera o cilindro largo) con convección variable.

Fase 2b. ρ·cp·∂T/∂t = (1/rⁿ)·∂(k rⁿ ∂T/∂r)/∂r (n = 2 esfera, n = 1 cilindro radial, 1D) con
-k ∂T/∂r = h(Ts)·(Ts - T_medio) en la superficie. Se resuelve por volúmenes finitos e integración
LSODA (banda tridiagonal). La temperatura de superficie Ts sale de igualar el flujo de conducción
del último nodo (media celda) con el de convección, que es una ecuación escalar monótona.

Forma de h(Ts) para aceite quieto: Liščić, Matijević, Totten y Canale (2016), Proc. 3rd MCHT&SE,
Portorož, Fig. 4 y Tabla 1 (Kalenol 32 a 28 °C, sonda de Liščić). Solo se calibra UN factor de
escala de esa forma; los nodos no se ajustan. Ver docs/fase2b-h-variable.md.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from tratamientos.temple import AUSTENITE, INCH, Steel

SPHERE, CYLINDER = 2, 1  # exponente n de la geometría: área ∝ rⁿ

# ---------------------------------------------------------------- forma de h(Ts) en aceite
# Nodos (Ts °C, h W/m²K) de Kalenol 32 quieto a 28 °C, sonda de Liščić. Texto y Tabla 1: pico 1.940
# a 490 °C y transición película -> nucleada (qcr2) a 620 °C. Los otros valores se leen de la Fig. 4
# (curva suave, ±50 W/m²K): mínimo de ~520 en 620 °C, película de 750-780 entre 700 y 800 °C
# (coherente con los 600-900 deducidos de Ramesh y Prabhu 2014), hombro de ~250 a 380 °C y cola de
# ~200 hasta 150 °C. La película por encima de 800 °C se prolonga plana. 5 nodos, ascendentes en Ts.
OIL_SHAPE = ((150.0, 200.0), (380.0, 250.0), (490.0, 1940.0), (620.0, 520.0), (800.0, 750.0))


@dataclass(frozen=True)
class HShape:
    """h(Ts) lineal por tramos y plana fuera de los nodos; ``scale`` es el único factor libre."""

    nodes: tuple[tuple[float, float], ...] = OIL_SHAPE
    scale: float = 1.0

    def __call__(self, temperature: float) -> float:
        temps, values = zip(*self.nodes, strict=True)
        return self.scale * float(np.interp(temperature, temps, values))

    def scaled(self, scale: float) -> HShape:
        return HShape(self.nodes, scale)


def constant_h(h: float) -> Callable[[float], float]:
    return lambda _ts: h


# ---------------------------------------------------------------------------- materiales
@dataclass(frozen=True)
class Material:
    """Propiedades tabuladas contra T (°C), interpoladas linealmente y planas fuera de la tabla."""

    temps: tuple[float, ...]
    k: tuple[float, ...]  # W/m·K
    cp: tuple[float, ...]  # J/kg·K
    rho: tuple[float, ...]  # kg/m³

    def conductivity(self, t: float | np.ndarray) -> float | np.ndarray:
        return np.interp(t, self.temps, self.k)

    def volumetric_capacity(self, t: float | np.ndarray) -> float | np.ndarray:
        return np.interp(t, self.temps, self.rho) * np.interp(t, self.temps, self.cp)

    def enthalpy(self, t: float, t_ref: float = 0.0) -> float:
        """∫ρ·cp dT desde ``t_ref`` (J/m³), por trapecios sobre una malla fina."""
        grid = np.linspace(t_ref, t, 2001)
        return float(np.trapezoid(self.volumetric_capacity(grid), grid))


def from_steel(steel: Steel = AUSTENITE) -> Material:
    return Material((0.0, 1000.0), (steel.k,) * 2, (steel.cp,) * 2, (steel.rho,) * 2)


def _gaps(temps, values) -> tuple[tuple[float, ...], tuple[float, ...]]:
    keep = [(t, v) for t, v in zip(temps, values, strict=True) if v is not None]
    return tuple(t for t, _ in keep), tuple(v for _, v in keep)


# Inconel 600, Tabla 1 de Ramesh y Prabhu (2014), ISIJ Int. 54:1426 (CC BY-NC-ND), 50-900 °C. La
# tabla tiene huecos (k en 600 y 800 °C, cp en varias): cada propiedad se interpola entre sus
# valores publicados. Es el material de la sonda de Liščić (el artículo de 2016 lo declara).
_T_IN = (50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900)
_K_IN = (13.4, 14.2, 15.1, 16.0, 16.9, 17.8, 18.7, 19.7, 20.7, 21.7, None, 25.9, None, 30.1)
_CP_IN = (451, 467, None, 491, None, 509, None, 522, None, 533, 591, 597, 597, 611)
_RHO_IN = (8400, 8370, None, 8340, None, 8300, None, 8270, None, 8230, 8190, 8150, 8100, 8060)


def _interp_table(values) -> tuple[float, ...]:
    t, v = _gaps(_T_IN, values)
    return tuple(float(x) for x in np.interp(_T_IN, t, v))


INCONEL_600 = Material(tuple(float(t) for t in _T_IN), _interp_table(_K_IN), _interp_table(_CP_IN),
                       _interp_table(_RHO_IN))  # fmt: skip


# --------------------------------------------------------------------------------- solver
@dataclass(frozen=True)
class RadialResult:
    exponent: int
    radius_m: float
    t_end: float
    radii: np.ndarray = field(repr=False)
    _solution: Callable[[float], np.ndarray] = field(repr=False)
    material: Material = field(repr=False, default=INCONEL_600)
    t_initial: float = 0.0
    shell_volumes: np.ndarray = field(repr=False, default_factory=lambda: np.zeros(0))

    def nodes(self, time_s: float) -> np.ndarray:
        return self._solution(time_s)[:-1]

    def temperature(self, time_s: float, radius_m: float = 0.0) -> float:
        """Temperatura (°C) a ``radius_m`` del eje o centro, interpolada entre nodos."""
        return float(np.interp(radius_m, self.radii, self.nodes(time_s)))

    def heat_out(self, time_s: float) -> float:
        """Calor cedido hasta ``time_s`` (J, o J/m en el cilindro)."""
        return float(self._solution(time_s)[-1])

    def stored_loss(self, time_s: float) -> float:
        """Entalpía perdida por el sólido hasta ``time_s`` (mismas unidades que heat_out)."""
        temps = self.nodes(time_s)
        h_now = np.array([self.material.enthalpy(t) for t in temps])
        h_0 = self.material.enthalpy(self.t_initial)
        return float(np.sum(self.shell_volumes * (h_0 - h_now)))

    def time_to(self, temperature: float, radius_m: float = 0.0) -> float:
        def gap(t: float) -> float:
            return self.temperature(t, radius_m) - temperature

        if gap(self.t_end) > 0:
            raise ValueError(f"no llega a {temperature} °C en {self.t_end:.0f} s")
        return float(brentq(gap, 0.0, self.t_end, xtol=1e-9))

    def rate_at(self, temperature: float, radius_m: float = 0.0) -> float:
        """Velocidad de enfriamiento (°C/s, positiva) al pasar por ``temperature``."""
        t = self.time_to(temperature, radius_m)
        dt = 1e-4 * max(t, 1e-3)
        return (self.temperature(t - dt, radius_m) - self.temperature(t + dt, radius_m)) / (2 * dt)


def _surface_temperature(
    g_cond: float, t_node: float, t_medium: float, h_fn: Callable[[float], float]
) -> float:
    """Ts tal que g·(Tn - Ts) = h(Ts)·(Ts - Tm); el lado izquierdo baja con Ts y el derecho sube."""
    lo, hi = sorted((t_medium, t_node))
    if hi - lo < 1e-12:
        return t_node

    def gap(ts: float) -> float:
        return g_cond * (t_node - ts) - h_fn(ts) * (ts - t_medium)

    return float(brentq(gap, lo, hi, xtol=1e-10, rtol=1e-12))


def quench_radial(
    exponent: int,
    radius_m: float,
    h_fn: Callable[[float], float],
    material: Material,
    t_initial: float,
    t_medium: float,
    t_end: float,
    nodes: int = 120,
    stop_center_below: float | None = None,
) -> RadialResult:
    """Enfría una esfera (``exponent`` 2) o un cilindro largo (1) desde ``t_initial`` uniforme.

    Las áreas y volúmenes son por unidad de A_n (4π en la esfera, 2π por metro en el cilindro),
    que se simplifica en las ecuaciones; el balance de energía lo conserva.
    """
    if not (radius_m > 0 and nodes >= 10 and exponent in (SPHERE, CYLINDER)):
        raise ValueError("radio positivo, al menos 10 nodos y geometría esfera o cilindro")
    n = exponent
    edges = np.linspace(0.0, radius_m, nodes + 1)
    radii = (edges[:-1] + edges[1:]) / 2
    dr = edges[1] - edges[0]
    volumes = (edges[1:] ** (n + 1) - edges[:-1] ** (n + 1)) / (n + 1)
    areas = edges[1:-1] ** n
    area_s = radius_m**n

    def rhs(_t: float, state: np.ndarray) -> np.ndarray:
        temps = state[:-1]
        k_face = material.conductivity(0.5 * (temps[:-1] + temps[1:]))
        flux = k_face * areas / dr * (temps[1:] - temps[:-1])  # hacia el nodo i (de i+1 a i)
        heat = np.zeros(nodes)
        heat[:-1] += flux
        heat[1:] -= flux
        g_half = float(material.conductivity(temps[-1])) * area_s / (dr / 2)
        ts = _surface_temperature(g_half / area_s, temps[-1], t_medium, h_fn)
        q_out = h_fn(ts) * (ts - t_medium) * area_s
        heat[-1] -= q_out
        out = np.empty(nodes + 1)
        out[:-1] = heat / (material.volumetric_capacity(temps) * volumes)
        out[-1] = q_out
        return out

    events = []
    if stop_center_below is not None:

        def cooled(_t: float, state: np.ndarray) -> float:
            return state[0] - stop_center_below

        cooled.terminal = True
        events.append(cooled)
    y0 = np.append(np.full(nodes, float(t_initial)), 0.0)
    solution = solve_ivp(
        rhs, (0.0, t_end), y0, method="LSODA", lband=1, uband=1, dense_output=True,
        rtol=1e-8, atol=1e-6, events=events or None,
    )  # fmt: skip
    if not solution.success:
        raise RuntimeError(f"no convergió el enfriamiento: {solution.message}")
    t_last = float(solution.t[-1])
    return RadialResult(n, radius_m, t_last, radii, solution.sol, material, t_initial, volumes)


# ----------------------------------------------------------------------- casos del repo
def sphere_center_rate(
    diameter_m: float,
    h_fn: Callable[[float], float],
    material: Material | None = None,
    t_initial: float = 875.0,
    t_medium: float = 20.0,
    temperature: float = 720.0,
    nodes: int = 120,
) -> float:
    """Velocidad del centro de una bola al pasar por ``temperature`` (como NBS_RATE)."""
    result = quench_radial(SPHERE, diameter_m / 2, h_fn, material or from_steel(), t_initial,
                           t_medium, t_end=5000.0, nodes=nodes,
                           stop_center_below=temperature - 20.0)  # fmt: skip
    return result.rate_at(temperature)


def calibrate_scale(
    diameter_m: float, center_rate: float, shape: HShape | None = None, **kwargs
) -> float:
    """El factor de escala de ``shape`` que da esa velocidad en el centro (UN solo parámetro)."""

    base = shape or HShape()

    def gap(log_s: float) -> float:
        h_fn = base.scaled(math.exp(log_s))
        return sphere_center_rate(diameter_m, h_fn, **kwargs) - center_rate

    return math.exp(brentq(gap, math.log(0.05), math.log(50.0), xtol=1e-6))


# Sonda de Liščić/Petrofer: cilindro de Inconel 600 de 50 mm de diámetro y 200 mm de largo
# (L/D = 4: se trata como cilindro infinito, 1D radial), desde 850 °C a un baño de 28 °C; termopares
# en el centro y a 1 mm de la superficie. ΔT = T(centro) - T(1 mm bajo la superficie).
PROBE_RADIUS_M = 0.025
PROBE_DEPTH_M = 0.001
PROBE_T_INITIAL, PROBE_T_MEDIUM = 850.0, 28.0
PROBE_PUBLISHED = {"dT10": 91.0, "dTmax": 257.0, "t_dTmax": 41.0, "dT100": 67.0}  # Tabla 1


def probe_gradients(h_fn: Callable[[float], float], nodes: int = 200) -> dict[str, float]:
    """ΔT10, ΔTmax (con su tiempo) y ΔT100 de la sonda de Liščić con ese h(Ts)."""
    result = quench_radial(CYLINDER, PROBE_RADIUS_M, h_fn, INCONEL_600, PROBE_T_INITIAL,
                           PROBE_T_MEDIUM, t_end=150.0, nodes=nodes)  # fmt: skip
    r_tc = PROBE_RADIUS_M - PROBE_DEPTH_M

    def gradient(t: float) -> float:
        return result.temperature(t, 0.0) - result.temperature(t, r_tc)

    times = np.linspace(0.5, 150.0, 600)
    values = np.array([gradient(t) for t in times])
    i = int(np.argmax(values))
    return {"dT10": gradient(10.0), "dTmax": float(values[i]), "t_dTmax": float(times[i]),
            "dT100": gradient(100.0)}  # fmt: skip


__all__ = [
    "CYLINDER",
    "INCH",
    "INCONEL_600",
    "OIL_SHAPE",
    "PROBE_PUBLISHED",
    "PROBE_RADIUS_M",
    "SPHERE",
    "HShape",
    "Material",
    "RadialResult",
    "calibrate_scale",
    "constant_h",
    "from_steel",
    "probe_gradients",
    "quench_radial",
    "sphere_center_rate",
]
