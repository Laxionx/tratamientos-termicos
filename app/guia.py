"""Pestaña «Guía» y ficha del temple: qué hace, qué datos necesita, qué devuelve, de qué autores
salen las ecuaciones y cuáles son sus límites. Los textos están en `textos_es.py` y
`textos_en.py`."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from controles import data_table
from i18n import current, t

REPO = "https://github.com/Laxionx/tratamientos-termicos"
PLANTA = "https://simulador-procesos-ntfmuyhlnqc9d73kkqljzk.streamlit.app/"
CONMINUCION = "https://simulador-conminucion-mtxoolyzuvvcxrq8rce3el.streamlit.app/"
N_LIMITS = 5  # los «límites del modelo» de la ficha (claves ficha.limit.1 a ficha.limit.5)


def markdown_table(df: pd.DataFrame) -> str:
    """Tabla en Markdown: el texto largo se ajusta a la columna en vez de cortarse."""

    def cell(v: object) -> str:
        return str(v).replace("|", "\\|").replace("\n", " ")

    head = "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n"
    return head + "\n".join("| " + " | ".join(cell(v) for v in row) + " |" for row in df.values)


def _app_link(url: str) -> str:
    """El enlace a otra app del autor, en el mismo idioma (`?lang=` solo vale es o en)."""
    return url + "?lang=en" if current() == "en" else url


def limits() -> list[str]:
    return [t(f"ficha.limit.{n}") for n in range(1, N_LIMITS + 1)]


def ficha() -> None:
    """Ficha del temple, arriba de su pestaña."""
    st.markdown(t("ficha.label.hace", text=t("ficha.hace")))
    st.markdown(t("ficha.label.entra", text=t("ficha.entra")))
    st.markdown(t("ficha.label.sale", text=t("ficha.sale")))
    with st.expander(t("ficha.expander.datos")):
        st.markdown(markdown_table(data_table()))
    with st.expander(t("ficha.expander.limites")):
        for item in limits():
            st.markdown(f"- {item}")
    doc = t("ficha.doc")
    st.caption(
        t("ficha.caption", autores=t("ficha.autores"), doc=doc, url=f"{REPO}/blob/main/{doc}")
    )


def guide_tab() -> None:
    st.markdown(t("guide.h.simula"))
    st.markdown(t("guide.simula"))
    st.markdown(t("guide.h.leer"))
    st.markdown(t("guide.leer"))
    st.markdown(t("guide.h.centro"))
    st.markdown(t("guide.centro"))
    st.markdown(t("guide.h.datos"))
    st.markdown(markdown_table(data_table()))
    st.markdown(t("guide.h.limites"))
    for item in limits():
        st.markdown(f"- {item}")
    st.markdown(t("guide.h.otras"))
    st.markdown(
        t("guide.otras", conminucion=_app_link(CONMINUCION), planta=_app_link(PLANTA), repo=REPO)
    )
