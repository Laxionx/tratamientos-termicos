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
