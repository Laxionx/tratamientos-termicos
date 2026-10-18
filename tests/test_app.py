"""App «Temple de la bola»: humo con AppTest, controles y tabla de datos desde UNA definición, y
valores manipulados que no deben tumbar el servidor."""

import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app" / "streamlit_app.py")
sys.path.insert(0, str(ROOT / "app"))

import controles  # noqa: E402
import i18n  # noqa: E402


def _widgets(at: AppTest) -> list:
    return [*at.sidebar.number_input, *at.sidebar.selectbox, *at.sidebar.checkbox]


def test_las_tres_pestanas_cargan_sin_excepciones():
    at = AppTest.from_file(APP, default_timeout=180).run()
    assert not at.exception and not at.error
    assert [t.label for t in at.tabs] == ["Guía", "Temple", "Validación"]
    values = {m.label: m.value for m in at.metric}
    assert values["Centro baja a 720 °C a los"] == "12,7 s"
    assert values["Velocidad del centro a 720 °C"] == "29,7 °C/s"
    assert values["Predicciones dentro de ±15 %"] == "7 de 11"
    assert not at.warning  # 2 pulgadas está dentro del rango validado


def test_los_controles_salen_de_la_misma_definicion_que_la_tabla():
    at = AppTest.from_file(APP, default_timeout=180).run()
    widgets = {w.key: w for w in _widgets(at)}
    assert set(widgets) == {controles.PREFIX + d.key for d in controles.DATOS}
    for d in controles.DATOS:  # el widget de la barra lateral es lo que dice la definición
        w = widgets[controles.PREFIX + d.key]
        if d.widget == "number":
            assert (w.min, w.max, w.value) == (d.lo, d.hi, d.default), d.key
        elif d.widget == "select":
            assert (list(w.options), w.value) == (list(d.options), d.default), d.key
        else:
            assert w.value == d.default, d.key
    table = controles.data_table()
    assert list(table["Dato"][: len(controles.DATOS)]) == [d.label for d in controles.DATOS]
    assert len(table) == len(controles.DATOS) + len(controles.FIJOS)
    text = " ".join(m.value for m in at.markdown)  # y la guía muestra la misma tabla
    for d in controles.DATOS:
        assert d.label in text
    for name, _, _ in controles.FIJOS:
        assert i18n.t(name) in text


def test_la_tabla_recoge_un_dato_nuevo_sola(monkeypatch):
    extra = controles.Dato("nuevo", "Dato nuevo", "", 0, 1, 0.5, 0.1, "x", "y")
    monkeypatch.setattr(controles, "DATOS", (*controles.DATOS, extra))
    assert "Dato nuevo" in list(controles.data_table()["Dato"])


def test_no_se_ofrece_un_h_libre_ni_de_manual_y_las_temperaturas_son_fijas():
    labels = " ".join(d.label.lower() for d in controles.DATOS)
    assert "coeficiente" not in labels and " h " not in f" {labels} "
    assert {d.key for d in controles.DATOS} == {"diameter", "medium", "compare", "critical"}
    assert [(i18n.t(n), v) for n, _, v in controles.FIJOS] == [
        ("Temperatura de austenización", 875.0),
        ("Temperatura del medio", 20.0),
    ]
    assert controles.BY_KEY["medium"].options == ("agua", "aceite")


def test_fuera_del_rango_validado_se_rotula():
    at = AppTest.from_file(APP, default_timeout=180).run()
    for diameter, warns in ((0.5, True), (0.75, False), (2.77, False), (3.0, True), (5.0, True)):
        at.sidebar.number_input[0].set_value(diameter).run()
        assert not at.exception
        assert any("Fuera del rango validado" in w.value for w in at.warning) is warns, diameter


def test_la_comparacion_critica_empieza_apagada_y_muestra_el_espesor():
    at = AppTest.from_file(APP, default_timeout=180).run()
    assert at.sidebar.checkbox[0].value is False
    assert not at.info
    at.sidebar.number_input[0].set_value(2.0)
    at.sidebar.checkbox[0].set_value(True)
    at.sidebar.number_input[1].set_value(100.0).run()
    assert not at.exception
    assert any("de espesor" in i.value and "no es dureza" in i.value for i in at.info)


@pytest.mark.parametrize("extreme", ["min", "max"])
@pytest.mark.parametrize("compare", [False, True])
def test_controles_en_los_extremos_no_tumban_la_app(extreme, compare):
    at = AppTest.from_file(APP, default_timeout=180).run()
    for w in at.sidebar.number_input:
        w.set_value(w.min if extreme == "min" else w.max)
    at.sidebar.selectbox[0].set_value("agua" if extreme == "min" else "aceite")
    at.sidebar.checkbox[0].set_value(compare).run()
    assert not at.exception and not at.error


@pytest.mark.parametrize("value", [10_000_000, -5, float("inf"), float("nan")])
def test_el_servidor_rechaza_valores_fuera_de_rango(value):
    # Un cliente puede mandar valores sin pasar por el navegador: Streamlit (versión fijada en
    # requirements.txt) los devuelve al valor por defecto en el servidor.
    at = AppTest.from_file(APP, default_timeout=180).run()
    for w in at.sidebar.number_input:
        w.set_value(value)
    at.run()
    assert not at.exception
    assert [w.value for w in at.sidebar.number_input] == [
        d.default for d in controles.DATOS if d.widget == "number"
    ]


def test_un_fallo_del_modelo_se_muestra_sin_traza(monkeypatch):
    import calculo

    def fails(params):
        raise ValueError("el diámetro debe ser positivo")

    monkeypatch.setattr(calculo, "run_quench", fails)
    at = AppTest.from_file(APP, default_timeout=180).run()
    assert not at.exception
    assert any("el diámetro debe ser positivo" in e.value for e in at.error)


def test_la_app_no_necesita_pycalphad():
    sep = chr(10)
    code = sep.join(
        [
            f"import sys; sys.path[:0] = [{str(ROOT)!r}, {str(ROOT / 'app')!r}]",
            "import calculo, bola_svg, graficos, controles, guia",
            "calculo.run_quench(calculo.QuenchParams()); calculo.nbs_rows()",
            "assert 'pycalphad' not in sys.modules, 'importó pycalphad'",
        ]
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr[-500:]
