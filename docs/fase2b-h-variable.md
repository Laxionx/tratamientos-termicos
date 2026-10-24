# Fase 2b: h que depende de la temperatura de superficie (aceite)

**Pregunta.** Si h sigue la forma real del temple en aceite (capa de vapor hasta unos 620 °C, pico
cerca de 490 °C, convección al final) y solo se calibra su magnitud con la esfera de 3/4 in, ¿desaparece
el sesgo de +10 a +16 % de las esferas grandes del NBS? ¿Y predice otra sonda medida en otro laboratorio?

**Respuesta corta.** **No, y empeora.** Con un solo factor de escala (2,67), las cinco esferas no
calibradas quedan entre +24 y +50 % de error (el h constante, entre −3 y +16 %), y el error medio
absoluto sube de 11,3 a 33,7 %. La sonda de Liščić, con ese mismo factor, sale entre 24 y 306 % por
encima de lo publicado. Los dos cortes fijados antes de correr fallan. La hipótesis de que la capa
de vapor explica el sesgo de las esferas grandes en aceite no se sostiene con estos datos.
El módulo es `tratamientos/temple_ht.py`; `temple.py` y la app no cambiaron.

## Qué se hizo

- **Forma de h(Ts)** (Liščić, Matijević, Totten y Canale 2016, Proc. 3rd MCHT&SE, Portorož; Kalenol 32
  quieto a 28 °C, sonda de Liščić). Cinco nodos, lineales por tramos y planos fuera de ellos:

| Ts (°C) | h (W/m²K) | Origen |
|---|---|---|
| ≥ 800 | 750 | película; leída de la Fig. 4 (750-780 entre 700 y 800 °C, ±50). Consistente con los 600-900 que se deducen de Ramesh y Prabhu 2014 |
| 620 | 520 | fin de la película (qcr2): 620 °C es dato del texto y la Tabla 1; 520 se lee de la Fig. 4 (±50) |
| 490 | 1.940 | pico, texto y Tabla 1 |
| 380 | 250 | hombro posterior al pico, Fig. 4 (±50) |
| ≤ 150 | 200 | cola convectiva, Fig. 4 (±50) |

  Los valores «Fig. 4» no son una digitalización fina: son la lectura de una curva suave, sin
  barras de error publicadas. No se ajustó ninguno.
- **Un solo parámetro libre:** el factor de escala `s` de toda la curva, calibrado para que la esfera de
  3/4 in dé 60 °C/s en el centro a 720 °C (NBS, aceite). Resultado: **s = 2,672** (pico de 5.185 W/m²K,
  2,7 veces el de Liščić; el h constante vigente es 1.657).
- **Solver** no lineal (volúmenes finitos, LSODA): esfera (propiedades constantes de la austenita, las
  mismas de `temple.py`) y cilindro radial 1D. Con h constante reproduce `temple.py` (diferencia del
  orden de 1e-6, la prueba exige ≤ 0,5 %); el balance de energía cierra a 0,2 % (prueba).
- **Sonda de Liščić:** cilindro de Inconel 600 de 50 mm de diámetro y 200 mm de largo, desde 850 °C a
  un baño de 28 °C; termopares en el centro y a 1 mm bajo la superficie. L/D = 4 se trata como cilindro
  infinito (1D), como hace la fuente. Propiedades de Inconel 600 de la Tabla 1 de Ramesh y Prabhu 2014
  (50-900 °C), con huecos que se interpolan. **Aclaración de la fuente:** ΔT es la diferencia entre
  el centro y el punto a 1 mm bajo la superficie (no superficie-centro); ΔT10 y ΔT100 son a los 10 y
  100 s tras la inmersión.

## Esferas del NBS, aceite

Velocidad de enfriamiento del centro a 720 °C (°C/s), desde 875 °C a 20 °C. Cifras de ejecutar el código.

| Esfera | Medido | h constante | Error | h(Ts) | Error | ¿±15 %? |
|---|---|---|---|---|---|---|
| 0,75 in (calibra) | 60,0 | 60,0 | 0 | 60,0 | 0 | — |
| 1,00 in | 43,5 | 42,3 | −2,7 % | 54,1 | +24,4 % | no |
| 1,36 in | 25,2 | 28,3 | +12,4 % | 37,8 | +50,0 % | no |
| 1,87 in | 16,6 | 18,3 | +10,2 % | 22,7 | +36,5 % | no |
| 2,35 in | 11,4 | 13,2 | +16,0 % | 15,2 | +33,1 % | no |
| 2,77 in | 9,0 | 10,4 | +15,1 % | 11,2 | +24,5 % | no |
| **Error medio absoluto** | | | **11,3 %** | | **33,7 %** | |

