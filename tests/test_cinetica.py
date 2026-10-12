"""Fase 1b. Tolerancias fijadas ANTES de mirar los números de la tabla (brief del 12-10):

1. Hipótesis cinética, sin ajuste: en Metals 9, 522 la AR baja con el tiempo (24 h < 4 h, en aire
   y en aceite) y a 24 h queda a ±10 puntos de la AR de equilibrio de la fase 1 (base masa).
2. Carburos a 24 h contra el equilibrio: ±5 puntos (se espera que falle).
3. Avrami con n = 1 ajustado solo a la serie en aceite de Metals 522 predice los experimentos 5
   (4 h, aceite) y 7 (8 h, aire) de Materials 12, 3252 a ±10 puntos. Es consistencia entre dos
   estudios del mismo laboratorio, no una validación independiente.
"""

from __future__ import annotations

import pytest

from tratamientos import destabilize
from tratamientos.cinetica import fit_avrami
from tratamientos.validacion import METALS_522_ALLOY, METALS_522_DATA, retained_cases

pytestmark = pytest.mark.usefixtures("database")


@pytest.fixture(scope="module")
def equilibrium():
    return destabilize(METALS_522_ALLOY, 1000)


@pytest.mark.parametrize("medium", list(METALS_522_DATA))
def test_hipotesis_cinetica(equilibrium, medium):
    data = METALS_522_DATA[medium]
    assert data[24][0] < data[4][0]
    ar_eq = 100 * equilibrium.retained_austenite("masa")
    assert data[24][0] == pytest.approx(ar_eq, abs=10.0)


@pytest.mark.xfail(strict=True, reason="carburos fuera del equilibrio: 46-53 % frente a 30 %")
@pytest.mark.parametrize("medium", list(METALS_522_DATA))
def test_carburos_a_24_horas(equilibrium, medium):
    carbides = 100 * equilibrium.carbides("masa")
    assert METALS_522_DATA[medium][24][1] == pytest.approx(carbides, abs=5.0)


# Resultado (12-10): los datos de Metals 522 quedan BAJO el equilibrio (2,2 frente a 10,6 % a 24 h)
# y ya a 4 h son bajos (6,6 %); el ajuste degenera (τ al límite) y predice ~4,5 % donde el otro
# estudio midió 34-42 %. Los dos estudios del mismo laboratorio no coinciden.
@pytest.mark.xfail(strict=True, reason="los dos estudios no coinciden: 6,6 % frente a 34,2 % a 4 h")
def test_avrami_predice_el_otro_estudio(equilibrium):
    oil = METALS_522_DATA["aceite"]
    fit = fit_avrami(list(oil), [v[0] for v in oil.values()],
                     100 * equilibrium.retained_austenite("masa"))  # fmt: skip
    other = {c.label: c for c in retained_cases()}
    for label, hours in (
        ("González-Pociño exp. 5 (1000 °C)", 4),
        ("González-Pociño exp. 7 (1000 °C)", 8),
    ):
        assert fit(hours) == pytest.approx(other[label].retained, abs=10.0), label


def test_avrami_recupera_parametros_sinteticos():
    true = fit_avrami([1.0, 2.0], [30.0, 20.0], 5.0)  # solo para construir la curva
    hours = [1, 3, 6, 12, 24]
    data = [true(h) for h in hours]
    fit = fit_avrami(hours, data, 5.0)
    assert fit.initial == pytest.approx(true.initial, rel=1e-6)
    assert fit.tau_h == pytest.approx(true.tau_h, rel=1e-6)
    with pytest.raises(ValueError):
        fit_avrami([0.0, 1.0], [10.0, 5.0], 2.0)
