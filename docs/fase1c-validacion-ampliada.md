# Fase 1c: validación ampliada de la austenita retenida

**Pregunta.** ¿La cadena de la fase 1 (equilibrio con pycalphad + Koistinen-Marburger) aguanta
datos nuevos e independientes de austenita retenida (AR), sin reajustar nada?

**Respuesta corta.** A medias: **9 de 18 casos comparables dentro de ±10 puntos**, justo la mitad.
Los 6 casos de tabla o texto (Nayak, González 2019, González-Pociño 2020) caen dentro; de los 12
leídos de una figura (Ortega-Cubillos) caen 3. Los 9 fallos son todos de la misma aleación (1,9 % Mo,
21 % Cr) y todos por debajo: el modelo da menos AR que la medida. Sumados a los 16 casos de la
fase 1 (7 aciertos), son 16 de 34. Nada del modelo cambió: ni parámetros ni código de cálculo.

## Los datos y cómo se compararon

Corte de la fase 1, fijado antes: ±10 puntos de AR por caso. La AR de todas las fuentes sale de
difracción de rayos X; el modelo se compara en la base de cada artículo. Los elementos que el
artículo no informa se toman como 0.

| Fuente | Aleación (% en peso) | Condición | Base | Dato |
|---|---|---|---|---|
| Nayak, Mücklich y Guitar (2023), *Met. Mater. Int.* 29, 934 (CC BY) | C 2,53; Cr 26,6; Mo 0,24; Ni 0,26; Mn 0,66; Si 0,37; Cu 0,03 | 980 °C, 0 / 0,5 / 1,5 h, aire | **volumen (supuesta)**: la tabla no la declara | tabla |
| González et al. (2019), *Metals* 9(9) 933 (CC BY) | C 3,01; Cr 18,2; Mo 2,05; Mn 0,82; Si 1,17 (sin Ni ni Cu) | 1.000 °C, 6 h, aire | masa | **texto** que describe la figura, no tabla |
| González-Pociño et al. (2020), *Metals* 10(3) 359 (CC BY) | C 2,7; Cr 25,1; Mo 0,5; Mn 0,8; Si 1,2 (sin Ni ni Cu) | 1.100 °C: exp. 2 (4 h, aire) y exp. 4 (8 h, aceite) | masa | tabla; **revenido posterior a 200 °C** |
| Ortega-Cubillos et al. (2015), *Rev. Fac. Ing. Univ. Antioquia* 76, 134 (CC BY-NC-SA 4.0) | C 2,98; Si 0,71; Mn 0,75; Mo 1,90; Ni 0,35; Cr 21,22; Cu 0,06 (Tabla 1) | 900-1.100 °C, 0,5-6 h; bruto de colada o recocido 700 °C 6 h | volumen (ASTM E975) | **digitalizado**, ±0,5 %; revenido de 200 °C 2 h |

## Resultados

Modelo = equilibrio a la temperatura indicada, temple a 25 °C. «Cuadra» es |diferencia| ≤ 10
puntos; en los digitalizados, ≤ 10,5 (10 más el error de lectura declarado). Diferencia = modelo −
publicado. Cifras salidas de ejecutar el código.

