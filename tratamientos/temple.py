"""Temple de una bola: conducción transitoria radial en una esfera con convección en la superficie.

ρ·cp·∂T/∂t = (1/r²)·∂(k r² ∂T/∂r)/∂r, con -k ∂T/∂r = h (T - T_medio) en r = R. Se resuelve por
volúmenes finitos en N capas esféricas e integración implícita (BDF). Propiedades constantes: las
de la austenita según EN 1993-1-2 (Eurocódigo 3), porque entre la austenización y unos 700 °C el
acero sigue austenítico: k = 27,3 W/m·K (T ≥ 800 °C), cp = 545 + 17.820/(875 - 731) = 669 J/kg·K
y ρ = 7.850 kg/m³. No se modela el calor latente de la transformación ni la ebullición: el
coeficiente h es efectivo y constante. Ver docs/fase2-temple.md.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

INCH = 0.0254  # m
POSITIONS = {"centro": 0.0, "medio radio": 0.5, "superficie": 1.0}


@dataclass(frozen=True)
class Steel:
    k: float = 27.3  # W/m·K
    rho: float = 7850.0  # kg/m³
    cp: float = 545.0 + 17820.0 / (875.0 - 731.0)  # J/kg·K

    @property
    def diffusivity(self) -> float:
        return self.k / (self.rho * self.cp)


AUSTENITE = Steel()


@dataclass(frozen=True)
class QuenchResult:
    diameter_m: float
    h: float
    t_initial: float
    t_medium: float
    steel: Steel
    _temperature: Callable[[float], np.ndarray] = field(repr=False)
    radii: np.ndarray = field(repr=False)
    t_end: float = 0.0

    def temperature(self, time_s: float, position: float = 0.0) -> float:
        """Temperatura (°C) a la fracción de radio ``position`` (0 centro, 1 superficie)."""
        nodes = self._temperature(time_s)
        if position >= 1.0:
            return self._surface(nodes)
        return float(np.interp(position * self.diameter_m / 2, self.radii, nodes))

    def _surface(self, nodes: np.ndarray) -> float:
        dr = 2 * (self.diameter_m / 2 - self.radii[-1])
        g = self.steel.k / (dr / 2)
        return float((g * nodes[-1] + self.h * self.t_medium) / (g + self.h))

    def time_to(self, temperature: float, position: float = 0.0) -> float:
        """Segundos hasta que esa posición baja a ``temperature``."""

        def gap(t: float) -> float:
            return self.temperature(t, position) - temperature

        if gap(self.t_end) > 0:
            raise ValueError(f"no llega a {temperature} °C en {self.t_end:.0f} s")
        return float(brentq(gap, 0.0, self.t_end, xtol=1e-9))

    def rate_at(self, temperature: float, position: float = 0.0) -> float:
        """Velocidad de enfriamiento (°C/s, positiva) al pasar por ``temperature``."""
        t = self.time_to(temperature, position)
        dt = 1e-4 * max(t, 1e-3)
        return (self.temperature(t - dt, position) - self.temperature(t + dt, position)) / (2 * dt)


def quench_sphere(
    diameter_m: float,
    h: float,
    t_initial: float = 875.0,
    t_medium: float = 20.0,
    steel: Steel = AUSTENITE,
    nodes: int = 120,
    t_end: float | None = None,
) -> QuenchResult:
    """Enfría una esfera de diámetro ``diameter_m`` en un medio con coeficiente ``h`` (W/m²K)."""
    if not (diameter_m > 0 and h > 0 and nodes >= 10):
        raise ValueError("diámetro y h positivos, y al menos 10 nodos")
    radius = diameter_m / 2
    edges = np.linspace(0.0, radius, nodes + 1)
    radii = (edges[:-1] + edges[1:]) / 2
    dr = edges[1] - edges[0]
    volumes = 4 / 3 * math.pi * (edges[1:] ** 3 - edges[:-1] ** 3)
    areas = 4 * math.pi * edges[1:-1] ** 2
    g_inner = steel.k * areas / dr  # W/K entre nodos vecinos
    area_s = 4 * math.pi * radius**2
    g_surface = 1.0 / (1.0 / (steel.k * area_s / (dr / 2)) + 1.0 / (h * area_s))
    capacity = steel.rho * steel.cp * volumes
    matrix = np.zeros((nodes, nodes))
    for i, g in enumerate(g_inner):
        matrix[i, i] -= g
        matrix[i, i + 1] += g
        matrix[i + 1, i + 1] -= g
        matrix[i + 1, i] += g
    matrix[-1, -1] -= g_surface
    matrix /= capacity[:, None]
    forcing = np.zeros(nodes)
    forcing[-1] = g_surface * t_medium / capacity[-1]

    def rhs(_t: float, temps: np.ndarray) -> np.ndarray:
        return matrix @ temps + forcing

    if t_end is None:
        tau = radius**2 / steel.diffusivity + steel.rho * steel.cp * radius / (3 * h)
        t_end = 3.0 * tau
    solution = solve_ivp(rhs, (0.0, t_end), np.full(nodes, float(t_initial)), method="BDF",
                         jac=matrix, dense_output=True, rtol=1e-8, atol=1e-6)  # fmt: skip
    if not solution.success:
        raise RuntimeError(f"no convergió el enfriamiento: {solution.message}")
    return QuenchResult(diameter_m, h, t_initial, t_medium, steel, solution.sol, radii,
                        float(t_end))  # fmt: skip


def calibrate_h(
    diameter_m: float,
    center_rate: float,
    temperature: float = 720.0,
    t_initial: float = 875.0,
    t_medium: float = 20.0,
    steel: Steel = AUSTENITE,
) -> float:
    """El h que da esa velocidad de enfriamiento en el centro al pasar por ``temperature``."""

    def gap(log_h: float) -> float:
        result = quench_sphere(diameter_m, math.exp(log_h), t_initial, t_medium, steel)
        return result.rate_at(temperature) - center_rate

    return math.exp(brentq(gap, math.log(10.0), math.log(2e5), xtol=1e-6))


def grossmann_h(h: float, steel: Steel = AUSTENITE) -> float:
    """Severidad de temple de Grossmann H = h/(2k), en 1/pulgada."""
    return h / (2 * steel.k) * INCH


def sphere_analytic(biot: float, fourier: float, r_star: float = 0.0, terms: int = 200) -> float:
    """θ/θ_i de una esfera con convección (serie clásica; Incropera, cap. 5)."""
    total = 0.0
    for n in range(terms):
        lo, hi = n * math.pi + 1e-9, (n + 1) * math.pi - 1e-9
        zeta = brentq(lambda z: 1 - z / math.tan(z) - biot, lo, hi)
        c = 4 * (math.sin(zeta) - zeta * math.cos(zeta)) / (2 * zeta - math.sin(2 * zeta))
        shape = 1.0 if r_star == 0 else math.sin(zeta * r_star) / (zeta * r_star)
        total += c * math.exp(-(zeta**2) * fourier) * shape
    return total


def hardening(result: QuenchResult, critical_rate: float, temperature: float = 720.0) -> dict:
    """Velocidad en cada posición y si supera la velocidad crítica de temple (dato del material)."""
    rates = {name: result.rate_at(temperature, pos) for name, pos in POSITIONS.items()}
    return {name: (rate, rate >= critical_rate) for name, rate in rates.items()}


# h efectivos calibrados con la esfera de 3/4 in del NBS (French y Klopsch 1925): agua y aceite
# quietos a 20 °C, desde 875 °C. Son efectivos: incluyen lo que el modelo no tiene.
H_NBS = {"agua": 6840.0, "aceite": 1657.0}


def ball_table(
    diameters_in: tuple[float, ...], h: float, temperature: float = 720.0, **kwargs
) -> list[tuple[float, dict[str, float]]]:
    """Velocidad de enfriamiento (°C/s) al pasar por ``temperature`` en cada posición, por bola."""
    rows = []
    for d in diameters_in:
        result = quench_sphere(d * INCH, h, **kwargs)
        rows.append((d, {n: result.rate_at(temperature, p) for n, p in POSITIONS.items()}))
    return rows
