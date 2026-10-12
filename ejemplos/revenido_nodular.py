"""Dureza estimada tras un revenido y tiempos equivalentes a otras temperaturas.

Uso: python ejemplos/revenido_nodular.py --temperatura 550 --tiempo 2 [--grupo agua]

La curva se arma con los revenidos de 1 h de la fundición nodular de Salas Vicente et al. (2021).
En la validación, 19 de 36 predicciones quedaron a ±25 HV: es orientativo (ver
docs/fase3b-revenido.md).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tratamientos.revenido import HardnessCurve, equivalent_time_h, tempering_parameter
from tratamientos.validacion import NODULAR_HV, NODULAR_QUENCHED_HV, NODULAR_TIMES_H


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--temperatura", type=float, required=True, help="°C de revenido")
    parser.add_argument("--tiempo", type=float, required=True, help="horas de revenido")
    parser.add_argument("--grupo", choices=list(NODULAR_HV), default="agua")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    one_hour = NODULAR_TIMES_H.index(1.0)
    tests = [(t, 1.0, hv[one_hour]) for t, hv in NODULAR_HV[args.grupo].items()]
    curve = HardnessCurve.from_tests(tests)
    p = tempering_parameter(args.temperatura, args.tiempo)
    print(f"Grupo «{args.grupo}» (parte de {NODULAR_QUENCHED_HV[args.grupo]:.0f} HV)")
    print(f"{args.temperatura:.0f} °C × {args.tiempo:g} h → P = {p:,.0f}")
    if curve.covers(args.temperatura, args.tiempo):
        print(f"Dureza estimada: {curve.predict(args.temperatura, args.tiempo):.0f} HV (±25 HV)")
    else:
        print("Fuera de lo ensayado (P de 400 a 700 °C × 1 h): no se extrapola")
    print("\nMismo P a otras temperaturas:")
    for temp in (400.0, 450.0, 500.0, 550.0, 600.0, 650.0, 700.0):
        hours = equivalent_time_h(args.temperatura, args.tiempo, temp)
        if 1 / 60 <= hours <= 1000:
            print(f"  {temp:4.0f} °C: {hours:8.2f} h")


if __name__ == "__main__":
    main()
