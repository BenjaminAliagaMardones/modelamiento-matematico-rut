"Validación de RUT chileno mediante el algoritmo oficial del módulo 11."


from __future__ import annotations

from src.rut.parser import parsear_rut


def calcular_dv(cuerpo: str) -> tuple[str, dict]:
    "Calcula el dígito verificador esperado para un cuerpo de RUT."
    filas = []
    suma_total = 0
    multiplicador = 2

    for i in range(len(cuerpo) - 1, -1, -1):
        digito = int(cuerpo[i])
        producto = digito * multiplicador
        suma_total += producto
        filas.append({
            "posicion": i + 1,
            "digito": digito,
            "multiplicador": multiplicador,
            "producto": producto,
        })
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2

    resto = suma_total % 11
    resta = 11 - resto

    if resta == 11:
        dv_esperado = "0"
        regla = "11 - resto = 11  →  DV = 0"
    elif resta == 10:
        dv_esperado = "K"
        regla = "11 - resto = 10  →  DV = K"
    else:
        dv_esperado = str(resta)
        regla = f"11 - resto = {resta}  →  DV = {resta}"

    traza = {
        "filas": filas,
        "suma_total": suma_total,
        "resto": resto,
        "resta": resta,
        "regla_aplicada": regla,
    }
    return dv_esperado, traza


def _extraer_digitos(cuerpo: str) -> dict:
    "Devuelve d1..d8 a partir del cuerpo"
    cuerpo_8 = cuerpo.zfill(8)
    return {f"d{i + 1}": int(cuerpo_8[i]) for i in range(8)}


def _valor_v(dv: str) -> int:
    "Variable auxiliar v asociada al DV"
    if dv == "K":
        return 10
    if dv == "0":
        return 11
    return int(dv)


def validar_rut(entrada: str) -> dict:
    "Orquesta parseo, cálculo del DV y armado del resultado completo."
    cuerpo, dv_ingresado = parsear_rut(entrada)
    dv_calculado, traza = calcular_dv(cuerpo)
    es_valido = dv_calculado == dv_ingresado

    return {
        "cuerpo": cuerpo,
        "dv_ingresado": dv_ingresado,
        "dv_calculado": dv_calculado,
        "es_valido": es_valido,
        "traza": traza,
        "digitos": _extraer_digitos(cuerpo),
        "v": _valor_v(dv_ingresado),
    }
