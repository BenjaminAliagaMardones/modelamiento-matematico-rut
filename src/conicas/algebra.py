from __future__ import annotations


def _mcd(a: int, b: int) -> int:
    "Máximo común divisor por el algoritmo de Euclides."
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a if a else 1


class Fraccion:
    "Número racional exacto con numerador y denominador enteros."

    def __init__(self, numerador: int, denominador: int = 1):
        if denominador == 0:
            raise ZeroDivisionError("Denominador cero en Fraccion.")
        if denominador < 0:
            numerador, denominador = -numerador, -denominador
        divisor = _mcd(numerador, denominador)
        self.n = numerador // divisor
        self.d = denominador // divisor

    @staticmethod
    def _coaccionar(otro) -> "Fraccion":
        if isinstance(otro, Fraccion):
            return otro
        if isinstance(otro, int):
            return Fraccion(otro)
        raise TypeError(f"No se puede operar Fraccion con {type(otro).__name__}.")

    def __add__(self, otro) -> "Fraccion":
        o = self._coaccionar(otro)
        return Fraccion(self.n * o.d + o.n * self.d, self.d * o.d)

    __radd__ = __add__

    def __sub__(self, otro) -> "Fraccion":
        o = self._coaccionar(otro)
        return Fraccion(self.n * o.d - o.n * self.d, self.d * o.d)

    def __rsub__(self, otro) -> "Fraccion":
        return self._coaccionar(otro).__sub__(self)

    def __mul__(self, otro) -> "Fraccion":
        o = self._coaccionar(otro)
        return Fraccion(self.n * o.n, self.d * o.d)

    __rmul__ = __mul__

    def __truediv__(self, otro) -> "Fraccion":
        o = self._coaccionar(otro)
        if o.n == 0:
            raise ZeroDivisionError("División por cero en Fraccion.")
        return Fraccion(self.n * o.d, self.d * o.n)

    def __rtruediv__(self, otro) -> "Fraccion":
        return self._coaccionar(otro).__truediv__(self)

    def __neg__(self) -> "Fraccion":
        return Fraccion(-self.n, self.d)

    def __eq__(self, otro) -> bool:
        try:
            o = self._coaccionar(otro)
        except TypeError:
            return NotImplemented
        return self.n == o.n and self.d == o.d

    def __hash__(self) -> int:
        return hash((self.n, self.d))

    def signo(self) -> int:
        "Devuelve -1, 0 o 1 según el signo."
        if self.n > 0:
            return 1
        if self.n < 0:
            return -1
        return 0

    def es_cero(self) -> bool:
        return self.n == 0

    def a_decimal(self) -> float:
        return self.n / self.d

    def __str__(self) -> str:
        if self.d == 1:
            return str(self.n)
        return f"{self.n}/{self.d}"

    def __repr__(self) -> str:
        return f"Fraccion({self.n}, {self.d})"


def raiz_cuadrada(x: float, tol: float = 1e-12, max_iter: int = 100) -> float:
    "Raíz cuadrada no negativa por el método de Newton-Raphson."
    if x < 0:
        raise ValueError("No existe raíz cuadrada real de un número negativo.")
    if x == 0:
        return 0.0
    estimado = x if x >= 1 else 1.0
    for _ in range(max_iter):
        siguiente = (estimado + x / estimado) / 2
        if abs(siguiente - estimado) < tol:
            return siguiente
        estimado = siguiente
    return estimado


def fmt_dec(valor: float, decimales: int = 4) -> str:
    "Formatea un decimal sin ceros sobrantes."
    if valor == int(valor):
        return str(int(valor))
    s = f"{valor:.{decimales}f}".rstrip("0").rstrip(".")
    return s


def fmt_frac_dec(fr: Fraccion, decimales: int = 4) -> str:
    "Muestra una fracción exacta y su decimal aproximado si difieren."
    if fr.d == 1:
        return str(fr.n)
    return f"{fr} = {fmt_dec(fr.a_decimal(), decimales)}"
