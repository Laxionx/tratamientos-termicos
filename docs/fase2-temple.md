# Fase 2: temple de la bola

**Pregunta.** Para una bola de diámetro D templada en agua o aceite, ¿a qué velocidad se enfrían
la superficie, el medio radio y el centro, y alcanza el centro la velocidad de temple?

**Respuesta corta.** Sí se puede predecir, con un coeficiente de transferencia calibrado una vez
por medio. Validado contra esferas de acero medidas por el NBS en 1925: 7 de 11 predicciones a
±15 % y la ley de tamaño del NBS reproducida. Las esferas grandes salen entre 10 y 19 % más
rápidas de lo medido.

## Modelo

- Conducción transitoria radial en una esfera, por volúmenes finitos (120 capas) e integración
  implícita, con convección en la superficie: −k ∂T/∂r = h (T − T_medio).
- **Propiedades de la austenita**, constantes, según EN 1993-1-2 (Eurocódigo 3, reproducido en
  artículos abiertos): k = 27,3 W/m·K, cp = 669 J/kg·K a 875 °C y ρ = 7.850 kg/m³. Entre la
  austenización y unos 700 °C el acero sigue austenítico.
- **h efectivo y constante:** no se modelan la capa de vapor, la ebullición ni el calor latente de
  la transformación.
- Severidad de Grossmann: H = h/(2k).
- La dureza no se predice: se compara la velocidad a 720 °C con una velocidad crítica que se da
  como dato del material.

```python
from tratamientos import quench_sphere, hardening
from tratamientos.temple import H_NBS, INCH

r = quench_sphere(3 * INCH, H_NBS["agua"])
print(r.rate_at(720, 0.0), hardening(r, critical_rate=10.0))
```

`python ejemplos/temple_bolas.py --velocidad-critica X` imprime la tabla de 1 a 5 pulgadas.

## Validación

Tolerancias fijadas antes de correr ([tests/test_temple.py](../tests/test_temple.py)).

**1. Contra la solución analítica** (serie de Fourier de la esfera con convección) para Bi de
0,1 a 50: error de 0,03 % o menos (tolerancia ±0,5 %).

**2. Contra el NBS.** French y Klopsch (1925), *Technologic Papers of the Bureau of Standards*
19, T295, de dominio público. Midieron con termocupla el centro de esferas de acero de
rodamiento (0,98 % C, 1,63 % Cr), templadas desde 875 °C en agua o aceite quietos a 20 °C. El h
se calibra con la esfera de 3/4" de cada medio y se predicen las demás:

| Esfera | Agua: medido → modelo | Aceite: medido → modelo |
|---|---|---|
| 0,75" | 148,5 → 148,5 (calibración) | 60,0 → 60,0 (calibración) |
| 1,00" | 95 → 94,9 (−0,1 %) | 43,5 → 42,3 (−2,7 %) |
| 1,36" | 55 → 57,2 (+4,0 %) | 25,2 → 28,3 (+12,4 %) |
| 1,61" | 39 → 43,2 (+10,7 %) | sin medición |
| 1,88" | 28 → 33,3 (**+18,8 %**) | 16,6 → 18,3 (+10,2 %) |
| 2,35" | 20 → 22,4 (+12,0 %) | 11,4 → 13,2 (**+16,0 %**) |
| 2,77" | 14 → 16,7 (**+19,4 %**) | 9,0 → 10,4 (**+15,1 %**) |

En °C/s en el centro al pasar por 720 °C. **7 de 11 dentro de ±15 %: pasa el criterio de corte**
(fallaría con más de la mitad fuera). Las cuatro de afuera quedan como fallos esperados.

**3. Ley de tamaño V·Dⁿ = c** del NBS: el modelo da n = 1,68 en agua (NBS 1,75) y 1,35 en aceite
(NBS 1,40), dentro de ±0,15. Un control de lectura confirma que los datos transcritos dan el n
publicado.

Las 8 mutaciones del código (geometría, resistencia de superficie, temperatura del medio, cp,
serie analítica, Grossmann, posición) hacen fallar las pruebas.

## Hallazgos

- **Sesgo sistemático en las esferas grandes:** el modelo las enfría entre 10 y 19 % más rápido de
  lo medido. Es lo esperable sin calor latente: la transformación libera calor en la capa
  exterior y frena al centro. Tampoco se modela la capa de vapor, que dura más en piezas grandes.
- **El h calibrado no es el de manual.** En agua quieta da H = 3,2 in⁻¹; los manuales citan cerca
  de 1. El h efectivo absorbe lo que el modelo no tiene: los valores de manual no deben usarse sin
  recalibrar.

## Límites

- Validado con esferas de **acero** (bolas forjadas). Para un **hierro blanco alto cromo** cambian
  la conductividad y el h efectivo: la tabla es orientativa.
- La velocidad crítica de temple es un dato del material. La fuente clásica para hierros alto
  cromo, el atlas de Maratray y Usseglio-Nanot (Climax Molybdenum, 1971), no es abierta.
- Un solo h por medio, sin agitación ni temperatura del baño.
