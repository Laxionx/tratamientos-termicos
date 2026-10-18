"""Pestaña «Guía» y ficha del temple: qué hace, qué datos necesita, qué devuelve, de qué autores
salen las ecuaciones y cuáles son sus límites."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from controles import data_table

REPO = "https://github.com/Laxionx/tratamientos-termicos"
PLANTA = "https://simulador-procesos-ntfmuyhlnqc9d73kkqljzk.streamlit.app/"
CONMINUCION = "https://simulador-conminucion-mtxoolyzuvvcxrq8rce3el.streamlit.app/"

FICHA = {
    "hace": "Calcula cómo se enfría por dentro una bola de acero que sale del horno a 875 °C y "
    "se mete en agua o aceite a 20 °C: la temperatura a cada radio, segundo a segundo, y cuándo "
    "y a qué velocidad cada capa pasa por 720 °C, la temperatura en que el NBS midió la "
    "velocidad de enfriamiento.",
    "entra": "El diámetro de la bola y el medio de temple (agua o aceite, en reposo). Opcional: "
    "una velocidad crítica de temple del material, para marcar la capa que la alcanza.",
    "sale": "La temperatura en cualquier punto y momento; el tiempo y la velocidad de "
    "enfriamiento (°C/s) en que la superficie, el medio radio y el centro pasan por 720 °C; "
    "y, si se pide, el espesor de la capa que alcanza la velocidad crítica. No calcula la "
    "dureza.",
    "autores": "Conducción de calor en una esfera con convección en la superficie, resuelta por "
    "volúmenes finitos y comprobada contra la solución analítica: Incropera et al., "
    "*Fundamentals of Heat and Mass Transfer*, cap. 5. Propiedades de la austenita (k, cp, ρ "
    "constantes): EN 1993-1-2 (Eurocódigo 3). Coeficientes de transferencia y validación: "
    "French y Klopsch (1925), *Technologic Papers of the Bureau of Standards* 19, T295, "
    "dominio público.",
    "limites": (
        "Sin calor latente de la transformación ni capa de vapor: el coeficiente de transferencia "
        "(h) es efectivo y constante.",
        "Solo hay dos h, calibrados con la esfera de 3/4 de pulgada del NBS a 875 °C → 20 °C; "
        "por eso esas temperaturas son fijas y no se ofrece un h libre ni de manual: los de "
        "manual fallan (el h efectivo calibrado en agua quieta da H = 3,2 in⁻¹; los manuales "
        "citan cerca de 1).",
        "Validado con acero de rodamiento (0,98 % C, 1,63 % Cr), entre 0,75 y 2,77 pulgadas. "
        "Para un hierro blanco alto cromo cambian la conductividad y el h efectivo: la tabla es "
        "orientativa.",
        "Las esferas grandes salen entre 10 y 19 % más rápidas que lo medido (ver Validación).",
        "La dureza no se calcula; la velocidad crítica es un dato del material, no del modelo.",
    ),
    "doc": "docs/fase2-temple.md",
}


def markdown_table(df: pd.DataFrame) -> str:
    """Tabla en Markdown: el texto largo se ajusta a la columna en vez de cortarse."""

    def cell(v: object) -> str:
        return str(v).replace("|", "\\|").replace("\n", " ")

    head = "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n"
    return head + "\n".join("| " + " | ".join(cell(v) for v in row) + " |" for row in df.values)


def ficha() -> None:
    """Ficha del temple, arriba de su pestaña."""
    f = FICHA
    st.markdown(f"**Qué hace.** {f['hace']}")
    st.markdown(f"**Qué entra.** {f['entra']}")
    st.markdown(f"**Qué devuelve.** {f['sale']}")
    with st.expander("Qué datos necesita"):
        st.markdown(markdown_table(data_table()))
    with st.expander("Límites del modelo"):
        for item in f["limites"]:
            st.markdown(f"- {item}")
    st.caption(
        f"**De dónde salen las ecuaciones.** {f['autores']} Detalle en "
        f"[{f['doc']}]({REPO}/blob/main/{f['doc']})."
    )


def guide_tab() -> None:
    st.markdown("### Qué simula")
    st.markdown(
        "El **temple de una bola de acero**, como las de molienda: sale del horno a 875 °C y se "
        "sumerge en agua o aceite. El simulador calcula, con ecuaciones publicadas, cómo baja la "
        "temperatura capa por capa y segundo a segundo. La animación dibuja esos números: no es "
        "un dibujo suelto."
    )
    st.markdown("### Cómo leer la animación")
    st.markdown(
        "- La bola se ve **en corte**: los anillos son capas de radio; el color de cada anillo "
        "es la temperatura que calcula el modelo a esa profundidad. El color es **ilustrativo**: "
        "de acero frío (oscuro) a naranja (875 °C).\n"
        "- El **reloj** marca los segundos reales. Los fotogramas están más juntos al principio, "
        "cuando todo cambia rápido, y el ciclo comprime el temple completo en unos segundos.\n"
        "- Los **puntos** de la superficie, el medio radio y el centro se ponen verdes cuando "
        "esa posición baja de 720 °C. Al lado, el tiempo y la velocidad de ese cruce.\n"
        "- Con la comparación activada, la capa **rayada** es la que se enfría a 720 °C al menos "
        "tan rápido como la velocidad crítica que des. Es un criterio simple; no es dureza."
    )
    st.markdown("### Por qué el centro se atrasa")
    st.markdown(
        "El calor del centro tiene que **viajar por dentro del acero** hasta la superficie, y el "
        "acero lo conduce con dificultad. Una vez en la superficie, el líquido se lo lleva. El "
        "**número de Biot** compara esos dos esfuerzos: lo que cuesta que el calor salga de la "
        "superficie al líquido frente a lo que cuesta que llegue hasta ella desde adentro. Si "
        "el líquido se lleva el calor más fácil de lo que el acero lo entrega (Biot grande), la "
        "superficie se enfría casi al instante y el centro queda atrás: se enfría **capa por "
        "capa, de afuera hacia adentro**. Cuanto más grande la bola, más camino tiene que hacer "
        "el calor y más acero hay que enfriar, así que el centro se atrasa más. Por eso una "
        "bola grande puede no templar a fondo aunque su superficie sí."
    )
    st.markdown("### Qué datos necesita")
    st.markdown(markdown_table(data_table()))
    st.markdown("### Lo que no hace")
    for item in FICHA["limites"]:
        st.markdown(f"- {item}")
    st.markdown("### Otras apps")
    st.markdown(
        f"- [Simulador de conminución]({CONMINUCION}): la molienda que viene antes, animada.\n"
        f"- [«Planta completa»]({PLANTA}): flotación, horno flash, convertidor y "
        "electroobtención, animados.\n"
        f"- Código de esta app: [repositorio]({REPO})."
    )
