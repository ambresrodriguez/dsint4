"""
Calculadora bonita con tkinter.

- Ratón: pulsa los botones.
- Teclado: números, + - * /, Enter (=), Backspace (borrar), Escape (limpiar).
"""

import ast
import math
import operator as op
import tkinter as tk

# ----- Paleta (estilo "Catppuccin Mocha") -----
BG = "#1e1e2e"
PANTALLA_BG = "#181825"
TEXTO = "#cdd6f4"
SUBTEXTO = "#7f849c"

NUM_BG, NUM_HOVER = "#313244", "#45475a"
OP_BG, OP_HOVER = "#fab387", "#ffc9a3"
FN_BG, FN_HOVER = "#89b4fa", "#b4d0fb"
IGUAL_BG, IGUAL_HOVER = "#a6e3a1", "#c5f0c1"
OSCURO = "#1e1e2e"

SIMBOLO_A_OPERADOR = {"×": "*", "÷": "/", "−": "-", "+": "+"}
OPERADORES_VALIDOS = {ast.Add: op.add, ast.Sub: op.sub,
                      ast.Mult: op.mul, ast.Div: op.truediv}
UNARIOS_VALIDOS = {ast.USub: op.neg, ast.UAdd: op.pos}


def evaluar(expresion):
    """Evalúa una expresión aritmética de forma segura (sin usar eval)."""
    def _ev(nodo):
        if isinstance(nodo, ast.Expression):
            return _ev(nodo.body)
        if isinstance(nodo, ast.Constant) and isinstance(nodo.value, (int, float)):
            return nodo.value
        if isinstance(nodo, ast.BinOp) and type(nodo.op) in OPERADORES_VALIDOS:
            return OPERADORES_VALIDOS[type(nodo.op)](_ev(nodo.left), _ev(nodo.right))
        if isinstance(nodo, ast.UnaryOp) and type(nodo.op) in UNARIOS_VALIDOS:
            return UNARIOS_VALIDOS[type(nodo.op)](_ev(nodo.operand))
        raise ValueError("Expresión no válida")
    return _ev(ast.parse(expresion, mode="eval"))


def formatear(valor):
    valor = float(valor)
    if valor.is_integer():
        return str(int(valor))
    return f"{valor:.10g}"


