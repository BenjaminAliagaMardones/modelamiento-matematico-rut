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
from src.conicas.elementos import calcular_elementos
import re

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

# Cada elemento de la cónica tiene un color; el campo de texto y su marca en la
# gráfica comparten ese color para vincularlos visualmente (leyenda por color).
COLOR_ASINTOTA = "#9aa0a6"
COLORES_ELEMENTOS = {
    "Centro": "#ff5555",
    "Vértice(s)": "#ffd24d",
    "Foco(s)": "#5dd39e",
    "Eje mayor / transverso": "#ff9f40",
    "Eje menor / conjugado": "#4dd2ff",
    "Directriz": "#c77dff",
    "Asíntotas": COLOR_ASINTOTA,
    "Eje": COLOR_ASINTOTA,
}

TIPOS_DISCONTINUIDAD = ["Removible", "Salto", "Infinita", "Ninguna"]
OPCION_VACIA = "Selecciona…"

# (nombre, tipo_widget, placeholder)
CAMPOS_LIMITE = [
    ("Límite por la izquierda", "texto", "número, +infinito o -infinito"),
    ("Límite por la derecha", "texto", "número, +infinito o -infinito"),
    ("¿Existe el límite?", "sino", ""),
    ("Valor de f(a)", "texto", 'número, o "No def" si no existe'),
    ("¿Es continua?", "sino", ""),
    ("Tipo de discontinuidad", "opcion", ""),
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


def _normalizar_limite(texto: str) -> str:
    "Normaliza una respuesta del módulo de límites para comparar con flexibilidad."
    t = texto.strip().lower().replace(" ", "")
    t = t.replace("í", "i").replace("é", "e").replace("∞", "inf")
    if t in ("", "..."):
        return ""
    if t in ("si", "yes", "verdadero", "true", "existe"):
        return "si"
    if t in ("no", "false", "falso", "noexiste"):
        return "no"
    if t in ("-infinito", "-inf"):
        return "-inf"
    if t in ("+infinito", "+inf", "infinito", "inf"):
        return "+inf"
    if t in ("nodef", "nodefinido", "nodefinida", "indefinido"):
        return "nodef"
    if t in ("removible", "salto", "saltofinito", "infinita", "ninguna", "continua"):
        return "salto" if t == "saltofinito" else ("ninguna" if t == "continua" else t)
    try:
        return f"{float(t):.2f}"
    except ValueError:
        return t


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EID N°1 — Geometría Analítica desde el RUT")
        self.geometry("1120x760")
        self._entries_elementos: dict[str, ctk.CTkEntry] = {}
        self._filas_elementos: dict[str, ctk.CTkFrame] = {}
        self._widgets_limite: dict[str, object] = {}
        self._estado_limite: dict[str, ctk.CTkLabel] = {}
        self._campos_validados_correctos: set[str] = set()
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
        self._construir_tab_limites(self._tabs.tab("Límites"))

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
        self._lbl_ayuda_elementos = ctk.CTkLabel(
            derecha,
            text="Analiza un RUT para ver los elementos que corresponden a la figura.",
            font=("", 12), justify="left", wraplength=260,
        )
        self._lbl_ayuda_elementos.pack(anchor="w", padx=8, pady=(4, 8))
        for nombre in CAMPOS_ELEMENTOS:
            fila = ctk.CTkFrame(derecha, fg_color="transparent")
            color_elem = COLORES_ELEMENTOS.get(nombre, "#ffffff")
            ctk.CTkLabel(fila, text=nombre, width=170, anchor="w", text_color=color_elem).pack(side="left")
            entrada = ctk.CTkEntry(fila, placeholder_text="...")
            entrada.pack(side="left", fill="x", expand=True)
            self._entries_elementos[nombre] = entrada
            self._filas_elementos[nombre] = fila

        self._lbl_resultado_val = ctk.CTkLabel(derecha, text="", font=("", 13, "bold"))
        self._lbl_resultado_val.pack(pady=(12, 4))

        self._btn_validar = ctk.CTkButton(
            derecha, text="Validar Elementos", command=self._validar_elementos
        )
        self._btn_validar.pack(pady=(0, 12))

    def _analizar_elementos(self, datos_canonica, datos_grafica):
        tipo = datos_canonica["tipo"]
        geom_elementos = calcular_elementos(datos_canonica, tipo)
        self._elementos_correctos = geom_elementos["validacion"]
        self._geom_elementos = geom_elementos

    def _mostrar_campos_aplicables(self) -> None:
        "Muestra solo los campos que corresponden a la figura; oculta los demás."
        correctos = getattr(self, "_elementos_correctos", {})
        aplican = [c for c in CAMPOS_ELEMENTOS if correctos.get(c, "No aplica") != "No aplica"]
        for nombre in CAMPOS_ELEMENTOS:
            fila = self._filas_elementos[nombre]
            if nombre in aplican:
                fila.pack(fill="x", padx=8, pady=4, before=self._lbl_resultado_val)
            else:
                fila.pack_forget()
        if aplican:
            self._lbl_ayuda_elementos.configure(
                text="Completa los elementos de la figura y pulsa «Validar Elementos»."
            )
        else:
            self._lbl_ayuda_elementos.configure(
                text="Analiza un RUT para ver los elementos que corresponden a la figura."
            )

    def _validar_elementos(self):
        if not hasattr(self, "_elementos_correctos"):
            self._lbl_resultado_val.configure(
                text="Primero debes analizar un RUT válido.", text_color="#ff6b6b"
            )
            return

        def evaluar_numero(s: str) -> float | None:
            s = s.strip()
            if not s:
                return None
            if "/" in s:
                try:
                    num, den = s.split("/")
                    return float(num) / float(den)
                except ValueError:
                    return None
            try:
                return float(s)
            except ValueError:
                return None

        def parsear_coordenadas(texto: str) -> list[tuple[float, float]]:
            bloques = re.findall(r'\(([^)]+)\)', texto)
            coords = []
            for b in bloques:
                partes = b.split(",")
                if len(partes) == 2:
                    x = evaluar_numero(partes[0])
                    y = evaluar_numero(partes[1])
                    if x is not None and y is not None:
                        coords.append((x, y))
            return coords

        def parsear_directriz(texto: str) -> tuple[str, float] | None:
            t = texto.replace(" ", "").lower()
            if "=" not in t:
                return None
            var, valor_str = t.split("=", 1)
            if var in ("x", "y"):
                val = evaluar_numero(valor_str)
                if val is not None:
                    return (var, val)
            return None

        def es_valido_elemento(usuario: str, correcto_val) -> bool:
            usuario = usuario.strip()
            if not usuario:
                return False
            if correcto_val == "No aplica":
                return usuario.lower() in ("", "no aplica", "noaplica")

            # Coordenadas
            if isinstance(correcto_val, list) or (isinstance(correcto_val, str) and correcto_val.startswith("(")):
                reales_lista = correcto_val if isinstance(correcto_val, list) else [correcto_val]
                reales_coords = []
                for r_str in reales_lista:
                    coords_r = parsear_coordenadas(r_str)
                    if coords_r:
                        reales_coords.extend(coords_r)
                
                usuario_coords = parsear_coordenadas(usuario)
                if not reales_coords or not usuario_coords:
                    return False
                if len(usuario_coords) != len(reales_coords):
                    return False
                
                reales_restantes = list(reales_coords)
                for uc in usuario_coords:
                    encontrado = None
                    for rc in reales_restantes:
                        if abs(uc[0] - rc[0]) < 0.05 and abs(uc[1] - rc[1]) < 0.05:
                            encontrado = rc
                            break
                    if encontrado is not None:
                        reales_restantes.remove(encontrado)
                    else:
                        return False
                return len(reales_restantes) == 0

            # Directriz
            if isinstance(correcto_val, str) and (correcto_val.startswith("y=") or correcto_val.startswith("x=")):
                real_dir = parsear_directriz(correcto_val)
                user_dir = parsear_directriz(usuario)
                if real_dir is None or user_dir is None:
                    return False
                return real_dir[0] == user_dir[0] and abs(real_dir[1] - user_dir[1]) < 0.05

            # Ejes
            real_num = evaluar_numero(str(correcto_val))
            user_num = evaluar_numero(usuario)
            if real_num is not None and user_num is not None:
                return abs(real_num - user_num) < 0.05

            return usuario.replace(" ", "").lower() == str(correcto_val).replace(" ", "").lower()

        errores = 0
        campos_revisados = 0
        self._campos_validados_correctos = set()

        for campo in CAMPOS_ELEMENTOS:
            valor_real = self._elementos_correctos[campo]
            if valor_real == "No aplica":
                continue

            entrada_usuario = self._entries_elementos[campo].get()
            es_ok = es_valido_elemento(entrada_usuario, valor_real)

            if es_ok:
                self._entries_elementos[campo].configure(fg_color="#1e3a1e")
                self._campos_validados_correctos.add(campo)
            else:
                self._entries_elementos[campo].configure(fg_color="#3a1e1e")
                errores += 1
            campos_revisados += 1

        if campos_revisados == 0:
            self._lbl_resultado_val.configure(text="")
        elif errores == 0:
            self._lbl_resultado_val.configure(
                text="¡Todos los elementos son correctos! 🎉", text_color="#5dd39e"
            )
        else:
            self._lbl_resultado_val.configure(
                text=f"Revisión completada. Tienes {errores} observaciones.", text_color="#ff6b6b"
            )
        
        if hasattr(self, "_datos_grafica_actual"):
            self._dibujar(self._datos_grafica_actual)

    # --------------------------------------------------- pestaña de límites
    def _construir_tab_limites(self, padre) -> None:
        contenedor = ctk.CTkFrame(padre, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=8, pady=8)

        izquierda = ctk.CTkFrame(contenedor, fg_color="transparent")
        izquierda.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self._txt_tramos = ctk.CTkTextbox(izquierda, font=FUENTE_MONO, wrap="none")
        self._txt_tramos.pack(fill="both", expand=True)
        self._txt_tramos.configure(state="disabled")

        derecha = ctk.CTkScrollableFrame(
            contenedor, label_text="Tu análisis", width=340
        )
        derecha.pack(side="left", fill="y")

        for nombre, tipo, placeholder in CAMPOS_LIMITE:
            cabecera = ctk.CTkFrame(derecha, fg_color="transparent")
            cabecera.pack(fill="x", padx=8, pady=(8, 0))
            ctk.CTkLabel(cabecera, text=nombre, anchor="w").pack(side="left")
            estado = ctk.CTkLabel(cabecera, text="", width=20, font=("", 15, "bold"))
            estado.pack(side="right")
            self._estado_limite[nombre] = estado

            if tipo == "sino":
                widget = ctk.CTkSegmentedButton(derecha, values=["Sí", "No"])
                widget.set("")
            elif tipo == "opcion":
                widget = ctk.CTkOptionMenu(
                    derecha, values=[OPCION_VACIA] + TIPOS_DISCONTINUIDAD
                )
                widget.set(OPCION_VACIA)
            else:
                widget = ctk.CTkEntry(derecha, placeholder_text=placeholder)
            widget.pack(fill="x", padx=8, pady=(0, 2))
            self._widgets_limite[nombre] = widget

        ctk.CTkLabel(derecha, text="Justificación del comportamiento:", anchor="w").pack(
            anchor="w", padx=8, pady=(10, 2)
        )
        self._txt_justificacion = ctk.CTkTextbox(derecha, height=80, wrap="word")
        self._txt_justificacion.pack(fill="x", padx=8, pady=(0, 8))

        self._lbl_resultado_lim = ctk.CTkLabel(derecha, text="", font=("", 13, "bold"))
        self._lbl_resultado_lim.pack(pady=(8, 4))
        ctk.CTkButton(
            derecha, text="Validar análisis", command=self._validar_limite
        ).pack(pady=(0, 12))

    def _valor_limite(self, nombre: str) -> str:
        "Lee el valor ingresado en un widget de la pestaña de límites."
        widget = self._widgets_limite[nombre]
        valor = widget.get()
        return "" if valor == OPCION_VACIA else valor

    def _analizar_limite_correctos(self, res_tramo: dict, res_limites: dict) -> None:
        "Calcula las respuestas correctas para contrastar con lo que ingrese el alumno."
        tipo = res_tramo["tipo"]
        a = res_tramo["a"]
        tramos = res_tramo["tramos"]
        existe = res_limites["existe_limite"]

        if tipo == "salto":
            valor_fa = str(a + tramos["d4"])
            continua = "Sí" if existe else "No"
            disc = "Ninguna" if existe else "Salto"
        elif tipo == "removible":
            valor_fa = "No def"
            continua = "No"
            disc = "Removible"
        else:  # infinita
            valor_fa = "No def"
            continua = "No"
            disc = "Infinita"

        self._limite_correctos = {
            "Límite por la izquierda": str(res_limites["limite_izquierdo"]),
            "Límite por la derecha": str(res_limites["limite_derecho"]),
            "¿Existe el límite?": "Sí" if existe else "No",
            "Valor de f(a)": valor_fa,
            "¿Es continua?": continua,
            "Tipo de discontinuidad": disc,
        }

    def _reset_entries_limite(self) -> None:
        for nombre, tipo, _ in CAMPOS_LIMITE:
            widget = self._widgets_limite[nombre]
            if tipo == "sino":
                widget.set("")
            elif tipo == "opcion":
                widget.set(OPCION_VACIA)
            else:
                widget.delete(0, "end")
            self._estado_limite[nombre].configure(text="")
        if hasattr(self, "_txt_justificacion"):
            self._txt_justificacion.delete("1.0", "end")
        if hasattr(self, "_lbl_resultado_lim"):
            self._lbl_resultado_lim.configure(text="")

    def _validar_limite(self) -> None:
        if not hasattr(self, "_limite_correctos"):
            self._lbl_resultado_lim.configure(
                text="Primero analiza un RUT válido.", text_color="#ff6b6b"
            )
            return

        errores = 0
        for nombre, _tipo, _ph in CAMPOS_LIMITE:
            usuario = _normalizar_limite(self._valor_limite(nombre))
            real = _normalizar_limite(self._limite_correctos[nombre])
            if usuario and usuario == real:
                self._estado_limite[nombre].configure(text="✓", text_color="#5dd39e")
            else:
                self._estado_limite[nombre].configure(text="✗", text_color="#ff6b6b")
                errores += 1

        if errores == 0:
            self._lbl_resultado_lim.configure(
                text="¡Análisis correcto! 🎉", text_color="#5dd39e"
            )
        else:
            self._lbl_resultado_lim.configure(
                text=f"Tienes {errores} de {len(CAMPOS_LIMITE)} por corregir.",
                text_color="#ff6b6b",
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
        self._can_parametros_actual = can["parametros"]
        self._tipo_conica_actual = tipo
        self._datos_grafica_actual = datos
        self._dibujar(datos)
        self._analizar_elementos(can["parametros"], datos)
        self._mostrar_campos_aplicables()

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

            self._analizar_limite_correctos(res_tramo, res_limites)
            self._reset_entries_limite()

            datos_grafica = obtener_puntos_grafica(res_tramo)
            self._dibujar_tramos(datos_grafica)

        except Exception:
            self._set_text(self._txt_tramos, "")
            if hasattr(self, "_limite_correctos"):
                del self._limite_correctos
            self._reset_entries_limite()
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

        # Sin figura válida: oculta todos los campos y vuelve al texto de ayuda.
        if hasattr(self, "_elementos_correctos"):
            del self._elementos_correctos
        if hasattr(self, "_geom_elementos"):
            del self._geom_elementos
        if hasattr(self, "_campos_validados_correctos"):
            self._campos_validados_correctos.clear()
        if hasattr(self, "_datos_grafica_actual"):
            del self._datos_grafica_actual
        if hasattr(self, "_can_parametros_actual"):
            del self._can_parametros_actual
        if hasattr(self, "_tipo_conica_actual"):
            del self._tipo_conica_actual
        self._mostrar_campos_aplicables()

        if hasattr(self, "_widgets_limite") and self._widgets_limite:
            self._reset_entries_limite()
        if hasattr(self, "_limite_correctos"):
            del self._limite_correctos

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

        # centro / vértice base
        hx, ky = datos["centro"]
        if xmin <= hx <= xmax and ymin <= ky <= ymax:
            cx, cy = px(hx), py(ky)
            self._canvas.create_line(cx - 6, cy, cx + 6, cy, fill=COLOR_CENTRO, width=2)
            self._canvas.create_line(cx, cy - 6, cx, cy + 6, fill=COLOR_CENTRO, width=2)

        # Dibujar elementos matemáticos detallados de la cónica (ejes, directriz, focos, vértices, etc.)
        geom = getattr(self, "_geom_elementos", None)

        if geom:
            # 1. Segmentos (Ejes)
            for x1, y1, x2, y2, campo in geom.get("segmentos", []):
                color = COLORES_ELEMENTOS.get(campo, "#ffffff")
                self._canvas.create_line(px(x1), py(y1), px(x2), py(y2), fill=color, width=2, dash=(4, 4))

            # 2. Rectas (Directriz, Asíntotas, Eje de simetría)
            for clase, val_datos, campo in geom.get("rectas", []):
                color = COLORES_ELEMENTOS.get(campo, "#ffffff")
                if clase == "vertical":
                    x_pix = px(val_datos)
                    self._canvas.create_line(x_pix, 0, x_pix, LIENZO, fill=color, width=2, dash=(6, 4))
                elif clase == "horizontal":
                    y_pix = py(val_datos)
                    self._canvas.create_line(0, y_pix, LIENZO, y_pix, fill=color, width=2, dash=(6, 4))
                elif clase == "oblicua":
                    hx_c, ky_c, m = val_datos
                    y_left = ky_c + m * (xmin - hx_c)
                    y_right = ky_c + m * (xmax - hx_c)
                    self._canvas.create_line(px(xmin), py(y_left), px(xmax), py(y_right), fill=color, width=1.5, dash=(4, 4))

            # 3. Puntos (Centro, Vértices, Focos)
            for x, y, campo in geom.get("puntos", []):
                color = COLORES_ELEMENTOS.get(campo, "#ffffff")
                cx, cy = px(x), py(y)
                if campo == "Centro":
                    self._canvas.create_line(cx - 8, cy, cx + 8, cy, fill=color, width=2)
                    self._canvas.create_line(cx, cy - 8, cx, cy + 8, fill=color, width=2)
                    self._canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=color, outline="#ffffff")
                elif campo == "Vértice(s)":
                    self._canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill=color, outline="#ffffff", width=1.5)
                elif campo == "Foco(s)":
                    self._canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=color, outline="")
                    self._canvas.create_oval(cx - 6, cy - 6, cx + 6, cy + 6, fill="", outline=color, width=1.5)

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

        # asíntota vertical (caso discontinuidad infinita)
        ax = datos.get("asintota_x")
        if ax is not None and xmin <= ax <= xmax:
            x_pix = px(ax)
            for y0 in range(0, LIENZO, 12):
                self._canvas_tramos.create_line(
                    x_pix, y0, x_pix, y0 + 6, fill=COLOR_CENTRO, width=1
                )

        # curva
        for (x, y) in datos["puntos"]:
            cx, cy = px(x), py(y)
            self._canvas_tramos.create_oval(cx - 1, cy - 1, cx + 1, cy + 1, fill=COLOR_CURVA, outline="")

        # marcadores en el punto crítico: hueco (abierto) o extremo (cerrado)
        for (x, y, clase) in datos.get("marcadores", []):
            if not (xmin <= x <= xmax and ymin <= y <= ymax):
                continue
            cx, cy = px(x), py(y)
            if clase == "cerrado":
                self._canvas_tramos.create_oval(
                    cx - 5, cy - 5, cx + 5, cy + 5, fill=COLOR_CENTRO, outline=""
                )
            else:  # abierto: círculo hueco para representar el punto faltante
                self._canvas_tramos.create_oval(
                    cx - 5, cy - 5, cx + 5, cy + 5,
                    fill=COLOR_FONDO, outline=COLOR_CENTRO, width=2,
                )

def lanzar() -> None:
    App().mainloop()


if __name__ == "__main__":
    lanzar()
