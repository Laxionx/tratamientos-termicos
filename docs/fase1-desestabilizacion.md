# Fase 1: desestabilización de hierros blancos alto cromo

**Pregunta.** Dada la composición de un hierro blanco alto cromo y la temperatura de
desestabilización, ¿se puede predecir desde la literatura cuánta austenita retenida y cuántos
carburos quedan después del temple?

**Respuesta corta.** No: la cadena no pasa el criterio de corte fijado antes de correr. Acierta
los carburos de las aleaciones solo al Cr y el signo de los efectos de la temperatura, pero la
austenita retenida falla por decenas de puntos fuera de una ventana estrecha. Dentro de esa
ventana (Yu, 950-1.050 °C) el acierto depende de un dato que el artículo no publica.

## La cadena

1. **Equilibrio a la temperatura de desestabilización.** Se calcula con pycalphad y la base de
   aceros de MatCalc (mc_fe v2.059, ODbL). Da la fracción de carburos (M7C3, M23C6…) y la
   composición de la austenita. Supone que la permanencia alcanza el equilibrio.
2. **Ms de esa austenita.** Andrews (1965) como fórmula principal y Steven y Haynes (1956) como
   contraste. Las dos se ajustaron para aceros: aplicarlas a la austenita de un hierro blanco es
   una extrapolación.
3. **Koistinen y Marburger (1959).** Al enfriar hasta la temperatura final transforma una fracción
   1 − exp(−0,011·(Ms − T)) de la austenita; el resto queda retenido.
4. **Masa y volumen.** Las fracciones salen en masa y, con densidades aproximadas (M7C3 6,9;
   matriz 7,7 g/cm³), en volumen.

No modela el medio de temple, la precipitación durante el enfriamiento ni el revenido.

## Datos de validación (acceso abierto)

| Fuente | Aleación | Tratamiento | Medido |
|---|---|---|---|
| Yu, Li, Feng y Wu (2026), *Materials* 19, 896 (CC BY) | 2,9 C; 18,9 Cr; Mn+Cu 3,1; Si 0,7 | 1 h a 900-1.050 °C, agua; revenido 300 °C | AR y carburos por XRD, % vol |
| González-Pociño et al. (2019), *Materials* 12, 3252 (CC BY) | 2,9 C; 18,1 Cr; 1,8 Mo; 0,8 Mn; 1,2 Si | 4-8 h a 1.000 y 1.100 °C, aire o aceite; revenido 200 °C | Rietveld, % masa |
| Higuera-Cobos et al. (2016), *Rev. Fac. Ing.* 25(41) (CC BY-NC) | 3,0 C; 25 Cr (no publica el resto) | 1 h a 950 °C; aire, agua, aceite y −80 °C | AR por XRD (ASTM E975) |
| Tupaj et al. (2020), *Materials* 13, 2760 (CC BY) | 3,5 C; 15,3 Cr; 0,5 Mo; 0,3 Ni; 0,65 Mn; 1,1 Si | 30 min a 1.000 °C | Ms por dilatometría; carburos |

Decisiones tomadas antes de comparar:
- Yu publica Mn y Cu sumados: se reparten 50/50.
- El La de Yu no está en la base y se omite.
- De González-Pociño solo entran los experimentos con revenido a 200 °C (2, 4, 5 y 7). Los
  revenidos a 500 °C transforman la AR, y eso queda fuera del modelo.
- En Higuera-Cobos los elementos no publicados se toman como cero.
- Se supone que los revenidos de 200 y 300 °C no cambian la AR. En alto cromo es estable hasta
  400-500 °C, según la introducción de Tupaj.

## Resultados

Tolerancias fijadas antes de correr: AR ±10 puntos; carburos ±5 puntos. Criterio de corte: si
fallan más de la mitad de los 16 casos de AR, la cadena no predice.

