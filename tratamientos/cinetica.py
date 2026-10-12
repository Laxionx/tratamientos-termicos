"""Fase 1b: aproximación al equilibrio con el tiempo de permanencia (Avrami/JMAK).

AR(t) = AR_eq + (AR_0 - AR_eq)·exp(-(t/τ)^n), con AR_eq la austenita retenida de equilibrio de la
fase 1. Con n fijo se ajustan AR_0 y τ a una serie medida a una sola temperatura. No se extrapola a
otras temperaturas ni aleaciones (ver docs/fase1b-cinetica.md).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares


@dataclass(frozen=True)
class AvramiFit:
    equilibrium: float  # AR de equilibrio (dato, de la fase 1)
    initial: float  # AR_0 ajustada
    tau_h: float  # tiempo característico (h)
    n: float  # exponente (fijo)
    rmse: float

    def __call__(self, hours: float) -> float:
        decay = math.exp(-((hours / self.tau_h) ** self.n))
        return self.equilibrium + (self.initial - self.equilibrium) * decay


def fit_avrami(
    hours: Sequence[float], retained: Sequence[float], equilibrium: float, n: float = 1.0
) -> AvramiFit:
    t, y = np.asarray(hours, float), np.asarray(retained, float)
    if t.size < 2 or t.shape != y.shape or np.any(t <= 0):
        raise ValueError("al menos 2 tiempos positivos, uno por medición")

    def residuals(p: np.ndarray) -> np.ndarray:
        initial, log_tau = p
        decay = np.exp(-((t / math.exp(log_tau)) ** n))
        return equilibrium + (initial - equilibrium) * decay - y

    guess = np.array([max(y.max(), equilibrium), math.log(float(np.median(t)))])
    result = least_squares(residuals, guess, bounds=([0.0, -10.0], [100.0, 10.0]))
    rmse = float(np.sqrt(np.mean(result.fun**2)))
    return AvramiFit(equilibrium, float(result.x[0]), math.exp(result.x[1]), n, rmse)
