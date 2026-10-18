"""La animación de la app sale del cálculo: el color de cada anillo en cada fotograma, el reloj,
las marcas de 720 °C, la capa sombreada y el gráfico de validación se deducen de
`tratamientos.temple` (que aquí se vuelve a ejecutar por separado) y de la tabla de
docs/fase2-temple.md. Cada fórmula de animación tiene una prueba que falla si se la cambia."""

import itertools
import re
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

import bola_svg  # noqa: E402
import calculo  # noqa: E402
import colores  # noqa: E402
import graficos  # noqa: E402
from dibujo import es  # noqa: E402

from tratamientos.temple import H_NBS, INCH, calibrate_h, quench_sphere  # noqa: E402
from tratamientos.validacion import NBS_RATE, nbs_diameters_in  # noqa: E402

P = calculo.QuenchParams
LEYENDA = "esquema, no a escala de tiempo: las temperaturas sí son del cálculo"
CASES = [P(), P(diameter_in=0.5, medium="aceite"), P(diameter_in=5.0), P(diameter_in=1.0)]


def _reference(params):
    return quench_sphere(params.diameter_in * INCH, H_NBS[params.medium], 875.0, 20.0)


def _keyframes(svg_text: str, name: str, prop: str) -> list[str]:
    start = svg_text.index(f"@keyframes {name}{{")
    segment = svg_text[start : svg_text.index("}}", start)]
    return re.findall(rf"{prop}:([^}};]+)", segment)


# ------------------------------------------------------------------ color por temperatura
def test_la_luminosidad_del_color_crece_con_la_temperatura():
    exact = [colores.luminance(colores.temperature_rgb_float(t)) for t in range(0, 1101, 5)]
    assert exact == sorted(exact) and exact[0] < exact[-1]  # monótona
    rounded = [colores.luminance(colores.temperature_rgb(t)) for t in range(0, 1101, 5)]
    assert all(b >= a - 1.0 for a, b in itertools.pairwise(rounded))  # redondeo a hex: ±1
    assert colores.temperature_rgb(-50) == colores.temperature_rgb(20)  # satura abajo
    assert colores.temperature_rgb(2000) == colores.temperature_rgb(1000)  # y arriba
    assert colores.temperature_color(20.0) == "#141E2A"  # acero frío


def test_el_acero_frio_es_azul_grisaceo_y_el_caliente_es_naranja():
    cold, hot = colores.temperature_rgb(20), colores.temperature_rgb(875)
    assert cold[2] > cold[0]  # más azul que rojo
    assert hot[0] > hot[1] > hot[2]  # rojo, luego verde, luego azul


# ------------------------------------------------------------------ anillos y reloj
@pytest.mark.parametrize("params", CASES)
def test_color_de_cada_anillo_en_cada_fotograma_es_la_temperatura_del_calculo(params):
    ref = _reference(params)
    view = calculo.run_quench(params)
    svg_text = bola_svg.ball_svg(view)
    assert len(view.frame_times) == calculo.FRAME_COUNT + 1
    for i in range(calculo.RING_COUNT):
        fills = _keyframes(svg_text, f"tt-ring{i}", "fill")
        assert len(fills) == len(view.frame_times)
        position = (i + 0.5) / calculo.RING_COUNT  # radio medio de la banda
        for t_k, fill in zip(view.frame_times, fills, strict=True):
            assert fill == colores.temperature_color(ref.temperature(t_k, position)), (i, t_k)


def test_los_anillos_se_dibujan_con_el_radio_de_su_banda():
    view = calculo.run_quench(P())
    svg_text = bola_svg.ball_svg(view)
    radii = {
        int(i): float(r) for i, r in re.findall(r'data-ring="(\d+)" [^>]*? r="([\d.]+)"', svg_text)
    }
    assert len(radii) == calculo.RING_COUNT
    for i, r in radii.items():
        assert r == pytest.approx(bola_svg.RADIUS * (i + 1) / calculo.RING_COUNT, abs=0.001)


