"""Fase 3a: cálculo de carga. Tolerancias fijadas ANTES de correr (brief del 12-10):

1. Contra Mędoń et al. (2023): precios publicados de W1, W8, W15 y de la carga con mínimo 10 % de
   chatarra (W16) a ±1 %; participación de cada material en las 19 cargas a ±2 puntos.
2. Guardas: la química garantizada cumple el objetivo, las participaciones suman 1, el óptimo de un
   caso de 3 materiales coincide con una búsqueda exhaustiva, y una carga imposible avisa.
"""

from __future__ import annotations

import itertools

import numpy as np
import pytest

from tratamientos.carga import ChargeError, Material, Target, optimize_charge
from tratamientos.validacion import (
    AFE_LIMITS,
    AFE_MATERIALS,
    AFE_PRICE_STEEL_10,
    AFE_PRICES,
    AFE_SHARES,
    AFE_TARGET,
)

TARGET = Target(AFE_TARGET)


def _materials(limits: dict) -> list[Material]:
    return [
        Material(name, price, comp, *limits.get(name, (0.0, 1.0)))
        for name, (price, comp) in AFE_MATERIALS.items()
    ]


def _solve(batch: str):
    return optimize_charge(_materials(AFE_LIMITS[batch]), TARGET)


@pytest.mark.parametrize("batch", list(AFE_PRICES))
def test_precios_publicados(batch):
    assert _solve(batch).price_per_t == pytest.approx(AFE_PRICES[batch], rel=0.01)


def test_precio_con_minimo_de_chatarra():
    assert _solve("W16").price_per_t == pytest.approx(AFE_PRICE_STEEL_10, rel=0.01)


@pytest.mark.parametrize("batch", list(AFE_SHARES))
def test_participaciones_de_las_19_cargas(batch):
    shares = _solve(batch).shares
    published = AFE_SHARES[batch]
    for name in AFE_MATERIALS:
        assert 100 * shares[name] == pytest.approx(published.get(name, 0.0), abs=2.0), name


@pytest.mark.parametrize("batch", list(AFE_LIMITS))
def test_la_quimica_garantizada_cumple(batch):
    result = _solve(batch)
    assert sum(result.shares.values()) == pytest.approx(1.0, abs=1e-9)
    for element, (lo, hi) in AFE_TARGET.items():
        low, high = result.chemistry[element]
        assert low >= lo - 1e-7 and high <= hi + 1e-7, element


def test_robusto_cuesta_lo_mismo_o_mas_que_con_puntos_medios():
    mid = optimize_charge(_materials({}), TARGET, robust=False)
    assert _solve("W1").price_per_t >= mid.price_per_t - 1e-9


def test_optimo_igual_a_busqueda_exhaustiva():
    materials = [
        Material("A", 100.0, {"C": (0.2, 0.2), "CR": (0.0, 0.0)}),
        Material("B", 400.0, {"C": (2.0, 2.0), "CR": (20.0, 20.0)}),
        Material("C", 900.0, {"C": (1.0, 1.0), "CR": (60.0, 60.0)}),
    ]
    target = Target({"C": (1.0, 3.0), "CR": (15.0, 25.0)})
    best = np.inf
    grid = np.linspace(0, 1, 401)
    for a, b in itertools.product(grid, grid):
        c = 1 - a - b
        if c < -1e-12:
            continue
        carbon = 0.2 * a + 2.0 * b + 1.0 * c
        chromium = 20.0 * b + 60.0 * c
        if 1.0 <= carbon <= 3.0 and 15.0 <= chromium <= 25.0:
            best = min(best, 100 * a + 400 * b + 900 * c)
    assert optimize_charge(materials, target).price_per_t == pytest.approx(best, rel=2e-3)


def test_carga_imposible_avisa():
    only_steel = [Material("Acero", 2200.0, {"C": (0.1, 0.2)})]
    with pytest.raises(ChargeError):
        optimize_charge(only_steel, Target({"C": (1.8, 2.4)}))
    with pytest.raises(ValueError):
        Material("X", -1.0, {})
    with pytest.raises(ValueError):
        Material("X", 1.0, {"C": (2.0, 1.0)})


def test_modo_puntos_medios_a_mano():
    # Cr en A de 0 a 0 y en B de 10 a 30 (medio 20): para 15 % de Cr con puntos medios hace falta
    # 75 % de B; en modo robusto (mínimo 10) haría falta 150 %, imposible.
    materials = [
        Material("A", 100.0, {"CR": (0.0, 0.0)}),
        Material("B", 300.0, {"CR": (10.0, 30.0)}),
    ]
    mid = optimize_charge(materials, Target({"CR": (15.0, 100.0)}), robust=False)
    assert mid.shares["B"] == pytest.approx(0.75, abs=1e-9)
    assert mid.price_per_t == pytest.approx(0.25 * 100 + 0.75 * 300, abs=1e-6)
    with pytest.raises(ChargeError):
        optimize_charge(materials, Target({"CR": (15.0, 100.0)}))
