"""Desestabilización de un hierro blanco alto cromo: austenita retenida y carburos tras el temple.

Cadena (cada paso desde la literatura; ver docs/fase1-desestabilizacion.md):
1. Equilibrio a la temperatura de desestabilización (pycalphad + MatCalc): cuánto carburo hay y
   con qué composición queda la austenita. Supone que la permanencia alcanza el equilibrio.
2. Ms de esa austenita (Andrews 1965 o Steven y Haynes 1956).
3. Koistinen y Marburger hasta la temperatura final del enfriamiento: la austenita que no
   alcanza a transformarse queda retenida. No se modela el efecto del medio de temple ni la
   precipitación durante el enfriamiento, ni el revenido.

Las fracciones salen en masa y, con densidades aproximadas, en volumen.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from .equilibrio import AUSTENITE, DEFAULT_DATABASE, FERRITE, equilibrium_at
from .martensita import martensite_fraction, martensite_start

# g/cm³, aproximadas (valores de manual): solo para pasar de masa a volumen.
DENSITY = {AUSTENITE: 7.7, FERRITE: 7.7, "M7C3": 6.9, "M23C6": 7.0, "CEMENTITE": 7.7}
CARBIDE_DENSITY = 7.0  # otros carburos


def _density(phase: str) -> float:
    return DENSITY.get(phase, CARBIDE_DENSITY)


@dataclass(frozen=True)
class DestabilizationResult:
    temperature_c: float
    quench_c: float
    austenite_wt: Mapping[str, float]  # composición de la austenita a la temperatura
    ms_c: float
    ms_formula: str
    mass_fractions: Mapping[str, float]  # fases a la temperatura de desestabilización
    martensite_of_austenite: float  # fracción de esa austenita que transforma

    def _fractions(self, basis: str) -> dict[str, float]:
        if basis == "masa":
            return dict(self.mass_fractions)
        volumes = {p: f / _density(p) for p, f in self.mass_fractions.items()}
        total = sum(volumes.values())
        return {p: v / total for p, v in volumes.items()}

    def carbides(self, basis: str = "volumen") -> float:
        return sum(f for p, f in self._fractions(basis).items() if p not in (AUSTENITE, FERRITE))

    def retained_austenite(self, basis: str = "volumen") -> float:
        """Fracción del total (carburos incluidos) que queda como austenita retenida."""
        austenite = self._fractions(basis).get(AUSTENITE, 0.0)
        return austenite * (1.0 - self.martensite_of_austenite)

    def martensite(self, basis: str = "volumen") -> float:
        return self._fractions(basis).get(AUSTENITE, 0.0) * self.martensite_of_austenite


def destabilize(
    wt_pct: Mapping[str, float],
    temperature_c: float,
    quench_c: float = 25.0,
    ms_formula: str = "andrews",
    database: Path = DEFAULT_DATABASE,
) -> DestabilizationResult:
    eq = equilibrium_at(wt_pct, temperature_c, database)
    austenite = eq.austenite_wt
    ms = martensite_start(austenite, ms_formula)
    return DestabilizationResult(
        float(temperature_c),
        float(quench_c),
        MappingProxyType(dict(austenite)),
        ms,
        ms_formula,
        eq.mass_fractions,
        martensite_fraction(ms, quench_c),
    )
