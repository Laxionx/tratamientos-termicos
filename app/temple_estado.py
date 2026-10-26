"""«Estado de la operación» y «Prueba esto» de la pestaña Temple. Los chequeos son de dos tipos:
validez del cálculo (el rango validado con el NBS, la solución numérica contra la serie analítica,
la convergencia del integrador) y nada más: los rangos con fuente citada en el repo que cabrían
aquí (la velocidad crítica) son datos del material sin fuente, así que no se chequean. Los
experimentos parten del ejemplo de la barra lateral (los valores por defecto de `controles.DATOS`)
y llevan números calculados en vivo."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from calculo import (
    BIOT_COMPROBADO,
    TOL_ANALITICA,
    VALIDATED_IN,
    QuenchParams,
    QuenchView,
    analytic_check,
    run_quench,
)
from controles import DATOS, PREFIX
from dibujo import es
from estado import Fila, Prueba
from i18n import num_g, opt, t

PREFIJO = "q_"  # claves de los botones de esta pestaña


def filas_estado(view: QuenchView) -> list[Fila]:
    """Los chequeos del panel: validez del cálculo para estos datos."""
    lo, hi = VALIDATED_IN
    if view.in_validated_range:
        rango = Fila("ok", t("q.chk.rango.ok", d=es(view.params.diameter_in, 2), lo=es(lo, 2),
                             hi=es(hi, 2)), t("q.crit.rango"))  # fmt: skip
    else:
        rango = Fila("aviso", t("q.range", lo=es(lo, 2), hi=es(hi, 2)), t("q.crit.rango"))
    an = analytic_check(view)
    if not an.checked:
        lo_bi, hi_bi = (num_g(x) for x in BIOT_COMPROBADO)
        serie = Fila("aviso", t("q.chk.serie.fuera", bi=es(an.biot, 2), lo=lo_bi, hi=hi_bi),
                     t("q.crit.serie"))  # fmt: skip
    else:
        serie = Fila(
            "ok" if an.within else "aviso",
            t("q.chk.serie", err=es(100 * an.error, 3), tol=es(100 * TOL_ANALITICA, 1),
              bi=es(an.biot, 2), fo=es(an.fourier, 3)),
            t("q.crit.serie"),
        )  # fmt: skip
    center = view.crossings[0].time_s
    integra = Fila(
        "ok",
        t("q.chk.integra", t=es(center, 1), pct=es(100 * center / view.result.t_end, 1),
          tend=es(view.result.t_end, 0)),
        t("q.crit.integra"),
    )  # fmt: skip
    return [rango, serie, integra]


# ---------------------------------------------------------------- Prueba esto
@dataclass(frozen=True)
class ExperimentoTemple:
    """Un cambio al ejemplo. `base`: lo que ya se cambia antes (el punto de partida del texto);
    `cambios`: lo que fija el botón; `direcciones`: magnitud → +1 sube / −1 baja."""

    clave: str
    cambios: dict[str, Any]
    direcciones: dict[str, int]
    base: dict[str, Any]


EXPERIMENTOS_TEMPLE: tuple[ExperimentoTemple, ...] = (
    ExperimentoTemple("medio", {"medium": "aceite"},
                      {"t_centro": +1, "v_centro": -1, "v_sup": -1, "biot": -1, "razon": -1}, {}),
    ExperimentoTemple("tamano", {"diameter": 2.5},
                      {"t_centro": +1, "v_centro": -1, "biot": +1, "razon": +1}, {}),
    ExperimentoTemple("capa", {"compare": True, "critical": 100.0}, {"capa": -1},
                      {"compare": True}),
)  # fmt: skip


def valores_ejemplo() -> dict[str, Any]:
    return {d.key: d.default for d in DATOS}


def evaluar(**cambios: object) -> QuenchView:
    """El temple del ejemplo de la barra lateral con esos cambios (claves de `DATOS`)."""
    v = {**valores_ejemplo(), **cambios}
    return run_quench(QuenchParams(float(v["diameter"]), str(v["medium"]), bool(v["compare"]),
                                   float(v["critical"])))  # fmt: skip


def magnitudes(view: QuenchView) -> dict[str, float]:
    """Las magnitudes que comparan los experimentos."""
    c, _, s = view.crossings
    capa = view.critical.depth_mm if view.critical is not None else float("nan")
    return {"t_centro": c.time_s, "v_centro": c.rate, "v_sup": s.rate, "biot": view.biot,
            "razon": s.rate / c.rate, "capa": capa}  # fmt: skip


@lru_cache(maxsize=1)
def pares() -> tuple:
    """(experimento, vista del punto de partida, vista tras el cambio) de cada experimento."""
    return tuple(
        (e, evaluar(**e.base), evaluar(**{**e.base, **e.cambios})) for e in EXPERIMENTOS_TEMPLE
    )


def numeros(a: QuenchView, b: QuenchView) -> dict[str, str]:
    ma, mb = magnitudes(a), magnitudes(b)
    return {
        "d0": num_g(a.params.diameter_in), "d1": num_g(b.params.diameter_in),
        "t0": es(ma["t_centro"], 1), "t1": es(mb["t_centro"], 1),
        "r0": es(ma["v_centro"], 1), "r1": es(mb["v_centro"], 1),
        "s0": es(ma["v_sup"], 0), "s1": es(mb["v_sup"], 0),
        "b0": es(ma["biot"], 1), "b1": es(mb["biot"], 1),
        "k0": es(ma["razon"], 1), "k1": es(mb["razon"], 1),
        "c0": num_g(a.params.critical_rate), "c1": num_g(b.params.critical_rate),
        "depth": es(mb["capa"], 1), "radius": es(b.radius_mm, 1),
    }  # fmt: skip


def cambios_de_la_barra(e: ExperimentoTemple) -> dict[str, object]:
    """Los valores que el botón fija en la barra lateral: los cuatro datos, partiendo del
    ejemplo, así el resultado no depende de lo que hubiera antes."""
    v = {**valores_ejemplo(), **e.base, **e.cambios}
    return {PREFIX + k: (opt(str(x)) if k == "medium" else x) for k, x in v.items()}


def pruebas_temple() -> list[Prueba]:
    """Los experimentos, con los números del modelo y los valores que fija su botón."""
    return [
        Prueba(e.clave, t(f"q.exp.{e.clave}.titulo"), t(f"q.exp.{e.clave}.texto", **numeros(a, b)),
               cambios_de_la_barra(e))
        for e, a, b in pares()
    ]  # fmt: skip
