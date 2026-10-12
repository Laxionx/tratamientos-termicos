"""Temperatura de inicio de la martensita (Ms) y fracción transformada al enfriar.

- Andrews (1965), J. Iron Steel Inst. 203, 721: Ms = 539 - 423C - 30,4Mn - 17,7Ni - 12,1Cr - 7,5Mo
- Steven y Haynes (1956), J. Iron Steel Inst. 183, 349: Ms = 561 - 474C - 33Mn - 17Ni - 17Cr - 21Mo
- Koistinen y Marburger (1959), Acta Metall. 7, 59: fracción de martensita
  f = 1 - exp(-0,011·(Ms - T)) para T < Ms.
Composiciones en % en peso; temperaturas en °C. Las fórmulas de Ms se ajustaron para aceros; aquí
se aplican a la austenita de un hierro blanco, que es una extrapolación (ver docs).
"""

from __future__ import annotations

import math
from collections.abc import Mapping

KM_ALPHA = 0.011  # 1/°C
FORMULAS = ("andrews", "steven_haynes")
_COEFFICIENTS = {
    "andrews": (539.0, {"C": 423.0, "MN": 30.4, "NI": 17.7, "CR": 12.1, "MO": 7.5}),
    "steven_haynes": (
        561.0,
        {"C": 474.0, "MN": 33.0, "NI": 17.0, "CR": 17.0, "MO": 21.0},
    ),
}


def martensite_start(wt_pct: Mapping[str, float], formula: str = "andrews") -> float:
    if formula not in _COEFFICIENTS:
        raise ValueError(f"fórmula de Ms desconocida {formula!r}; use una de {FORMULAS}")
    base, terms = _COEFFICIENTS[formula]
    return base - sum(k * float(wt_pct.get(e, 0.0)) for e, k in terms.items())


def martensite_fraction(ms_c: float, temp_c: float, alpha: float = KM_ALPHA) -> float:
    """Fracción de la austenita que pasa a martensita al enfriar hasta ``temp_c``."""
    if temp_c >= ms_c:
        return 0.0
    return -math.expm1(-alpha * (ms_c - temp_c))
