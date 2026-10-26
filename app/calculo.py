"""Cálculo de lo que muestra la app, sin Streamlit: llama a `tratamientos.temple.quench_sphere` y
reparte su resultado en fotogramas y anillos. El esquema dibuja exactamente estos números."""

from __future__ import annotations

import functools
from dataclasses import dataclass

from tratamientos.temple import (
    H_NBS,
    INCH,
    POSITIONS,
    QuenchResult,
    grossmann_h,
    quench_sphere,
    sphere_analytic,
)
from tratamientos.validacion import (
    NBS_RATE,
    NBS_T_INITIAL,
    NBS_T_MEDIUM,
    NBS_T_RATE,
    NBS_TOLERANCES,
    nbs_diameters_in,
)

T_INITIAL, T_MEDIUM, T_MARK = NBS_T_INITIAL, NBS_T_MEDIUM, NBS_T_RATE  # 875, 20 y 720 °C
VALIDATED_IN = (0.75, 2.77)  # esferas del NBS: de la de calibración a la más grande medida
MEDIA = tuple(H_NBS)  # «agua» y «aceite»: solo los h calibrados con el NBS
RING_COUNT = 16  # bandas de radio del corte
FRAME_COUNT = 40  # fotogramas del reloj, más el del cruce de 720 °C del centro
SAMPLING_POWER = 2.0  # t_k = t_fin · (k / (N − 1))^p: más densos al principio
ACCEPTED = NBS_TOLERANCES["velocidad"]  # ±15 % de la validación
BIOT_COMPROBADO = (0.1, 50.0)  # Bi con que se comparó la solución numérica con la serie analítica
TOL_ANALITICA = 5e-3  # ±0,5 % en θ = (T - T_medio)/(T_inicial - T_medio)
NOMINAL_IN = (0.75, 1.00, 1.36, 1.61, 1.88, 2.35, 2.77)  # como los rotula docs/fase2-temple.md


@dataclass(frozen=True)
class QuenchParams:
    diameter_in: float = 2.0
    medium: str = "agua"
    compare: bool = False  # comparar con una velocidad crítica (dato del material)
    critical_rate: float = 20.0  # °C/s, sin fuente: dato del material, no del modelo


@dataclass(frozen=True)
class Crossing:
    name: str
    position: float  # fracción de radio: 0 centro, 1 superficie
    time_s: float  # cuándo baja a 720 °C
    rate: float  # °C/s al pasar por 720 °C


@dataclass(frozen=True)
class CriticalLayer:
    """Capa exterior donde la velocidad a 720 °C es ≥ la crítica (criterio simple, no dureza)."""

    position: float | None  # fracción de radio donde la velocidad iguala la crítica
    depth_mm: float  # espesor de la capa desde la superficie
    whole: bool  # toda la bola supera la crítica
    none: bool  # ni la superficie la alcanza


@dataclass(frozen=True)
class QuenchView:
    params: QuenchParams
    result: QuenchResult
    frame_times: tuple[float, ...]
    still_frame: int  # el fotograma en que el centro cruza 720 °C
    ring_positions: tuple[float, ...]  # fracción de radio del centro de cada banda
    ring_temps: tuple[tuple[float, ...], ...]  # [fotograma][anillo], °C
    crossings: tuple[Crossing, ...]
    critical: CriticalLayer | None

    @property
    def h(self) -> float:
        return self.result.h

    @property
    def radius_mm(self) -> float:
        return self.result.diameter_m / 2 * 1000.0

    @property
    def biot(self) -> float:
        """Bi = h·R/k: cuánto cuesta sacar el calor de adentro frente a cuánto cuesta que salga
        de la superficie al líquido."""
        return self.h * (self.result.diameter_m / 2) / self.result.steel.k

    @property
    def grossmann(self) -> float:
        """Severidad de temple de Grossmann H = h/(2k), en 1/pulgada."""
        return grossmann_h(self.h, self.result.steel)

    @property
    def in_validated_range(self) -> bool:
        return VALIDATED_IN[0] <= self.params.diameter_in <= VALIDATED_IN[1]


def ring_positions(count: int = RING_COUNT) -> tuple[float, ...]:
    """Fracción de radio del centro de cada banda (la 0 es la del centro de la bola)."""
    return tuple((i + 0.5) / count for i in range(count))


def sample_times(t_end: float, t_center: float, count: int = FRAME_COUNT) -> tuple[float, ...]:
    """Tiempos reales de los fotogramas: t_end·(k/(count−1))^p más el del cruce del centro."""
    times = {t_end * (k / (count - 1)) ** SAMPLING_POWER for k in range(count)}
    return tuple(sorted(times | {t_center}))


def critical_layer(result: QuenchResult, critical_rate: float, temperature: float = T_MARK
                   ) -> CriticalLayer:  # fmt: skip
    """Bisección sobre la velocidad a 720 °C (crece del centro a la superficie)."""
    if result.rate_at(temperature, 0.0) >= critical_rate:
        return CriticalLayer(0.0, result.diameter_m / 2 * 1000.0, True, False)
    if result.rate_at(temperature, 1.0) < critical_rate:
        return CriticalLayer(None, 0.0, False, True)
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if result.rate_at(temperature, mid) < critical_rate:
            lo = mid
        else:
            hi = mid
    position = (lo + hi) / 2
    return CriticalLayer(position, (1.0 - position) * result.diameter_m / 2 * 1000.0, False, False)


