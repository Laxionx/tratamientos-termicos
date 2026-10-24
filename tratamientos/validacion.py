"""Datos medidos de artículos de acceso abierto para validar la fase 1 (desestabilización).

Composiciones en % en peso; austenita retenida (AR) y carburos en % del total, en la base que
reporta cada artículo («volumen» o «masa»). Las decisiones sobre datos incompletos están anotadas
en cada caso y se tomaron antes de comparar.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Case:
    source: str
    label: str
    composition: Mapping[str, float]
    temperature_c: float
    quench_c: float
    basis: str  # "volumen" o "masa"
    retained: float | None = None  # % medido
    carbides: float | None = None  # % medido
    note: str = ""
    read_error: float = 0.0  # ± puntos de AR por leer un valor de una figura (0 = tabla o texto)
    in_cut: bool = True  # False: contexto o contraste, fuera del corte de ±10 puntos


YU = "Yu, Li, Feng y Wu (2026), Materials 19(5) 896, CC BY"
GONZALEZ = "González-Pociño, Álvarez-Antolín y Asensio-Lozano (2019), Materials 12(19) 3252, CC BY"
HIGUERA = "Higuera-Cobos, Dumitru y Mesa-Grajales (2016), Rev. Fac. Ing. 25(41) 93, CC BY-NC"
TUPAJ = "Tupaj, Orłowicz, Trytek et al. (2020), Materials 13(12) 2760, CC BY"

# Yu: Mn y Cu se publican sumados; se reparte 50/50 (se informa la banda Mn o Cu solo). El La
# (0,1-0,15 %) no está en la base y se omite. Las probetas se revinieron 2 h a 300 °C después del
# temple al agua: se supone que el revenido bajo no cambia la AR (Tupaj et al., introducción).
YU_1 = {"C": 2.90, "CR": 18.90, "MN": 1.545, "CU": 1.545, "SI": 0.72}
YU_2 = {"C": 2.93, "CR": 19.24, "MN": 1.52, "CU": 1.52, "SI": 0.69}
_YU_DATA = {  # muestra: {T: (AR % vol, carburos % vol)}, XRD
    1: {
        900: (21.12, 29.58),
        950: (17.43, 31.11),
        1000: (18.15, 30.53),
        1050: (27.69, 27.98),
    },
    2: {
        900: (20.41, 29.45),
        950: (16.23, 31.21),
        1000: (15.87, 31.98),
        1050: (24.78, 28.27),
    },
}
# González-Pociño: Rietveld en % en masa. Solo los experimentos con revenido a 200 °C (2, 4, 5 y
# 7); los revenidos a 500 °C transforman AR y quedan fuera del modelo.
GONZALEZ_ALLOY = {"C": 2.9, "SI": 1.2, "MN": 0.8, "CR": 18.1, "MO": 1.8}
_GONZALEZ_DATA = {  # experimento: (T, AR % masa, carburo K2 % masa)
    5: (1000, 34.22, 36.63),  # 4 h, aceite
    7: (1000, 41.51, 39.48),  # 8 h, aire
    2: (1100, 42.20, 47.74),  # 4 h, aire
    4: (1100, 61.09, 29.57),  # 8 h, aceite
}
# Higuera-Cobos: solo C y Cr publicados (ASTM A532 III A); el resto se toma como cero. AR por
# XRD (ASTM E975) tras 1 h a 950 °C con distintos enfriamientos; el último, aire y luego -80 °C.
HIGUERA_ALLOY = {"C": 3.0, "CR": 25.0}
_HIGUERA_DATA = {"aire": (25.0, 26.2), "agua": (25.0, 28.5), "aceite": (25.0, 35.5),
                 "aire y CO2 a -80 °C": (-80.0, 14.3)}  # fmt: skip
# Tupaj: 30 min a 1000 °C. Ms por dilatometría según el enfriamiento; carburos 29,2-30,7 % vol.
TUPAJ_ALLOY = {
    "C": 3.50,
    "CR": 15.30,
    "MO": 0.50,
    "NI": 0.30,
    "MN": 0.65,
    "SI": 1.10,
    "CU": 0.04,
}
TUPAJ_MS = {"aire": 128.0, "agua": 62.0, "nitrógeno líquido": 20.0}
TUPAJ_CARBIDES = (29.2, 30.7)


def retained_cases() -> list[Case]:
    cases = []
    for sample, alloy in ((1, YU_1), (2, YU_2)):
        for t, (ar, carb) in _YU_DATA[sample].items():
            cases.append(Case(YU, f"Yu M{sample} {t} °C", alloy, t, 25.0, "volumen", ar, carb))
    for exp, (t, ar, carb) in _GONZALEZ_DATA.items():
        label = f"González-Pociño exp. {exp} ({t} °C)"
        cases.append(Case(GONZALEZ, label, GONZALEZ_ALLOY, t, 25.0, "masa", ar, carb))
    for medium, (tq, ar) in _HIGUERA_DATA.items():
        label = f"Higuera-Cobos {medium}"
        cases.append(Case(HIGUERA, label, HIGUERA_ALLOY, 950, tq, "volumen", ar))
    return cases


@dataclass(frozen=True)
class Tolerances:
    retained_points: float = 10.0
    carbide_points: float = 5.0
    liquid_nitrogen_max: float = 5.0  # % de AR esperado a -196 °C (Tupaj no observa AR)
    extra: dict = field(default_factory=dict)


TOLERANCES = Tolerances()


# ---------------------------------------------------------------------------- fase 2: temple
# French y Klopsch (1925), «Initial temperature and mass effects in quenching», Technologic Papers
# of the Bureau of Standards 19, T295 (NBS, hoy NIST; dominio público), Tablas 1 y 2. Esferas de
# acero de rodamiento (0,98 % C, 1,63 % Cr) templadas desde 875 °C en agua o aceite N.º 2 quietos
# a 20 °C; velocidad de enfriamiento en el centro al pasar por 720 °C, medida con termocupla. El
# diámetro sale del volumen tabulado, que es más preciso que la fracción de pulgada impresa.
NBS = "French y Klopsch (1925), NBS Technologic Paper T295, dominio público"
NBS_VOLUME_IN3 = (0.222, 0.523, 1.326, 2.186, 3.450, 6.790, 11.110)
NBS_RATE = {  # °C/s en el centro a 720 °C, por esfera (None: no medida)
    "agua": (148.5, 95.0, 55.0, 39.0, 28.0, 20.0, 14.0),
    "aceite": (60.0, 43.5, 25.2, None, 16.6, 11.4, 9.0),
}
NBS_EXPONENT = {"agua": 1.75, "aceite": 1.40}  # Tabla 1: V·D^n = c (D en pulgadas)
NBS_T_INITIAL, NBS_T_MEDIUM, NBS_T_RATE = 875.0, 20.0, 720.0
NBS_TOLERANCES = {"velocidad": 0.15, "exponente": 0.15}


def nbs_diameters_in() -> tuple[float, ...]:
    import math

    return tuple((6 * v / math.pi) ** (1 / 3) for v in NBS_VOLUME_IN3)


# ------------------------------------------------------------------- fase 1b: tiempo a 1000 °C
# González-Pociño, Álvarez-Antolín y Asensio-Lozano (2019), Metals 9(5) 522, CC BY, Tabla 2:
# Rietveld tras 4, 8, 12 y 24 h a 1000 °C, enfriadas al aire o en aceite. Antes de desestabilizar
# las piezas pasaron por 700 °C (austenita a perlita, para mecanizar). Columna «Volume %» del
# Rietveld; se toma como masa, que es lo que entrega Rietveld (decisión previa a comparar).
METALS_522 = "González-Pociño, Álvarez-Antolín y Asensio-Lozano (2019), Metals 9(5) 522, CC BY"
METALS_522_ALLOY = {"C": 3.0, "SI": 1.2, "MN": 0.8, "CR": 18.2, "MO": 2.0}
METALS_522_DATA = {  # medio: {horas: (AR %, M7C3 %)}
    "aire": {4: (8.24, 55.17), 8: (9.94, 54.58), 12: (2.61, 51.76), 24: (2.83, 52.87)},
    "aceite": {4: (6.59, 43.33), 8: (6.94, 56.52), 12: (2.26, 52.90), 24: (2.22, 46.43)},
}


# ------------------------------------------------------------------ fase 3a: cálculo de carga
# Mędoń, Szczęsny, Ziółkowski, Guzik, Czarny y Kopyciński (2023), Archives of Foundry Engineering
# 23(4) 54-64, doi 10.24425/afe.2023.146679, CC BY 4.0. Tablas 1 a 4 y texto. Hierro alto cromo
# EN-GJN-HV600 (XCr18). Rangos tal como se publican: «máx. X» -> (0, X); «mín. X» -> (X, 100);
# «-» o vacío -> (0, 0). El FeCr HC figura con 0,80-1,00 % de C (inusual; se usa tal cual).
AFE = "Mędoń et al. (2023), Archives of Foundry Engineering 23(4) 54, CC BY 4.0"
_MX, _100 = 0.0, 100.0
AFE_MATERIALS = {  # nombre: (precio PLN/t, {elemento: (mín, máx)})
    "Chatarra de acero": (2200.0, {"C": (0.10, 0.25), "SI": (0.20, 0.30), "MN": (_MX, 0.20),
                                   "P": (_MX, 0.04), "S": (_MX, 0.03)}),
    "Retorno": (4160.0, {"C": (1.80, 2.10), "SI": (0.72, 0.78), "MN": (1.00, 1.10),
                         "P": (0.03, 0.06), "S": (0.02, 0.05), "CR": (19.0, 20.0),
                         "NI": (1.40, 1.60), "MO": (2.40, 2.60)}),
    "FeCr HC": (9700.0, {"C": (0.80, 1.00), "SI": (1.80, 2.00), "MN": (_MX, 0.03),
                         "S": (_MX, 0.02), "CR": (60.0, 64.0)}),
    "FeCr LC": (19400.0, {"C": (0.08, 0.10), "SI": (1.40, 1.50), "MN": (_MX, 0.03),
                          "S": (_MX, 0.02), "CR": (60.0, 64.0)}),
    "FeMn75A": (5900.0, {"C": (6.40, 6.60), "SI": (3.60, 4.00), "MN": (75.0, _100),
                         "P": (_MX, 0.45), "S": (_MX, 0.03)}),
    "FeMo60": (167600.0, {"C": (_MX, 0.05), "SI": (0.70, 0.80), "P": (0.05, 0.10),
                          "S": (_MX, 0.03), "MO": (60.0, _100)}),
    "Ni": (109500.0, {"NI": (98.0, _100)}),
    "FeSi75A": (8900.0, {"C": (_MX, 0.10), "SI": (72.0, 78.0), "MN": (_MX, 0.40),
                         "P": (_MX, 0.05), "S": (_MX, 0.02), "CR": (_MX, 0.05)}),
    "Carbono": (7798.0, {"C": (98.0, _100)}),
    "Arrabio": (2689.0, {"C": (3.80, 4.00), "SI": (1.00, 1.20), "MN": (_MX, 0.20),
                         "P": (_MX, 0.04), "S": (_MX, 0.03)}),
}  # fmt: skip
AFE_TARGET = {
    "C": (1.80, 2.40),
    "SI": (0.0, 1.00),
    "MN": (0.50, 1.50),
    "P": (0.0, 0.08),
    "S": (0.0, 0.08),
    "CR": (18.0, 23.0),
    "NI": (0.0, 2.00),
    "MO": (0.0, 3.00),
}
# Tabla 3: límites de cada carga (fracción). Tabla 4: participaciones publicadas (%).
AFE_LIMITS = {
    "W1": {},
    **{f"W{i}": {"Retorno": (0.0, lim)} for i, lim in zip(range(2, 9),
       (0.90, 0.80, 0.70, 0.60, 0.50, 0.40, 0.30), strict=True)},
    **{f"W{i}": {"Arrabio": (lim, 1.0)} for i, lim in zip(range(9, 16),
       (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35), strict=True)},
    "W16": {"Chatarra de acero": (0.10, 1.0), "Arrabio": (0.20, 1.0)},
    "W17": {"Chatarra de acero": (0.20, 1.0), "Arrabio": (0.20, 1.0)},
    "W18": {"Chatarra de acero": (0.20, 1.0), "Arrabio": (0.25, 1.0)},
    "W19": {"Chatarra de acero": (0.20, 1.0), "Arrabio": (0.30, 1.0)},
}  # fmt: skip
AFE_SHARES = {  # carga: {material: %} (vacío en la tabla = 0)
    "W1": {"Chatarra de acero": 5.17, "Retorno": 94.74},
    "W2": {"Chatarra de acero": 8.34, "Retorno": 90.00, "FeCr HC": 1.50, "Carbono": 0.16},
    "W3": {"Chatarra de acero": 15.02, "Retorno": 80.00, "FeCr HC": 4.67, "Carbono": 0.31},
    "W4": {"Chatarra de acero": 21.70, "Retorno": 70.00, "FeCr HC": 7.83, "Carbono": 0.047},
    "W5": {"Chatarra de acero": 28.38, "Retorno": 60.00, "FeCr HC": 11.00, "Carbono": 0.62},
    "W6": {"Chatarra de acero": 35.07, "Retorno": 50.00, "FeCr HC": 14.17, "Carbono": 0.77},
    "W7": {"Chatarra de acero": 41.62, "Retorno": 40.00, "FeCr HC": 17.33, "FeMn75A": 0.13,
           "Carbono": 0.91},
    "W8": {"Chatarra de acero": 48.18, "Retorno": 30.00, "FeCr HC": 20.50, "FeMn75A": 0.27,
           "Carbono": 1.05},
    "W9": {"Chatarra de acero": 0.26, "Retorno": 94.74, "Arrabio": 5.00},
    "W10": {"Retorno": 87.80, "FeCr HC": 2.20, "Arrabio": 10.00},
    "W11": {"Retorno": 80.49, "FeCr HC": 4.51, "Arrabio": 15.00},
    "W12": {"Chatarra de acero": 0.21, "Retorno": 72.87, "FeCr HC": 6.92, "Arrabio": 20.00},
    "W13": {"Chatarra de acero": 3.15, "Retorno": 61.24, "FeCr HC": 10.61, "Arrabio": 25.00},
    "W14": {"Chatarra de acero": 2.44, "Retorno": 54.96, "FeCr HC": 3.01, "FeCr LC": 9.59,
            "Arrabio": 30.00},
    "W15": {"Chatarra de acero": 30.17, "Retorno": 5.10, "FeCr LC": 28.39, "FeMn75A": 0.60,
            "Carbono": 0.75, "Arrabio": 35.00},
    "W16": {"Chatarra de acero": 10.00, "Retorno": 58.54, "FeCr HC": 11.46, "Arrabio": 20.00},
    "W17": {"Chatarra de acero": 20.00, "Retorno": 43.64, "FeCr HC": 16.18, "FeMn75A": 0.08,
            "Carbono": 0.1, "Arrabio": 20.00},
    "W18": {"Chatarra de acero": 20.00, "Retorno": 36.25, "FeCr HC": 14.42, "FeCr LC": 4.10,
            "FeMn75A": 0.18, "Carbono": 0.05, "Arrabio": 25.00},
    "W19": {"Chatarra de acero": 20.0, "Retorno": 28.79, "FeCr HC": 6.17, "FeCr LC": 14.71,
            "FeMn75A": 0.28, "Carbono": 0.04, "Arrabio": 30.00},
}  # fmt: skip
AFE_PRICES = {"W1": 4061.96, "W8": 4394.25, "W15": 7417.87}  # PLN/t, citados en el texto
AFE_PRICE_STEEL_10 = 4304.87  # «mínimo 10 % de chatarra de acero» (texto); se compara con W16

# ---------------------------------------------------------------- Fase 3b: revenido
NODULAR = (
    "Salas Vicente, Carcel Carrasco, Fernández Antoni, Ferrero Taberner y Pascual Guillamón "
    "(2021), Metals 11(2) 297, CC BY; Figura 6 digitalizada"
)
# Fundición nodular (C 3,25-3,70; Si 2,40-3,00), templada y revenida 10 min, 20 min, 1 h, 5 h y
# 24 h a 400, 500, 600 y 700 °C. Dureza HV leída de la Figura 6 (imagen de 2550 × 2000 px): ejes
# calibrados con el marco y cada punto ajustado al centroide de su marcador; lectura ±5 HV.
# Grupos según el texto (secc. 3.1 y 4.1) y la leyenda de la Figura 6, que coinciden: 15 min a
# 880 °C y agua, 592 HV; 15 min y aire forzado, 291 HV (ferrita y perlita fina); 5 h y agua,
# 420 HV (ferrita y martensita). El pie de la Figura 5 cruza los paneles (b) y (c).
# La abscisa del artículo es T(20 + ln t), no la de Hollomon-Jaffe con log10.
NODULAR_TIMES_H = (1 / 6, 1 / 3, 1.0, 5.0, 24.0)
NODULAR_HV = {  # grupo: {temperatura °C: HV a cada tiempo}
    "agua": {400: (463.4, 448.7, 407.2, 387.9, 366.1), 500: (394.3, 347.3, 331.0, 273.1, 279.2),
             600: (312.1, 299.0, 278.3, 199.6, 151.8), 700: (242.9, 214.2, 157.2, 140.7, 137.3)},
    "aire": {400: (289.3, 292.1, 283.2, 288.8, 301.9), 500: (286.5, 290.7, 283.0, 245.3, 254.2),
             600: (276.7, 278.8, 271.2, 238.4, 165.5), 700: (238.5, 216.8, 163.8, 144.7, 136.3)},
    "agua tras 5 h": {400: (386.9, 392.8, 379.8, 317.3, 294.9),
                      500: (323.0, 317.8, 285.4, 255.8, 224.6),
                      600: (281.3, 270.0, 198.5, 186.3, 143.6),
                      700: (228.5, 204.0, 154.7, 133.5, 133.4)},
}  # fmt: skip
NODULAR_QUENCHED_HV = {"agua": 592.0, "aire": 291.0, "agua tras 5 h": 420.0}  # del texto


# ------------------------------------------------------- fase 1c: validación ampliada (AR)
# Datos nuevos de AR que NO se usaron para ajustar nada. Composiciones en % en peso, con los
# elementos que el artículo no informa tomados como cero (decidido antes de comparar).
NAYAK = "Nayak, Mücklich y Guitar (2023), Met. Mater. Int. 29, 934, CC BY"
GONZALEZ_933 = "González, Borja Peral, Zafra y Fernández-Pariente (2019), Metals 9(9) 933, CC BY"
GONZALEZ_359 = "González-Pociño, Álvarez-Antolín y Asensio-Lozano (2020), Metals 10(3) 359, CC BY"
ORTEGA = (
    "Ortega-Cubillos, Nannetti-Bernardini, Fredel y Campos (2015), Rev. Fac. Ing. Univ. Antioquia "
    "76, 134, CC BY-NC-SA 4.0; Figs. 6 y 7 digitalizadas"
)
FORTINI = "Fortini, Suman, Zanini y Cruciani (2022), Coatings 12(8) 1218, CC BY"

NAYAK_ALLOY = {"C": 2.53, "CR": 26.60, "MO": 0.24, "NI": 0.26, "MN": 0.66, "SI": 0.37, "CU": 0.03}
GONZALEZ_933_ALLOY = {"C": 3.01, "CR": 18.2, "MO": 2.05, "MN": 0.82, "SI": 1.17}
GONZALEZ_359_ALLOY = {"C": 2.7, "CR": 25.1, "MO": 0.5, "MN": 0.8, "SI": 1.2}
ORTEGA_ALLOY = {"C": 2.98, "SI": 0.71, "MN": 0.75, "MO": 1.90, "NI": 0.35, "CR": 21.22, "CU": 0.06}
FORTINI_1 = {"C": 3.83, "CR": 20.22, "SI": 0.88}
FORTINI_2 = {"C": 4.15, "CR": 21.04, "MO": 2.78, "MN": 0.56, "SI": 1.08}

# Error de lectura de las figuras de Ortega-Cubillos: mitad del paso de la escala más fina del eje
# de AR (marcas cada 1 %). La lectura en píxeles es mejor (≈0,1 %), pero se declara el paso entero.
ORTEGA_READ_ERROR = 0.5
# Fig. 6 (AR frente a T) y Fig. 7 (AR frente a t): leídas con scratch/digitalizar_ortega.py. Las
# condiciones fijas no están en el pie de la figura; se infieren de que Fig. 6 y Fig. 7 coinciden en
# su punto común (bruto 1000 °C 6 h: 23,08 y 23,15 %; recocido 1050 °C 0,5 h: 21,12 y 21,12 %) y
# del texto (la AR se midió solo en las condiciones de mayor dureza). Los dos puntos repetidos
# entran una sola vez al corte (de la Fig. 6).
ORTEGA_AS_CAST = {  # (T °C, horas): AR % vol leída
    (900, 6.0): 24.15, (1000, 6.0): 23.08, (1100, 6.0): 37.10,
    (1000, 1.0): 29.12, (1000, 2.0): 25.17, (1000, 4.0): 24.08,
}  # fmt: skip
ORTEGA_ANNEALED = {  # recocido previo 700 °C 6 h
    (900, 0.5): 26.10, (1000, 0.5): 27.18, (1050, 0.5): 21.12, (1100, 0.5): 39.13,
    (1050, 2.0): 22.12, (1050, 6.0): 38.13,
}  # fmt: skip
ORTEGA_REPEATED = {  # lectura independiente del mismo punto en la otra figura
    "bruto": ((1000, 6.0), 23.15), "recocido": ((1050, 0.5), 21.12),
}  # fmt: skip
_FORTINI_DATA = (  # aleación, T °C, horas, medio, AR % masa
    (FORTINI_1, 1000, 8, "aceite", 0.4), (FORTINI_1, 900, 0.5, "aire", 0.7),
    (FORTINI_1, 980, 1.5, "aire", 0.7), (FORTINI_2, 1000, 8, "aceite", 20.0),
    (FORTINI_2, 900, 0.5, "aire", 30.9), (FORTINI_2, 980, 1.5, "aire", 1.1),
)  # fmt: skip


def _nayak_cases() -> list[Case]:
    note = (
        "Rietveld (MAUD); la base no se declara, se compara en volumen. Sin revenido. Sin "
        "mantenimiento y a 30 min el equilibrio no se alcanza: es cinética (fase 1b)."
    )
    data = ((0.0, 10.2), (0.5, 7.1), (1.5, 5.1))
    return [
        Case(NAYAK, f"Nayak 980 °C {h:g} h", NAYAK_ALLOY, 980, 25.0, "volumen", ar, note=note)
        for h, ar in data
    ]


def _gonzalez_cases() -> list[Case]:
    ni_cu = "Ni y Cu no informados (se toman como 0)."
    cases = [
        Case(GONZALEZ_933, "González 2019 1000 °C 6 h", GONZALEZ_933_ALLOY, 1000, 25.0, "masa",
             13.0, note=f"{ni_cu} Dato del texto, no de tabla. Sin revenido."),
    ]  # fmt: skip
    # Tabla 7 de Metals 10(3) 359: Rietveld en masa, tras revenido a 200 °C (exp. 2: 6 h; exp. 4:
    # 3 h). Los exp. 5 y 7 (200 °C) y los de 500 °C no detectaron AR: no entran al corte.
    for exp, t, hours, medium, ar, tempering in (
        (2, 1100, 4, "aire", 9.0, "200 °C 6 h"),
        (4, 1100, 8, "aceite", 7.3, "200 °C 3 h"),
    ):
        note = f"{ni_cu} Con ablandamiento previo y revenido posterior de {tempering}."
        label = f"González-Pociño 2020 exp. {exp} (1100 °C {hours} h, {medium})"
        cases.append(Case(GONZALEZ_359, label, GONZALEZ_359_ALLOY, t, 25.0, "masa", ar, note=note))
    for exp, t, hours, medium, tempering in ((5, 1000, 4, "aceite", "200 °C 3 h"),
                                             (7, 1000, 8, "aire", "200 °C 6 h")):  # fmt: skip
        note = f"AR no detectada (sin dato numérico) tras revenido de {tempering}: contexto."
        label = f"González-Pociño 2020 exp. {exp} (1000 °C {hours} h, {medium})"
        cases.append(Case(GONZALEZ_359, label, GONZALEZ_359_ALLOY, t, 25.0, "masa", None,
                          note=note, in_cut=False))  # fmt: skip
    return cases


def _ortega_cases() -> list[Case]:
    note = (
        "AR digitalizada ±0,5 %, % en volumen (ASTM E975). Revenido posterior de 200 °C 2 h; "
        "el medio de enfriamiento tras desestabilizar no se informa (se supone temple a 25 °C)."
    )
    cases = []
    for state, data, extra in (
        ("bruto", ORTEGA_AS_CAST, "Bruto de colada."),
        ("recocido", ORTEGA_ANNEALED, "Recocido previo 700 °C 6 h (el modelo no lo ve)."),
    ):
        for (t, hours), ar in data.items():
            label = f"Ortega {state} {t} °C {hours:g} h"
            cases.append(Case(ORTEGA, label, ORTEGA_ALLOY, t, 25.0, "volumen", ar,
                              note=f"{extra} {note}", read_error=ORTEGA_READ_ERROR))  # fmt: skip
    return cases


def _fortini_cases() -> list[Case]:
    note = (
        "Recargue con Nb (fuera de A532, C > 3,6 %): contraste. Ni y Cu no informados. La base "
        "no tiene Nb: el NbC (6-10 % de la masa) queda sin modelar."
    )
    return [
        Case(FORTINI, f"Fortini aleación {1 if alloy is FORTINI_1 else 2} {t} °C {h:g} h",
             alloy, t, 25.0, "masa", ar, note=note, in_cut=False)
        for alloy, t, h, _medium, ar in _FORTINI_DATA
    ]  # fmt: skip


def extended_cases() -> list[Case]:
    """Casos nuevos de fase 1c: los comparables (in_cut) y los de contexto o contraste."""
    return _nayak_cases() + _gonzalez_cases() + _ortega_cases() + _fortini_cases()
