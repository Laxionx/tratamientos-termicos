"""App «Temple de la bola» (Ball quenching): cómo se enfría por dentro una bola de acero al
templarla, capa por capa y segundo a segundo, con los números de `tratamientos.temple`.
Pestañas: Guía, Temple y Validación (contra las esferas medidas por el NBS en 1925). Español e
inglés (`?lang=en`)."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Streamlit Community Cloud instala solo requirements.txt: el paquete se importa desde la raíz,
# y los módulos de la app, desde esta carpeta.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))

import pandas as pd  # noqa: E402
from bola_svg import ball_svg  # noqa: E402
from calculo import (  # noqa: E402
    ACCEPTED,
    QuenchParams,
    QuenchView,
    nbs_rows,
    run_quench,
)
from controles import reset_to_example, sidebar_config  # noqa: E402
from dibujo import MOTION_CSS, as_images, es  # noqa: E402
from estado import panel, pruebas  # noqa: E402
from graficos import temperature_figure, validation_figure  # noqa: E402
from guia import ficha, guide_tab, markdown_table  # noqa: E402
from i18n import activate, current, opt, sidebar_selector, t, tm, tr_error  # noqa: E402
from temple_estado import filas_estado, pruebas_temple  # noqa: E402

activate()  # idioma de esta corrida: la sesión o `?lang=` (solo es o en)
st.set_page_config(page_title=t("page.title"), layout="wide")


def _indicadores(view: QuenchView) -> None:
    """Seis indicadores en dos filas de tres: rótulos cortos (el nombre completo va en la ayuda)."""
    center, _, surface = view.crossings
    fila1, fila2 = st.columns(3), st.columns(3)
    fila1[0].metric(t("q.m.center"), f"{es(center.time_s, 1)} s", help=t("q.m.center.help"))
    fila1[1].metric(t("q.m.center_rate"), f"{es(center.rate, 1)} °C/s",
                    help=t("q.m.center_rate.help"))  # fmt: skip
    fila1[2].metric(t("q.m.surface_rate"), f"{es(surface.rate, 0)} °C/s",
                    help=t("q.m.surface_rate.help"))  # fmt: skip
    fila2[0].metric(t("q.m.biot"), es(view.biot, 1), help=t("q.m.biot.help"))
    fila2[1].metric(t("q.m.h"), es(view.h, 0), help=t("q.m.h.help"))
    fila2[2].metric(t("q.m.grossmann"), f"{es(view.grossmann, 1)} in⁻¹",
                    help=t("q.m.grossmann.help"))  # fmt: skip


def quench_tab(params: QuenchParams, animate: bool) -> None:
    ficha()
    try:
        view = run_quench(params)
    except (ValueError, RuntimeError, ArithmeticError) as exc:
        st.error(t("q.err", exc=tr_error(str(exc))))
        return
    _indicadores(view)
    st.subheader(t("q.h.estado"))
    panel(filas_estado(view))
    st.html(as_images(ball_svg(view, paused=not animate), ball_svg(view, paused=True),
                      t("q.alt")))  # fmt: skip
    st.caption(t("q.caption"))
    if view.critical is not None:
        layer = view.critical
        if layer.none:
            st.info(t("q.crit.none"))
        elif layer.whole:
            st.info(t("q.crit.whole"))
        else:
            st.info(t("q.crit.layer", depth=es(layer.depth_mm, 1), radius=es(view.radius_mm, 1)))
    st.plotly_chart(temperature_figure(view), width="stretch")
    table = pd.DataFrame({
        t("q.col.pos"): [tm(c.name) for c in view.crossings],
        t("q.col.time"): [round(c.time_s, 2) for c in view.crossings],
        t("q.col.rate"): [round(c.rate, 1) for c in view.crossings],
    })  # fmt: skip
    st.dataframe(table, hide_index=True)
    st.subheader(t("q.h.prueba"))
    st.markdown(t("q.prueba.intro"))
    pruebas(pruebas_temple(), "q_", reset_to_example)


def _deviation_text(deviation: float) -> str:
    return f"{100 * deviation:+.1f} %".replace(".", "," if current() == "es" else ".")


def _deviation(row) -> str:
    if row.calibration:
        return t("v.calibration")
    return _deviation_text(row.deviation)


def validation_tab() -> None:
    st.markdown(t("v.intro"))
    rows = nbs_rows()
    predictions = [r for r in rows if not r.calibration]
    inside = sum(r.inside for r in predictions)
    worst = max(predictions, key=lambda r: abs(r.deviation))
    mean = sum(r.deviation for r in predictions) / len(predictions)
    c1, c2, c3 = st.columns(3)
    c1.metric(t("v.metric", pct=f"{100 * ACCEPTED:.0f}"),
              t("v.metric.value", n=inside, m=len(predictions)))  # fmt: skip
    where = t("v.m.worst.help", d=es(worst.nominal_in, 2), medium=opt(worst.medium))
    c2.metric(t("v.m.worst"), _deviation(worst), help=where)
    c3.metric(t("v.m.mean"), _deviation_text(mean), help=t("v.m.mean.help"))
    st.plotly_chart(validation_figure(rows), width="stretch")
    table = pd.DataFrame({
        t("v.col.sphere"): [es(r.nominal_in, 2) for r in rows],
        t("v.col.medium"): [opt(r.medium) for r in rows],
        t("v.col.measured"): [es(r.measured, 1) for r in rows],
        t("v.col.model"): [es(r.model, 1) for r in rows],
        t("v.col.dev"): [_deviation(r) for r in rows],
        t("v.col.inside"): ["" if r.calibration else (t("yes") if r.inside else t("no"))
                            for r in rows],
    })  # fmt: skip
    st.markdown(markdown_table(table))
    st.caption(t("v.caption"))


def main() -> None:
    sidebar_selector()
    st.title(t("app.title"))
    st.caption(t("app.caption"))
    st.html(MOTION_CSS)
    params = sidebar_config()
    animate = st.toggle(t("toggle.label"), value=True, help=t("toggle.help"))
    tab_guide, tab_quench, tab_validation = st.tabs(
        [t("tab.guide"), t("tab.quench"), t("tab.validation")]
    )
    with tab_guide:
        guide_tab()
    with tab_quench:
        quench_tab(params, animate)
    with tab_validation:
        validation_tab()


main()
