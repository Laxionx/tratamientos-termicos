# Fase 1b: el tiempo de permanencia en la desestabilización

**Pregunta.** ¿Los fallos de la fase 1 se deben a que falta la cinética? Es decir, ¿la austenita
retenida (AR) medida tiende, con el tiempo de permanencia, al valor de equilibrio que predice la
fase 1?

**Respuesta corta.** En la serie de tiempos disponible, sí: la AR baja con el tiempo y a 24 h
queda cerca del equilibrio. Pero eso **no explica** el fallo con Mo de la fase 1: otro estudio del
mismo laboratorio, con casi la misma aleación, mide 28 puntos más de AR en las mismas condiciones.
El problema es la discrepancia entre los datos, no la falta de tiempo.

## Datos

González-Pociño, Álvarez-Antolín y Asensio-Lozano (2019), *Metals* 9(5), 522 (CC BY), Tabla 2:
- **Aleación:** 3,0 C; 18,2 Cr; 2,0 Mo; 0,8 Mn; 1,2 Si.
- **Tratamiento:** 4, 8, 12 y 24 h a 1.000 °C, enfriadas al aire o en aceite. Antes de
  desestabilizar las piezas pasaron por 700 °C, que transforma la austenita en perlita.
- **Medición:** Rietveld.

| Permanencia | AR, aire | AR, aceite | Carburos, aire | Carburos, aceite |
|---|---|---|---|---|
| 4 h | 8,2 | 6,6 | 55,2 | 43,3 |
| 8 h | 9,9 | 6,9 | 54,6 | 56,5 |
| 12 h | 2,6 | 2,3 | 51,8 | 52,9 |
| 24 h | 2,8 | 2,2 | 52,9 | 46,4 |

Equilibrio de la fase 1 para esta aleación a 1.000 °C: **AR 10,6 %**, carburos 30,4 % y Ms de 196 °C.

## Resultados

Tolerancias fijadas antes de mirar la tabla ([tests/test_cinetica.py](../tests/test_cinetica.py)):

| Prueba | Tolerancia | Resultado |
|---|---|---|
| 1. La AR baja con el tiempo y a 24 h queda cerca del equilibrio | ±10 puntos | ✅ 2,8 y 2,2 % frente a 10,6 % (aire y aceite) |
| 2. Carburos a 24 h contra el equilibrio | ±5 puntos | ❌ 52,9 y 46,4 % frente a 30,4 % (se esperaba) |
| 3. Avrami ajustado a la serie en aceite predice el otro estudio (*Materials* 12, 3252) | ±10 puntos | ❌ predice ~4,5 % donde se midió 34,2 y 41,5 % |

## Qué se aprendió

- **El otro estudio del mismo grupo no coincide.** En *Materials* 2019 (aleación con 1,8 % Mo, 4 h
  a 1.000 °C, aceite) midieron 34,2 % de AR; en *Metals* 2019, con 2,0 % Mo, 6,6 %. Son 28 puntos
  de diferencia en condiciones casi iguales. El fallo de la fase 1 con Mo no puede atribuirse a la
  falta de tiempo: con los datos de *Metals*, la fase 1 acierta.
- **Una posible causa** (hipótesis posterior a ver los datos, no probada): el punto de partida. En
  *Metals* las piezas se perlitizaron a 700 °C antes de desestabilizar; en *Materials* no se
  informa ese paso. Partir de perlita o de austenita bruta de colada cambiaría la cinética.
- **La AR medida queda por debajo del equilibrio del modelo** (2-3 % frente a 10,6 %). El modelo
  de aproximación al equilibrio desde arriba no puede representarla: el ajuste de Avrami
  degenera, con τ en el límite.
- **Los carburos no llegan al equilibrio ni en 24 h:** quedan carburos eutécticos de una
  solidificación fuera del equilibrio, más la precipitación al enfriar al aire.

## Lo que falta para cerrar

- Un mismo laboratorio midiendo AR en función del tiempo, partiendo del estado bruto de colada y
  del perlitizado, para probar la hipótesis del punto de partida.
- Series a varias temperaturas para poder extrapolar la cinética. Con una sola, no se extrapola.
