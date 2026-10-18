"""Esquema animado de la bola templada, en corte: anillos concéntricos cuyo color en cada
fotograma es la temperatura que calcula `quench_sphere` al radio medio de la banda y al tiempo
real del fotograma.

Lo que sale del cálculo: el color de cada anillo en cada fotograma, el reloj (tiempo real de cada
fotograma), las marcas del cruce de 720 °C (`time_to`) con su velocidad (`rate_at`) y, si se pide,
el espesor de la capa que alcanza la velocidad crítica. Lo ilustrativo, y así se rotula: el color
en sí (rampa ilustrativa) y la compresión del tiempo (el ciclo dura CYCLE_S segundos).
"""

from __future__ import annotations

import textwrap

from calculo import FRAME_COUNT, RING_COUNT, SAMPLING_POWER, T_INITIAL, T_MARK, T_MEDIUM, QuenchView
from colores import temperature_color
from dibujo import INK, STEEL, es, scheme_note, svg, text
from i18n import t, tm

W, H = 960, 600
CX, CY, RADIUS = 280.0, 270.0, 190.0
CYCLE_S = 16.0  # el temple completo, comprimido a este tiempo
GRAY, GREEN = "#8E979C", "#2E9E6B"
HATCH = "tt-hatch"
SWATCHES = 12


def clock_text(seconds: float) -> str:
    """Segundos reales del fotograma, como se rotulan."""
    return t("svg.clock", t=es(seconds, 1 if seconds < 100 else 0))


def ring_colors(view: QuenchView) -> list[list[str]]:
    """[fotograma][anillo] → color de la temperatura del cálculo."""
    return [[temperature_color(t) for t in frame] for frame in view.ring_temps]


def first_frame_at_or_after(times: tuple[float, ...], t: float) -> int:
    """Primer fotograma cuyo tiempo real ya alcanzó `t`."""
    return next(k for k, tk in enumerate(times) if tk >= t)


def frame_seconds(view: QuenchView) -> float:
    """Segundos de animación que dura cada fotograma."""
    return CYCLE_S / len(view.frame_times)


def _pct(k: int, frames: int) -> str:
    return f"{100.0 * k / frames:.4f}%"


def _motion_css(view: QuenchView) -> str:
    frames = len(view.frame_times)
    colors = ring_colors(view)
    css = f"@keyframes tt-clk{{0%{{opacity:1}}{_pct(1, frames)}{{opacity:0}}100%{{opacity:0}}}}"
    css += f".tt-svg .tt-clk{{opacity:0;animation:tt-clk {CYCLE_S:g}s step-end infinite}}"
    for i in range(RING_COUNT):
        stops = "".join(f"{_pct(k, frames)}{{fill:{colors[k][i]}}}" for k in range(frames))
        css += f"@keyframes tt-ring{i}{{{stops}}}"
        css += f".tt-svg .tt-ring{i}{{animation:tt-ring{i} {CYCLE_S:g}s step-end infinite}}"
    for j, crossing in enumerate(view.crossings):
        k = first_frame_at_or_after(view.frame_times, crossing.time_s)
        css += (
            f"@keyframes tt-mk{j}{{0%{{fill:{GRAY}}}{_pct(k, frames)}{{fill:{GREEN}}}"
            f"100%{{fill:{GREEN}}}}}.tt-svg .tt-mk{j}{{animation:tt-mk{j} {CYCLE_S:g}s step-end "
            "infinite}"
        )
    return css


def _rings(view: QuenchView, frame: int, paused: bool) -> str:
    colors = ring_colors(view)[frame]
    out = []
    for i in range(RING_COUNT - 1, -1, -1):  # de afuera hacia adentro: lo de adentro tapa
        cls = "" if paused else f' class="tt-ring{i}"'
        out.append(
            f'<circle{cls} data-ring="{i}" cx="{CX}" cy="{CY}" '
            f'r="{RADIUS * (i + 1) / RING_COUNT:.3f}" fill="{colors[i]}"/>'
        )
    return "".join(out)


def _circle_path(radius: float) -> str:
    """Contorno de un círculo centrado en la bola, para recortar el agujero con evenodd."""
    left, right = CX - radius, CX + radius
    return (
        f"M {left:.2f} {CY} A {radius:.2f} {radius:.2f} 0 1 0 {right:.2f} {CY} "
        f"A {radius:.2f} {radius:.2f} 0 1 0 {left:.2f} {CY} Z "
    )


def _critical(view: QuenchView) -> str:
    layer = view.critical
    if layer is None or layer.none:
        return ""
    inner = 0.0 if layer.whole or layer.position is None else layer.position * RADIUS
    pattern = (
        f'<pattern id="{HATCH}" width="9" height="9" patternUnits="userSpaceOnUse" '
        f'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="9" stroke="#FFFFFF" '
        f'stroke-width="3" stroke-opacity=".7"/></pattern>'
    )
    path = _circle_path(RADIUS) + (_circle_path(inner) if inner > 0 else "")
    shade = f'<path class="tt-layer" fill-rule="evenodd" d="{path}" fill="url(#{HATCH})"/>'
    ring = ""
    if inner > 0:
        ring = (
            f'<circle cx="{CX}" cy="{CY}" r="{inner:.2f}" fill="none" stroke="#FFFFFF" '
            f'stroke-width="2" stroke-dasharray="6 4"/>'
        )
    return pattern + shade + ring


