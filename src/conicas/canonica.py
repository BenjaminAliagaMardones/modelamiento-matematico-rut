from __future__ import annotations

from src.conicas.algebra import Fraccion, fmt_dec, fmt_frac_dec, raiz_cuadrada

DOS = Fraccion(2)
CUATRO = Fraccion(4)


def _binomio(var: str, centro: Fraccion) -> str:
    "Escribe (x - h) cuidando el signo de h."
    if centro.es_cero():
        return var
    if centro.signo() > 0:
        return f"({var} - {centro})"
    return f"({var} + {-centro})"


def _cuad(var: str, centro: Fraccion) -> str:
    if centro.es_cero():
        return f"{var}²"
    return f"{_binomio(var, centro)}²"


def _den(fr: Fraccion) -> str:
    "Denominador para la forma canónica: entre paréntesis si no es entero positivo."
    if fr.d == 1 and fr.n >= 0:
        return str(fr.n)
    return f"({fr})"


def _termino_frac(coef: Fraccion, simbolo: str) -> str | None:
    if coef.es_cero():
        return None
    abs_coef = coef if coef.signo() > 0 else -coef
    if abs_coef == Fraccion(1) and simbolo:
        cuerpo = simbolo
    else:
        cuerpo = f"{abs_coef}{simbolo}" if simbolo else str(abs_coef)
    return ("-" if coef.signo() < 0 else "") + cuerpo


def _mas(fr: Fraccion, simbolo: str = "") -> str:
    "Devuelve ' + 6x' / ' - 6x' / ' + 1', omitiendo términos nulos."
    t = _termino_frac(fr, simbolo)
    if t is None:
        return ""
    if t.startswith("-"):
        return f" - {t[1:]}"
    return f" + {t}"


def _factor(coef: Fraccion, grupo: str) -> tuple[str, str]:
    "Devuelve (signo, 'c(grupo)') para escribir coef·grupo con el signo aparte."
    signo = "-" if coef.signo() < 0 else "+"
    c = coef if coef.signo() > 0 else -coef
    cuerpo = grupo if c == Fraccion(1) else f"{c}{grupo}"
    return signo, cuerpo


def _ecuacion_general_str(A, B, C, D, E) -> str:
    partes = []
    for coef, simbolo in [(A, "x²"), (B, "y²"), (C, "x"), (D, "y"), (E, "")]:
        t = _termino_frac(coef, simbolo)
        if t is None:
            continue
        if not partes:
            partes.append(t)
        elif t.startswith("-"):
            partes.append(f"- {t[1:]}")
        else:
            partes.append(f"+ {t}")
    if not partes:
        return "0 = 0"
    return " ".join(partes) + " = 0"


# --------------------------------------------------------------------------
# General  ->  Canónica
# --------------------------------------------------------------------------

def general_a_canonica(coef_frac: dict, tipo: str) -> dict:
    "Lleva Ax² + By² + Cx + Dy + E = 0 a su forma canónica, mostrando los pasos."
    A, B, C, D, E = (coef_frac[k] for k in "ABCDE")

    if tipo == "parábola":
        return _parabola_canonica(A, B, C, D, E)
    if tipo == "degenerada":
        return {
            "pasos": ["Con A = 0 y B = 0 no hay forma canónica: no es una cónica."],
            "forma_canonica": "—",
            "parametros": {"tipo": tipo},
        }
    return _central_canonica(A, B, C, D, E, tipo)