@pytest.mark.parametrize("params", CASES)
def test_el_reloj_de_cada_fotograma_es_su_tiempo_real(params):
    ref = _reference(params)
    view = calculo.run_quench(params)
    svg_text = bola_svg.ball_svg(view)
    clocks = [
        (t, delay, label)
        for delay, t, label in re.findall(
            r'animation-delay:([\d.]+)s" class="[^"]*" data-t="([\d.e+-]+)">([^<]+)<', svg_text
        )
    ]
    assert len(clocks) == len(view.frame_times)
    step = bola_svg.CYCLE_S / len(view.frame_times)
    times = [float(t) for t, _, _ in clocks]
    assert times == sorted(times) and times[0] == 0.0
    assert times[-1] == pytest.approx(ref.t_end, rel=1e-12)  # el último fotograma es el fin
    for k, (t, delay, label) in enumerate(clocks):
        assert float(t) == view.frame_times[k]
        assert label == bola_svg.clock_text(float(t))
        shown = float(
            label.removeprefix("t = ").removesuffix(" s").replace(" ", "").replace(",", ".")
        )
        assert shown == pytest.approx(view.frame_times[k], abs=0.051 if float(t) < 100 else 0.51)
        assert float(delay) == pytest.approx(k * step, abs=1e-4)


def test_el_muestreo_es_mas_denso_al_principio_y_esta_declarado():
    view = calculo.run_quench(P())
    gaps = [b - a for a, b in zip(view.frame_times, view.frame_times[1:], strict=False)]
    assert gaps[0] < gaps[-1] and max(gaps[:5]) < min(gaps[-5:])
    expected = {view.result.t_end * (k / 39) ** 2 for k in range(40)}
    assert expected <= set(view.frame_times)  # t_k = t_fin·(k/39)² más el cruce del centro
    svg_text = bola_svg.ball_svg(view)
    for fragment in ("t_k = t_fin·(k/39)^2", "más densos al principio", "comprime", "16 s",
                     "color ilustrativo de la temperatura", LEYENDA):  # fmt: skip
        assert fragment in svg_text


# ------------------------------------------------------------------ marcas de 720 °C
@pytest.mark.parametrize("params", CASES)
def test_las_marcas_son_el_cruce_de_720_del_calculo(params):
    ref = _reference(params)
    view = calculo.run_quench(params)
    svg_text = bola_svg.ball_svg(view)
    for crossing, position in zip(view.crossings, (0.0, 0.5, 1.0), strict=True):
        t = ref.time_to(720.0, position)
        assert crossing.time_s == pytest.approx(t, rel=1e-9)
        dt = 1e-4 * max(t, 1e-3)  # velocidad por diferencia central, sin rate_at
        rate = (ref.temperature(t - dt, position) - ref.temperature(t + dt, position)) / (2 * dt)
        assert crossing.rate == pytest.approx(rate, rel=1e-6)
        assert f"a los {es(t, 1)} s" in svg_text and f"a {es(crossing.rate, 1)} °C/s" in svg_text
        assert ref.temperature(t, position) == pytest.approx(720.0, abs=1e-6)


def test_cada_punto_se_pone_verde_en_el_primer_fotograma_que_ya_cruzo():
    view = calculo.run_quench(P())
    svg_text = bola_svg.ball_svg(view)
    frames = len(view.frame_times)
    for j, crossing in enumerate(view.crossings):
        start = svg_text.index(f"@keyframes tt-mk{j}{{")
        stops = re.findall(r"([\d.]+)%\{fill:(#[0-9A-F]{6})\}", svg_text[start : start + 200])
        switch = float(stops[1][0])
        k = next(k for k, t in enumerate(view.frame_times) if t >= crossing.time_s)
        assert switch == pytest.approx(100 * k / frames, abs=1e-3)
        assert view.frame_times[k] >= crossing.time_s > view.frame_times[max(k - 1, 0)] or k == 0


def test_los_puntos_de_las_posiciones_estan_en_su_radio():
    svg_text = bola_svg.ball_svg(calculo.run_quench(P()))
    xs = [float(x) for x in re.findall(r'data-mark="\d" cx="([\d.]+)"', svg_text)]
    assert xs == [pytest.approx(bola_svg.CX + f * bola_svg.RADIUS, abs=0.01) for f in (0, 0.5, 1)]


