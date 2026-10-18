"""Español e inglés: mismas claves, mismos números, sin restos de un idioma en el otro, y el
parámetro `?lang=` validado."""

import ast
import json
import re
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app" / "streamlit_app.py")
sys.path.insert(0, str(ROOT / "app"))

import bola_svg  # noqa: E402
import calculo  # noqa: E402
import controles  # noqa: E402
import graficos  # noqa: E402
import guia  # noqa: E402
import i18n  # noqa: E402
import modelo_en  # noqa: E402
from i18n import TEXTS  # noqa: E402

ES, EN = TEXTS["es"], TEXTS["en"]
# restos de español que no deben aparecer en un texto en inglés
SPANISH = re.compile(
    r"[áéíóúñ¿¡]|\b(de|del|la|las|los|el|con|para|por|una|sin|que|se|más|muy)\b", re.IGNORECASE
)


def run(lang: str | None = None, **values) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    if lang is not None:
        at.query_params["lang"] = lang
    at.run()
    for key, value in values.items():
        for w in [*at.sidebar.number_input, *at.sidebar.selectbox, *at.sidebar.checkbox]:
            if w.key == "dato_" + key:
                if isinstance(value, str):
                    with i18n.use(lang or "es"):
                        value = i18n.opt(value)  # las listas muestran el rótulo del idioma
                w.set_value(value)
    if values:
        at.run()
    return at


# ------------------------------------------------------------------ las claves
def test_los_dos_idiomas_tienen_las_mismas_claves():
    assert set(ES) == set(EN), sorted(set(ES) ^ set(EN))


def test_cada_texto_tiene_los_mismos_campos_en_los_dos_idiomas():
    for key in ES:
        assert i18n.fields(ES[key]) == i18n.fields(EN[key]), key


def test_ningun_texto_esta_vacio_y_solo_los_cognados_son_iguales_en_los_dos_idiomas():
    assert not {k for k in ES if not ES[k].strip() or not EN[k].strip()}
    same = {k for k in ES if ES[k] == EN[k]}
    # la ruta de un archivo, «no» (se escribe igual), el reloj «t = … s» y el texto de un hover
    # que solo lleva campos
    assert same == {"ficha.doc", "no", "plot.temp.hover", "svg.clock"}