(La esfera de 1,61 in no tiene dato medido en aceite.) **Corte 1: falla** (0 de 5 dentro de ±15 %, y
MAE mayor).

**Por qué.** Cuando el centro de cualquiera de las esferas llega a 720 °C, la superficie está entre 387 y
461 °C, es decir, ya pasó el pico de 490 °C y la capa de vapor. La velocidad del centro a 720 °C la
decide el h del flanco posterior al pico, no la película. Calibrar en la esfera pequeña (superficie
a 461 °C, h = 3.989) fija ese flanco muy alto y las esferas grandes, con superficie más fría y h más
bajo, igual se quedan con demasiada extracción. La capa de vapor, que era la hipótesis, apenas
interviene en esta medida. Coincide con la advertencia de Fernandes y Prabhu (2007): en aceite el
flujo pico no baja con el diámetro.

## Sonda de Liščić (predicción, sin recalibrar)

Con el mismo factor s = 2,672:

| Medida | Publicado (Tabla 1) | Predicho | Diferencia | ¿±20 %? |
|---|---|---|---|---|
| ΔT10 | 91 °C | 369 °C | +306 % | no |
| ΔTmax | 257 °C | 370 °C | +44 % | no |
| tiempo de ΔTmax | 41 s | 10,5 s | −74 % | no |
| ΔT100 | 67 °C | 83 °C | +24 % | no |

**Corte 2: falla** (0 de 4). Es el resultado esperable de que s sea 2,7 veces mayor que el h medido en
esa sonda: la esfera de 3/4 in, en el NBS, pide un h mucho mayor que el medido por Liščić con Kalenol 32.

**Diagnóstico (no es un corte).** Con s = 1, o sea el h de Liščić tal cual, la sonda da ΔT10 = 138 °C
(+52 %), ΔTmax = 249 °C (−3 %) a los 33 s (−19 %) y ΔT100 = 51 °C (−24 %). ΔTmax y su tiempo caen dentro
de ±20 %, lo que indica que el solver y la forma funcionan. ΔT10 sale alto en parte porque la medida
real arranca hacia los 5 s (la Fig. 3 muestra h casi nulo antes de eso, por la inmersión) y el modelo
enfría desde t = 0. No se ajustó nada para mejorar estas cifras.

## Supuestos y límites

- Los nodos de la forma salen de una curva suave (±50 W/m²K) de una sola sonda y un solo aceite
  (Kalenol 32 a 28 °C). Los aceites del NBS (aceite N.º 2, 1925) no se conocen con esa precisión;
  que la forma de uno sea la del otro es un supuesto.
- Se aplica h(Ts) sin dependencia del diámetro. Fernandes y Prabhu (2007) sugieren que en
  aceite el flujo pico crece con el diámetro; este modelo no lo tiene.
- Esferas con propiedades constantes de la austenita (EN 1993-1-2), igual que `temple.py`, para
  aislar el efecto de h. El calor latente y las propiedades variables de la austenita ya se descartaron
  en un análisis previo aparte (calor latente sin ajustar: no explica el sesgo; Furlan lo empeora).
- La sonda se modela 1D (L/D = 4); la fuente usa la misma simplificación.
- El agua queda fuera: no se encontró una tabla h(Ts) de acero en agua quieta a 20 °C en acceso abierto.

## Conclusión

Con la forma real del aceite y un único factor de escala, el sesgo de las esferas grandes no
desaparece: empeora, y la escala que pide el NBS es incompatible con la de la sonda de Liščić. El
h constante efectivo (1.657 W/m²K, calibrado con la esfera de 3/4 in) sigue siendo mejor para esta medida.
Lo que falta para cerrar la pregunta es un h(Ts) de un aceite que sí sea el del NBS, o curvas medidas
de esferas de varios diámetros en un aceite con h(Ts) conocido.

## Reproducir

```
pytest tests/test_temple_ht.py
```
