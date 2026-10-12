"""Fase 2: temple de esferas. Tolerancias fijadas ANTES de correr (brief del 12-10):

1. Solución numérica contra la serie analítica de la esfera con convección: ±0,5 %.
2. NBS T295 (French y Klopsch 1925): con h calibrado en la esfera más chica de cada medio, la
   velocidad en el centro a 720 °C de las demás esferas a ±15 %. Corte: falla si más de la
   mitad de las predicciones se sale.
3. La ley de tamaño V·D^n = c del NBS: el n de las predicciones a ±0,15 de la Tabla 1 (1,75 en
   agua y 1,40 en aceite).
"""

from __future__ import annotations

import numpy as np
import pytest

from tratamientos.temple import (
    AUSTENITE,
    INCH,
    calibrate_h,
    grossmann_h,
    hardening,
    quench_sphere,
    sphere_analytic,
)
from tratamientos.validacion import (
    NBS_EXPONENT,
    NBS_RATE,
    NBS_T_INITIAL,
    NBS_T_MEDIUM,
    NBS_T_RATE,
    NBS_TOLERANCES,
    nbs_diameters_in,
)

DIAMETERS = nbs_diameters_in()


@pytest.mark.parametrize("biot", [0.1, 1.0, 10.0, 50.0])
def test_contra_la_solucion_analitica(biot):
    radius = 0.02
    result = quench_sphere(2 * radius, biot * AUSTENITE.k / radius)
    for fourier in (0.05, 0.2, 0.6):
        t = fourier * radius**2 / AUSTENITE.diffusivity
        for position in (0.0, 0.5, 1.0):
            numeric = (result.temperature(t, position) - 20.0) / (875.0 - 20.0)
            assert numeric == pytest.approx(sphere_analytic(biot, fourier, position), rel=5e-3)


@pytest.fixture(scope="module")
def predictions():
    out = {}
    for medium, rates in NBS_RATE.items():
        h = calibrate_h(DIAMETERS[0] * INCH, rates[0], NBS_T_RATE, NBS_T_INITIAL, NBS_T_MEDIUM)
        predicted = [
            quench_sphere(d * INCH, h, NBS_T_INITIAL, NBS_T_MEDIUM).rate_at(NBS_T_RATE)
            for d in DIAMETERS
        ]
        out[medium] = (h, predicted)
    return out


CASES = [(m, i) for m, rates in NBS_RATE.items() for i in range(1, 7) if rates[i] is not None]
# Resultado (12-10): el modelo enfría de más las esferas grandes, de +10 a +19 % (sin calor latente
# ni capa de vapor). Estas cuatro quedan fuera de ±15 %; el criterio de corte sí pasa (4 de 11).
FUERA = {
    ("agua", 4): "1,88 in: +18,8 %",
    ("agua", 6): "2,77 in: +19,4 %",
    ("aceite", 5): "2,35 in: +16,0 %",
    ("aceite", 6): "2,77 in: +15,1 %",
}
PARAMS = [
    pytest.param(m, i, marks=pytest.mark.xfail(strict=True, reason=FUERA[(m, i)]))
    if (m, i) in FUERA
    else (m, i)
    for m, i in CASES
]


@pytest.mark.parametrize(("medium", "index"), PARAMS)
def test_nbs_velocidad_en_el_centro(predictions, medium, index):
    _, predicted = predictions[medium]
    measured = NBS_RATE[medium][index]
    assert predicted[index] == pytest.approx(measured, rel=NBS_TOLERANCES["velocidad"])


def test_nbs_criterio_de_corte(predictions):
    misses = sum(
        abs(predictions[m][1][i] / NBS_RATE[m][i] - 1) > NBS_TOLERANCES["velocidad"]
        for m, i in CASES
    )
    assert misses <= len(CASES) / 2


@pytest.mark.parametrize("medium", list(NBS_RATE))
def test_nbs_ley_de_tamano(predictions, medium):
    _, predicted = predictions[medium]
    slope = np.polyfit(np.log(DIAMETERS), np.log(predicted), 1)[0]
    assert -slope == pytest.approx(NBS_EXPONENT[medium], abs=NBS_TOLERANCES["exponente"])


@pytest.mark.parametrize("medium", list(NBS_RATE))
def test_la_transcripcion_reproduce_el_exponente_del_nbs(medium):
    """Control de lectura: los datos transcritos dan el n que publica el NBS (±0,1)."""
    pairs = [(d, r) for d, r in zip(DIAMETERS, NBS_RATE[medium], strict=True) if r is not None]
    slope = np.polyfit(np.log([p[0] for p in pairs]), np.log([p[1] for p in pairs]), 1)[0]
    assert -slope == pytest.approx(NBS_EXPONENT[medium], abs=0.1)


def test_guardas_del_temple():
    result = quench_sphere(0.05, 2000.0)
    assert result.temperature(0.0, 0.0) == pytest.approx(875.0)
    rates = hardening(result, critical_rate=10.0)
    assert rates["superficie"][0] > rates["medio radio"][0] > rates["centro"][0]
    assert grossmann_h(2 * AUSTENITE.k) == pytest.approx(INCH)
    with pytest.raises(ValueError):
        quench_sphere(-0.05, 1000.0)
    with pytest.raises(ValueError):
        result.time_to(-50.0)


def test_tabla_de_bolas_coherente():
    from tratamientos.temple import H_NBS, ball_table

    rows = ball_table((1.0, 3.0, 5.0), H_NBS["agua"])
    centers = [rates["centro"] for _, rates in rows]
    assert centers[0] > centers[1] > centers[2]
    direct = quench_sphere(3.0 * INCH, H_NBS["agua"]).rate_at(720.0)
    assert rows[1][1]["centro"] == pytest.approx(direct, rel=1e-12)
