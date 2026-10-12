"""Cálculo de carga del horno: la mezcla de materias primas más barata que da la química objetivo.

Programación lineal (scipy, HiGHS). Cada material tiene su precio, su composición como rango
(mín., máx.) en % y, si se quiere, límites a su participación. La carga se calcula por tonelada
(las participaciones suman 1).

Modo robusto (por defecto, como Mędoń et al. 2023, Archives of Foundry Engineering 23(4)): la
química debe cumplirse para CUALQUIER contenido dentro de los rangos. Para el mínimo de un
elemento en la aleación se usan los contenidos mínimos de los materiales; para el máximo, los
máximos. Con ``robust=False`` se usan los puntos medios. Opcionalmente, un rendimiento por elemento
(fracción que queda en el metal) multiplica los contenidos; por defecto no hay pérdidas.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType

import numpy as np
from scipy.optimize import linprog


class ChargeError(ValueError):
    """No existe una carga que cumpla la química y los límites."""


@dataclass(frozen=True)
class Material:
    name: str
    price_per_t: float
    composition: Mapping[str, tuple[float, float]]  # elemento -> (mín., máx.) en %
    min_share: float = 0.0  # fracción de la carga
    max_share: float = 1.0

    def __post_init__(self) -> None:
        if not (math.isfinite(self.price_per_t) and self.price_per_t >= 0):
            raise ValueError(f"{self.name}: precio inválido {self.price_per_t}")
        if not 0.0 <= self.min_share <= self.max_share <= 1.0:
            raise ValueError(f"{self.name}: límites de participación inválidos")
        clean = {}
        for element, (lo, hi) in self.composition.items():
            if not 0.0 <= lo <= hi <= 100.0:
                raise ValueError(f"{self.name}: rango de {element} inválido ({lo}, {hi})")
            clean[element] = (float(lo), float(hi))
        object.__setattr__(self, "composition", MappingProxyType(clean))

    def content(self, element: str, bound: str) -> float:
        lo, hi = self.composition.get(element, (0.0, 0.0))
        return {"min": lo, "max": hi, "mid": (lo + hi) / 2}[bound]


@dataclass(frozen=True)
class ChargeResult:
    shares: Mapping[str, float]  # fracción de cada material
    price_per_t: float
    chemistry: Mapping[str, tuple[float, float]]  # elemento -> (mín., máx.) garantizado, %
    robust: bool

    def kg_per_t(self) -> dict[str, float]:
        return {name: 1000.0 * share for name, share in self.shares.items()}


@dataclass(frozen=True)
class Target:
    ranges: Mapping[str, tuple[float, float]]  # elemento -> (mín., máx.) en %; usar 0 o inf
    recoveries: Mapping[str, float] = field(default_factory=dict)  # elemento -> fracción

    def recovery(self, element: str) -> float:
        value = self.recoveries.get(element, 1.0)
        if not 0.0 < value <= 1.0:
            raise ValueError(f"rendimiento de {element} fuera de (0, 1]: {value}")
        return value


def optimize_charge(
    materials: Sequence[Material], target: Target, robust: bool = True
) -> ChargeResult:
    names = [m.name for m in materials]
    if len(set(names)) != len(names) or not materials:
        raise ValueError("materiales repetidos o lista vacía")
    lower, upper = ("min", "max") if robust else ("mid", "mid")
    a_ub, b_ub = [], []
    for element, (lo, hi) in target.ranges.items():
        r = target.recovery(element)
        if lo > 0:  # Σ a_min·x ≥ lo  ->  -Σ a_min·x ≤ -lo
            a_ub.append([-r * m.content(element, lower) for m in materials])
            b_ub.append(-lo)
        if math.isfinite(hi):
            a_ub.append([r * m.content(element, upper) for m in materials])
            b_ub.append(hi)
    result = linprog(
        c=[m.price_per_t for m in materials],
        A_ub=np.array(a_ub) if a_ub else None,
        b_ub=np.array(b_ub) if b_ub else None,
        A_eq=np.ones((1, len(materials))),
        b_eq=[1.0],
        bounds=[(m.min_share, m.max_share) for m in materials],
        method="highs",
    )
    if result.status != 0:
        raise ChargeError(f"no hay carga que cumpla la química y los límites: {result.message}")
    shares = {m.name: float(x) for m, x in zip(materials, result.x, strict=True)}
    chemistry = {}
    for element in target.ranges:
        r = target.recovery(element)
        lo = sum(r * m.content(element, lower) * shares[m.name] for m in materials)
        hi = sum(r * m.content(element, upper) * shares[m.name] for m in materials)
        chemistry[element] = (lo, hi)
    return ChargeResult(MappingProxyType(shares), float(result.fun),
                        MappingProxyType(chemistry), robust)  # fmt: skip
