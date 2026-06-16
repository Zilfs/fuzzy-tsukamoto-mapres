"""
widgets.py  -  Komponen UI reusable
"""
import tkinter as tk
from theme import CARD, BORDER, PRIMARY, ACCENT, SUBTEXT, FONT_LABEL, FONT_VALUE


def card(parent, **kw):
    return tk.Frame(parent, bg=CARD, relief="flat",
                    highlightbackground=BORDER, highlightthickness=1, **kw)

def label(parent, text, font=FONT_LABEL, color=None, **kw):
    from theme import TEXT
    return tk.Label(parent, text=text, font=font,
                    fg=color or TEXT, bg=parent["bg"], **kw)


class SliderInput(tk.Frame):
    """Label | Slider | Nilai angka."""

    def __init__(self, parent, text, from_, to, resolution, **kw):
        super().__init__(parent, bg=CARD, **kw)
        self.var = tk.DoubleVar(value=from_)

        label(self, text, font=FONT_LABEL, color=SUBTEXT).grid(
            row=0, column=0, sticky="w", padx=(0, 12))

        tk.Scale(
            self, from_=from_, to=to, resolution=resolution,
            orient="horizontal", variable=self.var,
            length=260, showvalue=False,
            bg=CARD, fg=PRIMARY, troughcolor=BORDER,
            activebackground=ACCENT, highlightthickness=0,
        ).grid(row=0, column=1)

        tk.Label(
            self, textvariable=self.var,
            font=FONT_VALUE, fg=PRIMARY, bg=CARD, width=6, anchor="e"
        ).grid(row=0, column=2, padx=(8, 0))

    def get(self):
        return self.var.get()
