"Cálculo de los elementos geométricos de cada cónica (centro, vértices, focos, ejes…)."

from __future__ import annotations

from src.conicas.algebra import fmt_dec, raiz_cuadrada

CAMPOS = [
    "Centro",
    "Vértice(s)",
    "Foco(s)",
    "Eje mayor / transverso",
    "Eje menor / conjugado",
    "Directriz",
]


def _pt(x: float, y: float) -> str:
    return f"({fmt_dec(x)},{fmt_dec(y)})"


def _vacio() -> dict:
    return {
        "puntos": [],       # (x, y, campo)
        "segmentos": [],    # (x1, y1, x2, y2, campo)
        "rectas": [],       # (clase, datos, campo): clase ∈ vertical|horizontal|oblicua
        "validacion": {c: "No aplica" for c in CAMPOS},
    }


def calcular_elementos(parametros: dict, tipo: str) -> dict:
    "Devuelve la geometría a dibujar y los valores correctos para validar."
    res = _vacio()
    if tipo == "degenerada":
        return res

    h = parametros.get("h")
    k = parametros.get("k")
    hx = h.a_decimal() if h is not None else 0.0
    ky = k.a_decimal() if k is not None else 0.0

    if tipo == "circunferencia":
        if parametros.get("r"):  # solo si tiene puntos reales
            res["puntos"].append((hx, ky, "Centro"))
            res["validacion"]["Centro"] = _pt(hx, ky)
        else:
            res["puntos"].append((hx, ky, "Centro"))
            res["validacion"]["Centro"] = _pt(hx, ky)
        return res

    if tipo == "elipse":
        dx = parametros.get("denom_x")
        dy = parametros.get("denom_y")
        res["puntos"].append((hx, ky, "Centro"))
        res["validacion"]["Centro"] = _pt(hx, ky)
        if dx is None or dy is None or dx.signo() <= 0 or dy.signo() <= 0:
            return res  # sin puntos reales: solo centro
        a = raiz_cuadrada(dx.a_decimal())   # semieje en x
        b = raiz_cuadrada(dy.a_decimal())   # semieje en y
        vertices = [(hx + a, ky), (hx - a, ky), (hx, ky + b), (hx, ky - b)]
        c = raiz_cuadrada(abs(a * a - b * b))
        if a >= b:
            focos = [(hx + c, ky), (hx - c, ky)]
            res["segmentos"].append((hx - a, ky, hx + a, ky, "Eje mayor / transverso"))
            res["segmentos"].append((hx, ky - b, hx, ky + b, "Eje menor / conjugado"))
        else:
            focos = [(hx, ky + c), (hx, ky - c)]
            res["segmentos"].append((hx, ky - b, hx, ky + b, "Eje mayor / transverso"))
            res["segmentos"].append((hx - a, ky, hx + a, ky, "Eje menor / conjugado"))
        for vx, vy in vertices:
            res["puntos"].append((vx, vy, "Vértice(s)"))
        for fx, fy in focos:
            res["puntos"].append((fx, fy, "Foco(s)"))
        res["validacion"]["Vértice(s)"] = [_pt(vx, vy) for vx, vy in vertices]
        res["validacion"]["Foco(s)"] = [_pt(fx, fy) for fx, fy in focos]
        res["validacion"]["Eje mayor / transverso"] = fmt_dec(2 * max(a, b))
        res["validacion"]["Eje menor / conjugado"] = fmt_dec(2 * min(a, b))
        return res

    if tipo == "hipérbola":
        dx = parametros["denom_x"]
        dy = parametros["denom_y"]
        res["puntos"].append((hx, ky, "Centro"))
        res["validacion"]["Centro"] = _pt(hx, ky)
        if dx.signo() > 0:   # eje transverso horizontal
            a = raiz_cuadrada(dx.a_decimal())
            b = raiz_cuadrada(abs(dy.a_decimal()))
            vertices = [(hx + a, ky), (hx - a, ky)]
            c = raiz_cuadrada(a * a + b * b)
            focos = [(hx + c, ky), (hx - c, ky)]
            res["segmentos"].append((hx - a, ky, hx + a, ky, "Eje mayor / transverso"))
            res["segmentos"].append((hx, ky - b, hx, ky + b, "Eje menor / conjugado"))
            m = b / a if a else 0.0
        else:                # eje transverso vertical
            a = raiz_cuadrada(dy.a_decimal())
            b = raiz_cuadrada(abs(dx.a_decimal()))
            vertices = [(hx, ky + a), (hx, ky - a)]
            c = raiz_cuadrada(a * a + b * b)
            focos = [(hx, ky + c), (hx, ky - c)]
            res["segmentos"].append((hx, ky - a, hx, ky + a, "Eje mayor / transverso"))
            res["segmentos"].append((hx - b, ky, hx + b, ky, "Eje menor / conjugado"))
            m = a / b if b else 0.0
        res["rectas"].append(("oblicua", (hx, ky, m), "Asíntotas"))
        res["rectas"].append(("oblicua", (hx, ky, -m), "Asíntotas"))
        for vx, vy in vertices:
            res["puntos"].append((vx, vy, "Vértice(s)"))
        for fx, fy in focos:
            res["puntos"].append((fx, fy, "Foco(s)"))
        res["validacion"]["Vértice(s)"] = [_pt(vx, vy) for vx, vy in vertices]
        res["validacion"]["Foco(s)"] = [_pt(fx, fy) for fx, fy in focos]
        res["validacion"]["Eje mayor / transverso"] = fmt_dec(2 * a)
        res["validacion"]["Eje menor / conjugado"] = fmt_dec(2 * b)
        return res

    if tipo == "parábola" and not parametros.get("degenerada"):
        p = parametros["p"].a_decimal()
        res["puntos"].append((hx, ky, "Vértice(s)"))
        res["validacion"]["Vértice(s)"] = _pt(hx, ky)
        if parametros.get("orientacion") == "vertical":
            fx, fy = hx, ky + p
            res["puntos"].append((fx, fy, "Foco(s)"))
            res["rectas"].append(("horizontal", ky - p, "Directriz"))
            res["rectas"].append(("vertical", hx, "Eje"))   # eje de simetría
            res["validacion"]["Foco(s)"] = _pt(fx, fy)
            res["validacion"]["Directriz"] = f"y={fmt_dec(ky - p)}"
        else:
            fx, fy = hx + p, ky
            res["puntos"].append((fx, fy, "Foco(s)"))
            res["rectas"].append(("vertical", hx - p, "Directriz"))
            res["rectas"].append(("horizontal", ky, "Eje"))
            res["validacion"]["Foco(s)"] = _pt(fx, fy)
            res["validacion"]["Directriz"] = f"x={fmt_dec(hx - p)}"
        return res

    return res
