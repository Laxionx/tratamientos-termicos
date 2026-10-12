# tratamientos-termicos

Tratamientos térmicos de fundiciones blancas y aceros, implementados **desde la literatura** y
validados contra mediciones publicadas en acceso abierto. Usa termodinámica computacional
(pycalphad) con una base de datos abierta, sin software comercial.

## Fase 1: desestabilización de hierros blancos alto cromo (ASTM A532)

Para una composición y una temperatura de desestabilización, la cadena calcula:
1. el equilibrio de fases con pycalphad y la base MatCalc;
2. la Ms de la austenita (Andrews 1965);
3. la martensita que se forma al enfriar (Koistinen y Marburger 1959);
4. la austenita retenida y los carburos.

```python
from tratamientos import destabilize

r = destabilize({"C": 2.9, "CR": 18.9, "MN": 1.5, "CU": 1.5, "SI": 0.7}, 1000)
print(r.ms_c, r.retained_austenite("volumen"), r.carbides("volumen"))
```

**Resultado de la validación: no pasa el criterio de corte fijado antes de correr.** Solo 7 de
16 casos de austenita retenida, de 3 artículos, quedan dentro de ±10 puntos.
- **Acierta los carburos** de las aleaciones solo al Cr (a 2 puntos o menos). En esas
  aleaciones, la austenita retenida entre 950 y 1.050 °C queda a 8 puntos o menos, pero el
  acierto depende de un reparto Mn/Cu que el artículo no publica: es una confirmación débil.
- **Falla** a 900 °C, donde la precipitación no llega al equilibrio en 1 h.
- **Falla** con 1,8 % de Mo: subestima la austenita retenida en 24 a 31 puntos.
- **No captura** el efecto del medio de temple.

El detalle, con cada caso, está en
[docs/fase1-desestabilizacion.md](docs/fase1-desestabilizacion.md).

## Instalación

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
curl -L --create-dirs -o tdb/mc_fe_v2.059.pycalphad.tdb https://raw.githubusercontent.com/pycalphad/pycalphad/develop/examples/databases/mc_fe_v2.059.pycalphad.tdb
.venv\Scripts\python -m pytest
```

La base `mc_fe_v2.059` es la base de aceros de MatCalc (TU Wien, E. Povoden-Karadeniz), con
licencia [ODbL 1.0](http://opendatacommons.org/licenses/odbl/1.0/). No se versiona: se descarga
con el comando de arriba.

## Hoja de ruta

| Fase | Contenido |
|---|---|
| 1 ✅ | Desestabilización: austenita retenida y carburos (validada; acierta solo en una ventana) |
| 2 | Temple de la bola: enfriamiento según diámetro y medio, y perfil de dureza |
| 3 | Revenido (Hollomon-Jaffe) y cálculo de carga del horno |
| Más adelante | Pirometalurgia no ferrosa: fundición de Cu y Sn, y refinación |

## Licencia

MIT · Anthony Vera Baldeón. Construido con desarrollo asistido por IA (Claude Code), con revisión
y pruebas propias.
