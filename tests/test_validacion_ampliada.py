"""Fase 1c: la cadena de desestabilización frente a datos NUEVOS de austenita retenida (AR), sin
reajustar nada. Corte fijado en la fase 1: ±10 puntos de AR por caso. Para los datos leídos de una
figura (Ortega-Cubillos), el corte se aplica SUMANDO el error de lectura declarado (±0,5 %): la
tolerancia es 10,5 puntos, para no castigar al modelo por lo que se midió con regla.

Resultado (docs/fase1c-validacion-ampliada.md): 9 de 18 casos comparables dentro del corte; 6 de 6
en los datos de tabla o texto y 3 de 12 en los digitalizados. Los fallos se documentan abajo.
"""

from __future__ import annotations

import functools

import pytest

from tratamientos import destabilize
from tratamientos.validacion import (
    ORTEGA_READ_ERROR,
    ORTEGA_REPEATED,
    TOLERANCES,
    extended_cases,
    retained_cases,
)

pytestmark = pytest.mark.usefixtures("database")

# Fallos esperados (modelo - publicado, en puntos de AR). No se maquillan ni se reajusta nada.
MO_ALTO = "Mo 1,9 %: la AR medida es 14-23 puntos mayor que la de equilibrio (hueco de la fase 1)"
A_900 = "a 900 °C el equilibrio da casi nada de AR y se midió 24-26 %: cinética, no equilibrio"
TIEMPO = "el modelo no tiene tiempo: la AR medida cambia con las horas a igual T y el modelo no"
FALLOS = {
    "Ortega bruto 900 °C 6 h": f"{A_900} (-21,0 puntos)",
    "Ortega bruto 1000 °C 6 h": f"{MO_ALTO} (-14,5)",
    "Ortega bruto 1000 °C 1 h": f"{TIEMPO}: 29 % a 1 h frente a 8,6 % (-20,6)",
    "Ortega bruto 1000 °C 2 h": f"{TIEMPO}: -16,6 puntos",
    "Ortega bruto 1000 °C 4 h": f"{MO_ALTO} (-15,5)",
    "Ortega recocido 900 °C 0.5 h": f"{A_900} (-23,0 puntos)",
    "Ortega recocido 1000 °C 0.5 h": f"{MO_ALTO} (-18,6)",
    "Ortega recocido 1100 °C 0.5 h": "por 0,2 puntos sobre 10,5 (-10,7): sin margen de lectura",
    "Ortega recocido 1050 °C 6 h": f"{TIEMPO}: 38 % a 6 h frente a 22 % a 2 h (-22,9 puntos)",
}
HITS_EXPECTED = 9
TOTAL_EXPECTED = 18
PHASE1_HITS, PHASE1_TOTAL = 7, 16  # docs/fase1-desestabilizacion.md

EXTENDED = extended_cases()
IN_CUT = [c for c in EXTENDED if c.in_cut]


@functools.cache
def _model_ar(composition: tuple, temperature_c: float, quench_c: float, basis: str) -> float:
    result = destabilize(dict(composition), temperature_c, quench_c)
    return 100 * result.retained_austenite(basis)


def _predict(case) -> float:
    key = tuple(sorted(case.composition.items()))
    return _model_ar(key, case.temperature_c, case.quench_c, case.basis)


def _tolerance(case) -> float:
    return TOLERANCES.retained_points + case.read_error


def _hit(case) -> bool:
    return abs(_predict(case) - case.retained) <= _tolerance(case)


def _param(case):
    if case.label in FALLOS:
        return pytest.param(case, marks=pytest.mark.xfail(strict=True, reason=FALLOS[case.label]))
    return case


@pytest.mark.parametrize("case", [_param(c) for c in IN_CUT], ids=lambda c: c.label)
def test_austenita_retenida_nueva(case):
    assert _predict(case) == pytest.approx(case.retained, abs=_tolerance(case))


def test_conteo_exacto_de_casos_nuevos():
    hits = [c.label for c in IN_CUT if _hit(c)]
    misses = [c.label for c in IN_CUT if not _hit(c)]
    assert (len(hits), len(IN_CUT)) == (HITS_EXPECTED, TOTAL_EXPECTED)
    assert sorted(misses) == sorted(FALLOS)


def test_conteo_por_origen_del_dato():
    tables = [c for c in IN_CUT if c.read_error == 0.0]
    figures = [c for c in IN_CUT if c.read_error > 0.0]
    assert (sum(map(_hit, tables)), len(tables)) == (6, 6)
    assert (sum(map(_hit, figures)), len(figures)) == (3, 12)


def test_conteo_junto_con_la_fase_1():
    hits = PHASE1_HITS + sum(map(_hit, IN_CUT))
    assert (hits, PHASE1_TOTAL + len(IN_CUT)) == (16, 34)
    assert len(retained_cases()) == PHASE1_TOTAL


@pytest.mark.xfail(strict=True, reason="9 de 18: justo la mitad, no más de la mitad")
def test_criterio_de_corte_mayoria_en_los_nuevos():
    hits = sum(map(_hit, IN_CUT))
    assert hits > len(IN_CUT) / 2, f"solo {hits} de {len(IN_CUT)} casos dentro del corte"


def test_error_de_lectura_solo_en_los_digitalizados():
    for case in EXTENDED:
        digitized = case.label.startswith("Ortega")
        assert case.read_error == (ORTEGA_READ_ERROR if digitized else 0.0), case.label
    assert ORTEGA_READ_ERROR == 0.5


def test_puntos_repetidos_de_las_figuras_coinciden():
    by_label = {c.label: c for c in EXTENDED}
    labels = {"bruto": "Ortega bruto 1000 °C 6 h", "recocido": "Ortega recocido 1050 °C 0.5 h"}
    for state, ((t, _hours), second_reading) in ORTEGA_REPEATED.items():
        case = by_label[labels[state]]
        assert case.temperature_c == t
        assert abs(case.retained - second_reading) <= case.read_error


def test_bases_y_fuera_del_corte():
    by_source = {}
    for c in EXTENDED:
        by_source.setdefault(c.source.split(" (")[0], set()).add(c.basis)
    assert by_source["Nayak, Mücklich y Guitar"] == {"volumen"}  # base no declarada
    assert by_source["Ortega-Cubillos, Nannetti-Bernardini, Fredel y Campos"] == {"volumen"}
    assert by_source["González, Borja Peral, Zafra y Fernández-Pariente"] == {"masa"}
    assert by_source["Fortini, Suman, Zanini y Cruciani"] == {"masa"}
    out = [c for c in EXTENDED if not c.in_cut]
    assert (len(EXTENDED), len(IN_CUT), len(out)) == (26, 18, 8)
    assert sum(c.retained is None for c in out) == 2  # AR no detectada: sin dato numérico


def test_tendencia_con_la_temperatura_en_ortega():
    by_label = {c.label: c for c in EXTENDED}
    low, high = by_label["Ortega bruto 1000 °C 6 h"], by_label["Ortega bruto 1100 °C 6 h"]
    assert high.retained > low.retained
    assert _predict(high) > _predict(low)
