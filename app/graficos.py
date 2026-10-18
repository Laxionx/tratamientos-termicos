"""Gráficos de la app con Plotly: temperatura contra tiempo en tres posiciones y validación de la
velocidad del centro contra las esferas medidas por el NBS (French y Klopsch 1925)."""

from __future__ import annotations

import math

import plotly.graph_objects as go
from calculo import ACCEPTED, T_MARK, VALIDATED_IN, NbsRow, QuenchView, curve, model_curve
from dibujo import INK, PAPER, STEEL, es
from i18n import t, tm

FONT = dict(family="Segoe UI, Helvetica, Arial, sans-serif", color=INK, size=13)
POSITION_COLORS = {"centro": "#C0462B", "medio radio": "#B7791F", "superficie": "#3B82A6"}
MEDIUM_COLORS = {"agua": "#3B82A6", "aceite": "#B7791F"}
BAD = "#C0462B"


def _layout(fig: go.Figure, title: str, height: int, x: dict, y: dict) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(family="Georgia, serif", size=17)),
        paper_bgcolor=PAPER, plot_bgcolor="#FBF9F4", font=FONT, height=height,
        margin=dict(l=60, r=20, t=60, b=50), legend=dict(bgcolor="rgba(0,0,0,0)"),
    )  # fmt: skip
    fig.update_xaxes(gridcolor="#E4DED2", linecolor=STEEL, **x)
    fig.update_yaxes(gridcolor="#E4DED2", linecolor=STEEL, **y)
    return fig


def temperature_figure(view: QuenchView) -> go.Figure:
    """T contra tiempo en el centro, el medio radio y la superficie, con la línea de 720 °C."""
    fig = go.Figure()
    for c in view.crossings:
        times, temps = curve(view.result, c.position)
        fig.add_trace(go.Scatter(
            x=times, y=temps, mode="lines", name=tm(c.name),
            line=dict(color=POSITION_COLORS[c.name], width=3),
        ))  # fmt: skip
        fig.add_trace(go.Scatter(
            x=[c.time_s], y=[T_MARK], mode="markers", showlegend=False,
            marker=dict(size=10, color=POSITION_COLORS[c.name], line=dict(color=PAPER, width=2)),
            hovertemplate=t("plot.temp.hover", name=tm(c.name), t=es(c.time_s, 1),
                            rate=es(c.rate, 1)),
        ))  # fmt: skip
    fig.add_hline(y=T_MARK, line=dict(color=STEEL, dash="dash", width=1.5),
                  annotation_text=f"{T_MARK:g} °C", annotation_position="top right")  # fmt: skip
    return _layout(fig, t("plot.temp.title"), 420,
                   x=dict(title=t("plot.temp.x")), y=dict(title=t("plot.temp.y")))  # fmt: skip


def validation_figure(rows: tuple[NbsRow, ...]) -> go.Figure:
    """Velocidad del centro a 720 °C contra el diámetro: medido por el NBS y el modelo, con la
    banda de ±15 %, la esfera de calibración y las predicciones que caen fuera."""
    fig = go.Figure()
    for medium, color in MEDIUM_COLORS.items():
        mine = [r for r in rows if r.medium == medium]
        lo, hi = VALIDATED_IN
        xs, ys = model_curve(medium, lo, hi)
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines", name=t("plot.val.model", medium=tm(medium)),
            line=dict(color=color, width=2),
        ))  # fmt: skip
        fig.add_trace(go.Scatter(
            x=[r.nominal_in for r in mine], y=[r.measured for r in mine], mode="markers",
            name=t("plot.val.measured", medium=tm(medium), pct=f"{ACCEPTED:.0%}"),
            marker=dict(size=10, color=color, symbol="diamond", line=dict(color=INK, width=1)),
            error_y=dict(type="data", symmetric=False, color=color, thickness=1.5, width=5,
                         array=[ACCEPTED * r.measured for r in mine],
                         arrayminus=[ACCEPTED * r.measured for r in mine]),
            customdata=[[es(100 * r.deviation, 1), t("yes") if r.inside else t("no")]
                        for r in mine],
            hovertemplate=t("plot.val.hover"),
        ))  # fmt: skip
        out = [r for r in mine if not r.inside]
        if out:
            fig.add_trace(go.Scatter(
                x=[r.nominal_in for r in out], y=[r.model for r in out], mode="markers",
                name=t("plot.val.out", pct=f"{ACCEPTED:.0%}"),
                marker=dict(size=11, color=BAD, symbol="x"), showlegend=medium == "agua",
            ))  # fmt: skip
        cal = next(r for r in mine if r.calibration)
        fig.add_annotation(
            x=math.log10(cal.nominal_in),
            y=math.log10(cal.measured),
            text=t("plot.val.cal"),
            ax=40,
            ay=-30,
            showarrow=True,
            arrowcolor=STEEL,
            font=dict(size=12),
        )
    return _layout(fig, t("plot.val.title"), 480,
                   x=dict(title=t("plot.val.x"), type="log"),
                   y=dict(title=t("plot.val.y"), type="log"))  # fmt: skip