| Caso | Publicado | Modelo | Diferencia | ¿Cuadra? |
|---|---|---|---|---|
| Nayak 980 °C, 0 h | 10,2 | 5,3 | −4,9 | sí |
| Nayak 980 °C, 0,5 h | 7,1 | 5,3 | −1,8 | sí |
| Nayak 980 °C, 1,5 h | 5,1 | 5,3 | +0,2 | sí |
| González 2019, 1.000 °C 6 h | 13,0 | 10,8 | −2,2 | sí |
| González-Pociño 2020 exp. 2, 1.100 °C | 9,0 | 15,5 | +6,5 | sí |
| González-Pociño 2020 exp. 4, 1.100 °C | 7,3 | 15,5 | +8,2 | sí |
| Ortega bruto, 900 °C 6 h | 24,2 ± 0,5 | 3,1 | −21,0 | no |
| Ortega bruto, 1.000 °C 1 h | 29,1 ± 0,5 | 8,6 | −20,6 | no |
| Ortega bruto, 1.000 °C 2 h | 25,2 ± 0,5 | 8,6 | −16,6 | no |
| Ortega bruto, 1.000 °C 4 h | 24,1 ± 0,5 | 8,6 | −15,5 | no |
| Ortega bruto, 1.000 °C 6 h | 23,1 ± 0,5 | 8,6 | −14,5 | no |
| Ortega bruto, 1.100 °C 6 h | 37,1 ± 0,5 | 28,4 | −8,7 | sí |
| Ortega recocido, 900 °C 0,5 h | 26,1 ± 0,5 | 3,1 | −23,0 | no |
| Ortega recocido, 1.000 °C 0,5 h | 27,2 ± 0,5 | 8,6 | −18,6 | no |
| Ortega recocido, 1.050 °C 0,5 h | 21,1 ± 0,5 | 15,3 | −5,9 | sí |
| Ortega recocido, 1.050 °C 2 h | 22,1 ± 0,5 | 15,3 | −6,9 | sí |
| Ortega recocido, 1.050 °C 6 h | 38,1 ± 0,5 | 15,3 | −22,9 | no |
| Ortega recocido, 1.100 °C 0,5 h | 39,1 ± 0,5 | 28,4 | −10,7 | no (por 0,2) |

**Conteo: 9 de 18** (6 de 6 en tabla o texto; 3 de 12 en digitalizados). El criterio de la fase 1
(más de la mitad dentro del corte) no se cumple en este conjunto: 9 de 18 no es más de la mitad.

### Contexto y contraste (fuera del corte)

- **González-Pociño 2020, exp. 5 y 7** (1.000 °C, revenido de 200 °C): el artículo reporta «AR no
  detectada», sin cifra ni límite de detección. Es un dato censurado, no un cero: no entra al corte.
  El modelo da 5,7 % de AR en masa. Los otros 4 experimentos (revenido a 500 °C) tampoco se comparan,
  porque ese revenido transforma la AR.
- **Fortini et al. (2022)**, *Coatings* 12(8) 1218: aleaciones de recargue con Nb y 3,8-4,2 % de C,
  fuera de A532. La base no tiene Nb, así que el NbC (6-10 % de la masa) queda sin modelar. Solo
  como contraste. Diferencias del modelo: aleación 1 (1.000 °C 8 h, 900 °C 0,5 h, 980 °C 1,5 h)
  +18,1; +5,5 y +14,0; aleación 2 (las mismas) −8,2; −26,8 y +8,3 puntos. Sin patrón claro; no
  se usan.

## La digitalización (Ortega-Cubillos)

- **Fuente.** Acceso abierto en el sitio de la revista, CC BY-NC-SA 4.0. El PDF se bajó sin
  verificación anti-bots a `referencias-plantas/fundicion/austenita-retenida/ortega-cubillos2015/`.
  La AR solo está en las Figs. 6 (frente a la temperatura) y 7 (frente al tiempo), cada una con un
  panel de bruto de colada y otro de recocido. Se usan los datos, no el texto del artículo.
- **Método.** Cada figura es una imagen de unos 470 × 340 px. Los ejes se calibran con las marcas
  del eje derecho (21 marcas de 1 %, entre 40 y 20 %) y del inferior; cada marcador de AR
  (triángulo relleno de 8 px) se aísla por morfología y se ubica por su base. El script es
  reproducible (`digitalizar_ortega.py`, junto al PDF) y la tabla CSV con cada punto, su error y su figura
  de origen (`ar_digitalizada.csv`) está junto al PDF.