def test_la_version_quieta_es_el_fotograma_en_que_el_centro_cruza_720():
    view = calculo.run_quench(P())
    ref = _reference(P())
    still = bola_svg.ball_svg(view, paused=True)
    assert "@keyframes" not in still and "animation" not in still
    t_center = ref.time_to(720.0, 0.0)
    assert view.frame_times[view.still_frame] == t_center
    assert re.search(r'data-t="([\d.e+-]+)"', still).group(1) == repr(t_center)
    colors = re.findall(r'data-ring="(\d+)" [^>]*? fill="(#[0-9A-F]{6})"', still)
    for i, fill in colors:
        position = (int(i) + 0.5) / calculo.RING_COUNT
        assert fill == colores.temperature_color(ref.temperature(t_center, position))
    assert bola_svg.clock_text(t_center) in still and LEYENDA in still


# ------------------------------------------------------------------ capa crítica
def _bisect_layer(ref, critical):
    """Bisección independiente sobre rate_at: la posición donde la velocidad iguala la crítica."""
    lo, hi = 0.0, 1.0
    while hi - lo > 1e-9:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if ref.rate_at(720.0, mid) < critical else (lo, mid)
    return (lo + hi) / 2


@pytest.mark.parametrize(
    "params",
    [
        P(diameter_in=2.0, compare=True, critical_rate=100.0),
        P(diameter_in=5.0, compare=True, critical_rate=20.0),
        P(diameter_in=1.5, medium="aceite", compare=True, critical_rate=35.0),
    ],
)
def test_la_capa_sombreada_es_la_biseccion_sobre_rate_at(params):
    ref = _reference(params)
    view = calculo.run_quench(params)
    layer = view.critical
    assert not layer.whole and not layer.none
    position = _bisect_layer(ref, params.critical_rate)
    assert layer.position == pytest.approx(position, abs=1e-6)
    radius_mm = params.diameter_in * 25.4 / 2
    assert layer.depth_mm == pytest.approx((1 - position) * radius_mm, abs=1e-4)
    assert ref.rate_at(720.0, position) == pytest.approx(params.critical_rate, rel=1e-5)
    svg_text = bola_svg.ball_svg(view)
    inner = re.search(r'stroke-dasharray="6 4"', svg_text) and re.search(
        r'<circle cx="[\d.]+" cy="[\d.]+" r="([\d.]+)" fill="none" stroke="#FFFFFF"', svg_text
    )
    assert float(inner.group(1)) == pytest.approx(position * bola_svg.RADIUS, abs=0.01)
    assert f"{es(layer.depth_mm, 1)} mm" in svg_text and "no es dureza" in svg_text


def test_la_capa_critica_cubre_toda_la_bola_o_ninguna():
    whole = calculo.run_quench(P(diameter_in=0.5, compare=True, critical_rate=1.0)).critical
    assert whole.whole and whole.depth_mm == pytest.approx(0.5 * 25.4 / 2)
    none = calculo.run_quench(P(diameter_in=5.0, medium="aceite", compare=True,
                                critical_rate=200.0)).critical  # fmt: skip
    assert none.none and none.depth_mm == 0.0
    svg_text = bola_svg.ball_svg(
        calculo.run_quench(P(diameter_in=5.0, medium="aceite", compare=True, critical_rate=200.0))
    )
    assert "Ninguna capa alcanza" in svg_text and "tt-layer" not in svg_text


def test_sin_la_comparacion_no_hay_capa_sombreada():
    view = calculo.run_quench(P(compare=False, critical_rate=50.0))
    assert view.critical is None and "tt-layer" not in bola_svg.ball_svg(view)


def test_la_velocidad_a_720_crece_hacia_la_superficie():
    ref = _reference(P())
    rates = [ref.rate_at(720.0, p / 10) for p in range(11)]
    assert rates == sorted(rates)  # lo que hace válida la bisección


# ------------------------------------------------------------------ validación
def _doc_table():
    text = (ROOT / "docs" / "fase2-temple.md").read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        m = re.match(r'\| (\d,\d\d)" \| (.*?) \| (.*?) \|$', line)
        if m:
            rows.append((float(m.group(1).replace(",", ".")), m.group(2), m.group(3)))
    return rows


def _cell(cell: str):
    """(medido, modelo, desvío % o None) de una celda de la tabla del doc."""
    cell = cell.replace("**", "").replace("−", "-").replace(",", ".")
    m = re.match(r"([\d.]+) → ([\d.]+) \(([-+][\d.]+) %\)", cell)
    if m:
        return float(m.group(1)), float(m.group(2)), float(m.group(3))
    m = re.match(r"([\d.]+) → ([\d.]+) \(calibración\)", cell)
    return (float(m.group(1)), float(m.group(2)), None) if m else None


