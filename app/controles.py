"""Cada dato de entrada se define una sola vez: arma la barra lateral y la tabla «Qué datos
necesita» de la guía, así las dos no se pueden desfasar."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st
from calculo import MEDIA, T_INITIAL, T_MEDIUM, QuenchParams

PREFIX = "dato_"


@dataclass(frozen=True)
class Dato:
    key: str
    label: str
    unit: str
    lo: float
    hi: float
    default: float | bool | str
    step: float
    meaning: str
    source: str
    widget: str = "number"  # number | select | check
    options: tuple[str, ...] = ()

    @property
    def range_text(self) -> str:
        if self.widget == "select":
            return " o ".join(self.options)
        if self.widget == "check":
            return "sí o no"
        return f"{_num(self.lo)} a {_num(self.hi)}"

    @property
    def default_text(self) -> str:
        if self.widget == "check":
            return "no" if not self.default else "sí"
        return self.default if isinstance(self.default, str) else _num(self.default)

    @property
    def help(self) -> str:
        unit = f" ({self.unit})" if self.unit else ""
        return f"{self.meaning} Rango{unit}: {self.range_text}. En planta: {self.source}"


def _num(x: float) -> str:
    """Número en español: «1 000», «2,7»."""
    if float(x).is_integer():
        return f"{int(x):,}".replace(",", " ")
    return f"{x:g}".replace(".", ",")


DATOS: tuple[Dato, ...] = (
    Dato("diameter", "Diámetro de la bola", "pulgadas", 0.5, 5.0, 2.0, 0.05,
         "Diámetro de la bola de acero. El NBS midió entre 0,75 y 2,77 pulgadas: fuera de ese "
         "rango el resultado es una extrapolación.",
         "medida de la bola (1 pulgada = 25,4 mm)."),
    Dato("medium", "Medio de temple", "", 0, 0, "agua", 0,
         "Líquido en reposo a 20 °C. Solo hay dos, los que midió el NBS: el modelo trae un "
         "coeficiente de transferencia calibrado para cada uno.",
         "el tanque de temple.", widget="select", options=MEDIA),
    Dato("compare", "Comparar con una velocidad crítica", "", 0, 1, False, 0,
         "Opcional. Sombrea en la bola la capa que se enfría a 720 °C al menos tan rápido como "
         "la velocidad crítica. Es un criterio simple; no es dureza.",
         "ensayos del material (curvas de enfriamiento continuo).", widget="check"),
    Dato("critical", "Velocidad crítica de temple", "°C/s", 1, 200, 20, 1,
         "Dato del material, no del modelo: el valor de partida no tiene fuente. Solo se usa si "
         "se activa la comparación.",
         "ensayos del material (dilatometría o curvas de enfriamiento continuo)."),
)  # fmt: skip
BY_KEY = {d.key: d for d in DATOS}
# Datos que la app fija: el h calibrado solo vale con estas dos temperaturas.
FIJOS = (
    ("Temperatura de austenización", "°C", T_INITIAL),
    ("Temperatura del medio", "°C", T_MEDIUM),
)


def _ask(d: Dato) -> float | bool | str:
    key, label = PREFIX + d.key, f"{d.label} ({d.unit})" if d.unit else d.label
    sb = st.sidebar
    if d.widget == "select":
        return sb.selectbox(label, list(d.options), d.options.index(str(d.default)), key=key,
                            help=d.help)  # fmt: skip
    if d.widget == "check":
        return sb.checkbox(label, value=bool(d.default), key=key, help=d.help)
    lo, hi, v, step = (float(x) for x in (d.lo, d.hi, d.default, d.step))
    return sb.number_input(label, lo, hi, v, step, help=d.help, key=key)


def reset_to_example() -> None:
    """Vuelve todos los datos al ejemplo."""
    for k in [k for k in st.session_state if str(k).startswith(PREFIX)]:
        del st.session_state[k]


def sidebar_config() -> QuenchParams:
    """Lee la barra lateral y arma los parámetros del temple."""
    sb = st.sidebar
    sb.button("Cargar ejemplo", on_click=reset_to_example, width="stretch")
    v = {d.key: _ask(d) for d in DATOS}
    sb.caption(
        f"Fijos: {_num(T_INITIAL)} °C → {_num(T_MEDIUM)} °C. Los coeficientes de transferencia "
        "del NBS solo valen con estas temperaturas."
    )
    return QuenchParams(float(v["diameter"]), str(v["medium"]), bool(v["compare"]),
                        float(v["critical"]))  # fmt: skip


def data_table() -> pd.DataFrame:
    """La tabla «Qué datos necesita», hecha de las mismas definiciones que la barra lateral."""
    rows = [
        {
            "Dato": d.label,
            "Unidad": d.unit,
            "Rango": d.range_text,
            "Ejemplo": d.default_text,
            "Qué es": d.meaning,
            "Cómo se obtiene": d.source[0].upper() + d.source[1:],
        }
        for d in DATOS
    ]
    rows += [
        {"Dato": name, "Unidad": unit, "Rango": "fijo", "Ejemplo": _num(value),
         "Qué es": "La app no lo deja cambiar: el h calibrado solo vale así.",
         "Cómo se obtiene": "Condición del ensayo del NBS."}
        for name, unit, value in FIJOS
    ]  # fmt: skip
    return pd.DataFrame(rows)
