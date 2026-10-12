"""Carga más barata para un hierro alto cromo XCr18 (EN-GJN-HV600) con los materiales y precios
de Mędoń et al. (2023). Uso: python ejemplos/carga_xcr18.py [--max-retorno 0.4]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tratamientos.carga import Material, Target, optimize_charge
from tratamientos.validacion import AFE_MATERIALS, AFE_TARGET


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--max-retorno", type=float, default=1.0, help="fracción máxima de retorno")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    materials = [
        Material(name, price, comp, 0.0, args.max_retorno if name == "Retorno" else 1.0)
        for name, (price, comp) in AFE_MATERIALS.items()
    ]
    result = optimize_charge(materials, Target(AFE_TARGET))
    print(f"Carga más barata: {result.price_per_t:,.2f} PLN/t")
    for name, kg in result.kg_per_t().items():
        if kg > 0.05:
            print(f"  {name:18} {kg:8.1f} kg/t")
    print("Química garantizada (%):")
    for element, (lo, hi) in result.chemistry.items():
        low, high = AFE_TARGET[element]
        print(f"  {element:3} {lo:6.2f} a {hi:6.2f}  (objetivo {low} a {high})")


if __name__ == "__main__":
    main()
