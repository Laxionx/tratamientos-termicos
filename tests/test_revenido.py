"""Fase 3b: revenido con Hollomon-Jaffe. Criterios fijados ANTES de digitalizar (12-10):

- Datos: fundición nodular de Salas Vicente et al. (2021), Metals 11(2) 297, CC BY; Figura 6
  digitalizada (60 puntos: 3 grupos × 4 temperaturas × 5 tiempos), lectura ±5 HV.
- Modelo: P = T (20 + log10 t), el de Hollomon y Jaffe; C = 18 solo como sensibilidad.
- Ajuste: por grupo, solo los revenidos de 1 h (4 temperaturas), interpolación lineal en P.
- Predicción: los revenidos de 10 min, 20 min, 5 h y 24 h cuyo P cae dentro de lo ajustado
  (12 por grupo, 36 en total), sin extrapolar.
- Tolerancia: ±25 HV (entre ±2 y ±4 HRC según la dureza). Corte: falla si quedan fuera más de
  la mitad.
"""

from __future__ import annotations

import math

import pytest

from tratamientos.revenido import (
    HardnessCurve,
    OutOfRange,
    equivalent_time_h,
    tempering_parameter,
)
from tratamientos.validacion import NODULAR_HV, NODULAR_TIMES_H

TOL_HV = 25.0
FIT_TIME = 1.0


def _curve(group: str, c: float = 20.0) -> HardnessCurve:
    tests = [
        (t, FIT_TIME, hv[NODULAR_TIMES_H.index(FIT_TIME)]) for t, hv in NODULAR_HV[group].items()
    ]
    return HardnessCurve.from_tests(tests, c)


def _predictions(c: float = 20.0) -> list[tuple[str, int, float, float, float]]:
    """(grupo, °C, h, medida, predicha) de los casos dentro del rango."""
    out = []
    for group, temps in NODULAR_HV.items():
        curve = _curve(group, c)
        for temp, values in temps.items():
            for time_h, measured in zip(NODULAR_TIMES_H, values, strict=True):
                if time_h == FIT_TIME or not curve.covers(temp, time_h):
                    continue
                out.append((group, temp, time_h, measured, curve.predict(temp, time_h)))
    return out


PREDICTIONS = _predictions()


def test_hay_36_predicciones_dentro_del_rango():
    assert len(PREDICTIONS) == 36


# Marcados a mano tras correr (12-10): a tiempos cortos la curva de 1 h predice menos dureza que la
# medida y a tiempos largos, más; el tiempo pesa más de lo que da C = 20.
FUERA = pytest.mark.xfail(strict=True, reason="fuera de ±25 HV")
FAILS = {
    ("agua", 500, 1 / 6), ("agua", 500, 5.0), ("agua", 600, 5.0), ("agua", 600, 24.0),
    ("agua", 700, 1 / 6), ("agua", 700, 1 / 3),
    ("aire", 500, 5.0), ("aire", 600, 24.0), ("aire", 700, 1 / 6), ("aire", 700, 1 / 3),
    ("agua tras 5 h", 400, 5.0), ("agua tras 5 h", 400, 24.0), ("agua tras 5 h", 600, 1 / 6),
    ("agua tras 5 h", 600, 1 / 3), ("agua tras 5 h", 600, 24.0), ("agua tras 5 h", 700, 1 / 6),
    ("agua tras 5 h", 700, 1 / 3),
}  # fmt: skip


@pytest.mark.parametrize(
    ("group", "temp", "time_h", "measured", "predicted"),
    [pytest.param(*row, marks=FUERA if row[:3] in FAILS else (),
                  id=f"{row[0]}-{row[1]}-{row[2]:.2f}h") for row in PREDICTIONS],
)  # fmt: skip
def test_prediccion(group, temp, time_h, measured, predicted):
    assert predicted == pytest.approx(measured, abs=TOL_HV)


def _outside(rows: list) -> list:
    return [r for r in rows if abs(r[4] - r[3]) > TOL_HV]


def test_corte():
    assert len(_outside(PREDICTIONS)) <= len(PREDICTIONS) / 2


def test_sensibilidad_c18():
    rows = _predictions(18.0)
    assert len(rows) == 36
    assert len(_outside(rows)) <= len(rows) / 2


# ------------------------------------------------------------------ guardas
def test_parametro_a_mano():
    assert tempering_parameter(600.0, 10.0) == pytest.approx(873.15 * 21.0)
    assert tempering_parameter(600.0, 1.0, c=18.0) == pytest.approx(873.15 * 18.0)
    with pytest.raises(ValueError):
        tempering_parameter(600.0, 0.0)


def test_tiempo_equivalente():
    t = equivalent_time_h(600.0, 2.0, 650.0)
    assert tempering_parameter(650.0, t) == pytest.approx(tempering_parameter(600.0, 2.0))
    assert t < 2.0  # más caliente, menos tiempo
    assert equivalent_time_h(600.0, 2.0, 600.0) == pytest.approx(2.0)


def test_curva_interpola_y_no_extrapola():
    curve = HardnessCurve.from_tests([(500.0, 1.0, 400.0), (600.0, 1.0, 300.0)])
    p_mid = (tempering_parameter(500.0, 1.0) + tempering_parameter(600.0, 1.0)) / 2
    temp_mid = p_mid / 20.0 - 273.15
    assert curve.predict(temp_mid, 1.0) == pytest.approx(350.0)
    assert curve.predict(500.0, 1.0) == pytest.approx(400.0)
    reverse = HardnessCurve.from_tests([(600.0, 1.0, 300.0), (500.0, 1.0, 400.0)])
    assert reverse.predict(temp_mid, 1.0) == pytest.approx(
        350.0
    )  # el orden de los ensayos no importa
    with pytest.raises(OutOfRange):
        curve.predict(700.0, 1.0)
    with pytest.raises(ValueError):
        HardnessCurve.from_tests([(500.0, 1.0, 400.0)])
    with pytest.raises(ValueError):
        HardnessCurve.from_tests([(500.0, 1.0, 400.0), (500.0, 1.0, 390.0)])


def test_datos_digitalizados_bien_copiados():
    # 60 puntos; en cada serie la dureza a 24 h es menor que a 10 min, salvo a 400 °C en el grupo
    # enfriado con aire, que casi no cambia (parte de 291 HV).
    count = 0
    for group, temps in NODULAR_HV.items():
        for temp, values in temps.items():
            count += len(values)
            assert all(100 < v < 600 for v in values)
            if not (group == "aire" and temp == 400):
                assert values[-1] < values[0], (group, temp)
    assert count == 60
    assert math.isclose(NODULAR_TIMES_H[0], 1 / 6)