| Caso | AR modelo | AR medida | Diferencia | Carburos modelo | Carburos medidos |
|---|---|---|---|---|---|
| Yu M1, 900 °C | 6,9 | 21,1 | **−14,2** | 31,4 | 29,6 |
| Yu M1, 950 °C | 11,2 | 17,4 | −6,2 | 30,6 | 31,1 |
| Yu M1, 1.000 °C | 19,1 | 18,1 | +0,9 | 29,8 | 30,5 |
| Yu M1, 1.050 °C | 33,6 | 27,7 | +5,9 | 28,9 | 28,0 |
| Yu M2, 900 °C | 6,7 | 20,4 | **−13,8** | 31,8 | 29,4 |
| Yu M2, 950 °C | 10,8 | 16,2 | −5,4 | 31,1 | 31,2 |
| Yu M2, 1.000 °C | 18,4 | 15,9 | +2,5 | 30,3 | 32,0 |
| Yu M2, 1.050 °C | 32,4 | 24,8 | +7,6 | 29,4 | 28,3 |
| González-Pociño exp. 5, 1.000 °C | 10,4 | 34,2 | **−23,8** | 29,1 | **36,6** |
| González-Pociño exp. 7, 1.000 °C | 10,4 | 41,5 | **−31,1** | 29,1 | **39,5** |
| González-Pociño exp. 2, 1.100 °C | 35,3 | 42,2 | −6,9 | 27,2 | **47,7** |
| González-Pociño exp. 4, 1.100 °C | 35,3 | 61,1 | **−25,8** | 27,2 | 29,6 |
| Higuera-Cobos, aire | 3,4 | 26,2 | **−22,8** | | |
| Higuera-Cobos, agua | 3,4 | 28,5 | **−25,1** | | |
| Higuera-Cobos, aceite | 3,4 | 35,5 | **−32,1** | | |
| Higuera-Cobos, −80 °C | 1,1 | 14,3 | **−13,2** | | |

**7 de 16 casos de AR dentro de ±10 puntos: no pasa el criterio de corte.** Carburos: los 8 de
Yu y uno de González-Pociño dentro de ±5 puntos; los otros 3 de González-Pociño, fuera.

Otras pruebas fijadas antes:
- **Tendencia:** la AR del modelo sube de 1.000 a 1.050 °C (Yu) y de 1.000 a 1.100 °C
  (González-Pociño), como lo medido. ✅
- **Ms de Tupaj:** 66 °C con Andrews, dentro de lo medido según el enfriamiento (20-128 °C). ✅ Con
  Steven y Haynes, 18 °C.
- **Tupaj en nitrógeno líquido:** el modelo deja ≤ 5 % de AR a −196 °C, y el artículo no observó
  AR. ✅
- **Carburos de Tupaj:** 35,7 % frente a 29,2-30,7 %. ❌ Por 0,7 puntos.

## Qué dicen los fallos

- **A 900 °C el equilibrio no llega en 1 h.** La AR medida es mayor a 900 que a 950 °C; el modelo,
  que supone equilibrio, la da mínima a 900 °C. Es cinética de precipitación, que el modelo no
  tiene.
- **Con 1,8 % de Mo el modelo subestima la AR por 24-31 puntos a 1.000 °C,** aun con 4 a 8 h de
  permanencia. No es tiempo: algo de la austenita con Mo no lo captura la cadena. Puede ser la
  partición del Mo en la base o la fórmula de Ms, que da al Mo un efecto chico (−7,5 °C/%).
- **Higuera-Cobos solo publica C y Cr.** Sin Mo, Ni ni Mn, la austenita queda con 0,37 % C y Ms de
  296 °C. El caso estaba mal especificado desde el inicio, pero se declaró antes de correr y
  cuenta.
- **El medio de temple no entra al modelo.** En Higuera-Cobos la AR va de 26 % (aire) a 36 %
  (aceite) con la misma aleación; en Tupaj la Ms medida va de 128 a 20 °C según el enfriamiento.

## Ojo con el acierto de Yu

Yu publica el Mn y el Cu sumados (3,1 %), y el reparto pesa mucho, porque Andrews no tiene
término de Cu. AR del modelo para la muestra 1 según el reparto:

| Temperatura | Todo Mn | 50/50 (el usado) | Todo Cu |
|---|---|---|---|
| 900 °C | 9,1 | 6,9 | 0 |
| 950 °C | 15,2 | 11,2 | 0 |
| 1.000 °C | 26,6 | 19,1 | 0 |
| 1.050 °C | 48,3 | 33,6 | 22,8 |

El acierto a 1.000 °C (19,1 frente a 18,1 %) depende del reparto 50/50, que se decidió antes de
comparar pero no se conoce. Es una confirmación débil.

## Lo que sí sirve

- Los **carburos** de las aleaciones solo al Cr salen a 2 puntos o menos (Yu, 8 casos). Eso casi
  no depende del reparto Mn/Cu.
- El **signo** del efecto de la temperatura sobre la AR entre 1.000 y 1.100 °C.
- La casi desaparición de la AR al enfriar en **nitrógeno líquido**.
- La **Ms** de Tupaj, dentro del rango medido.

Para predecir la AR de una aleación concreta, esta cadena no sirve: el error es de decenas de
puntos fuera de la ventana de Yu, y dentro de ella depende de un dato no publicado.

No se calibró nada contra estos datos. Las mutaciones del código hacen fallar las pruebas.

La fase 1c ([docs](fase1c-validacion-ampliada.md)) repite la prueba con datos nuevos de AR, sin
reajustar: 9 de 18 casos dentro del corte.
