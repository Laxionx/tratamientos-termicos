"""Validación de la fase 1 contra mediciones publicadas. Tolerancias fijadas ANTES de correr
(brief del 12-10 y tratamientos/validacion.py):

1. Austenita retenida (AR) predicha frente a la medida: ±10 puntos por caso (16 casos de 3
   artículos). Criterio de corte: si fallan más de la mitad, la cadena no predice.
2. Carburos frente a los medidos: ±5 puntos (Yu, González-Pociño y Tupaj).
3. Tendencia: la AR del modelo sube de 1000 a 1050 °C (Yu) y de 1000 a 1100 °C
   (González-Pociño), como en lo medido.
4. Tupaj: la Ms predicha cae en el rango medido según el enfriamiento (20-128 °C), y a -196 °C la
   AR del modelo es ≤ 5 % (en nitrógeno líquido no se observó AR).
"""

from __future__ import annotations

import pytest

from tratamientos import destabilize
from tratamientos.validacion import (
    GONZALEZ_ALLOY,
    TOLERANCES,
    TUPAJ_ALLOY,
    TUPAJ_CARBIDES,
    TUPAJ_MS,
    YU_1,
    retained_cases,
)

pytestmark = pytest.mark.usefixtures("database")

# Resultados (12-10), documentados en docs/fase1-desestabilizacion.md. Fallos esperados:
FALLOS = {
    "Yu M1 900 °C": "a 900 °C la precipitación no llega al equilibrio en 1 h (-14 puntos)",
    "Yu M2 900 °C": "a 900 °C la precipitación no llega al equilibrio en 1 h (-14 puntos)",
    "González-Pociño exp. 5 (1000 °C)": "aleación con 1,8 % Mo: subestima la AR (-24 puntos)",
    "González-Pociño exp. 7 (1000 °C)": "aleación con 1,8 % Mo: subestima la AR (-31 puntos)",
    "González-Pociño exp. 4 (1100 °C)": "aleación con 1,8 % Mo: subestima la AR (-26 puntos)",
    "Higuera-Cobos aire": "solo se publican C y Cr: Ms de 296 °C, casi sin AR (-23 puntos)",
    "Higuera-Cobos agua": "solo se publican C y Cr: Ms de 296 °C, casi sin AR (-25 puntos)",
    "Higuera-Cobos aceite": "solo se publican C y Cr: Ms de 296 °C, casi sin AR (-32 puntos)",
    "Higuera-Cobos aire y CO2 a -80 °C": "solo se publican C y Cr (-13 puntos)",
}
FALLOS_CARBUROS = {
    "González-Pociño exp. 5 (1000 °C)": "el modelo da 29 % de carburos frente a 37 % medido",
    "González-Pociño exp. 7 (1000 °C)": "el modelo da 29 % de carburos frente a 39 % medido",
    "González-Pociño exp. 2 (1100 °C)": "el modelo da 27 % frente a 48 % (en el exp. 4, 30 %)",
}


def _param(case, fallos):
    if case.label in fallos:
        return pytest.param(case, marks=pytest.mark.xfail(strict=True, reason=fallos[case.label]))
    return case


CASES = retained_cases()


def _predict(case):
    result = destabilize(case.composition, case.temperature_c, case.quench_c)
    return 100 * result.retained_austenite(case.basis), 100 * result.carbides(case.basis)


@pytest.mark.parametrize("case", [_param(c, FALLOS) for c in CASES], ids=lambda c: c.label)
def test_austenita_retenida(case):
    retained, _ = _predict(case)
    assert retained == pytest.approx(case.retained, abs=TOLERANCES.retained_points)


@pytest.mark.xfail(strict=True, reason="7 de 16 casos dentro de ±10 puntos: la cadena no predice")
def test_criterio_de_corte_la_mayoria_acierta():
    hits = sum(abs(_predict(c)[0] - c.retained) <= TOLERANCES.retained_points for c in CASES)
    assert hits > len(CASES) / 2, f"solo {hits} de {len(CASES)} casos dentro de ±10 puntos"


@pytest.mark.parametrize(
    "case",
    [_param(c, FALLOS_CARBUROS) for c in CASES if c.carbides is not None],
    ids=lambda c: c.label,
)
def test_carburos(case):
    _, carbides = _predict(case)
    assert carbides == pytest.approx(case.carbides, abs=TOLERANCES.carbide_points)


def test_tendencia_con_la_temperatura():
    def ar(alloy, t, basis):
        return destabilize(alloy, t).retained_austenite(basis)

    assert ar(YU_1, 1050, "volumen") > ar(YU_1, 1000, "volumen")
    assert ar(GONZALEZ_ALLOY, 1100, "masa") > ar(GONZALEZ_ALLOY, 1000, "masa")


def test_tupaj_ms():
    result = destabilize(TUPAJ_ALLOY, 1000)
    assert min(TUPAJ_MS.values()) <= result.ms_c <= max(TUPAJ_MS.values())


@pytest.mark.xfail(strict=True, reason="el modelo da 35,7 % de carburos frente a 29,2-30,7 %")
def test_tupaj_carburos():
    result = destabilize(TUPAJ_ALLOY, 1000)
    low, high = TUPAJ_CARBIDES
    expected = (low + high) / 2
    tolerance = TOLERANCES.carbide_points
    assert 100 * result.carbides("volumen") == pytest.approx(expected, abs=tolerance)


def test_tupaj_nitrogeno_liquido_casi_sin_austenita():
    result = destabilize(TUPAJ_ALLOY, 1000, quench_c=-196.0)
    assert 100 * result.retained_austenite("volumen") <= TOLERANCES.liquid_nitrogen_max
