"""All the app texts in English (key → text). Citations and titles of sources are not translated.
The {fields} are filled in with `t(key, field=value)`."""

TEXTS: dict[str, str] = {
    "page.title": "Ball quenching",
    "app.title": "Ball quenching",
    "app.caption": (
        "How a steel ball cools inside when it is quenched, with the numbers of a model "
        "validated with 1925 measurements. Start with the **Guide**; change the data in the "
        "sidebar."
    ),
    "toggle.label": "Animate",
    "toggle.help": (
        "Turns off the diagram animation. It also turns off by itself if the system has "
        "«reduce motion» enabled."
    ),
    "tab.guide": "Guide",
    "tab.quench": "Quench",
    "tab.validation": "Validation",
    "yes": "yes",
    "no": "no",
    "sidebar.example": "Load example",
    "sidebar.fixed": (
        "Fixed: {t0} °C → {t1} °C. The NBS heat-transfer coefficients are only valid at these "
        "temperatures."
    ),
    "q.err": "The quench could not be calculated with these data: {exc}",
    "q.range": (
        "Outside the range validated with the NBS ({lo} to {hi} inches): the result is an "
        "extrapolation."
    ),
    "q.m.center": "Center drops to 720 °C at",
    "q.m.center_rate": "Center cooling rate at 720 °C",
    "q.m.surface_rate": "Surface cooling rate at 720 °C",
    "q.m.biot": "Biot number (h·R/k)",
    "q.alt": "Section of a quenched steel ball, cooling ring by ring",
    "q.caption": (
        "Each ring takes the color of the temperature the model calculates at its radius and at "
        "that time. The dots turn green when that position drops below 720 °C."
    ),
    "q.crit.none": "No layer reaches the critical rate at 720 °C. Simple criterion; not hardness.",
    "q.crit.whole": (
        "The whole ball, down to the center, cools at 720 °C at least as fast as the critical "
        "rate. Simple criterion; not hardness."
    ),
    "q.crit.layer": (
        "The layer that cools at 720 °C at least as fast as the critical rate is **{depth} mm** "
        "thick, out of a {radius} mm radius. Simple criterion; not hardness."
    ),
    "q.col.pos": "Position",
    "q.col.time": "Drops to 720 °C at (s)",
    "q.col.rate": "Rate at 720 °C (°C/s)",
    "v.intro": (
        "The h of each medium is calibrated with the 3/4-inch sphere that the NBS measured, and "
        "with that h the others are predicted. French and Klopsch (1925) measured with a "
        "thermocouple the center of bearing-steel spheres (0.98 % C, 1.63 % Cr), quenched from "
        "875 °C in still water or oil at 20 °C."
    ),
    "v.metric": "Predictions within ±{pct} %",
    "v.metric.value": "{n} of {m}",
    "v.col.sphere": "Sphere (inches)",
    "v.col.medium": "Medium",
    "v.col.measured": "Measured (°C/s)",
    "v.col.model": "Model (°C/s)",
    "v.col.dev": "Deviation",
    "v.col.inside": "Within ±15 %",
    "v.calibration": "calibration",
    "v.caption": (
        "The large spheres come out 10 to 19 % faster than measured: that is expected without "
        "latent heat or a vapor layer. Oil has no measurement at 1.61 inches. Source of the "
        "measured data: French and Klopsch (1925), T295, public domain."
    ),
    "plot.temp.title": "How the temperature drops at each position",
    "plot.temp.hover": "{name}: {t} s, {rate} °C/s<extra></extra>",
    "plot.temp.x": "Time (s)",
    "plot.temp.y": "Temperature (°C)",
    "plot.val.model": "model, {medium}",
    "plot.val.measured": "NBS measured, {medium} (±{pct})",
    "plot.val.hover": (
        "%{x}″: measured %{y} °C/s<br>model vs measured: %{customdata[0]} %<extra></extra>"
    ),
    "plot.val.out": "model outside ±{pct}",
    "plot.val.cal": "calibration (¾″)",
    "plot.val.title": "Center cooling rate at 720 °C: NBS versus the model",
    "plot.val.x": "Sphere diameter (inches)",
    "plot.val.y": "Center cooling rate (°C/s)",
    "scheme.note": "diagram, not to time scale: the temperatures do come from the calculation",
    "scheme.temp": "illustrative color of the temperature",
    "svg.title": "{d}-inch ball quenched in {medium}, in section",
    "svg.label": "Section of a quenched steel ball, cooling ring by ring",
    "svg.clock": "t = {t} s",
    "svg.cross": "{mark} °C crossing",
    "svg.cross.at": "{name}: at {t} s",
    "svg.cross.rate": "at {rate} °C/s",
    "svg.bar": "Temperature ({note})",
    "svg.legend1": (
        "Clock: {frames} frames, t_k = t_end·(k/{n})^{power} (denser at the start), plus the "
        "frame in which the center crosses 720 °C. Each lasts {frame_s} s of animation: the "
        "{cycle} s cycle compresses {real} real seconds. {rings} rings; each shows the "
        "temperature at half its thickness."
    ),
    "svg.legend2": (
        "Medium: {medium}; effective h {h} W/m²K, constant. No latent heat or vapor layer. "
        "Color: {note}."
    ),
    "svg.legend3": "Outside the range validated with the NBS (0.75 to 2.77 inches).",
    "svg.crit.none": "No layer reaches the critical rate.",
    "svg.crit.whole": "The whole ball reaches it (layer of {depth} mm: the radius).",
    "svg.crit.layer": "Hatched layer: {depth} mm out of a {radius} mm radius.",
    "svg.crit.note": "Critical rate of {rate} °C/s (material datum). ",
    "svg.crit.simple": "Simple criterion; not hardness.",
    "ficha.hace": (
        "Calculates how a steel ball cools inside when it leaves the furnace at 875 °C and is "
        "dropped in water or oil at 20 °C: the temperature at each radius, second by second, and "
        "when and how fast each layer passes through 720 °C, the temperature at which the NBS "
        "measured the cooling rate."
    ),
    "ficha.entra": (
        "The ball diameter and the quenching medium (water or oil, still). Optional: a critical "
        "quenching rate of the material, to mark the layer that reaches it."
    ),
    "ficha.sale": (
        "The temperature at any point and time; the time and cooling rate (°C/s) at which the "
        "surface, the mid-radius and the center pass through 720 °C; and, if requested, the "
        "thickness of the layer that reaches the critical rate. It does not calculate hardness."
    ),
    "ficha.autores": (
        "Heat conduction in a sphere with surface convection, solved by finite volumes and "
        "checked against the analytical solution: Incropera et al., *Fundamentals of Heat and "
        "Mass Transfer*, ch. 5. Austenite properties (constant k, cp, ρ): EN 1993-1-2 "
        "(Eurocode 3). Heat-transfer coefficients and validation: French and Klopsch (1925), "
        "*Technologic Papers of the Bureau of Standards* 19, T295, public domain."
    ),
    "ficha.doc": "docs/fase2-temple.md",
    "ficha.limit.1": (
        "No latent heat of the transformation or vapor layer: the heat-transfer coefficient (h) "
        "is effective and constant."
    ),
    "ficha.limit.2": (
        "There are only two h, calibrated with the NBS 3/4-inch sphere at 875 °C → 20 °C; that "
        "is why those temperatures are fixed and no free or handbook h is offered: handbook ones "
        "fail (the effective h calibrated in still water gives H = 3.2 in⁻¹; handbooks quote "
        "close to 1)."
    ),
    "ficha.limit.3": (
        "Validated with bearing steel (0.98 % C, 1.63 % Cr), between 0.75 and 2.77 inches. For a "
        "high-chromium white iron the conductivity and the effective h change: the table is "
        "indicative."
    ),
    "ficha.limit.4": "The large spheres come out 10 to 19 % faster than measured (see Validation).",
    "ficha.limit.5": "Hardness is not calculated; the critical rate is a material datum, not a model one.",
    "ficha.label.hace": "**What it does.** {text}",
    "ficha.label.entra": "**What goes in.** {text}",
    "ficha.label.sale": "**What comes out.** {text}",
    "ficha.expander.datos": "What data it needs",
    "ficha.expander.limites": "Model limits",
    "ficha.caption": "**Where the equations come from.** {autores} Details in [{doc}]({url}).",
    "guide.h.simula": "### What it simulates",
    "guide.simula": (
        "The **quenching of a steel ball**, like grinding balls: it leaves the furnace at 875 °C "
        "and is dropped in water or oil. The simulator calculates, with published equations, how "
        "the temperature drops layer by layer and second by second. The animation draws those "
        "numbers: it is not a loose drawing."
    ),
    "guide.h.leer": "### How to read the animation",
    "guide.leer": (
        "- The ball is seen **in section**: the rings are layers of radius; the color of each "
        "ring is the temperature the model calculates at that depth. The color is "
        "**illustrative**: from cold steel (dark) to orange (875 °C).\n"
        "- The **clock** shows the real seconds. The frames are closer together at the start, "
        "when everything changes fast, and the cycle compresses the whole quench into a few "
        "seconds.\n"
        "- The **dots** of the surface, the mid-radius and the center turn green when that "
        "position drops below 720 °C. Beside them, the time and rate of that crossing.\n"
        "- With the comparison on, the **hatched** layer is the one that cools at 720 °C at "
        "least as fast as the critical rate you give. It is a simple criterion; not hardness."
    ),
    "guide.h.centro": "### Why the center lags behind",
    "guide.centro": (
        "The heat of the center has to **travel through the steel** to the surface, and steel "
        "conducts it with difficulty. Once at the surface, the liquid carries it away. The "
        "**Biot number** compares those two efforts: how hard it is for the heat to leave the "
        "surface into the liquid against how hard it is for it to reach the surface from "
        "inside. If the liquid takes the heat away more easily than the steel delivers it (large "
        "Biot), the surface cools almost instantly and the center is left behind: it cools "
        "**layer by layer, from the outside in**. The larger the ball, the longer the path the "
        "heat has to travel and the more steel there is to cool, so the center lags more. That "
        "is why a large ball may not quench all the way through even though its surface does."
    ),
    "guide.h.datos": "### What data it needs",
    "guide.h.limites": "### What it does not do",
    "guide.h.otras": "### Other apps",
    "guide.otras": (
        "- [Comminution simulator]({conminucion}): the grinding that comes before, animated.\n"
        "- [«Full plant»]({planta}): flotation, flash furnace, converter and electrowinning, "
        "animated.\n"
        "- Code of this app: [repository]({repo})."
    ),
    "dato.help": "{meaning} Range{unit}: {range}. In the plant: {source}",
    "dato.or": " or ",
    "dato.range": "{lo} to {hi}",
    "yesno": "yes or no",
    "col.dato": "Input",
    "col.unit": "Unit",
    "col.range": "Range",
    "col.example": "Example",
    "col.what": "What it is",
    "col.how": "How it is obtained",
    "unit.pulgadas": "inches",
    "opt.agua": "water",
    "opt.aceite": "oil",
    "dato.diameter.label": "Ball diameter",
    "dato.diameter.meaning": (
        "Diameter of the steel ball. The NBS measured between 0.75 and 2.77 inches: outside that "
        "range the result is an extrapolation."
    ),
    "dato.diameter.source": "measurement of the ball (1 inch = 25.4 mm).",
    "dato.medium.label": "Quenching medium",
    "dato.medium.meaning": (
        "Liquid at rest at 20 °C. There are only two, those the NBS measured: the model carries "
        "a heat-transfer coefficient calibrated for each one."
    ),
    "dato.medium.source": "the quenching tank.",
    "dato.compare.label": "Compare with a critical rate",
    "dato.compare.meaning": (
        "Optional. It shades on the ball the layer that cools at 720 °C at least as fast as the "
        "critical rate. It is a simple criterion; not hardness."
    ),
    "dato.compare.source": "material tests (continuous-cooling curves).",
    "dato.critical.label": "Critical quenching rate",
    "dato.critical.meaning": (
        "Material datum, not a model one: the starting value has no source. It is only used if "
        "the comparison is switched on."
    ),
    "dato.critical.source": "material tests (dilatometry or continuous-cooling curves).",
    "fixed.austenitizing": "Austenitizing temperature",
    "fixed.medium": "Medium temperature",
    "fixed.range": "fixed",
    "fixed.meaning": "The app does not let you change it: the calibrated h is only valid this way.",
    "fixed.source": "Condition of the NBS test.",
}
