# Fase 3: cálculo de carga del horno (y por qué no hay revenido)

## 3a. Cálculo de carga

**Pregunta.** ¿Qué mezcla de materias primas da la química objetivo de un hierro alto cromo al
menor costo? ¿Coincide con un óptimo publicado?

**Respuesta corta.** Sí: reproduce las 19 cargas de un estudio publicado a 0,42 puntos o menos
y sus precios al centavo.

### Modelo

Programación lineal (scipy, HiGHS):
- **Variables:** la participación de cada material, que suman una tonelada, con mínimos y máximos
  opcionales por material.
- **Objetivo:** el precio.
- **Restricciones:** la química de la aleación dentro de sus rangos.
- **Modo robusto** (por defecto, como el estudio): la composición de cada material es un rango y la
  química debe cumplirse para cualquier contenido dentro de él. Para el mínimo de cada elemento
  se usan los contenidos mínimos; para el máximo, los máximos. Con `robust=False` se usan los
  puntos medios.
- **Rendimientos** por elemento opcionales (fracción que queda en el metal); por defecto no hay
  pérdidas.
- Si no existe una carga posible, avisa (`ChargeError`).

```python
from tratamientos.carga import Material, Target, optimize_charge

materiales = [
    Material("Chatarra", 2200, {"C": (0.10, 0.25)}),
    Material("Arrabio", 2689, {"C": (3.8, 4.0)}),
]
r = optimize_charge(materiales, Target({"C": (1.8, 2.4)}))
print(r.kg_per_t(), r.price_per_t, r.chemistry)
```

`python ejemplos/carga_xcr18.py --max-retorno 0.3` calcula la carga del estudio.

### Validación

Mędoń, Szczęsny, Ziółkowski, Guzik, Czarny y Kopyciński (2023), *Archives of Foundry
Engineering* 23(4), 54-64 (CC BY 4.0):
- **Aleación:** hierro alto cromo EN-GJN-HV600 (XCr18).
- **Materias primas:** 10 materiales con composición en rangos y precios en PLN/t.
- **Cargas:** 19, sin límites o limitando el retorno, el arrabio o la chatarra.

Decisión previa sobre los rangos: «máx. X» se toma como (0, X), «mín. X» como (X, 100) y «-» o
vacío como cero. El FeCr HC figura con 0,80-1,00 % de C (inusual) y se usa tal cual.

| Prueba (tolerancia fijada antes) | Resultado |
|---|---|
| Precio de la carga más barata W1 (4.061,96 PLN/t), ±1 % | 4.061,96 |
| W8, retorno ≤ 30 % (4.394,25), ±1 % | 4.394,25 |
| W15, arrabio ≥ 35 % (7.417,87), ±1 % | 7.417,57 (−0,004 %) |
| Con chatarra ≥ 10 % (4.304,87), ±1 % | 4.304,87 (W16) |
| Participación de los 10 materiales en las 19 cargas, ±2 puntos | desvío máximo 0,42 puntos; la mayoría ≤ 0,005 |

El único desvío de 0,42 puntos es el carbono de W4. El estudio publica 0,047 %, pero la serie va
0,16 → 0,31 → (0,47) → 0,62 → 0,77: casi seguro es una errata del artículo.

Guardas: la química garantizada cumple el objetivo en las 19 cargas, el óptimo de un caso de 3
materiales coincide con una búsqueda exhaustiva, el modo de puntos medios coincide con un cálculo
a mano, y una carga imposible avisa. Las 7 mutaciones del código hacen fallar las pruebas.

### Límites

- Sin pérdidas por oxidación salvo que se den los rendimientos, y sin escoria.
- Los rendimientos multiplican los contenidos; no se recalcula la masa de metal perdida.
- Los precios y materiales del ejemplo son los del estudio (Polonia, mayo de 2023), no de una
  planta peruana.

## 3b. Revenido: no validable con datos abiertos

El brief pedía validar el parámetro de Hollomon-Jaffe, P = T·(C + log t), ajustando la curva de
dureza a un tiempo de revenido y prediciendo otro, a ±2 HRC, **solo con datos abiertos
tabulados**. No se encontraron:
- Informe del ORNL sobre aceros 2,25-12 % Cr (OSTI 6792269, dominio público): revenidos de 2 h y
  de 2 + 8 h, pero la dureza está solo en gráficos.
- Judge et al. (2018), *Scientific Reports* 8, 445 (acero 4340, revenidos de 1 s y 1 h
  «equivalentes»): la dureza está solo en gráficos.
- AISI D2 en *Materials Research* (SciELO, 2023): muestra que el parámetro falla cerca del pico de
  endurecimiento secundario.

Por eso no hay módulo de revenido: sin validación no se publica. Para los hierros blancos alto
cromo, además, el parámetro no aplica: su endurecimiento secundario por transformación de la
austenita retenida a 450-550 °C rompe la equivalencia entre tiempo y temperatura.

Para hacerlo haría falta una tabla de dureza del mismo acero a al menos dos tiempos y varias
temperaturas de revenido. También serviría digitalizar las figuras, con un error de lectura
declarado.
