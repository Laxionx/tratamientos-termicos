"""Velocidad de enfriamiento de bolas de 1 a 5 pulgadas en agua y aceite quietos.

Uso: python ejemplos/temple_bolas.py [--velocidad-critica 8]

Los h son los efectivos calibrados con el NBS (acero de rodamiento, 875 °C). Para un hierro
blanco alto cromo cambian las propiedades y el h: es orientativo (ver docs/fase2-temple.md).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tratamientos.temple import H_NBS, ball_table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--velocidad-critica", type=float, default=None,
                        help="°C/s a 720 °C que necesita el material para templar")  # fmt: skip
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for medium, h in H_NBS.items():
        print(f"\n{medium} (h efectivo {h:,.0f} W/m²K) · velocidad a 720 °C en °C/s")
        print(f"{'bola':>6} {'superficie':>11} {'medio radio':>12} {'centro':>8}")
        for d, rates in ball_table((1.0, 2.0, 3.0, 4.0, 5.0), h):
            line = (f'{d:5.0f}" {rates["superficie"]:11.1f} {rates["medio radio"]:12.1f} '
                    f'{rates["centro"]:8.1f}')  # fmt: skip
            if args.velocidad_critica is not None:
                ok = rates["centro"] >= args.velocidad_critica
                line += "  templa el centro" if ok else "  el centro NO templa"
            print(line)


if __name__ == "__main__":
    main()
