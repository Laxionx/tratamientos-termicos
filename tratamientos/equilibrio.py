"""Equilibrio de fases con pycalphad y la base de aceros de MatCalc (mc_fe v2.059, ODbL 1.0).

La composición entra en % en peso y se pasa a fracción molar (pycalphad 0.11 no resuelve con
condiciones en fracción en peso). Las fases candidatas son la austenita (FCC_A1), la ferrita
(BCC_A2) y los carburos M7C3, M23C6, cementita, M3C2 y M6C. La base no se versiona: ver README.
"""

from __future__ import annotations

import warnings
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache, lru_cache
from pathlib import Path
from types import MappingProxyType

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE = ROOT / "tdb" / "mc_fe_v2.059.pycalphad.tdb"
MOLAR_MASS = {  # g/mol (IUPAC)
    "FE": 55.845, "C": 12.011, "CR": 51.996, "MO": 95.95, "MN": 54.938,
    "SI": 28.085, "NI": 58.693, "CU": 63.546,
}  # fmt: skip
ALLOYING = tuple(e for e in MOLAR_MASS if e != "FE")
PHASES = ("FCC_A1", "BCC_A2", "M7C3", "M23C6", "CEMENTITE", "M3C2", "M6C")
AUSTENITE, FERRITE = "FCC_A1", "BCC_A2"


def mole_fractions(wt_pct: Mapping[str, float]) -> dict[str, float]:
    """% en peso de los aleantes (Fe por diferencia) a fracción molar."""
    unknown = sorted(set(wt_pct) - set(ALLOYING))
    if unknown:
        raise ValueError(f"elementos no admitidos {unknown}; use {ALLOYING}")
    if any(x < 0 for x in wt_pct.values()) or sum(wt_pct.values()) >= 100:
        raise ValueError("composición imposible: negativa o que no deja hierro")
    grams = {e: float(x) for e, x in wt_pct.items() if x > 0}
    grams["FE"] = 100.0 - sum(grams.values())
    moles = {e: g / MOLAR_MASS[e] for e, g in grams.items()}
    total = sum(moles.values())
    return {e: n / total for e, n in moles.items()}


@cache
def _database(path: str):
    from pycalphad import Database

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # avisos de TYPE_DEFINITION de la base
        return Database(path)


@dataclass(frozen=True)
class PhaseEquilibrium:
    temperature_c: float
    mass_fractions: Mapping[str, float]  # fase -> fracción en masa (suman 1)
    compositions_wt: Mapping[str, Mapping[str, float]]  # fase -> elemento -> % en peso

    @property
    def austenite_wt(self) -> Mapping[str, float]:
        if AUSTENITE not in self.compositions_wt:
            raise ValueError(f"no hay austenita en equilibrio a {self.temperature_c} °C")
        return self.compositions_wt[AUSTENITE]

    @property
    def carbide_mass(self) -> float:
        return sum(f for p, f in self.mass_fractions.items() if p not in (AUSTENITE, FERRITE))


@lru_cache(maxsize=256)
def _solve(key: tuple[tuple[str, float], ...], temp_c: float, database: str) -> PhaseEquilibrium:
    from pycalphad import equilibrium
    from pycalphad import variables as v

    x = dict(key)
    db = _database(database)
    comps = ["FE", *x.keys() - {"FE"}, "VA"]
    phases = [p for p in PHASES if p in db.phases]
    conds = {v.T: temp_c + 273.15, v.P: 101325, v.N: 1}
    conds.update({v.X(e): f for e, f in x.items() if e != "FE"})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        eq = equilibrium(db, comps, phases, conds)
    names = eq.Phase.values.squeeze()
    amounts = eq.NP.values.squeeze()
    fractions = eq.X.values.squeeze()
    elements = [str(c) for c in eq.component.values]
    rows = [
        (str(name), float(amount), xs)
        for name, amount, xs in zip(names, amounts, fractions, strict=True)
        if name and np.isfinite(amount) and amount > 0
    ]
    if not rows:
        raise ValueError(f"pycalphad no encontró el equilibrio a {temp_c} °C")
    # Si hay dos FCC, la de menos carbono es la austenita y la otra un carburo MC.
    carbon = elements.index("C")
    fcc = sorted((r for r in rows if r[0] == AUSTENITE), key=lambda r: r[2][carbon])
    rows = [r for r in rows if r[0] != AUSTENITE] + fcc[:1] + [("MC", a, x) for _, a, x in fcc[1:]]
    masses: dict[str, float] = {}
    grams: dict[str, dict[str, float]] = {}
    for name, amount, xs in rows:
        bucket = grams.setdefault(name, {})
        for e, xi in zip(elements, xs, strict=True):
            bucket[e] = bucket.get(e, 0.0) + amount * xi * MOLAR_MASS[e]
        masses[name] = sum(bucket.values())
    total = sum(masses.values())
    compositions = {
        phase: MappingProxyType({e: 100.0 * g / masses[phase] for e, g in bucket.items()})
        for phase, bucket in grams.items()
    }
    return PhaseEquilibrium(
        float(temp_c),
        MappingProxyType({p: m / total for p, m in masses.items()}),
        MappingProxyType(compositions),
    )


def equilibrium_at(
    wt_pct: Mapping[str, float], temp_c: float, database: Path = DEFAULT_DATABASE
) -> PhaseEquilibrium:
    """Fases en equilibrio y su composición a ``temp_c`` (°C) para la aleación dada en % peso."""
    if not Path(database).is_file():
        raise FileNotFoundError(f"falta la base termodinámica {database}; ver README")
    x = mole_fractions(wt_pct)
    key = tuple(sorted((e, round(f, 12)) for e, f in x.items()))
    return _solve(key, float(temp_c), str(database))
