"""Fase 2b: temple con h(Ts) de la forma de Liščić 2016 (aceite quieto), un solo factor de escala.

Cortes fijados ANTES de correr (brief del 24-10):
1. NBS aceite: las 5 esferas con dato y no calibradas (1,00 a 2,77 in) dentro de ±15 % en la
   velocidad del centro a 720 °C y menor error medio absoluto que el h constante.
2. Sonda de Liščić (50 × 200 mm, Inconel 600, Kalenol 32 a 28 °C), predicción con el factor de
   escala calibrado en la esfera de 3/4 in, sin recalibrar: ΔT10, ΔTmax, su tiempo y ΔT100 dentro
   de ±20 % de la Tabla 1.
Resultado: AMBOS FALLAN (docs/fase2b-h-variable.md). Se documentan como xfail estricto con la causa.
"""

from __future__ import annotations

import functools

import numpy as np
import pytest

from tratamientos.temple import H_NBS, INCH, quench_sphere
from tratamientos.temple_ht import (
    CYLINDER,
    INCONEL_600,
    OIL_SHAPE,
    PROBE_PUBLISHED,
    PROBE_RADIUS_M,
    SPHERE,
    HShape,
    calibrate_scale,
    constant_h,
    probe_gradients,
    quench_radial,
    sphere_center_rate,
)
from tratamientos.validacion import NBS_RATE, nbs_diameters_in

DIAMETERS = nbs_diameters_in()
OIL = NBS_RATE["aceite"]
MEASURED = [(i, d, m) for i, (d, m) in enumerate(zip(DIAMETERS, OIL, strict=True)) if m is not None]
UNCALIBRATED = [(d, m) for i, d, m in MEASURED if i > 0]
SPHERE_TOL, PROBE_TOL = 0.15, 0.20
SCALE_EXPECTED = 2.6725  # factor calibrado con la esfera de 3/4 in (pico de 5.185 W/m²K)

SPHERE_FAILS = {  # diámetro (in, 2 decimales) -> error con h(Ts) (cifras de la corrida)
    1.00: "+24,4 %",
    1.36: "+50,0 %",
    1.87: "+36,5 %",
    2.35: "+33,1 %",
    2.77: "+24,5 %",
}
PROBE_FAILS = {
    "dT10": "369 °C frente a 91 (+306 %)",
    "dTmax": "370 °C frente a 257 (+44 %)",
    "t_dTmax": "10,5 s frente a 41 s (-74 %)",
    "dT100": "83 °C frente a 67 (+24 %)",
}
CAUSE = (
    "con el factor 2,67 que pide la esfera de 3/4 in (la velocidad del centro a 720 °C se decide "
    "con la superficie a 390-460 °C, en el flanco posterior al pico) el h queda demasiado alto"
)


@functools.cache
def _scale() -> float:
    return calibrate_scale(DIAMETERS[0] * INCH, OIL[0])


@functools.cache
def _sphere_rates(diameter_in: float) -> tuple[float, float]:
    constant = quench_sphere(diameter_in * INCH, H_NBS["aceite"]).rate_at(720.0)
    variable = sphere_center_rate(diameter_in * INCH, HShape().scaled(_scale()))
    return constant, variable


@functools.cache
def _probe(scale: float) -> dict[str, float]:
    return probe_gradients(HShape().scaled(scale))


# --------------------------------------------------------------------- solver y entradas
def test_forma_de_aceite_con_los_nodos_publicados():
    temps = [t for t, _ in OIL_SHAPE]
    assert temps == sorted(temps)
    assert len(OIL_SHAPE) == 5
    shape = HShape()
    assert shape(490.0) == 1940.0  # pico de Liščić 2016, Tabla 1
    assert shape(620.0) < shape(490.0)  # mínimo en qcr2, por debajo del pico
    assert shape(620.0) < shape(800.0)
    assert shape(1200.0) == shape(800.0)  # plana fuera de los nodos
    assert shape(20.0) == shape(150.0)
    assert shape.scaled(2.0)(490.0) == 3880.0


def test_inconel_en_los_puntos_publicados():
    assert INCONEL_600.conductivity(50.0) == pytest.approx(13.4)
    assert INCONEL_600.conductivity(300.0) == pytest.approx(17.8)
    assert INCONEL_600.conductivity(900.0) == pytest.approx(30.1)
    assert INCONEL_600.conductivity(600.0) == pytest.approx((21.7 + 25.9) / 2)  # hueco: interpola
    assert INCONEL_600.volumetric_capacity(50.0) == pytest.approx(451 * 8400)


@pytest.mark.parametrize("index", [0, 3, 6], ids=lambda i: f'{DIAMETERS[i]:.2f}"')
def test_h_constante_reproduce_el_modelo_actual(index):
    d = DIAMETERS[index] * INCH
    old = quench_sphere(d, H_NBS["aceite"]).rate_at(720.0)
    new = sphere_center_rate(d, constant_h(H_NBS["aceite"]))
    assert new == pytest.approx(old, rel=0.005)


@pytest.mark.parametrize("exponent", [SPHERE, CYLINDER], ids=["esfera", "cilindro"])
def test_conservacion_de_energia(exponent):
    result = quench_radial(exponent, 0.0127, HShape().scaled(2.0), INCONEL_600, 850.0, 28.0, 60.0)
    for t in (5.0, 20.0, 40.0, 60.0):
        assert result.heat_out(t) == pytest.approx(result.stored_loss(t), rel=2e-3)


