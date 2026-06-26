"Interfaz CustomTkinter para la mitad de geometría analítica del proyecto."

from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from src.conicas.canonica import canonica_a_general, general_a_canonica
from src.conicas.clasificador import clasificar
from src.conicas.constructor import construir_ecuacion
from src.conicas.grafica import puntos_conica
from src.rut.validador import validar_rut
from src.conicas.algebra import raiz_cuadrada

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FUENTE_MONO = ("Menlo", 13)
LIENZO = 560
COLOR_FONDO = "#1b1b1b"
COLOR_GRILLA = "#333333"
COLOR_EJE = "#888888"
COLOR_CURVA = "#4da6ff"
COLOR_CENTRO = "#ff5555"

CAMPOS_ELEMENTOS = [
    "Centro",
    "Vértice(s)",
    "Foco(s)",
    "Eje mayor / transverso",
    "Eje menor / conjugado",
    "Directriz",
]


def _texto_validacion(rut: dict) -> str:
    t = rut["traza"]
    lineas = [
        f"RUT {rut['cuerpo']}-{rut['dv_ingresado']}",
        "",
        "Multiplicamos cada dígito (de derecha a izquierda) por 2,3,4,5,6,7 y repetimos:",
        "",
        f"  {'Pos':>3} | {'Díg':>3} | {'Mult':>4} | {'Producto':>8}",
        f"  {'-'*3}-+-{'-'*3}-+-{'-'*4}-+-{'-'*8}",
    ]
    for f in t["filas"]:
        lineas.append(
            f"  {f['posicion']:>3} | {f['digito']:>3} | {f['multiplicador']:>4} | {f['producto']:>8}"
        )
    lineas += [
        "",
        f"Suma = {t['suma_total']};  resto = {t['suma_total']} mod 11 = {t['resto']}",
        t["regla_aplicada"],
        "",
        f"DV calculado: {rut['dv_calculado']}   ·   DV ingresado: {rut['dv_ingresado']}",
        "El RUT es válido." if rut["es_valido"] else "El RUT no es válido.",
    ]
    return "\n".join(lineas)


