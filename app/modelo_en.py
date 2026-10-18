"""Los rótulos que salen del modelo (`tratamientos`) en español, vertidos al inglés para la app.

El modelo no cambia: sus cifras y sus textos siguen en español. Aquí se traducen los nombres de
los medios y de las posiciones de la bola y los mensajes de error conocidos. La prueba
`test_i18n.py` recorre todos los rótulos que el modelo produce y comprueba que no queda español.
"""

from __future__ import annotations

import re

WORDS = {
    "agua": "water",
    "aceite": "oil",
    "centro": "center",
    "medio radio": "mid-radius",
    "superficie": "surface",
}
ERRORS: tuple[tuple[str, str], ...] = (
    (r"medio desconocido: (.+); solo (.+)", "unknown medium: {0}; only {1}"),
    (
        r"el diámetro y la velocidad crítica deben ser positivos",
        "the diameter and the critical rate must be positive",
    ),
    (
        r"diámetro y h positivos, y al menos 10 nodos",
        "positive diameter and h, and at least 10 nodes",
    ),
    (r"no llega a (.+) °C en (.+) s", "does not reach {0} °C in {1} s"),
    (r"no convergió el enfriamiento: (.+)", "the cooling did not converge: {0}"),
)


def translate(text: str) -> str:
    """El nombre de un medio o de una posición, en inglés (lo que no se conoce queda igual)."""
    return WORDS.get(text, text)


def translate_error(message: str) -> str:
    """Un mensaje de error del modelo en inglés; si no se conoce, el original."""
    for pattern, template in ERRORS:
        m = re.fullmatch(pattern, message, flags=re.S)
        if m:
            return template.format(
                *(re.sub(r"\w+", lambda w: WORDS.get(w.group(), w.group()), g) for g in m.groups())
            )
    return message