def test_estabilidad_enfriamiento_monotono_y_acotado():
    result = quench_radial(CYLINDER, PROBE_RADIUS_M, HShape(), INCONEL_600, 850.0, 28.0, 150.0)
    centre = np.array([result.temperature(t, 0.0) for t in np.linspace(0.0, 150.0, 120)])
    assert np.all(np.diff(centre) <= 1e-6)
    assert centre.max() <= 850.0 + 1e-6
    assert centre.min() >= 28.0


def test_malla_mas_fina_no_cambia_el_resultado():
    d = DIAMETERS[2] * INCH
    h = HShape().scaled(2.0)
    coarse_rate = sphere_center_rate(d, h, nodes=120)
    assert sphere_center_rate(d, h, nodes=240) == pytest.approx(coarse_rate, rel=0.01)
    coarse, fine = probe_gradients(h, nodes=100), probe_gradients(h, nodes=200)
    assert fine["dTmax"] == pytest.approx(coarse["dTmax"], rel=0.02)


# ---------------------------------------------------------------------------- calibración
def test_calibracion_reproduce_la_esfera_de_tres_cuartos():
    constant, variable = _sphere_rates(DIAMETERS[0])
    assert variable == pytest.approx(OIL[0], rel=1e-3)
    assert constant == pytest.approx(OIL[0], rel=1e-3)
    assert _scale() == pytest.approx(SCALE_EXPECTED, rel=0.002)


# --------------------------------------------------------------------------- corte 1: NBS
def _sphere_param(d, measured):
    marks = []
    key = round(d, 2)
    if key in SPHERE_FAILS:
        reason = f"{SPHERE_FAILS[key]} con h(Ts): {CAUSE}"
        marks.append(pytest.mark.xfail(strict=True, reason=reason))
    return pytest.param(d, measured, marks=marks, id=f'{d:.2f}"')


@pytest.mark.parametrize(("diameter", "measured"), [_sphere_param(d, m) for d, m in UNCALIBRATED])
def test_corte_nbs_aceite_esfera_dentro_de_15_por_ciento(diameter, measured):
    _, variable = _sphere_rates(diameter)
    assert variable == pytest.approx(measured, rel=SPHERE_TOL)


@pytest.mark.xfail(strict=True, reason="MAE con h(Ts) 33,7 % frente a 11,3 % del h constante")
def test_corte_nbs_aceite_error_medio_menor_que_h_constante():
    def mae(index):
        return np.mean([abs(_sphere_rates(d)[index] - m) / m for d, m in UNCALIBRATED]) * 100

    assert mae(1) < mae(0)


def test_corte_nbs_aceite_cifras_documentadas():
    errs_c = [(_sphere_rates(d)[0] - m) / m * 100 for d, m in UNCALIBRATED]
    errs_v = [(_sphere_rates(d)[1] - m) / m * 100 for d, m in UNCALIBRATED]
    assert [round(e, 1) for e in errs_c] == pytest.approx([-2.7, 12.4, 10.2, 16.0, 15.1], abs=0.15)
    assert [round(e, 1) for e in errs_v] == pytest.approx([24.4, 50.0, 36.5, 33.1, 24.5], abs=0.15)
    assert np.mean(np.abs(errs_c)) == pytest.approx(11.3, abs=0.1)
    assert np.mean(np.abs(errs_v)) == pytest.approx(33.7, abs=0.1)


# ---------------------------------------------------------------- corte 2: sonda de Liščić
def _probe_param(name):
    marks = []
    if name in PROBE_FAILS:
        reason = f"{PROBE_FAILS[name]} (corte ±20 %): {CAUSE}"
        marks.append(pytest.mark.xfail(strict=True, reason=reason))
    return pytest.param(name, marks=marks, id=name)


@pytest.mark.parametrize("name", [_probe_param(n) for n in PROBE_PUBLISHED])
def test_corte_sonda_de_liscic_con_la_escala_calibrada(name):
    assert _probe(_scale())[name] == pytest.approx(PROBE_PUBLISHED[name], rel=PROBE_TOL)


def test_sonda_con_la_escala_calibrada_cifras_documentadas():
    got = _probe(_scale())
    assert got["dT10"] == pytest.approx(369.4, abs=1.0)
    assert got["dTmax"] == pytest.approx(369.9, abs=1.0)
    assert got["t_dTmax"] == pytest.approx(10.5, abs=0.5)
    assert got["dT100"] == pytest.approx(82.9, abs=0.5)
    for name in PROBE_FAILS:
        assert abs(got[name] / PROBE_PUBLISHED[name] - 1) > PROBE_TOL, name


def test_sonda_con_escala_uno_diagnostico_de_la_forma_no_es_un_corte():
    """Con el factor 1 (el h de Liščić tal cual), solo ΔTmax y su tiempo caen dentro de ±20 %."""
    got = _probe(1.0)
    assert got["dTmax"] == pytest.approx(249.2, abs=1.0)
    assert got["t_dTmax"] == pytest.approx(33.2, abs=0.5)
    assert got["dT10"] == pytest.approx(138.2, abs=1.0)  # la medida arranca ~5 s tras inmersión
    assert got["dT100"] == pytest.approx(51.1, abs=0.5)
    inside = [n for n in PROBE_PUBLISHED if abs(got[n] / PROBE_PUBLISHED[n] - 1) <= PROBE_TOL]
    assert inside == ["dTmax", "t_dTmax"]