def run_quench(p: QuenchParams) -> QuenchView:
    """Lanza ValueError si los datos no son válidos (diámetro, medio o velocidad crítica)."""
    if p.medium not in H_NBS:
        raise ValueError(f"medio desconocido: {p.medium!r}; solo {', '.join(MEDIA)}")
    if not (p.diameter_in > 0 and p.critical_rate > 0):
        raise ValueError("el diámetro y la velocidad crítica deben ser positivos")
    result = quench_sphere(p.diameter_in * INCH, H_NBS[p.medium], T_INITIAL, T_MEDIUM)
    t_center = result.time_to(T_MARK, 0.0)
    times = sample_times(result.t_end, t_center)
    positions = ring_positions()
    temps = tuple(tuple(result.temperature(t, pos) for pos in positions) for t in times)
    crossings = tuple(
        Crossing(name, pos, result.time_to(T_MARK, pos), result.rate_at(T_MARK, pos))
        for name, pos in POSITIONS.items()
    )
    layer = critical_layer(result, p.critical_rate) if p.compare else None
    return QuenchView(p, result, times, times.index(t_center), positions, temps, crossings, layer)


@dataclass(frozen=True)
class AnalyticCheck:
    """La solución numérica contra la serie analítica de la esfera, en el centro y en el instante
    en que baja a 720 °C. Solo se calcula con un Biot dentro de lo comprobado (`checked`)."""

    biot: float
    fourier: float
    theta_model: float
    theta_series: float  # nan si no se calculó
    checked: bool

    @property
    def error(self) -> float:
        """Diferencia relativa de θ entre el modelo y la serie (nan si no se calculó)."""
        return self.theta_model / self.theta_series - 1.0 if self.checked else float("nan")

    @property
    def within(self) -> bool:
        return self.checked and abs(self.error) <= TOL_ANALITICA


def analytic_check(view: QuenchView) -> AnalyticCheck:
    """Compara θ del centro, a los segundos en que el modelo lo baja a 720 °C, con la serie de
    `sphere_analytic` (Incropera, cap. 5)."""
    res, bi = view.result, view.biot
    t_center = view.crossings[0].time_s
    fourier = res.steel.diffusivity * t_center / (res.diameter_m / 2) ** 2
    theta = (res.temperature(t_center, 0.0) - T_MEDIUM) / (T_INITIAL - T_MEDIUM)
    if not BIOT_COMPROBADO[0] <= bi <= BIOT_COMPROBADO[1]:
        return AnalyticCheck(bi, fourier, theta, float("nan"), False)
    return AnalyticCheck(bi, fourier, theta, sphere_analytic(bi, fourier, 0.0), True)


def curve(result: QuenchResult, position: float, points: int = 240) -> tuple[list, list]:
    """Temperatura contra tiempo en una posición, para el gráfico (tiempos más densos al inicio)."""
    times = [result.t_end * (k / (points - 1)) ** SAMPLING_POWER for k in range(points)]
    return times, [result.temperature(t, position) for t in times]


# ------------------------------------------------------------------ validación con el NBS
@dataclass(frozen=True)
class NbsRow:
    medium: str
    diameter_in: float
    measured: float  # °C/s en el centro a 720 °C
    model: float
    calibration: bool  # la esfera de 3/4": el h se calibró con ella
    nominal_in: float = 0.0  # el diámetro como lo rotula el NBS (el cálculo usa el exacto)

    @property
    def deviation(self) -> float:
        return self.model / self.measured - 1.0

    @property
    def inside(self) -> bool:
        return abs(self.deviation) <= ACCEPTED


@functools.lru_cache(maxsize=512)
def center_rate(diameter_in: float, medium: str) -> float:
    """Velocidad del centro a 720 °C (°C/s). Se recuerda: la validación no cambia nunca."""
    result = quench_sphere(diameter_in * INCH, H_NBS[medium], T_INITIAL, T_MEDIUM)
    return result.rate_at(T_MARK, 0.0)


def nbs_rows() -> tuple[NbsRow, ...]:
    """Las 14 esferas medidas con el modelo de cada una (11 predicciones y 3 de calibración,
    contando la de aceite sin medir como ausente)."""
    diameters = nbs_diameters_in()
    rows = []
    for medium, rates in NBS_RATE.items():
        for i, (d, measured) in enumerate(zip(diameters, rates, strict=True)):
            if measured is not None:
                rows.append(
                    NbsRow(medium, d, measured, center_rate(d, medium), i == 0, NOMINAL_IN[i])
                )
    return tuple(rows)


def model_curve(medium: str, lo: float, hi: float, points: int = 14) -> tuple[list, list]:
    diameters = [lo + (hi - lo) * k / (points - 1) for k in range(points)]
    return diameters, [center_rate(d, medium) for d in diameters]