def _central_canonica(A, B, C, D, E, tipo) -> dict:
    pasos = [f"Partimos de:  {_ecuacion_general_str(A, B, C, D, E)}"]
    _, ta = _factor(A, f"(x²{_mas(C / A, 'x')})")
    sb, tb = _factor(B, f"(y²{_mas(D / B, 'y')})")
    pasos.append(f"Factorizamos A y B:  {ta} {sb} {tb}{_mas(E)} = 0")

    h = -(C / (DOS * A))
    k = -(D / (DOS * B))
    termino_x = (C * C) / (CUATRO * A)
    termino_y = (D * D) / (CUATRO * B)
    F = termino_x + termino_y - E

    pasos.append("Completamos cuadrados y pasamos las constantes a la derecha:")
    _, ta = _factor(A, _cuad("x", h))
    sb, tb = _factor(B, _cuad("y", k))
    pasos.append(f"  {ta} {sb} {tb} = {fmt_frac_dec(F)}")
    pasos.append(f"El centro es ({fmt_frac_dec(h)} , {fmt_frac_dec(k)}).")

    parametros = {"tipo": tipo, "h": h, "k": k, "F": F}

    if tipo == "circunferencia":
        r2 = F / A
        parametros["r2"] = r2
        pasos.append(f"Dividimos por {A}:  {_cuad('x', h)} + {_cuad('y', k)} = {fmt_frac_dec(r2)}")
        if r2.signo() <= 0:
            pasos.append("Como r² ≤ 0, la circunferencia no tiene puntos reales.")
            forma = "sin puntos reales"
        else:
            r = raiz_cuadrada(r2.a_decimal())
            parametros["r"] = r
            forma = f"{_cuad('x', h)} + {_cuad('y', k)} = {fmt_frac_dec(r2)}"
            pasos.append(f"El radio es r = √{fmt_frac_dec(r2)} ≈ {fmt_dec(r)}.")
    else:
        denom_x = F / A
        denom_y = F / B
        parametros["denom_x"] = denom_x
        parametros["denom_y"] = denom_y

        if tipo == "elipse":
            forma = f"{_cuad('x', h)}/{_den(denom_x)} + {_cuad('y', k)}/{_den(denom_y)} = 1"
            pasos.append(f"Dividimos por {fmt_frac_dec(F)} para igualar a 1:")
            pasos.append(f"  {forma}")
            if denom_x.signo() > 0 and denom_y.signo() > 0:
                a = raiz_cuadrada(denom_x.a_decimal())
                b = raiz_cuadrada(denom_y.a_decimal())
                parametros["a"] = a
                parametros["b"] = b
                pasos.append(f"Semiejes: a ≈ {fmt_dec(a)} y b ≈ {fmt_dec(b)}.")
            else:
                pasos.append("Algún denominador es ≤ 0: la elipse no tiene puntos reales.")
        else:  # hipérbola
            if denom_x.signo() > 0:
                forma = (
                    f"{_cuad('x', h)}/{_den(denom_x)} - {_cuad('y', k)}/{_den(-denom_y)} = 1"
                )
            else:
                forma = (
                    f"{_cuad('y', k)}/{_den(denom_y)} - {_cuad('x', h)}/{_den(-denom_x)} = 1"
                )
            pasos.append(f"Dividimos por {fmt_frac_dec(F)} y dejamos primero el término positivo:")
            pasos.append(f"  {forma}")

    parametros["forma"] = forma
    return {"pasos": pasos, "forma_canonica": forma, "parametros": parametros}


def _parabola_canonica(A, B, C, D, E) -> dict:
    pasos = [f"Partimos de:  {_ecuacion_general_str(A, B, C, D, E)}"]

    if B.es_cero():  # eje vertical: A x² + C x + D y + E = 0
        if A.es_cero() or D.es_cero():
            return _parabola_degenerada(A, B, C, D, E, "vertical")
        h = -(C / (DOS * A))
        k = ((C * C) / (CUATRO * A) - E) / D
        factor = -D / A          # (x-h)² = factor (y-k)
        pasos.append(f"Completamos el cuadrado en x:  {A}{_cuad('x', h)} = {-D}{_binomio('y', k)}")
        pasos.append(f"Dividimos por {A}:  {_cuad('x', h)} = {fmt_frac_dec(factor)}·{_binomio('y', k)}")
        forma = f"{_cuad('x', h)} = {fmt_frac_dec(factor)} · {_binomio('y', k)}"
        orientacion = "vertical"
    else:  # eje horizontal: B y² + C x + D y + E = 0
        if B.es_cero() or C.es_cero():
            return _parabola_degenerada(A, B, C, D, E, "horizontal")
        k = -(D / (DOS * B))
        h = ((D * D) / (CUATRO * B) - E) / C
        factor = -C / B          # (y-k)² = factor (x-h)
        pasos.append(f"Completamos el cuadrado en y:  {B}{_cuad('y', k)} = {-C}{_binomio('x', h)}")
        pasos.append(f"Dividimos por {B}:  {_cuad('y', k)} = {fmt_frac_dec(factor)}·{_binomio('x', h)}")
        forma = f"{_cuad('y', k)} = {fmt_frac_dec(factor)} · {_binomio('x', h)}"
        orientacion = "horizontal"

    p = factor / CUATRO
    pasos.append(
        f"Vértice ({fmt_frac_dec(h)} , {fmt_frac_dec(k)}); como 4p = {fmt_frac_dec(factor)}, "
        f"entonces p = {fmt_frac_dec(p)}."
    )

    return {
        "pasos": pasos,
        "forma_canonica": forma,
        "parametros": {
            "tipo": "parábola", "orientacion": orientacion,
            "h": h, "k": k, "factor": factor, "p": p, "forma": forma,
        },
    }


