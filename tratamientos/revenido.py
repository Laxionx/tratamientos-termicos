"""Revenido: equivalencia entre tiempo y temperatura con el parámetro de Hollomon y Jaffe (1945).

    P = T · (C + log10 t)      T en K, t en horas

Dos revenidos con el mismo P dejan la misma dureza. La curva dureza-P se arma con los ensayos a un
solo tiempo (interpolación lineal en P) y predice la dureza a cualquier otro par tiempo-
temperatura cuyo P caiga dentro de lo ensayado; fuera de ese rango no extrapola. C = 20 es el
valor clásico; aquí 18 se usa solo como sensibilidad.

No sirve para los hierros blancos alto cromo: su endurecimiento secundario (la austenita retenida
que se transforma a 450-550 °C) rompe la equivalencia. Ver docs/fase3b-revenido.md.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

KELVIN = 273.15
C_HOLLOMON_JAFFE = 20.0


def tempering_parameter(temp_c: float, time_h: float, c: float = C_HOLLOMON_JAFFE) -> float:
    """P = T (C + log10 t), en K (sin dividir por 1000)."""
    if time_h <= 0:
        raise ValueError("el tiempo de revenido debe ser positivo")
    if temp_c <= -KELVIN:
        raise ValueError("temperatura imposible")
    return (temp_c + KELVIN) * (c + math.log10(time_h))


def equivalent_time_h(temp_c: float, time_h: float, new_temp_c: float,
                      c: float = C_HOLLOMON_JAFFE) -> float:  # fmt: skip
    """Tiempo a ``new_temp_c`` que deja el mismo P que ``time_h`` a ``temp_c``."""
    p = tempering_parameter(temp_c, time_h, c)
    return 10 ** (p / (new_temp_c + KELVIN) - c)


class OutOfRange(ValueError):
    """El P pedido cae fuera de los ensayos con que se armó la curva."""


@dataclass(frozen=True)
class HardnessCurve:
    """Dureza contra P, interpolada linealmente entre los ensayos (ordenados por P)."""

    p: tuple[float, ...]
    hardness: tuple[float, ...]
    c: float

    @classmethod
    def from_tests(cls, tests: Sequence[tuple[float, float, float]],
                   c: float = C_HOLLOMON_JAFFE) -> HardnessCurve:  # fmt: skip
        """``tests``: (temperatura °C, tiempo h, dureza). Hacen falta al menos dos."""
        if len(tests) < 2:
            raise ValueError("hacen falta al menos dos ensayos")
        pairs = sorted((tempering_parameter(t, h, c), hv) for t, h, hv in tests)
        ps = [p for p, _ in pairs]
        if len(set(ps)) != len(ps):
            raise ValueError("dos ensayos con el mismo P")
        return cls(tuple(ps), tuple(hv for _, hv in pairs), c)

    def predict(self, temp_c: float, time_h: float) -> float:
        p = tempering_parameter(temp_c, time_h, self.c)
        if not self.p[0] <= p <= self.p[-1]:
            raise OutOfRange(f"P = {p:.0f} fuera de lo ensayado ({self.p[0]:.0f}-{self.p[-1]:.0f})")
        return float(np.interp(p, self.p, self.hardness))

    def covers(self, temp_c: float, time_h: float) -> bool:
        return self.p[0] <= tempering_parameter(temp_c, time_h, self.c) <= self.p[-1]
