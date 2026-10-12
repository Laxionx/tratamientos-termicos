# Fase 3: cálculo de carga del horno

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

## 3b. Revenido

Pasó a su propio documento: [fase3b-revenido.md](fase3b-revenido.md). No se hallaron tablas
abiertas; se validó con la figura digitalizada de un artículo CC BY sobre fundición nodular.