def _paso_agradable(span: float) -> float:
    "Espaciado de grilla 'redondo' para ~10 divisiones, sin usar math."
    raw = span / 10.0 if span > 0 else 1.0
    p = 1.0
    while raw >= 10:
        raw /= 10
        p *= 10
    while raw < 1:
        raw *= 10
        p /= 10
    if raw < 1.5:
        m = 1
    elif raw < 3:
        m = 2
    elif raw < 7:
        m = 5
    else:
        m = 10
    return m * p


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EID N°1 — Geometría Analítica desde el RUT")
        self.geometry("1120x760")
        self._entries_elementos: dict[str, ctk.CTkEntry] = {}
        self._construir()

    # ------------------------------------------------------------------ UI
    def _construir(self) -> None:
        barra = ctk.CTkFrame(self)
        barra.pack(fill="x", padx=12, pady=(12, 6))

        ctk.CTkLabel(barra, text="RUT:", font=("", 14)).pack(side="left", padx=(12, 6))
        self._entry_rut = ctk.CTkEntry(barra, width=200, placeholder_text="12345678-5")
        self._entry_rut.pack(side="left", pady=10)
        self._entry_rut.bind("<Return>", lambda _e: self._analizar())
        ctk.CTkButton(barra, text="Analizar", command=self._analizar).pack(
            side="left", padx=10
        )
        self._estado = ctk.CTkLabel(barra, text="", font=("", 13))
        self._estado.pack(side="left", padx=10)

        self._tabs = ctk.CTkTabview(self)
        self._tabs.pack(fill="both", expand=True, padx=12, pady=(6, 12))
        for nombre in ("RUT", "Ecuación general", "Clasificación / Canónica", "Gráfica", "Límites","Gráfica Tramos"):
            self._tabs.add(nombre)

        self._txt_rut = self._textbox(self._tabs.tab("RUT"))
        self._txt_ecuacion = self._textbox(self._tabs.tab("Ecuación general"))
        self._txt_canonica = self._textbox(self._tabs.tab("Clasificación / Canónica"))
        self._construir_tab_grafica(self._tabs.tab("Gráfica"))
        self._txt_tramos = self._textbox(self._tabs.tab("Límites"))

    def _textbox(self, padre) -> ctk.CTkTextbox:
        caja = ctk.CTkTextbox(padre, font=FUENTE_MONO, wrap="none")
        caja.pack(fill="both", expand=True, padx=8, pady=8)
        caja.configure(state="disabled")
        return caja

    def _construir_tab_grafica(self, padre) -> None:
        contenedor = ctk.CTkFrame(padre, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=8, pady=8)

        izquierda = ctk.CTkFrame(contenedor)
        izquierda.pack(side="left", padx=(0, 8))
        self._lbl_grafica = ctk.CTkLabel(izquierda, text="Ingrese un RUT y presione Analizar.", font=("", 13))
        self._lbl_grafica.pack(pady=(8, 4))
        self._canvas = tk.Canvas(
            izquierda, width=LIENZO, height=LIENZO, bg=COLOR_FONDO, highlightthickness=0
        )
        self._canvas.pack(padx=10, pady=(0, 10))

        derecha = ctk.CTkScrollableFrame(contenedor, label_text="Elementos de la cónica")
        derecha.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(
            derecha,
            text="",
            font=("", 12), justify="left",
        ).pack(anchor="w", padx=8, pady=(4, 8))
        for nombre in CAMPOS_ELEMENTOS:
            fila = ctk.CTkFrame(derecha, fg_color="transparent")
            fila.pack(fill="x", padx=8, pady=4)
            ctk.CTkLabel(fila, text=nombre, width=170, anchor="w").pack(side="left")
            entrada = ctk.CTkEntry(fila, placeholder_text="...")
            entrada.pack(side="left", fill="x", expand=True)
            self._entries_elementos[nombre] = entrada
        
        self._lbl_resultado_val = ctk.CTkLabel(derecha, text="", font=("", 13, "bold"))
        self._lbl_resultado_val.pack(pady=(12, 4))

        self._btn_validar = ctk.CTkButton(
            derecha, text="Validar Elementos", command=self._validar_elementos
        )
        self._btn_validar.pack(pady=(0, 12))

    def _analizar_elementos(self, datos_canonica, datos_grafica):
            from src.conicas.algebra import fmt_dec
            
            tipo = datos_canonica["tipo"]
            h = datos_canonica["h"]
            k = datos_canonica["k"]
            
            self._elementos_correctos = {campo: "No aplica" for campo in CAMPOS_ELEMENTOS}
            
            if tipo == "degenerada":
                return

            if tipo in ("circunferencia", "elipse", "hipérbola"):
                self._elementos_correctos["Centro"] = f"({h},{k})"

            if tipo == "elipse":
                a = datos_canonica.get("a", 0.0)
                b = datos_canonica.get("b", 0.0)
                self._elementos_correctos["Eje mayor / transverso"] = fmt_dec(2 * a)
                self._elementos_correctos["Eje menor / conjugado"] = fmt_dec(2 * b)
                self._elementos_correctos["Vértice(s)"] = f"a={fmt_dec(a)}"
                self._elementos_correctos["Foco(s)"] = "Ver ecuación canónica"

            elif tipo == "hipérbola":
                dx_abs = raiz_cuadrada(abs(datos_canonica["denom_x"].a_decimal()))
                dy_abs = raiz_cuadrada(abs(datos_canonica["denom_y"].a_decimal()))
                self._elementos_correctos["Eje mayor / transverso"] = fmt_dec(2 * dx_abs)
                self._elementos_correctos["Eje menor / conjugado"] = fmt_dec(2 * dy_abs)
                self._elementos_correctos["Vértice(s)"] = "Ver desarrollo"

            elif tipo == "parábola" and not datos_canonica.get("degenerada"):
                # En la parábola el (h, k) es el Vértice, no el Centro
                self._elementos_correctos["Centro"] = "No aplica"
                self._elementos_correctos["Vértice(s)"] = f"({h},{k})"
                
                p = datos_canonica["p"]
                factor = datos_canonica["factor"]
                self._elementos_correctos["Eje mayor / transverso"] = "No aplica" # Parábola no tiene ambos ejes
                self._elementos_correctos["Eje menor / conjugado"] = "No aplica"
                
                if datos_canonica["orientacion"] == "vertical":
                    # Foco (h, k + p), Directriz y = k - p
                    foco_y = k.a_decimal() + p.a_decimal()
                    dir_y = k.a_decimal() - p.a_decimal()
                    self._elementos_correctos["Foco(s)"] = f"({h},{fmt_dec(foco_y)})"
                    self._elementos_correctos["Directriz"] = f"y={fmt_dec(dir_y)}"
                else:
                    # Horizontal: Foco (h + p, k), Directriz x = h - p
                    foco_x = h.a_decimal() + p.a_decimal()
                    dir_x = h.a_decimal() - p.a_decimal()
                    self._elementos_correctos["Foco(s)"] = f"({fmt_dec(foco_x)},{k})"
                    self._elementos_correctos["Directriz"] = f"x={fmt_dec(dir_x)}"

    def _validar_elementos(self):
        # Si aún no se ha ejecutado un análisis de RUT válido
        if not hasattr(self, "_elementos_correctos"):
            self._lbl_resultado_val.configure(
                text="Primero debes analizar un RUT válido.", text_color="#ff6b6b"
            )
            return

        errores = 0
        campos_revisados = 0

        def normalizar_y_evaluar(texto: str) -> str:
            """Limpia espacios y resuelve fracciones simples (ej: '1/2' -> '0.5') 
            para poder comparar valores numéricos con flexibilidad."""
            t = texto.replace(" ", "").lower()
            if not t or t == "..." or t == "noaplica":
                return "noaplica"
            # Intentar parsear si es un formato de coordenada (x,y)
            if t.startswith("(") and t.endswith(")"):
                partes = t[1:-1].split(",")
                if len(partes) == 2:
                    return f"({normalizar_y_evaluar(partes[0])},{normalizar_y_evaluar(partes[1])})"
            # Intentar resolver si contiene una barra de división (Fracción)
            if "/" in t and not t.startswith("x=") and not t.startswith("y="):
                try:
                    num, den = t.split("/")
                    return f"{float(num)/float(den):.2f}"
                except ValueError:
                    pass
            # Intentar convertir un número plano a float estándar
            try:
                return f"{float(t):.2f}"
            except ValueError:
                return t

        for campo in CAMPOS_ELEMENTOS:
            entrada_usuario = self._entries_elementos[campo].get()
            valor_real = self._elementos_correctos[campo]

            usuario_norm = normalizar_y_evaluar(entrada_usuario)
            real_norm = normalizar_y_evaluar(str(valor_real))

            if usuario_norm == "noaplica" and real_norm != "noaplica":
                self._entries_elementos[campo].configure(fg_color="#3a2f1d")
                errores += 1
            elif usuario_norm == real_norm:
                self._entries_elementos[campo].configure(fg_color="#1e3a1e")
            else:
                self._entries_elementos[campo].configure(fg_color="#3a1e1e")
                errores += 1
            campos_revisados += 1

        if errores == 0:
            self._lbl_resultado_val.configure(
                text="¡Todos los elementos son correctos! 🎉", text_color="#5dd39e"
            )
        else:
            self._lbl_resultado_val.configure(
                text=f"Revisión completada. Tienes {errores} observaciones.", text_color="#ff6b6b"
            )
        


    # ------------------------------------------------------------- lógica
    def _set_text(self, caja: ctk.CTkTextbox, texto: str) -> None:
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        caja.insert("1.0", texto)
        caja.configure(state="disabled")

    def _analizar(self) -> None:
        entrada = self._entry_rut.get()
        try:
            rut = validar_rut(entrada)
        except ValueError as err:
            self._estado.configure(text=str(err), text_color="#ff6b6b")
            self._set_text(self._txt_rut, f"Entrada inválida:\n{err}")
            self._limpiar_resultados()
            return

        self._set_text(self._txt_rut, _texto_validacion(rut))

        if not rut["es_valido"]:
            self._estado.configure(
                text=f"RUT inválido (DV esperado: {rut['dv_calculado']})",
                text_color="#ff6b6b",
            )
            self._limpiar_resultados()
            return

        res = construir_ecuacion(entrada)
        coef_frac = res["coeficientes_frac"]
        clasi = clasificar(coef_frac)
        tipo = clasi["tipo"]
        can = general_a_canonica(coef_frac, tipo)
        inv = canonica_a_general(can["parametros"], tipo)

        self._estado.configure(
            text=f"RUT válido  ·  {tipo.upper()}", text_color="#5dd39e"
        )

        self._set_text(self._txt_ecuacion, "\n".join(res["pasos"]))

        bloque = clasi["pasos"]
        bloque += ["", "De la ecuación general a la forma canónica:"] + can["pasos"]
        bloque += ["", "Y de vuelta, de la canónica a la general:"] + inv["pasos"]
        self._set_text(self._txt_canonica, "\n".join(bloque))

        self._lbl_grafica.configure(
            text=f"{tipo.upper()}   ·   {res['ecuacion']}\nCanónica:  {can['forma_canonica']}"
        )
        datos = puntos_conica(res["coeficientes"], can["parametros"], tipo)
        self._dibujar(datos)
        self._analizar_elementos(can["parametros"], datos)

        try:
            from src.tramos.constructor import construir_funcion
            from src.tramos.limites import analizar_limites
            from src.tramos.tablas import generar_tabla_valores
            from src.tramos.grafica import obtener_puntos_grafica
            
            res_tramo = construir_funcion(entrada)
            
            res_limites = analizar_limites(res_tramo)
            
            res_tabla = generar_tabla_valores(res_tramo)
            
            bloque_final = res_tramo["pasos"]
            bloque_final += ["", "="*60]
            bloque_final += res_limites["pasos"]
            bloque_final += ["", "="*60]
            bloque_final += res_tabla["pasos"]
            
            self._set_text(self._txt_tramos, "\n".join(bloque_final))
            
            datos_grafica = obtener_puntos_grafica(res_tramo)
            self._dibujar_tramos(datos_grafica)
            
        except Exception:
            self._set_text(self._txt_tramos, "")
    def _limpiar_resultados(self) -> None:
        for caja in (self._txt_ecuacion, self._txt_canonica, self._txt_tramos):
            self._set_text(caja, "")

        self._canvas.delete("all")

        if hasattr(self, "_canvas_tramos"):
            self._canvas_tramos.delete("all")
        self._lbl_grafica.configure(text="—")
        
        if hasattr(self, "_lbl_tramos_grafica"):
            self._lbl_tramos_grafica.configure(text="—")
        
        if hasattr(self, "_lbl_resultado_val"):
            self._lbl_resultado_val.configure(text="")
        
        # Restablece las entradas de texto a su estado base
        for entrada in self._entries_elementos.values():
            entrada.delete(0, "end")
            entrada.configure(fg_color=("#F9F9FA", "#343638"))

    # ------------------------------------------------------------- dibujo
    def _dibujar(self, datos: dict) -> None:
        self._canvas.delete("all")
        xmin, xmax, ymin, ymax = datos["ventana"]
        if xmax - xmin <= 0 or ymax - ymin <= 0:
            return
        sx = LIENZO / (xmax - xmin)
        sy = LIENZO / (ymax - ymin)

        def px(x: float) -> float:
            return (x - xmin) * sx

        def py(y: float) -> float:
            return LIENZO - (y - ymin) * sy

        # grilla
        paso = _paso_agradable(xmax - xmin)
        k = int(xmin / paso) - 1
        while k * paso <= xmax + paso:
            gx = k * paso
            if xmin <= gx <= xmax:
                self._canvas.create_line(px(gx), 0, px(gx), LIENZO, fill=COLOR_GRILLA)
            gy = k * paso
            if ymin <= gy <= ymax:
                self._canvas.create_line(0, py(gy), LIENZO, py(gy), fill=COLOR_GRILLA)
            k += 1

        # ejes
        if ymin <= 0 <= ymax:
            self._canvas.create_line(0, py(0), LIENZO, py(0), fill=COLOR_EJE, width=2)
        if xmin <= 0 <= xmax:
            self._canvas.create_line(px(0), 0, px(0), LIENZO, fill=COLOR_EJE, width=2)

        # curva (puntos densos calculados a mano)
        for (x, y) in datos["puntos"]:
            cx, cy = px(x), py(y)
            self._canvas.create_oval(cx - 1, cy - 1, cx + 1, cy + 1, fill=COLOR_CURVA, outline="")

        # centro / vértice
        hx, ky = datos["centro"]
        if xmin <= hx <= xmax and ymin <= ky <= ymax:
            cx, cy = px(hx), py(ky)
            self._canvas.create_line(cx - 6, cy, cx + 6, cy, fill=COLOR_CENTRO, width=2)
            self._canvas.create_line(cx, cy - 6, cx, cy + 6, fill=COLOR_CENTRO, width=2)

