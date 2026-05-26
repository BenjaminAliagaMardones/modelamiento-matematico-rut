"Normalización del RUT ingresado."

from __future__ import annotations


def parsear_rut(entrada: str) -> tuple[str, str]:
    "Limpia y separa el RUT en (cuerpo, dv)."
    
    if entrada is None:
        raise ValueError("Debe ingresar un RUT.")

    texto = entrada.strip()
    if texto == "":
        raise ValueError("Debe ingresar un RUT.")

    if "." in texto:
        raise ValueError("No use puntos. Formato esperado: 12345678-9")

    if texto.count("-") != 1:
        raise ValueError("Falta el guion separador. Formato esperado: 12345678-9")

    cuerpo, dv = texto.split("-")
    cuerpo = cuerpo.strip()
    dv = dv.strip().upper()

    if cuerpo == "" or dv == "":
        raise ValueError("Cuerpo o dígito verificador vacío.")

    if not cuerpo.isdigit():
        raise ValueError("El cuerpo del RUT solo puede contener dígitos.")

    if len(cuerpo) < 7 or len(cuerpo) > 8:
        raise ValueError("El cuerpo del RUT debe tener 7 u 8 dígitos.")

    if dv != "K" and not (len(dv) == 1 and dv.isdigit()):
        raise ValueError("El dígito verificador debe ser 0-9 o K.")

    return cuerpo, dv