def _parabola_degenerada(A, B, C, D, E, orientacion) -> dict:
    return {
        "pasos": [
            f"Partimos de:  {_ecuacion_general_str(A, B, C, D, E)}",
            "Falta el término lineal: la ecuación degenera en rectas o en el vacío, "
            "no es una parábola.",
        ],
        "forma_canonica": "—",
        "parametros": {"tipo": "parábola", "orientacion": orientacion, "degenerada": True},
    }


# --------------------------------------------------------------------------
# Canónica  ->  General
# --------------------------------------------------------------------------

def canonica_a_general(parametros: dict, tipo: str) -> dict:
    "Expande la forma canónica para recuperar la ecuación general, paso a paso."
    if parametros.get("degenerada") or tipo == "degenerada":
        return {"pasos": ["La cónica es degenerada: no hay forma canónica que expandir."],
                "ecuacion": "—"}

    if tipo == "parábola":
        return _parabola_inversa(parametros)
    if tipo == "circunferencia":
        return _circunferencia_inversa(parametros)
    return _central_inversa(parametros)  # elipse / hipérbola


def _circunferencia_inversa(p: dict) -> dict:
    h, k, r2 = p["h"], p["k"], p.get("r2")
    if r2 is None:
        return {"pasos": ["Sin puntos reales: no hay nada que expandir."], "ecuacion": "—"}
    A, B = Fraccion(1), Fraccion(1)
    C = -DOS * h
    D = -DOS * k
    E = h * h + k * k - r2
    eq = _ecuacion_general_str(A, B, C, D, E)
    pasos = [
        f"Partimos de:  {_cuad('x', h)} + {_cuad('y', k)} = {fmt_frac_dec(r2)}",
        "Desarrollamos los cuadrados y pasamos todo a un lado:",
        f"  {eq}",
        "Recuperamos la ecuación general original (salvo un factor).",
    ]
    return {"pasos": pasos, "ecuacion": eq,
            "coeficientes": {"A": A, "B": B, "C": C, "D": D, "E": E}}


def _central_inversa(p: dict) -> dict:
    h, k = p["h"], p["k"]
    dx, dy = p["denom_x"], p["denom_y"]
    A, B = dy, dx
    C = -DOS * h * dy
    D = -DOS * k * dx
    E = dy * (h * h) + dx * (k * k) - dx * dy
    eq = _ecuacion_general_str(A, B, C, D, E)
    pasos = [
        f"Partimos de:  {_cuad('x', h)}/{_den(dx)} + {_cuad('y', k)}/{_den(dy)} = 1",
        f"Multiplicamos por ({dx})·({dy}) y desarrollamos los cuadrados:",
        f"  {eq}",
        "Es proporcional a la ecuación general original.",
    ]
    return {"pasos": pasos, "ecuacion": eq,
            "coeficientes": {"A": A, "B": B, "C": C, "D": D, "E": E}}


def _parabola_inversa(p: dict) -> dict:
    h, k, factor = p["h"], p["k"], p["factor"]
    if p["orientacion"] == "vertical":
        forma = f"{_cuad('x', h)} = {fmt_frac_dec(factor)}·{_binomio('y', k)}"
        A, B = Fraccion(1), Fraccion(0)
        C = -DOS * h
        D = -factor
        E = h * h + factor * k
    else:
        forma = f"{_cuad('y', k)} = {fmt_frac_dec(factor)}·{_binomio('x', h)}"
        A, B = Fraccion(0), Fraccion(1)
        C = -factor
        D = -DOS * k
        E = k * k + factor * h
    eq = _ecuacion_general_str(A, B, C, D, E)
    pasos = [
        f"Partimos de:  {forma}",
        "Desarrollamos el cuadrado y ordenamos:",
        f"  {eq}",
        "Es proporcional a la ecuación general original.",
    ]
    return {"pasos": pasos, "ecuacion": eq,
            "coeficientes": {"A": A, "B": B, "C": C, "D": D, "E": E}}
