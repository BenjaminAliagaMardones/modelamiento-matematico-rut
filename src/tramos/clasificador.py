# Este archivo contiene la lógica relacionada con seleccionar el caso de función en base
# a d8.


from __future__ import annotations


def clasificar_tramo(d8: int) -> dict:
    residuo = d8 % 3
    pasos = [
        f"Se evalúa el octavo dígito del cuerpo del RUT: d8 = {d8}.",
        f"Calculamos el residuo de la división por 3: {d8} % 3 = {residuo}."
    ]

    if residuo == 0:
        tipo = "removible"
        razon = f"El dígito d8 ({d8}) es múltiplo de 3 (residuo 0). Se generará el caso de discontinuidad removible."
    elif residuo == 1:
        tipo = "salto"
        razon = f"El dígito d8 ({d8}) deja residuo 1 al dividirse por 3. Se generará el caso de discontinuidad de salto."
    else:  # residuo == 2
        tipo = "infinita"
        razon = f"El dígito d8 ({d8}) deja residuo 2 al dividirse por 3. Se generará el caso de discontinuidad infinita."

    pasos.append(razon)

    return {
        "tipo": tipo,
        "razon": razon,
        "pasos": pasos
    }
