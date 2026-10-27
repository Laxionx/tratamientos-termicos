"""Cada dato de entrada se define una sola vez: arma la barra lateral y la tabla «Qué datos
necesita» de la guía, así las dos no se pueden desfasar. Sus textos están en `textos_es.py` y
`textos_en.py`, con las claves `dato.<clave>.label|meaning|source`."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st
from calculo import MEDIA, T_INITIAL, T_MEDIUM, QuenchParams
from i18n import current, int_num, num_g, opt, t, use

PREFIX = "dato_"


def _tx(text: str) -> str:
    """El texto de una clave de `textos_*`; si no es una clave, el propio texto."""
    try:
        return t(text)
    except KeyError:
        return text


@dataclass(frozen=True)
class Dato:
    key: str
    label_k: str
    unit_k: str
    lo: float
    hi: float
    default: float | bool | str
    step: float
    meaning_k: str
    source_k: str
    widget: str = "number"  # number | select | check
    options: tuple[str, ...] = ()

    @property
    def label(self) -> str:
        return _tx(self.label_k)

    @property
    def unit(self) -> str:
        return _tx(self.unit_k)

    @property
    def meaning(self) -> str:
        return _tx(self.meaning_k)

    @property
    def source(self) -> str:
        return _tx(self.source_k)

    @property
    def range_text(self) -> str:
        if self.widget == "select":
            return t("dato.or").join(opt(o) for o in self.options)
        if self.widget == "check":
            return t("yesno")
        return t("dato.range", lo=_num(self.lo), hi=_num(self.hi))

    @property
    def default_text(self) -> str:
        if self.widget == "check":
            return t("yes") if self.default else t("no")
        return opt(self.default) if isinstance(self.default, str) else _num(self.default)

    @property
    def help(self) -> str:
        unit = f" ({self.unit})" if self.unit else ""
        return t("dato.help", meaning=self.meaning, unit=unit, range=self.range_text,
                 source=self.source)  # fmt: skip


def _num(x: float) -> str:
    """Número en el formato del idioma: «1 000», «2,7» (es) o «1,000», «2.7» (en)."""
    return int_num(x) if float(x).is_integer() else num_g(x)


DATOS: tuple[Dato, ...] = (
    Dato("diameter", "dato.diameter.label", "unit.pulgadas", 0.5, 5.0, 2.0, 0.05,
         "dato.diameter.meaning", "dato.diameter.source"),
    Dato("medium", "dato.medium.label", "", 0, 0, "agua", 0,
         "dato.medium.meaning", "dato.medium.source", widget="select", options=MEDIA),
    Dato("compare", "dato.compare.label", "", 0, 1, False, 0,
         "dato.compare.meaning", "dato.compare.source", widget="check"),
    Dato("critical", "dato.critical.label", "°C/s", 1, 200, 20, 1,
         "dato.critical.meaning", "dato.critical.source"),
)  # fmt: skip
BY_KEY = {d.key: d for d in DATOS}
# Datos que la app fija: el h calibrado solo vale con estas dos temperaturas.
FIJOS = (
    ("fixed.austenitizing", "°C", T_INITIAL),
    ("fixed.medium", "°C", T_MEDIUM),
)


def _ask(d: Dato) -> float | bool | str:
    key, label = PREFIX + d.key, f"{d.label} ({d.unit})" if d.unit else d.label
    sb = st.sidebar
    if d.widget == "select":
        labels = [opt(o) for o in d.options]  # el valor del modelo (en español) se rotula aquí
        chosen = sb.selectbox(label, labels, labels.index(opt(str(d.default))), key=key,
                              help=d.help)  # fmt: skip
        if chosen is None:  # con un índice fijo no ocurre; los tipos de Streamlit 1.66 lo admiten
            return d.default
        return d.options[labels.index(chosen)]
    if d.widget == "check":
        return sb.checkbox(label, value=bool(d.default), key=key, help=d.help)
    lo, hi, v, step = (float(x) for x in (d.lo, d.hi, d.default, d.step))
    return sb.number_input(label, lo, hi, v, step, help=d.help, key=key)


def _relabel_selects(previous: str) -> None:
    """Al cambiar de idioma, cada lista conserva su elección: se pasa del rótulo del idioma
    anterior al del idioma actual (el valor guardado en la sesión es el rótulo)."""
    for d in DATOS:
        key = PREFIX + d.key
        if d.widget != "select" or key not in st.session_state:
            continue
        for raw in d.options:
            with use(previous):
                old = opt(raw)
            if old == st.session_state[key]:
                st.session_state[key] = opt(raw)
                break


def reset_to_example() -> None:
    """Vuelve todos los datos al ejemplo."""
    for k in [k for k in st.session_state if str(k).startswith(PREFIX)]:
        del st.session_state[k]


def sidebar_config() -> QuenchParams:
    """Lee la barra lateral y arma los parámetros del temple."""
    sb = st.sidebar
    seen = st.session_state.get("_lang_seen")
    if seen and seen != current():
        _relabel_selects(seen)
    st.session_state["_lang_seen"] = current()
    sb.button(t("sidebar.example"), on_click=reset_to_example, width="stretch")
    v = {d.key: _ask(d) for d in DATOS}
    sb.caption(t("sidebar.fixed", t0=_num(T_INITIAL), t1=_num(T_MEDIUM)))
    return QuenchParams(float(v["diameter"]), str(v["medium"]), bool(v["compare"]),
                        float(v["critical"]))  # fmt: skip


def data_table() -> pd.DataFrame:
    """La tabla «Qué datos necesita», hecha de las mismas definiciones que la barra lateral."""
    rows = [
        {
            t("col.dato"): d.label,
            t("col.unit"): d.unit,
            t("col.range"): d.range_text,
            t("col.example"): d.default_text,
            t("col.what"): d.meaning,
            t("col.how"): d.source[0].upper() + d.source[1:],
        }
        for d in DATOS
    ]
    rows += [
        {t("col.dato"): t(name), t("col.unit"): unit, t("col.range"): t("fixed.range"),
         t("col.example"): _num(value), t("col.what"): t("fixed.meaning"),
         t("col.how"): t("fixed.source")}
        for name, unit, value in FIJOS
    ]  # fmt: skip
    return pd.DataFrame(rows)