- **Error de lectura declarado: ±0,5 % de AR**, la mitad del paso de la escala más fina. La
  resolución real es mejor (unos 0,08 % por píxel, y los 14 puntos quedan a menos de 0,2 de un
  entero), pero se declara el paso entero.
- **Control.** Dos puntos salen en las dos figuras: bruto 1.000 °C 6 h (23,08 y 23,15 %) y recocido
  1.050 °C 0,5 h (21,12 y 21,12 %). Esa coincidencia, más el texto (la AR se midió solo en las
  condiciones de mayor dureza), fija lo que los pies de figura no dicen: Fig. 6 con 6 h (bruto) y
  0,5 h (recocido); Fig. 7 con 1.000 °C (bruto) y 1.050 °C (recocido). Los dos puntos repetidos
  entran una sola vez al corte: por eso son 12 y no 14.
- **Cómo se aplicó el corte.** Tolerancia = 10 + 0,5 puntos. El caso que falla por poco (recocido
  1.100 °C, −10,7) falla aun con el error sumado.

## Supuestos

- Ni y Cu no informados (González, González-Pociño) se toman como 0, decidido antes de comparar.
- **Nayak:** la base de la AR no se declara; se compara en volumen (5,3 %; en masa daría 5,4 %).
- **El modelo no ve** el estado inicial (bruto o recocido), el revenido de 200 °C ni el medio de
  enfriamiento tras desestabilizar (Ortega no lo informa; se supone temple a 25 °C). Tampoco el
  tiempo: da el mismo valor a 1, 2, 4 y 6 h.
- **Nayak a 0 y 0,5 h:** lo medido queda por encima del modelo porque aún no se llega al
  equilibrio. Es cinética (fase 1b), no un fallo de la cadena de equilibrio.

## Qué dicen los fallos

- **Ortega a 1.000 °C o menos: AR medida de 23-29 % frente a 3-9 %.** El hueco de Mo de la fase 1
  (1,8 % de Mo: −24 a −31 puntos) vuelve a aparecer con 1,9 % de Mo (−14 a −21). Pero González 2019,
  con 2,05 % de Mo, **sí cuadra** (−2,2): el Mo solo no lo explica y el hueco sigue abierto.
- **900 °C con horas.** Ortega mide 24-26 % de AR a 900 °C tras 6 h (bruto) y 0,5 h (recocido); el
  equilibrio da 3 %. Es el mismo patrón que Yu a 900 °C en la fase 1 (−14 puntos a 1 h), y 6 h
  no lo cierran.
- **El tiempo mueve la AR medida en sentidos que el modelo no tiene.** Bruto a 1.000 °C: baja de 29
  a 23 % de 1 a 6 h, como tendiendo al equilibrio (8,6 %) sin llegar. Recocido a 1.050 °C: sube de
  22 a 38 % entre 2 y 6 h, lo opuesto; Ortega lo atribuye a la redisolución de carburos secundarios.
- **Lo que sí se sostiene:** la AR sube de 1.000 a 1.100 °C, en el modelo y en lo medido, y las
  aleaciones con poco Mo (≤ 0,5 %) entre 980 y 1.100 °C caen dentro del corte (5 de 5).

## Huecos abiertos

- **900 °C con horas:** el equilibrio no explica AR de 24-26 % (Ortega) ni de 31 % (Fortini
  aleación 2, 0,5 h).
- **Mo alto (clase III):** Ortega (1,9 %) falla; González 2019 (2,05 %) cuadra. Falta una serie
  con Mo variable sobre una misma base.
- **Estado inicial:** la AR de Ortega depende del recocido previo, que el modelo no ve.
- **Ni, Cu y medio de enfriamiento:** varios artículos no los informan.

## Reproducir

```
pytest tests/test_validacion_ampliada.py
```

Los datos están en `tratamientos/validacion.py` (`extended_cases()`), con su fuente, base y notas.
Las pruebas fijan el conteo exacto (9 de 18) y los fallos como `xfail` estricto con su causa.