def test_la_validacion_reproduce_la_tabla_del_doc():
    rows = calculo.nbs_rows()
    doc = _doc_table()
    assert len(doc) == 7
    by_key = {(r.medium, r.nominal_in): r for r in rows}
    checked = 0
    for nominal, water, oil in doc:
        for medium, cell in (("agua", water), ("aceite", oil)):
            parsed = _cell(cell)
            if parsed is None:  # «sin medición»
                assert (medium, nominal) not in by_key
                continue
            measured, model, deviation = parsed
            row = by_key[(medium, nominal)]
            assert row.measured == measured
            assert round(row.model, 1) == pytest.approx(model, abs=0.0501)
            if deviation is None:
                assert row.calibration
            else:
                assert 100 * row.deviation == pytest.approx(deviation, abs=0.06)
            checked += 1
    assert checked == len(rows) == 13  # 11 predicciones y 2 esferas de calibración


def test_siete_de_once_predicciones_caen_dentro_de_15_por_ciento():
    predictions = [r for r in calculo.nbs_rows() if not r.calibration]
    assert len(predictions) == 11 and sum(r.inside for r in predictions) == 7
    outside = {(r.medium, r.nominal_in) for r in predictions if not r.inside}
    assert outside == {("agua", 1.88), ("agua", 2.77), ("aceite", 2.35), ("aceite", 2.77)}


def test_los_datos_medidos_y_los_diametros_son_los_del_paquete():
    rows = calculo.nbs_rows()
    diameters = nbs_diameters_in()
    for r in rows:
        i = calculo.NOMINAL_IN.index(r.nominal_in)
        assert r.diameter_in == diameters[i] and r.measured == NBS_RATE[r.medium][i]
    assert [r.nominal_in for r in rows if r.calibration] == [0.75, 0.75]


def test_los_h_del_nbs_son_la_calibracion_con_la_esfera_de_tres_cuartos():
    for medium, measured in (("agua", 148.5), ("aceite", 60.0)):
        h = calibrate_h(nbs_diameters_in()[0] * INCH, measured, 720.0, 875.0, 20.0)
        assert h == pytest.approx(H_NBS[medium], rel=2e-3)


def test_el_grafico_de_validacion_trae_los_puntos_de_la_tabla():
    rows = calculo.nbs_rows()
    fig = graficos.validation_figure(rows)
    measured = {t.name.split(",")[1].split()[0]: t for t in fig.data if t.name.startswith("medido")}
    for medium in ("agua", "aceite"):
        mine = [r for r in rows if r.medium == medium]
        trace = measured[medium]
        assert list(trace.x) == [r.nominal_in for r in mine]
        assert list(trace.y) == [r.measured for r in mine]
        assert list(trace.error_y.array) == pytest.approx([0.15 * r.measured for r in mine])
    out = next(t for t in fig.data if t.name.startswith("modelo fuera"))
    assert len(out.x) == 2  # las del agua; las del aceite van en otra traza sin leyenda
    xs_out = sorted(x for t in fig.data if t.name.startswith("modelo fuera") for x in t.x)
    assert xs_out == [1.88, 2.35, 2.77, 2.77]
    assert any("calibración" in a.text for a in fig.layout.annotations)
    assert fig.layout.xaxis.type == "log" and fig.layout.yaxis.type == "log"


def test_el_grafico_de_temperatura_cruza_720_en_el_tiempo_calculado():
    view = calculo.run_quench(P())
    fig = graficos.temperature_figure(view)
    lines = {t.name: t for t in fig.data if t.mode == "lines"}
    assert set(lines) == {"centro", "medio radio", "superficie"}
    for crossing in view.crossings:
        marker = next(t for t in fig.data if t.mode == "markers"
                      and list(t.x) == [crossing.time_s])  # fmt: skip
        assert list(marker.y) == [720.0]
    center = lines["centro"]
    assert center.y[0] == 875.0 and center.y[-1] == pytest.approx(20.0, abs=5.0)


def test_ningun_esquema_ejecuta_codigo():
    view = calculo.run_quench(P(compare=True, critical_rate=50.0))
    for s in (bola_svg.ball_svg(view), bola_svg.ball_svg(view, paused=True)):
        low = s.lower()
        assert "<script" not in low and "onload" not in low and "javascript:" not in low
