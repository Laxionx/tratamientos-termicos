"""Guardas del modelo: fórmulas contra cálculo a mano y balances del equilibrio."""

from __future__ import annotations

import math

import pytest

from tratamientos import (
    destabilize,
    equilibrium_at,
    martensite_fraction,
    martensite_start,
)
from tratamientos.equilibrio import MOLAR_MASS, mole_fractions

STEEL = {"C": 0.4, "MN": 0.7, "NI": 1.8, "CR": 0.8, "MO": 0.25}


def test_ms_andrews_y_steven_haynes_a_mano():
    andrews = 539 - 423 * 0.4 - 30.4 * 0.7 - 17.7 * 1.8 - 12.1 * 0.8 - 7.5 * 0.25
    steven = 561 - 474 * 0.4 - 33 * 0.7 - 17 * 1.8 - 17 * 0.8 - 21 * 0.25
    assert martensite_start(STEEL) == pytest.approx(andrews, abs=1e-9)
    assert martensite_start(STEEL, "steven_haynes") == pytest.approx(steven, abs=1e-9)
    with pytest.raises(ValueError):
        martensite_start(STEEL, "otra")


def test_koistinen_marburger():
    assert martensite_fraction(200.0, 25.0) == pytest.approx(1 - math.exp(-0.011 * 175), 1e-12)
    assert martensite_fraction(100.0, 150.0) == 0.0


def test_fracciones_molares():
    x = mole_fractions({"C": 3.0, "CR": 20.0})
    moles = {
        "C": 3 / MOLAR_MASS["C"],
        "CR": 20 / MOLAR_MASS["CR"],
        "FE": 77 / MOLAR_MASS["FE"],
    }
    total = sum(moles.values())
    assert x == pytest.approx({e: n / total for e, n in moles.items()}, rel=1e-12)
    with pytest.raises(ValueError):
        mole_fractions({"W": 1.0})
    with pytest.raises(ValueError):
        mole_fractions({"C": -1.0})


@pytest.mark.usefixtures("database")
def test_equilibrio_conserva_la_masa():
    alloy = {"C": 2.9, "CR": 18.1, "MO": 1.8, "MN": 0.8, "SI": 1.2}
    eq = equilibrium_at(alloy, 1000)
    assert sum(eq.mass_fractions.values()) == pytest.approx(1.0, abs=1e-12)
    for element, wt in alloy.items():
        total = sum(
            f * eq.compositions_wt[p].get(element, 0.0) for p, f in eq.mass_fractions.items()
        )
        assert total == pytest.approx(wt, rel=1e-6), element


@pytest.mark.usefixtures("database")
def test_fracciones_de_fase_cierran():
    result = destabilize({"C": 2.9, "CR": 18.9, "SI": 0.7}, 1000)
    for basis in ("masa", "volumen"):
        total = result.carbides(basis) + result.retained_austenite(basis) + result.martensite(basis)
        assert total == pytest.approx(1.0, abs=1e-12)
    # El carburo M7C3 es menos denso: ocupa más volumen que masa.
    assert result.carbides("volumen") > result.carbides("masa")
