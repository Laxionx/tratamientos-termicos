"""«Estado de la operación» y «Prueba esto» de la pestaña Temple: el ejemplo está en rango, cada
experimento hace lo que dice su texto, sus botones ponen el cambio en la barra lateral y los
indicadores nuevos no mueven ninguna cifra que la app ya mostraba."""

import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app" / "streamlit_app.py")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "app"))

import calculo  # noqa: E402
import i18n  # noqa: E402
import temple_estado as te  # noqa: E402
from dibujo import es  # noqa: E402


def run(lang: str = "es") -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    at.query_params["lang"] = lang
    return at.run()


def lines(at: AppTest) -> list[str]:
    return [m.value for m in at.markdown]


def niveles(view) -> list[str]:
    with i18n.use("es"):
        return [f.nivel for f in te.filas_estado(view)]


def test_el_ejemplo_esta_en_rango_y_son_tres_chequeos():
    assert niveles(te.evaluar()) == ["ok", "ok", "ok"]


def test_la_solucion_numerica_coincide_con_la_serie_en_todo_el_rango_de_los_controles():
    for medium in calculo.MEDIA:
        for d in (0.5, 0.75, 1.36, 2.0, 2.77, 5.0):
            an = calculo.analytic_check(te.evaluar(diameter=d, medium=medium))
            assert an.checked and an.within and abs(an.error) < 1e-3, (medium, d, an.error)


def test_fuera_del_biot_comprobado_el_panel_avisa_y_no_inventa_un_error(monkeypatch):
    monkeypatch.setattr(calculo, "BIOT_COMPROBADO", (20.0, 50.0))
    monkeypatch.setattr(te, "BIOT_COMPROBADO", (20.0, 50.0))
    an = calculo.analytic_check(te.evaluar())  # Bi = 6,4
    assert not an.checked and not an.within and an.error != an.error  # nan
    assert niveles(te.evaluar()) == ["ok", "aviso", "ok"]


@pytest.mark.parametrize("diameter", [0.5, 3.0, 5.0])
def test_fuera_del_rango_validado_el_panel_avisa_con_el_texto_de_siempre(diameter):
    view = te.evaluar(diameter=diameter)
    with i18n.use("es"):
        rows = te.filas_estado(view)
    assert rows[0].nivel == "aviso" and rows[0].texto.startswith("Fuera del rango validado")
    assert [f.nivel for f in rows[1:]] == ["ok", "ok"]


@pytest.mark.parametrize("exp", te.EXPERIMENTOS_TEMPLE, ids=lambda e: e.clave)
def test_cada_experimento_del_temple_hace_lo_que_dice_su_texto(exp):
    base = te.magnitudes(te.evaluar(**exp.base))
    nuevo = te.magnitudes(te.evaluar(**{**exp.base, **exp.cambios}))
    for nombre, signo in exp.direcciones.items():
        assert (nuevo[nombre] - base[nombre]) * signo > 0, (exp.clave, nombre)
    assert niveles(te.evaluar(**{**exp.base, **exp.cambios})) == ["ok", "ok", "ok"]


def test_los_numeros_de_los_experimentos():
    pares = {e.clave: (a, b) for e, a, b in te.pares()}
    a, b = pares["tamano"]
    ma, mb = te.magnitudes(a), te.magnitudes(b)
    assert abs(mb["v_sup"] / ma["v_sup"] - 1) < 0.05  # «la superficie casi no cambia»
    assert b.params.diameter_in == 2.5 and b.in_validated_range
    a, b = pares["capa"]
    assert a.critical is not None and a.critical.whole  # con 20 °C/s toda la bola la alcanza
    assert b.critical is not None and not b.critical.whole and not b.critical.none
    assert 0 < b.critical.depth_mm < b.radius_mm
    a, b = pares["medio"]
    assert (a.params.medium, b.params.medium) == ("agua", "aceite")


@pytest.mark.parametrize("lang", ["es", "en"])
def test_los_textos_de_las_pruebas_llevan_las_cifras_del_modelo(lang):
    with i18n.use(lang):
        pruebas = {p.clave: p for p in te.pruebas_temple()}
        base = te.magnitudes(te.evaluar())
        assert es(base["t_centro"], 1) in pruebas["medio"].texto
        assert es(base["biot"], 1) in pruebas["tamano"].texto
        assert "100" in pruebas["capa"].texto
        assert set(pruebas) == {e.clave for e in te.EXPERIMENTOS_TEMPLE}
        # los cuatro datos van siempre: el resultado no depende de lo que hubiera antes
        assert all(len(p.cambios) == 4 for p in pruebas.values())
        assert pruebas["medio"].cambios["dato_medium"] == i18n.opt("aceite")


