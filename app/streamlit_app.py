"""App «Temple de la bola»: cómo se enfría por dentro una bola de acero al templarla, capa por
capa y segundo a segundo, con los números de `tratamientos.temple`. Pestañas: Guía, Temple y
Validación (contra las esferas medidas por el NBS en 1925)."""

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
from calculo import ACCEPTED, VALIDATED_IN, QuenchParams, nbs_rows, run_quench  # noqa: E402
from controles import sidebar_config  # noqa: E402
from dibujo import MOTION_CSS, as_images, es  # noqa: E402
from graficos import temperature_figure, validation_figure  # noqa: E402
from guia import ficha, guide_tab, markdown_table  # noqa: E402

st.set_page_config(page_title="Temple de la bola", layout="wide")


def quench_tab(params: QuenchParams, animate: bool) -> None:
    ficha()
    try:
        view = run_quench(params)
    except (ValueError, RuntimeError, ArithmeticError) as exc:
        st.error(f"No se pudo calcular el temple con estos datos: {exc}")
        return
    if not view.in_validated_range:
        lo, hi = VALIDATED_IN
        st.warning(
            f"Fuera del rango validado con el NBS ({es(lo, 2)} a {es(hi, 2)} pulgadas): el "
            "resultado es una extrapolación."
        )
    center, _, surface = view.crossings
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Centro baja a 720 °C a los", f"{es(center.time_s, 1)} s")
    c2.metric("Velocidad del centro a 720 °C", f"{es(center.rate, 1)} °C/s")
    c3.metric("Velocidad de la superficie a 720 °C", f"{es(surface.rate, 0)} °C/s")
    c4.metric("Número de Biot (h·R/k)", es(view.biot, 1))
    st.html(as_images(ball_svg(view, paused=not animate), ball_svg(view, paused=True),
                      "Corte de una bola de acero templada, enfriándose por anillos"))  # fmt: skip
    st.caption(
        "Cada anillo toma el color de la temperatura que calcula el modelo a su radio y a ese "
        "tiempo. Los puntos se ponen verdes cuando esa posición baja de 720 °C."
    )
    if view.critical is not None:
        layer = view.critical
        if layer.none:
            st.info(
                "Ninguna capa alcanza la velocidad crítica a 720 °C. Criterio simple; no es dureza."
            )
        elif layer.whole:
            st.info("Toda la bola, hasta el centro, se enfría a 720 °C al menos tan rápido como la "
                    "velocidad crítica. Criterio simple; no es dureza.")  # fmt: skip
        else:
            st.info(
                f"La capa que se enfría a 720 °C al menos tan rápido como la velocidad crítica "
                f"tiene **{es(layer.depth_mm, 1)} mm** de espesor, de {es(view.radius_mm, 1)} mm "
                "de radio. Criterio simple; no es dureza."
            )
    st.plotly_chart(temperature_figure(view), width="stretch")
    table = pd.DataFrame({
        "Posición": [c.name for c in view.crossings],
        "Baja a 720 °C a los (s)": [round(c.time_s, 2) for c in view.crossings],
        "Velocidad a 720 °C (°C/s)": [round(c.rate, 1) for c in view.crossings],
    })  # fmt: skip
    st.dataframe(table, hide_index=True)


def _deviation(row) -> str:
    if row.calibration:
        return "calibración"
    return f"{100 * row.deviation:+.1f} %".replace(".", ",")


def validation_tab() -> None:
    st.markdown(
        "El h de cada medio se calibra con la esfera de 3/4 de pulgada que midió el NBS, y con "
        "ese h se predicen las demás. French y Klopsch (1925) midieron con termocupla el centro "
        "de esferas de acero de rodamiento (0,98 % C, 1,63 % Cr), templadas desde 875 °C en "
        "agua o aceite quietos a 20 °C."
    )
    rows = nbs_rows()
    predictions = [r for r in rows if not r.calibration]
    inside = sum(r.inside for r in predictions)
    st.metric(f"Predicciones dentro de ±{100 * ACCEPTED:.0f} %", f"{inside} de {len(predictions)}")
    st.plotly_chart(validation_figure(rows), width="stretch")
    table = pd.DataFrame({
        "Esfera (pulgadas)": [es(r.nominal_in, 2) for r in rows],
        "Medio": [r.medium for r in rows],
        "Medido (°C/s)": [es(r.measured, 1) for r in rows],
        "Modelo (°C/s)": [es(r.model, 1) for r in rows],
        "Desvío": [_deviation(r) for r in rows],
        "Dentro de ±15 %": ["" if r.calibration else ("sí" if r.inside else "no") for r in rows],
    })  # fmt: skip
    st.markdown(markdown_table(table))
    st.caption(
        "Las esferas grandes salen entre 10 y 19 % más rápidas de lo medido: es lo esperable sin "
        "calor latente ni capa de vapor. El aceite no tiene medición a 1,61 pulgadas. "
        "Fuente de los datos medidos: French y Klopsch (1925), T295, dominio público."
    )


def main() -> None:
    st.title("Temple de la bola")
    st.caption(
        "Cómo se enfría por dentro una bola de acero al templarla, con los números de un modelo "
        "validado con medidas de 1925. Empieza por la **Guía**; los datos se cambian en la barra "
        "lateral."
    )
    st.html(MOTION_CSS)
    params = sidebar_config()
    animate = st.toggle(
        "Mover la animación", value=True,
        help="Apaga la animación del esquema. También se apaga sola si el sistema tiene "
        "activado «reducir movimiento».",
    )  # fmt: skip
    tab_guide, tab_quench, tab_validation = st.tabs(["Guía", "Temple", "Validación"])
    with tab_guide:
        guide_tab()
    with tab_quench:
        quench_tab(params, animate)
    with tab_validation:
        validation_tab()


main()