class Calculadora(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora")
        self.configure(bg=BG, padx=16, pady=16)
        self.resizable(False, False)

        self.expresion = ""        # texto que se muestra y se evalúa
        self.historial = ""        # última operación completada
        self.recien_calculado = False

        self._crear_pantalla()
        self._crear_botones()
        self.bind("<Key>", self._tecla)
        self._refrescar()

    # ----- Interfaz -----

    def _crear_pantalla(self):
        marco = tk.Frame(self, bg=PANTALLA_BG, padx=18, pady=14)
        marco.pack(fill="x", pady=(0, 14))

        self.lbl_historial = tk.Label(
            marco, text="", bg=PANTALLA_BG, fg=SUBTEXTO,
            font=("Helvetica", 12), anchor="e")
        self.lbl_historial.pack(fill="x")

        self.lbl_principal = tk.Label(
            marco, text="0", bg=PANTALLA_BG, fg=TEXTO,
            font=("Helvetica", 44, "bold"), anchor="e")
        self.lbl_principal.pack(fill="x")

    def _crear_botones(self):
        self.rejilla = tk.Frame(self, bg=BG)
        self.rejilla.pack()

        for c in range(4):
            self.rejilla.grid_columnconfigure(c, weight=1, minsize=82)
        for r in range(5):
            self.rejilla.grid_rowconfigure(r, weight=1, minsize=70)

        # (texto, fila, columna, columnas ocupadas, tipo, acción)
        diseño = [
            ("C", 0, 0, 1, "fn", lambda: self._pulsar("C")),
            ("⌫", 0, 1, 1, "fn", lambda: self._pulsar("⌫")),
            ("÷", 0, 2, 1, "op", lambda: self._pulsar("÷")),
            ("×", 0, 3, 1, "op", lambda: self._pulsar("×")),

            ("7", 1, 0, 1, "num", lambda: self._pulsar("7")),
            ("8", 1, 1, 1, "num", lambda: self._pulsar("8")),
            ("9", 1, 2, 1, "num", lambda: self._pulsar("9")),
            ("−", 1, 3, 1, "op", lambda: self._pulsar("−")),

            ("4", 2, 0, 1, "num", lambda: self._pulsar("4")),
            ("5", 2, 1, 1, "num", lambda: self._pulsar("5")),
            ("6", 2, 2, 1, "num", lambda: self._pulsar("6")),
            ("+", 2, 3, 1, "op", lambda: self._pulsar("+")),

            ("1", 3, 0, 1, "num", lambda: self._pulsar("1")),
            ("2", 3, 1, 1, "num", lambda: self._pulsar("2")),
            ("3", 3, 2, 1, "num", lambda: self._pulsar("3")),
            ("=", 3, 3, 1, "igual", lambda: self._pulsar("=")),

            ("0", 4, 0, 2, "num", lambda: self._pulsar("0")),
            (".", 4, 2, 1, "num", lambda: self._pulsar(".")),
        ]
        for texto, fila, col, span, tipo, accion in diseño:
            self._boton(texto, fila, col, span, tipo, accion)

    def _boton(self, texto, fila, col, span, tipo, accion):
        colores = {
            "num": (NUM_BG, NUM_HOVER, TEXTO),
            "op": (OP_BG, OP_HOVER, OSCURO),
            "fn": (FN_BG, FN_HOVER, OSCURO),
            "igual": (IGUAL_BG, IGUAL_HOVER, OSCURO),
        }
        fondo, hover, letra = colores[tipo]
        lbl = tk.Label(
            self.rejilla, text=texto, bg=fondo, fg=letra,
            font=("Helvetica", 20, "bold"), cursor="hand2")
        lbl.grid(row=fila, column=col, columnspan=span,
                 sticky="nsew", padx=6, pady=6, ipady=10)
        lbl.bind("<Enter>", lambda _e: lbl.config(bg=hover))
        lbl.bind("<Leave>", lambda _e: lbl.config(bg=fondo))
        lbl.bind("<Button-1>", lambda _e: accion())

    # ----- Lógica -----

    def _pulsar(self, tecla):
        if tecla == "C":
            self.expresion, self.historial = "", ""
            self.recien_calculado = False
        elif tecla == "⌫":
            self.expresion = self.expresion[:-1]
        elif tecla == "=":
            self._calcular()
        elif tecla in "+−×÷":
            self._añadir_operador(tecla)
        else:  # dígitos y punto
            self._añadir_numero(tecla)
        self._refrescar()

    def _añadir_numero(self, digito):
        if self.recien_calculado:
            self.expresion = ""
            self.historial = ""
            self.recien_calculado = False
        if len(self.expresion) >= 16:
            return
        if digito == "." and self._ultimo_numero_tiene_punto():
            return
        if digito == "." and (not self.expresion or self.expresion[-1] in "+−×÷"):
            self.expresion += "0"
        self.expresion += digito

    def _ultimo_numero_tiene_punto(self):
        for caracter in reversed(self.expresion):
            if caracter == ".":
                return True
            if caracter in "+−×÷":
                return False
        return False

    def _añadir_operador(self, simbolo):
        if self.recien_calculado:
            self.historial = ""
            self.recien_calculado = False
        if not self.expresion:
            if simbolo == "−":          # permite números negativos
                self.expresion = "−"
            return
        if self.expresion[-1] in "+−×÷":
            self.expresion = self.expresion[:-1]   # reemplaza el operador previo
        self.expresion += simbolo

    def _calcular(self):
        while self.expresion and self.expresion[-1] in "+−×÷":
            self.expresion = self.expresion[:-1]
        if not self.expresion or self.expresion == "−":
            return
        texto = self.expresion
        for simbolo, operador in SIMBOLO_A_OPERADOR.items():
            texto = texto.replace(simbolo, operador)
        try:
            valor = float(evaluar(texto))
            if not math.isfinite(valor):
                raise OverflowError
            self.historial = self.expresion + " ="
            self.expresion = formatear(valor)
            self.recien_calculado = True
        except ZeroDivisionError:
            self.historial = self.expresion + " ="
            self.expresion = "No se puede dividir entre 0"
            self.recien_calculado = True
        except (ValueError, SyntaxError, TypeError, OverflowError):
            self.historial = ""
            self.expresion = "Error"
            self.recien_calculado = True

    def _refrescar(self):
        self.lbl_historial.config(text=self.historial)
        texto = self.expresion or "0"
        if len(texto) <= 9:
            tamaño = 44
        elif len(texto) <= 14:
            tamaño = 32
        else:
            tamaño = 22
        self.lbl_principal.config(text=texto, font=("Helvetica", tamaño, "bold"))

    # ----- Teclado -----

    def _tecla(self, evento):
        mapa = {
            "*": "×", "/": "÷", "-": "−", "+": "+", ".": ".", ",": ".",
        }
        simbolo = evento.char
        if evento.keysym in ("Return", "KP_Enter", "equal") or simbolo == "=":
            self._pulsar("=")
        elif evento.keysym == "BackSpace":
            self._pulsar("⌫")
        elif evento.keysym == "Escape":
            self._pulsar("C")
        elif simbolo in mapa:
            self._pulsar(mapa[simbolo])
        elif simbolo.isdigit():
            self._pulsar(simbolo)


if __name__ == "__main__":
    Calculadora().mainloop()