# ------------------------------------------------------- dibujo tramos
    def _dibujar_tramos(self, datos: dict) -> None:
        # Inicializa los componentes en la pestaña "Gráfica Tramos" de forma aislada
        if not hasattr(self, "_canvas_tramos"):
            padre = self._tabs.tab("Gráfica Tramos")
            
            self._lbl_tramos_grafica = ctk.CTkLabel(padre, text="Visualización Función por Tramos", font=("", 13))
            self._lbl_tramos_grafica.pack(pady=(8, 4))
            
            self._canvas_tramos = tk.Canvas(
                padre, width=LIENZO, height=LIENZO, bg=COLOR_FONDO, highlightthickness=0
            )
            self._canvas_tramos.pack(padx=10, pady=(0, 10))

        self._canvas_tramos.delete("all")
        xmin, xmax, ymin, ymax = datos["ventana"]
        if xmax - xmin <= 0 or ymax - ymin <= 0:
            return
        sx = LIENZO / (xmax - xmin)
        sy = LIENZO / (ymax - ymin)

        def px(x: float) -> float:
            return (x - xmin) * sx

        def py(y: float) -> float:
            return LIENZO - (y - ymin) * sy

        # grilla
        paso = _paso_agradable(xmax - xmin)
        k = int(xmin / paso) - 1
        while k * paso <= xmax + paso:
            gx = k * paso
            if xmin <= gx <= xmax:
                self._canvas_tramos.create_line(px(gx), 0, px(gx), LIENZO, fill=COLOR_GRILLA)
            gy = k * paso
            if ymin <= gy <= ymax:
                self._canvas_tramos.create_line(0, py(gy), LIENZO, py(gy), fill=COLOR_GRILLA)
            k += 1

        # ejes
        if ymin <= 0 <= ymax:
            self._canvas_tramos.create_line(0, py(0), LIENZO, py(0), fill=COLOR_EJE, width=2)
        if xmin <= 0 <= xmax:
            self._canvas_tramos.create_line(px(0), 0, px(0), LIENZO, fill=COLOR_EJE, width=2)

        # curva
        for (x, y) in datos["puntos"]:
            cx, cy = px(x), py(y)
            self._canvas_tramos.create_oval(cx - 1, cy - 1, cx + 1, cy + 1, fill=COLOR_CURVA, outline="")

        # punto crítico de acumulación
        hx, ky = datos["punto_a"]
        if xmin <= hx <= xmax and ymin <= ky <= ymax:
            cx, cy = px(hx), py(ky)
            self._canvas_tramos.create_line(cx - 6, cy, cx + 6, cy, fill=COLOR_CENTRO, width=2)
            self._canvas_tramos.create_line(cx, cy - 6, cx, cy + 6, fill=COLOR_CENTRO, width=2)

def lanzar() -> None:
    App().mainloop()


if __name__ == "__main__":
    lanzar()
