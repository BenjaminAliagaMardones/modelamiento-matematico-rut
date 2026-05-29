"Generación de los puntos de la cónica para dibujar en un Canvas (sin numpy)."

from __future__ import annotations

from src.conicas.algebra import raiz_cuadrada

EPS = 1e-9


def _resolver_y(A, B, C, D, E, x) -> list[float]:
    "Resuelve B·y² + D·y + (A·x² + C·x + E) = 0 para y."
    c = A * x * x + C * x + E
    if abs(B) > EPS:
        disc = D * D - 4 * B * c
        if disc < 0:
            return []
        s = raiz_cuadrada(disc)
        return [(-D + s) / (2 * B), (-D - s) / (2 * B)]
    if abs(D) > EPS:
        return [-c / D]
    return []


def _resolver_x(A, B, C, D, E, y) -> list[float]:
    "Resuelve A·x² + C·x + (B·y² + D·y + E) = 0 para x."
    c = B * y * y + D * y + E
    if abs(A) > EPS:
        disc = C * C - 4 * A * c
        if disc < 0:
            return []
        s = raiz_cuadrada(disc)
        return [(-C + s) / (2 * A), (-C - s) / (2 * A)]
    if abs(C) > EPS:
        return [-c / C]
    return []


def _centro(parametros: dict) -> tuple[float, float]:
    h = parametros.get("h")
    k = parametros.get("k")
    hx = h.a_decimal() if h is not None else 0.0
    ky = k.a_decimal() if k is not None else 0.0
    return hx, ky


def _extension(parametros: dict, tipo: str) -> float:
    "Semi-ancho aproximado del contenido para encuadrar la ventana."
    if tipo == "circunferencia" and parametros.get("r"):
        return parametros["r"]
    if tipo == "elipse":
        a = parametros.get("a", 0.0)
        b = parametros.get("b", 0.0)
        if a or b:
            return max(a, b)
    if tipo == "hipérbola":
        valores = []
        for clave in ("denom_x", "denom_y"):
            fr = parametros.get(clave)
            if fr is not None:
                valores.append(raiz_cuadrada(abs(fr.a_decimal())))
        if valores:
            return max(valores) * 2.2
    return 6.0


def puntos_conica(coef_float: dict, parametros: dict, tipo: str) -> dict:
    "Devuelve {ventana, centro, puntos} en coordenadas del mundo."
    A, B, C, D, E = (coef_float[k] for k in "ABCDE")
    hx, ky = _centro(parametros)
    W = max(_extension(parametros, tipo) * 1.5, 4.0)

    xmin, xmax = hx - W, hx + W
    ymin, ymax = ky - W, ky + W

    puntos: list[tuple[float, float]] = []
    n = 700
    paso_x = (xmax - xmin) / n
    paso_y = (ymax - ymin) / n

    x = xmin
    while x <= xmax:
        for y in _resolver_y(A, B, C, D, E, x):
            if ymin <= y <= ymax:
                puntos.append((x, y))
        x += paso_x

    y = ymin
    while y <= ymax:
        for xv in _resolver_x(A, B, C, D, E, y):
            if xmin <= xv <= xmax:
                puntos.append((xv, y))
        y += paso_y

    return {
        "ventana": (xmin, xmax, ymin, ymax),
        "centro": (hx, ky),
        "puntos": puntos,
    }