def _marks(view: QuenchView, paused: bool) -> str:
    out = []
    for j, c in enumerate(view.crossings):
        x = CX + c.position * RADIUS
        cls = "" if paused else f' class="tt-mk{j}"'
        fill = GREEN if paused else GRAY  # quieto: el fotograma ya pasó por los 720 °C
        out.append(
            f'<circle{cls} data-mark="{j}" cx="{x:.2f}" cy="{CY}" r="7" fill="{fill}" '
            f'stroke="#FFFFFF" stroke-width="2"/>'
        )
    return "".join(out)


def _panel(view: QuenchView) -> str:
    x, out = 560.0, []
    out.append(text(x, 150, t("svg.cross", mark=f"{T_MARK:g}"), 15, cls="t"))
    for j, c in enumerate(reversed(view.crossings)):
        y = 180 + 44 * j
        out.append(f'<circle cx="{x + 6}" cy="{y - 5}" r="6" fill="{GREEN}"/>')
        out.append(
            text(x + 20, y, t("svg.cross.at", name=tm(c.name).capitalize(), t=es(c.time_s, 1)), 14)
        )
        out.append(text(x + 20, y + 18, t("svg.cross.rate", rate=es(c.rate, 1)), 13, color=STEEL))
    return "".join(out)


def _bar() -> str:
    x0, y0, w = 560.0, 336.0, 26.0
    out = [text(x0, y0 - 10, t("svg.bar", note=t("scheme.temp")), 12, color=STEEL)]
    for j in range(SWATCHES):
        temp = T_MEDIUM + (T_INITIAL - T_MEDIUM) * j / (SWATCHES - 1)
        out.append(f'<rect x="{x0 + j * w:.1f}" y="{y0}" width="{w}" height="18" fill="'
                   f'{temperature_color(temp)}"/>')  # fmt: skip
    out.append(text(x0, y0 + 34, f"{T_MEDIUM:g} °C", 12, color=STEEL))
    out.append(text(x0 + SWATCHES * w, y0 + 34, f"{T_INITIAL:g} °C", 12, "end", color=STEEL))
    return "".join(out)


def _legend(view: QuenchView) -> str:
    frames = len(view.frame_times)
    p = view.params
    paragraphs = [
        t("svg.legend1", frames=frames, n=FRAME_COUNT - 1, power=f"{SAMPLING_POWER:g}",
          frame_s=es(frame_seconds(view), 2), cycle=f"{CYCLE_S:g}", real=es(view.result.t_end, 0),
          rings=RING_COUNT),
        t("svg.legend2", medium=tm(p.medium), h=es(view.h, 0), note=t("scheme.temp")),
    ]  # fmt: skip
    if not view.in_validated_range:
        paragraphs.append(t("svg.legend3"))
    lines = [ln for para in paragraphs for ln in textwrap.wrap(para, 140)] + [scheme_note()]
    top = H - 17 * len(lines) - 4
    return "".join(
        text(24, top + 17 * n, ln, 12, color=INK if n == len(lines) - 1 else STEEL)
        for n, ln in enumerate(lines)
    )


def _critical_note(view: QuenchView) -> str:
    layer = view.critical
    if layer is None:
        return ""
    if layer.none:
        msg = t("svg.crit.none")
    elif layer.whole:
        msg = t("svg.crit.whole", depth=es(layer.depth_mm, 1))
    else:
        msg = t("svg.crit.layer", depth=es(layer.depth_mm, 1), radius=es(view.radius_mm, 1))
    note = t("svg.crit.note", rate=es(view.params.critical_rate, 0))
    first = textwrap.wrap(msg, 52)
    lines = [*first, *textwrap.wrap(note + t("svg.crit.simple"), 52)]
    return "".join(
        text(560, 440 + 17 * n, ln, 12, color=INK if n < len(first) else STEEL)
        for n, ln in enumerate(lines)
    )


def _clocks(view: QuenchView, paused: bool) -> str:
    if paused:
        t = view.frame_times[view.still_frame]
        return text(560, 90, clock_text(t), 34, cls="t", extra=f' data-t="{t!r}"')
    d = frame_seconds(view)
    return "".join(
        text(
            560,
            90,
            clock_text(t),
            34,
            cls="t clk",
            extra=f' data-t="{t!r}"',
            style=f"animation-delay:{k * d:.4f}s",
        )
        for k, t in enumerate(view.frame_times)
    )


def ball_svg(view: QuenchView, paused: bool = False) -> str:
    frame = view.still_frame if paused else 0
    title = text(24, 30, t("svg.title", d=es(view.params.diameter_in, 2),
                           medium=tm(view.params.medium)), 18, cls="t")  # fmt: skip
    outline = (f'<circle cx="{CX}" cy="{CY}" r="{RADIUS}" fill="none" stroke="{INK}" '
               f'stroke-width="3"/>')  # fmt: skip
    body = (
        title + _rings(view, frame, paused) + _critical(view) + outline + _marks(view, paused)
        + _clocks(view, paused) + _panel(view) + _bar() + _critical_note(view) + _legend(view)
    )  # fmt: skip
    return svg(W, H, body, paused, t("svg.label"),
               "" if paused else _motion_css(view))  # fmt: skip
