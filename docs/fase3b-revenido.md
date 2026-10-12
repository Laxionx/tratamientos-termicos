# Fase 3b: revenido (Hollomon-Jaffe)

**Pregunta.** Si se mide la dureza tras revenidos de 1 h a varias temperaturas, ¿se puede predecir
la dureza tras revenidos de otra duración con el parámetro de Hollomon-Jaffe?

**Respuesta corta.** Pasa el corte, pero por poco: 19 de 36 predicciones quedan a ±25 HV (el corte
admitía hasta 18 fuera y quedaron 17). El error es sistemático: en los revenidos cortos (10 y 20
min) la dureza medida es mayor que la predicha, y en los largos (5 y 24 h), menor. Con C = 20 el
tiempo pesa menos de lo que pesa en esta fundición. Sirve para estimar, no para fijar un ciclo de
revenido sin ensayo.

## Modelo

- Parámetro de Hollomon y Jaffe: P = T·(C + log10 t), con T en K, t en horas y C = 20. Dos
  revenidos con el mismo P dejan la misma dureza.
- La curva dureza-P se arma con ensayos a un solo tiempo, interpolando linealmente en P. Predice
  cualquier par tiempo-temperatura cuyo P caiga dentro de lo ensayado; fuera de ese rango no
  extrapola y lanza un error.
- Tiempo equivalente: el que da el mismo P a otra temperatura.

```python
from tratamientos.revenido import HardnessCurve, equivalent_time_h

curve = HardnessCurve.from_tests([(400, 1, 407), (500, 1, 331), (600, 1, 278), (700, 1, 157)])
print(curve.predict(550, 5), equivalent_time_h(600, 2, 650))
```

## Datos

Salas Vicente, Carcel Carrasco, Fernández Antoni, Ferrero Taberner y Pascual Guillamón (2021),
*Metals* 11(2), 297, CC BY. Fundición nodular (C 3,25-3,70 %, Si 2,40-3,00 %) en tres grupos,
revenidos 10 min, 20 min, 1 h, 5 h y 24 h a 400, 500, 600 y 700 °C:

| Grupo | Tratamiento previo | Dureza de partida |
|---|---|---|
| agua | 15 min a 880 °C y temple en agua | 592 HV |
| aire | 15 min a 880 °C y aire forzado (ferrita y perlita fina) | 291 HV |
| agua tras 5 h | 5 h a 880 °C y temple en agua (ferrita y martensita) | 420 HV |

El artículo no publica la tabla de durezas: los 60 valores se leyeron de su Figura 6 (ejes
calibrados con el marco, cada punto ajustado al centro de su marcador y revisado sobre la imagen),
con un error de lectura de ±5 HV.

Dos discrepancias del artículo, documentadas y no corregidas:
- El pie de la Figura 5 cruza los paneles (b) y (c). El texto (tres veces) y la leyenda de la
  Figura 6 coinciden en que el grupo enfriado con aire parte de 291 HV y el de 5 h, de 420 HV; se
  sigue el texto.
- Su abscisa es T·(20 + ln t), con logaritmo natural, no la de Hollomon-Jaffe con log10. Equivale
  a 2,303·T·(8,7 + log10 t), es decir, a C ≈ 8,7.

Antes se buscaron tablas abiertas, sin éxito: el informe del ORNL sobre aceros 2,25-12 % Cr (OSTI
6792269), Judge et al. (2018) en *Scientific Reports* 8, 445, y un estudio de AISI D2 en
*Materials Research* (2023) tienen la dureza solo en gráficos. El del ORNL tiene revenidos de 2 h
y de 2 + 8 h que se superponen en sus curvas y no se pueden separar.

## Validación

Criterios fijados antes de digitalizar:
- Por grupo, la curva se arma solo con los 4 revenidos de 1 h y predice los de 10 min, 20 min, 5 h
  y 24 h cuyo P cae dentro de lo ajustado: 36 casos. Quedan fuera de rango, y no se predicen, los
  de 400 °C a 10 y 20 min y los de 700 °C a 5 y 24 h.
- Tolerancia ±25 HV (entre ±2 y ±4 HRC según la dureza). Corte: falla si quedan fuera más de la
  mitad.

| Grupo | Dentro de ±25 HV | Sesgo, revenidos cortos | Sesgo, revenidos largos |
|---|---|---|---|
| agua | 6 de 12 | −22,8 HV | +28,3 HV |
| aire | 8 de 12 | −13,3 HV | +12,3 HV |
| agua tras 5 h | 5 de 12 | −37,9 HV | +21,5 HV |
| **Total** | **19 de 36** | | |

Sesgo = predicha − medida. El error absoluto medio es 24,1 HV. Los 17 casos fuera están marcados
uno a uno como fallos esperados (xfail estricto) en `tests/test_revenido.py`.

**Sensibilidad.** Con C = 18 también quedan 17 fuera (error medio 21,9 HV). Solo como dato, fuera
del veredicto: con la abscisa del propio artículo (C ≈ 8,7) quedan 10 fuera de 33 casos en rango
(17,6 HV). Un C menor da más peso al tiempo, como ya indica el sesgo. No se adopta: elegir C con
los mismos datos que se validan sería ajustar sobre la prueba.

**Mutaciones.** Se probaron 10 cambios deliberados al código y a los datos (logaritmo natural, °C
en vez de K, otro C por defecto, tiempo equivalente sin C, extrapolar, no ordenar los ensayos,
aceptar P repetidos o un solo ensayo, un dato de 1 h mal copiado y un tiempo mal copiado): las
pruebas detectan los 10.

## Límites

- Una sola fundición nodular de un solo laboratorio. No son los hierros blancos alto cromo de las
  bolas de molienda: en ellos el parámetro no aplica, porque la austenita retenida que se
  transforma a 450-550 °C los endurece al revenir y rompe la equivalencia entre tiempo y
  temperatura.
- El grupo enfriado con aire casi no se ablanda hasta que el parámetro del artículo llega a 16:
  a 400 °C su dureza no cambia en 24 h.
- La lectura de la figura agrega ±5 HV a cada dato.

Ejemplo: `python ejemplos/revenido_nodular.py --temperatura 550 --tiempo 2`.