def _literals_and_prefixes() -> tuple[set[str], set[str]]:
    literals, prefixes = set(), set()
    for path in (ROOT / "app").glob("*.py"):
        if path.name.startswith("textos_"):
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                literals.add(node.value)
            if isinstance(node, ast.JoinedStr) and node.values:
                first = node.values[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    prefixes.add(first.value)
            if (
                isinstance(node, ast.BinOp)
                and isinstance(node.op, ast.Add)
                and isinstance(node.left, ast.Constant)
                and isinstance(node.left.value, str)
            ):
                prefixes.add(node.left.value)
    return literals, {p for p in prefixes if "." in p and len(p) >= 3}


def test_no_hay_claves_sin_usar():
    literals, prefixes = _literals_and_prefixes()
    unused = [k for k in ES if k not in literals and not any(k.startswith(p) for p in prefixes)]
    assert not unused, unused


def test_las_familias_dinamicas_estan_completas():
    for d in controles.DATOS:
        for field in ("label", "meaning", "source"):
            assert f"dato.{d.key}.{field}" in ES, (d.key, field)
        for option in d.options:
            assert "opt." + option in ES and "opt." + option in EN
    assert all(f"ficha.limit.{n}" in ES for n in range(1, guia.N_LIMITS + 1))
    assert f"ficha.limit.{guia.N_LIMITS + 1}" not in ES  # ningún límite queda fuera de la ficha
    for name, _, _ in controles.FIJOS:
        assert name in ES and name in EN
    assert "unit.pulgadas" in ES


def test_los_textos_en_ingles_no_llevan_palabras_en_espanol():
    bad = {}
    for key, text in EN.items():
        clean = re.sub(r"\{[^}]*\}|`[^`]*`|\*[^*]+\*", "", text)
        if key != "ficha.doc" and SPANISH.search(clean):
            bad[key] = text[:80]
    assert not bad, bad


# ------------------------------------------------------------------ el idioma y la URL
@pytest.mark.parametrize("value", ["fr", "EN", "es ", "", "en;alert(1)", "<script>", "../en"])
def test_un_parametro_lang_invalido_es_espanol_sin_error(value):
    at = run(value)
    assert not at.exception
    assert at.tabs[0].label == "Guía"
    assert at.sidebar.radio[0].value == "es"
    assert at.query_params["lang"] in (["es"], "es")


def test_parse_lang_solo_acepta_es_y_en():
    assert [i18n.parse_lang(v) for v in ("es", "en")] == ["es", "en"]
    assert {i18n.parse_lang(v) for v in ("fr", None, 3, ["en"], "EN", " en")} == {"es"}


def test_lang_en_en_la_url_abre_en_ingles_y_el_selector_cambia_el_idioma():
    en = run("en")
    assert [t.label for t in en.tabs] == ["Guide", "Quench", "Validation"]
    assert en.sidebar.radio[0].value == "en"
    en.sidebar.radio[0].set_value("es").run()
    assert en.tabs[0].label == "Guía"
    assert en.query_params["lang"] in (["es"], "es")
    es_ = run()
    es_.sidebar.radio[0].set_value("en").run()
    assert es_.tabs[0].label == "Guide" and not es_.exception


def test_el_valor_de_lang_nunca_llega_al_html_ni_al_svg():
    at = run("en<script>alert(1)</script>")
    blob = json.dumps([m.value for m in at.markdown] + [c.value for c in at.caption])
    assert "alert(1)" not in blob and "<script" not in blob.lower()


def test_los_datos_y_las_listas_se_conservan_al_cambiar_de_idioma():
    at = run("es", diameter=3.0, medium="aceite")
    at.sidebar.radio[0].set_value("en").run()
    diameter = next(w for w in at.sidebar.number_input if w.key == "dato_diameter")
    medium = next(w for w in at.sidebar.selectbox if w.key == "dato_medium")
    assert diameter.value == 3.0 and medium.value == "oil"
    at.sidebar.radio[0].set_value("es").run()
    medium = next(w for w in at.sidebar.selectbox if w.key == "dato_medium")
    assert medium.value == "aceite" and not at.exception


# ------------------------------------------------------------------ humo de todas las pestañas
@pytest.mark.parametrize("lang", ["es", "en"])
def test_humo_de_todas_las_pestanas(lang):
    at = run(lang)
    assert not at.exception and not at.error
    assert len(at.tabs) == 3 and len(at.metric) == 5


@pytest.mark.parametrize("lang", ["es", "en"])
def test_humo_con_comparacion_critica_y_fuera_de_rango(lang):
    at = run(lang, diameter=4.5, medium="aceite", compare=True, critical=40.0)
    assert not at.exception and at.warning  # fuera del rango validado
    assert any("**" in i.value for i in at.info) or at.info


# ------------------------------------------------------------------ mismas cifras
_NUMBER = {
    "es": re.compile(r"-?\d+(?: \d{3})*(?:[.,]\d+)?(?:e-?\d+)?"),
    "en": re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?(?:e-?\d+)?"),
}


def _numbers(text: str, lang: str) -> list[float]:
    """Los números de un texto, leídos con el formato de su idioma."""
    out = []
    for item in _NUMBER[lang].findall(text.replace("\xa0", " ")):
        item = item.replace(",", "") if lang == "en" else item.replace(" ", "").replace(",", ".")
        out.append(float(item))
    return out


def _figures(at: AppTest, lang: str) -> list:
    parts = [m.value for m in at.metric] + [m.delta for m in at.metric]
    out = [_numbers(p or "", lang) for p in parts]
    for df in at.dataframe:
        for row in df.value.values.tolist():
            out.append([x for x in row if isinstance(x, int | float)])
    for md in at.markdown:
        if md.value.startswith("| "):
            for line in md.value.splitlines()[2:]:
                out.append([_numbers(c, lang) for c in line.strip("| ").split(" | ")])
    return out


@pytest.mark.parametrize(
    "values",
    [
        {},
        {"diameter": 1.0, "medium": "aceite"},
        {"diameter": 3.7, "compare": True, "critical": 55.0},
        {"diameter": 4.8, "medium": "aceite", "compare": True, "critical": 5.0},
    ],
)
def test_las_cifras_son_identicas_en_los_dos_idiomas(values):
    es_, en = run("es", **values), run("en", **values)
    assert not es_.exception and not en.exception
    a, b = _figures(es_, "es"), _figures(en, "en")
    assert len(a) == len(b) > 20 and a == b
    assert len(es_.metric) == len(en.metric) == 5


# ------------------------------------------------------------------ los gráficos y el esquema
def _fig_text(fig) -> str:
    return json.dumps(fig.to_plotly_json(), ensure_ascii=False)


def test_los_graficos_en_ingles_no_llevan_espanol_y_en_espanol_siguen_igual():
    view = calculo.run_quench(calculo.QuenchParams())
    for lang in ("es", "en"):
        with i18n.use(lang):
            figs = [
                graficos.temperature_figure(view),
                graficos.validation_figure(calculo.nbs_rows()),
            ]
            blob = " ".join(_fig_text(f) for f in figs)
        texts = re.findall(r'"(?:text|title|name|hovertemplate)": "([^"]+)"', blob)
        texts += re.findall(r'"title": \{"text": "([^"]+)"', blob)
        if lang == "en":
            bad = [x for x in texts if SPANISH.search(x)]
            assert not bad, bad[:5]
            assert "Center cooling rate" in blob and "calibration" in blob
        else:
            assert "Velocidad del centro" in blob and "calibración" in blob


def test_el_esquema_en_ingles_no_lleva_espanol():
    params = calculo.QuenchParams(diameter_in=4.0, medium="aceite", compare=True, critical_rate=8.0)
    view = calculo.run_quench(params)
    for lang in ("es", "en"):
        with i18n.use(lang):
            svg = bola_svg.ball_svg(view)
            still = bola_svg.ball_svg(view, paused=True)
        texts = re.findall(r">([^<]+)</text>", svg + still)
        label = re.findall(r'aria-label="([^"]+)"', svg)
        if lang == "en":
            assert not [x for x in texts + label if SPANISH.search(x)], texts
            assert any("quenched in oil" in x for x in texts)
            assert any("Outside the range validated" in x for x in texts)
        else:
            assert any("templada en aceite" in x for x in texts)


def test_los_numeros_del_esquema_cambian_de_formato_pero_no_de_valor():
    view = calculo.run_quench(calculo.QuenchParams())
    with i18n.use("es"):
        es_svg = bola_svg.ball_svg(view, paused=True)
    with i18n.use("en"):
        en_svg = bola_svg.ball_svg(view, paused=True)
    h = f"{view.h:,.0f}"
    assert h.replace(",", " ") in es_svg and h in en_svg
    center = f"{view.crossings[0].time_s:.1f}"
    assert center.replace(".", ",") in es_svg and center in en_svg


def test_formato_de_numeros_por_idioma():
    with i18n.use("es"):
        assert i18n.num(1234.5, 1) == "1 234,5" and i18n.num(0.5, 2) == "0,50"
        assert i18n.int_num(20000) == "20 000" and i18n.num_g(2.5) == "2,5"
    with i18n.use("en"):
        assert i18n.num(1234.5, 1) == "1,234.5" and i18n.num(0.5, 2) == "0.50"
        assert i18n.int_num(20000) == "20,000" and i18n.num_g(2.5) == "2.5"


# ------------------------------------------------------------------ lo que sale del modelo
def test_ningun_rotulo_del_modelo_queda_en_espanol_en_ingles():
    view = calculo.run_quench(calculo.QuenchParams())
    labels = {c.name for c in view.crossings} | set(calculo.MEDIA)
    labels |= {r.medium for r in calculo.nbs_rows()}
    with i18n.use("en"):
        for label in sorted(labels):
            out = i18n.tm(label)
            assert out != label and not SPANISH.search(out), (label, out)
    with i18n.use("es"):
        assert all(i18n.tm(label) == label for label in labels)


def test_los_errores_conocidos_del_modelo_se_traducen():
    with i18n.use("en"):
        assert i18n.tr_error("medio desconocido: 'x'; solo agua, aceite") == (
            "unknown medium: 'x'; only water, oil"
        )
        assert i18n.tr_error("el diámetro y la velocidad crítica deben ser positivos") == (
            "the diameter and the critical rate must be positive"
        )
        assert "does not reach" in i18n.tr_error("no llega a 720 °C en 90 s")
        assert i18n.tr_error("un error que no se conoce") == "un error que no se conoce"
    with i18n.use("es"):
        msg = "no llega a 720 °C en 90 s"
        assert i18n.tr_error(msg) == msg
    assert all(re.compile(p) for p, _ in modelo_en.ERRORS)


def test_un_error_del_modelo_se_muestra_sin_traza_en_los_dos_idiomas(monkeypatch):
    def fails(params):
        raise ValueError("medio desconocido: 'x'; solo agua, aceite")

    monkeypatch.setattr(calculo, "run_quench", fails)
    for lang, expected in (("es", "medio desconocido: 'x'; solo agua"), ("en", "unknown medium")):
        at = run(lang)
        assert not at.exception
        assert any(expected in e.value for e in at.error), [e.value for e in at.error]


# ------------------------------------------------------------------ README y GIF
def test_los_readme_se_enlazan_entre_si_y_los_gif_existen_y_pesan_menos_de_3_mb():
    es_, en = (ROOT / "README.md").read_text("utf-8"), (ROOT / "README.en.md").read_text("utf-8")
    assert es_.splitlines()[0] == "[English version](README.en.md)"
    assert en.splitlines()[0] == "[Versión en español](README.md)"
    assert "?lang=en" in en
    for readme, name in ((es_, "temple-bola.es.gif"), (en, "ball-quench.en.gif")):
        assert f"docs/img/{name}" in readme
        gif = ROOT / "docs" / "img" / name
        assert gif.read_bytes()[:6] in (b"GIF89a", b"GIF87a")
        assert 0 < gif.stat().st_size < 3_000_000


def test_el_ingles_usa_comillas_inglesas_y_no_las_espanolas():
    bad = [k for k, v in EN.items() if "«" in v or "»" in v]
    assert not bad, bad
