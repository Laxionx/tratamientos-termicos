"""Todos los textos de la app en español (clave → texto). Las citas y los títulos de las fuentes no
se traducen. Los {campos} se rellenan con `t(clave, campo=valor)`."""

TEXTS: dict[str, str] = {
    "page.title": "Temple de la bola",
    "app.title": "Temple de la bola",
    "app.caption": (
        "Cómo se enfría por dentro una bola de acero al templarla, con los números de un modelo "
        "validado con medidas de 1925. Empieza por la **Guía**; los datos se cambian en la barra "
        "lateral."
    ),
    "toggle.label": "Mover la animación",
    "toggle.help": (
        "Apaga la animación del esquema. También se apaga sola si el sistema tiene activado "
        "«reducir movimiento»."
    ),
    "tab.guide": "Guía",
    "tab.quench": "Temple",
    "tab.validation": "Validación",
    "yes": "sí",
    "no": "no",
    "sidebar.example": "Cargar ejemplo",
    "sidebar.fixed": (
        "Fijos: {t0} °C → {t1} °C. Los coeficientes de transferencia del NBS solo valen con "
        "estas temperaturas."
    ),
    # ------------------------------------------------------------ pestaña Temple
    "q.err": "No se pudo calcular el temple con estos datos: {exc}",
    "q.range": (
        "Fuera del rango validado con el NBS ({lo} a {hi} pulgadas): el resultado es una "
        "extrapolación."
    ),
    "q.m.center": "Centro baja a 720 °C a los",
    "q.m.center_rate": "Velocidad del centro a 720 °C",
    "q.m.surface_rate": "Velocidad de la superficie a 720 °C",
    "q.m.biot": "Número de Biot (h·R/k)",
    "q.alt": "Corte de una bola de acero templada, enfriándose por anillos",
    "q.caption": (
        "Cada anillo toma el color de la temperatura que calcula el modelo a su radio y a ese "
        "tiempo. Los puntos se ponen verdes cuando esa posición baja de 720 °C."
    ),
    "q.crit.none": "Ninguna capa alcanza la velocidad crítica a 720 °C. Criterio simple; no es dureza.",
    "q.crit.whole": (
        "Toda la bola, hasta el centro, se enfría a 720 °C al menos tan rápido como la "
        "velocidad crítica. Criterio simple; no es dureza."
    ),
    "q.crit.layer": (
        "La capa que se enfría a 720 °C al menos tan rápido como la velocidad crítica tiene "
        "**{depth} mm** de espesor, de {radius} mm de radio. Criterio simple; no es dureza."
    ),
    "q.col.pos": "Posición",
    "q.col.time": "Baja a 720 °C a los (s)",
    "q.col.rate": "Velocidad a 720 °C (°C/s)",
    # ------------------------------------------------------------ pestaña Validación
    "v.intro": (
        "El h de cada medio se calibra con la esfera de 3/4 de pulgada que midió el NBS, y con "
        "ese h se predicen las demás. French y Klopsch (1925) midieron con termocupla el centro "
        "de esferas de acero de rodamiento (0,98 % C, 1,63 % Cr), templadas desde 875 °C en "
        "agua o aceite quietos a 20 °C."
    ),
    "v.metric": "Predicciones dentro de ±{pct} %",
    "v.metric.value": "{n} de {m}",
    "v.col.sphere": "Esfera (pulgadas)",
    "v.col.medium": "Medio",
    "v.col.measured": "Medido (°C/s)",
    "v.col.model": "Modelo (°C/s)",
    "v.col.dev": "Desvío",
    "v.col.inside": "Dentro de ±15 %",
    "v.calibration": "calibración",
    "v.caption": (
        "Las esferas grandes salen entre 10 y 19 % más rápidas de lo medido: es lo esperable sin "
        "calor latente ni capa de vapor. El aceite no tiene medición a 1,61 pulgadas. "
        "Fuente de los datos medidos: French y Klopsch (1925), T295, dominio público."
    ),
    # ------------------------------------------------------------ gráficos
    "plot.temp.title": "Cómo baja la temperatura en cada posición",
    "plot.temp.hover": "{name}: {t} s, {rate} °C/s<extra></extra>",
    "plot.temp.x": "Tiempo (s)",
    "plot.temp.y": "Temperatura (°C)",
    "plot.val.model": "modelo, {medium}",
    "plot.val.measured": "medido NBS, {medium} (±{pct})",
    "plot.val.hover": (
        "%{x}″: medido %{y} °C/s<br>modelo vs medido: %{customdata[0]} %<extra></extra>"
    ),
    "plot.val.out": "modelo fuera de ±{pct}",
    "plot.val.cal": "calibración (¾″)",
    "plot.val.title": "Velocidad del centro a 720 °C: NBS frente al modelo",
    "plot.val.x": "Diámetro de la esfera (pulgadas)",
    "plot.val.y": "Velocidad en el centro (°C/s)",
    # ------------------------------------------------------------ esquema de la bola
    "scheme.note": "esquema, no a escala de tiempo: las temperaturas sí son del cálculo",
    "scheme.temp": "color ilustrativo de la temperatura",
    "svg.title": "Bola de {d} pulgadas templada en {medium}, en corte",
    "svg.label": "Corte de una bola de acero templada, enfriándose por anillos",
    "svg.clock": "t = {t} s",
    "svg.cross": "Cruce de {mark} °C",
    "svg.cross.at": "{name}: a los {t} s",
    "svg.cross.rate": "a {rate} °C/s",
    "svg.bar": "Temperatura ({note})",
    "svg.legend1": (
        "Reloj: {frames} fotogramas, t_k = t_fin·(k/{n})^{power} (más densos al principio), más "
        "el fotograma en que el centro cruza 720 °C. Cada uno dura {frame_s} s de animación: el "
        "ciclo de {cycle} s comprime {real} s reales. {rings} anillos; cada uno muestra la "
        "temperatura a la mitad de su espesor."
    ),
    "svg.legend2": (
        "Medio: {medium}; h efectivo {h} W/m²K, constante. Sin calor latente ni capa de vapor. "
        "Color: {note}."
    ),
    "svg.legend3": "Fuera del rango validado con el NBS (0,75 a 2,77 pulgadas).",
    "svg.crit.none": "Ninguna capa alcanza la velocidad crítica.",
    "svg.crit.whole": "Toda la bola la alcanza (capa de {depth} mm: el radio).",
    "svg.crit.layer": "Capa rayada: {depth} mm de {radius} mm de radio.",
    "svg.crit.note": "Velocidad crítica de {rate} °C/s (dato del material). ",
    "svg.crit.simple": "Criterio simple; no es dureza.",
    # ------------------------------------------------------------ guía y ficha
    "ficha.hace": (
        "Calcula cómo se enfría por dentro una bola de acero que sale del horno a 875 °C y se "
        "mete en agua o aceite a 20 °C: la temperatura a cada radio, segundo a segundo, y cuándo "
        "y a qué velocidad cada capa pasa por 720 °C, la temperatura en que el NBS midió la "
        "velocidad de enfriamiento."
    ),
    "ficha.entra": (
        "El diámetro de la bola y el medio de temple (agua o aceite, en reposo). Opcional: una "
        "velocidad crítica de temple del material, para marcar la capa que la alcanza."
    ),
    "ficha.sale": (
        "La temperatura en cualquier punto y momento; el tiempo y la velocidad de enfriamiento "
        "(°C/s) en que la superficie, el medio radio y el centro pasan por 720 °C; y, si se "
        "pide, el espesor de la capa que alcanza la velocidad crítica. No calcula la dureza."
    ),
    "ficha.autores": (
        "Conducción de calor en una esfera con convección en la superficie, resuelta por "
        "volúmenes finitos y comprobada contra la solución analítica: Incropera et al., "
        "*Fundamentals of Heat and Mass Transfer*, cap. 5. Propiedades de la austenita (k, cp, ρ "
        "constantes): EN 1993-1-2 (Eurocódigo 3). Coeficientes de transferencia y validación: "
        "French y Klopsch (1925), *Technologic Papers of the Bureau of Standards* 19, T295, "
        "dominio público."
    ),
    "ficha.doc": "docs/fase2-temple.md",
    "ficha.limit.1": (
        "Sin calor latente de la transformación ni capa de vapor: el coeficiente de transferencia "
        "(h) es efectivo y constante."
    ),
    "ficha.limit.2": (
        "Solo hay dos h, calibrados con la esfera de 3/4 de pulgada del NBS a 875 °C → 20 °C; "
        "por eso esas temperaturas son fijas y no se ofrece un h libre ni de manual: los de "
        "manual fallan (el h efectivo calibrado en agua quieta da H = 3,2 in⁻¹; los manuales "
        "citan cerca de 1)."
    ),
    "ficha.limit.3": (
        "Validado con acero de rodamiento (0,98 % C, 1,63 % Cr), entre 0,75 y 2,77 pulgadas. "
        "Para un hierro blanco alto cromo cambian la conductividad y el h efectivo: la tabla es "
        "orientativa."
    ),
    "ficha.limit.4": "Las esferas grandes salen entre 10 y 19 % más rápidas que lo medido (ver Validación).",
    "ficha.limit.5": "La dureza no se calcula; la velocidad crítica es un dato del material, no del modelo.",
    "ficha.label.hace": "**Qué hace.** {text}",
    "ficha.label.entra": "**Qué entra.** {text}",
    "ficha.label.sale": "**Qué devuelve.** {text}",
    "ficha.expander.datos": "Qué datos necesita",
    "ficha.expander.limites": "Límites del modelo",
    "ficha.caption": "**De dónde salen las ecuaciones.** {autores} Detalle en [{doc}]({url}).",
    "guide.h.simula": "### Qué simula",
    "guide.simula": (
        "El **temple de una bola de acero**, como las de molienda: sale del horno a 875 °C y se "
        "sumerge en agua o aceite. El simulador calcula, con ecuaciones publicadas, cómo baja la "
        "temperatura capa por capa y segundo a segundo. La animación dibuja esos números: no es "
        "un dibujo suelto."
    ),
    "guide.h.leer": "### Cómo leer la animación",
    "guide.leer": (
        "- La bola se ve **en corte**: los anillos son capas de radio; el color de cada anillo "
        "es la temperatura que calcula el modelo a esa profundidad. El color es **ilustrativo**: "
        "de acero frío (oscuro) a naranja (875 °C).\n"
        "- El **reloj** marca los segundos reales. Los fotogramas están más juntos al principio, "
        "cuando todo cambia rápido, y el ciclo comprime el temple completo en unos segundos.\n"
        "- Los **puntos** de la superficie, el medio radio y el centro se ponen verdes cuando "
        "esa posición baja de 720 °C. Al lado, el tiempo y la velocidad de ese cruce.\n"
        "- Con la comparación activada, la capa **rayada** es la que se enfría a 720 °C al menos "
        "tan rápido como la velocidad crítica que des. Es un criterio simple; no es dureza."
    ),
    "guide.h.centro": "### Por qué el centro se atrasa",
    "guide.centro": (
        "El calor del centro tiene que **viajar por dentro del acero** hasta la superficie, y el "
        "acero lo conduce con dificultad. Una vez en la superficie, el líquido se lo lleva. El "
        "**número de Biot** compara esos dos esfuerzos: lo que cuesta que el calor salga de la "
        "superficie al líquido frente a lo que cuesta que llegue hasta ella desde adentro. Si "
        "el líquido se lleva el calor más fácil de lo que el acero lo entrega (Biot grande), la "
        "superficie se enfría casi al instante y el centro queda atrás: se enfría **capa por "
        "capa, de afuera hacia adentro**. Cuanto más grande la bola, más camino tiene que hacer "
        "el calor y más acero hay que enfriar, así que el centro se atrasa más. Por eso una "
        "bola grande puede no templar a fondo aunque su superficie sí."
    ),
    "guide.h.datos": "### Qué datos necesita",
    "guide.h.limites": "### Lo que no hace",
    "guide.h.otras": "### Otras apps",
    "guide.otras": (
        "- [Simulador de conminución]({conminucion}): la molienda que viene antes, animada.\n"
        "- [«Planta completa»]({planta}): flotación, horno flash, convertidor y "
        "electroobtención, animados.\n"
        "- Código de esta app: [repositorio]({repo})."
    ),
    # ------------------------------------------------------------ datos de entrada
    "dato.help": "{meaning} Rango{unit}: {range}. En planta: {source}",
    "dato.or": " o ",
    "dato.range": "{lo} a {hi}",
    "yesno": "sí o no",
    "col.dato": "Dato",
    "col.unit": "Unidad",
    "col.range": "Rango",
    "col.example": "Ejemplo",
    "col.what": "Qué es",
    "col.how": "Cómo se obtiene",
    "unit.pulgadas": "pulgadas",
    "opt.agua": "agua",
    "opt.aceite": "aceite",
    "dato.diameter.label": "Diámetro de la bola",
    "dato.diameter.meaning": (
        "Diámetro de la bola de acero. El NBS midió entre 0,75 y 2,77 pulgadas: fuera de ese "
        "rango el resultado es una extrapolación."
    ),
    "dato.diameter.source": "medida de la bola (1 pulgada = 25,4 mm).",
    "dato.medium.label": "Medio de temple",
    "dato.medium.meaning": (
        "Líquido en reposo a 20 °C. Solo hay dos, los que midió el NBS: el modelo trae un "
        "coeficiente de transferencia calibrado para cada uno."
    ),
    "dato.medium.source": "el tanque de temple.",
    "dato.compare.label": "Comparar con una velocidad crítica",
    "dato.compare.meaning": (
        "Opcional. Sombrea en la bola la capa que se enfría a 720 °C al menos tan rápido como "
        "la velocidad crítica. Es un criterio simple; no es dureza."
    ),
    "dato.compare.source": "ensayos del material (curvas de enfriamiento continuo).",
    "dato.critical.label": "Velocidad crítica de temple",
    "dato.critical.meaning": (
        "Dato del material, no del modelo: el valor de partida no tiene fuente. Solo se usa si "
        "se activa la comparación."
    ),
    "dato.critical.source": "ensayos del material (dilatometría o curvas de enfriamiento continuo).",
    "fixed.austenitizing": "Temperatura de austenización",
    "fixed.medium": "Temperatura del medio",
    "fixed.range": "fijo",
    "fixed.meaning": "La app no lo deja cambiar: el h calibrado solo vale así.",
    "fixed.source": "Condición del ensayo del NBS.",
}