@pytest.mark.app
@pytest.mark.parametrize("lang", ["es", "en"])
def test_el_ejemplo_muestra_seis_indicadores_cortos_y_el_panel_en_rango(lang):
    at = run(lang)
    assert not at.exception and not at.error and not at.warning
    view = te.evaluar()
    c, _, s = view.crossings
    with i18n.use(lang):
        valores = {m.label: m.value for m in at.metric}
        assert valores[i18n.t("q.m.center")] == f"{es(c.time_s, 1)} s"
        assert valores[i18n.t("q.m.center_rate")] == f"{es(c.rate, 1)} °C/s"
        assert valores[i18n.t("q.m.surface_rate")] == f"{es(s.rate, 0)} °C/s"
        assert valores[i18n.t("q.m.biot")] == es(view.biot, 1)
        assert valores[i18n.t("q.m.h")] == es(view.h, 0)
        assert valores[i18n.t("q.m.grossmann")] == f"{es(view.grossmann, 1)} in⁻¹"
        cortos = [m.label for m in at.metric if m.label != i18n.t("v.metric", pct="15")]
        assert all(len(label) <= 24 for label in cortos), cortos
        assert any(ln.startswith(":green-badge[") and i18n.t("estado.todo_ok") in ln
                   for ln in lines(at))  # fmt: skip


@pytest.mark.app
@pytest.mark.parametrize("lang", ["es", "en"])
def test_los_botones_ponen_el_cambio_y_el_panel_y_los_indicadores_lo_reflejan(lang):
    at = run(lang)
    next(b for b in at.button if b.key == "q_prueba_medio").click().run()
    assert not at.exception and not at.error
    medio = next(w for w in at.sidebar.selectbox if w.key == "dato_medium")
    with i18n.use(lang):
        assert medio.value == i18n.opt("aceite")
        c = te.evaluar(medium="aceite").crossings[0]
        valores = {m.label: m.value for m in at.metric}
        assert valores[i18n.t("q.m.center_rate")] == f"{es(c.rate, 1)} °C/s"
    next(b for b in at.button if b.key == "q_prueba_tamano").click().run()
    diametro = next(w for w in at.sidebar.number_input if w.key == "dato_diameter")
    medio = next(w for w in at.sidebar.selectbox if w.key == "dato_medium")
    with i18n.use(lang):
        assert diametro.value == 2.5 and medio.value == i18n.opt("agua")  # parte del ejemplo
    next(b for b in at.button if b.key == "q_prueba_capa").click().run()
    assert not at.exception and not at.error
    assert next(w for w in at.sidebar.checkbox if w.key == "dato_compare").value is True
    assert next(w for w in at.sidebar.number_input if w.key == "dato_critical").value == 100.0
    assert any("mm" in i.value and "**" in i.value for i in at.info)
    next(b for b in at.button if b.key == "q_prueba_reset").click().run()
    assert not at.exception and not at.info
    assert next(w for w in at.sidebar.number_input if w.key == "dato_diameter").value == 2.0


@pytest.mark.app
def test_fuera_de_rango_el_aviso_va_en_el_panel_y_nada_mas_avisa():
    at = run("es")
    at.sidebar.number_input[0].set_value(4.0).run()
    assert not at.exception and not at.warning
    avisos = [ln for ln in lines(at) if ln.startswith(":orange-badge[Aviso]")]
    assert len(avisos) == 1 and "Fuera del rango validado" in avisos[0]


@pytest.mark.app
@pytest.mark.parametrize("lang", ["es", "en"])
def test_la_validacion_resume_sus_cifras_en_una_fila(lang):
    at = run(lang)
    rows = [r for r in calculo.nbs_rows() if not r.calibration]
    peor = max(rows, key=lambda r: abs(r.deviation))
    media = sum(r.deviation for r in rows) / len(rows)
    fmt = (lambda x: f"{100 * x:+.1f} %") if lang == "en" else (
        lambda x: f"{100 * x:+.1f} %".replace(".", ","))  # fmt: skip
    with i18n.use(lang):
        valores = {m.label: m.value for m in at.metric}
        assert valores[i18n.t("v.metric", pct="15")] == i18n.t("v.metric.value", n=7, m=11)
        assert valores[i18n.t("v.m.worst")] == fmt(peor.deviation) == fmt(0.1935)
        assert valores[i18n.t("v.m.mean")] == fmt(media)
