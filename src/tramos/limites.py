"Análisis analítico de límites laterales y determinación de continuidad."

from __future__ import annotations


def analizar_limites(datos_funcion: dict) -> dict:
    """
    Recibe el diccionario generado por construir_funcion y calcula
    analíticamente los límites laterales en el punto 'a'.
    """
    tipo = datos_funcion["tipo"]
    a = datos_funcion["a"]
    tramos = datos_funcion["tramos"]
    pasos = []

    pasos.append(
        f"--- Análisis de Límites en el punto de acumulación a = {a} ---")

    limite_izq = None
    limite_der = None
    existe_limite = False
    conclusion_continuidad = ""

    if tipo == "removible":
        d1 = tramos["d1"]
        # f(x) = ((x - a)(x + d1)) / (x - a)
        # Para x != a, f(x) = x + d1
        valor_limite = a + d1
        limite_izq = valor_limite
        limite_der = valor_limite
        existe_limite = True

        pasos.append("Para el límite lateral izquierdo (x → a⁻):")
        pasos.append(f"  lim_(x→{a}⁻) ((x - {a})(x + {d1})) / (x - {a})")
        pasos.append(
            f"  Como x ≠ {a}, simplificamos el factor algebraico (x - {a}):")
        pasos.append(
            f"  lim_(x→{a}⁻) (x + {d1}) = {a} + {d1} = {valor_limite}")

        pasos.append("Para el límite lateral derecho (x → a⁺):")
        pasos.append(f"  lim_(x→{a}⁺) ((x - {a})(x + {d1})) / (x - {a})")
        pasos.append(f"  Simplificando el factor algebraico (x - {a}):")
        pasos.append(
            f"  lim_(x→{a}⁺) (x + {d1}) = {a} + {d1} = {valor_limite}")

        pasos.append(
            f"Resultado: Ambos límites laterales son iguales, por lo tanto el límite existe y es {valor_limite}.")
        pasos.append(
            f"Evaluación de la función: f({a}) no está definido debido a una división por cero.")
        conclusion_continuidad = f"Existe el límite general L = {valor_limite}, pero f({a}) no existe. Discontinuidad REMOVIBLE."

    elif tipo == "salto":
        d2 = tramos["d2"]
        d4 = tramos["d4"]

        limite_izq = a + d2
        limite_der = a + d4
        existe_limite = (limite_izq == limite_der)

        pasos.append(
            "Para el límite lateral izquierdo (x → a⁻), evaluamos en la rama izquierda (x < a):")
        pasos.append(f"  lim_(x→{a}⁻) (x + {d2}) = {a} + {d2} = {limite_izq}")

        pasos.append(
            "Para el límite lateral derecho (x → a⁺), evaluamos en la rama derecha (x ≥ a):")
        pasos.append(f"  lim_(x→{a}⁺) (x + {d4}) = {a} + {d4} = {limite_der}")

        if existe_limite:
            pasos.append(
                f"Resultado: Coincidentemente, los límites laterales son iguales a {limite_izq}.")
            pasos.append(
                f"Evaluación de la función: f({a}) = {a} + {d4} = {limite_der}.")
            conclusion_continuidad = f"Los límites laterales coinciden y f({a}) está definido. La función es CONTINUA en x = {a} para este RUT."
        else:
            pasos.append(
                f"Resultado: Los límites laterales son distintos ({limite_izq} ≠ {limite_der}), el límite general NO existe.")
            pasos.append(
                f"Evaluación de la función: f({a}) = {a} + {d4} = {limite_der}.")
            conclusion_continuidad = f"Límites laterales finitos pero distintos. Discontinuidad de SALTO FINITO (Magnitud del salto: {abs(limite_der - limite_izq)})."

    elif tipo == "infinita":
        numerador = tramos["numerador"]

        limite_izq = "-infinito"
        limite_der = "+infinito"
        existe_limite = False

        pasos.append("Para el límite lateral izquierdo (x → a⁻):")
        pasos.append(f"  lim_(x→{a}⁻) {numerador} / (x - {a})")
        pasos.append(
            f"  Cuando x se aproxima a {a} por la izquierda, el denominador (x - {a}) tiende a 0 a través de valores negativos (0⁻).")
        pasos.append(
            f"  Como el numerador ({numerador}) es positivo, la constante dividida por 0⁻ tiende a -∞.")

        pasos.append("Para el límite lateral derecho (x → a⁺):")
        pasos.append(f"  lim_(x→{a}⁺) {numerador} / (x - {a})")
        pasos.append(
            f"  Cuando x se aproxima a {a} por la derecha, el denominador (x - {a}) tiende a 0 a través de valores positivos (0⁺).")
        pasos.append(f"  La constante dividida por 0⁺ tiende a +∞.")

        conclusion_continuidad = "Los límites laterales tienden al infinito. Discontinuidad INFINITA (Existe una asíntota vertical en x = " + str(
            a) + ")."

    pasos.append(f"Conclusión de continuidad: {conclusion_continuidad}")

    return {
        "limite_izquierdo": limite_izq,
        "limite_derecho": limite_der,
        "existe_limite": existe_limite,
        "conclusion": conclusion_continuidad,
        "pasos": pasos
    }
