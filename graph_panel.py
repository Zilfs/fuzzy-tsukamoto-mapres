"""
graph_panel.py  -  Panel grafik MF ter-embed di tkinter (tanpa jendela baru)
"""
import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from theme import BG, PRIMARY, BORDER, SUBTEXT, MF_COLORS, CARD
from fuzzy_engine import (
    trapezoid_down, triangle, trapezoid_up,
    z_cukup, z_baik, z_sangat_baik, OUTPUT_MF,
)

X_IPK  = np.linspace(0, 4, 300)
X_100  = np.linspace(0, 100, 300)
X_ORG  = np.linspace(0, 10, 300)

INPUT_SPECS = [
    ("IPK",             X_IPK,  "Nilai IPK",
        [("Rendah", lambda x: trapezoid_down(x, 2.0, 2.75)),
         ("Sedang", lambda x: triangle(x, 2.5, 3.0, 3.5)),
         ("Tinggi", lambda x: trapezoid_up(x, 3.25, 3.75))]),
    ("Prestasi Lomba",  X_100,  "Skor Prestasi",
        [("Rendah", lambda x: trapezoid_down(x, 30, 50)),
         ("Sedang", lambda x: triangle(x, 30, 55, 80)),
         ("Tinggi", lambda x: trapezoid_up(x, 65, 85))]),
    ("Organisasi",      X_ORG,  "Skor Keterlibatan",
        [("Rendah", lambda x: trapezoid_down(x, 3, 5)),
         ("Sedang", lambda x: triangle(x, 3, 5, 8)),
         ("Tinggi", lambda x: trapezoid_up(x, 6, 9))]),
    ("Kehadiran",       X_100,  "% Kehadiran",
        [("Rendah", lambda x: trapezoid_down(x, 60, 75)),
         ("Sedang", lambda x: triangle(x, 65, 78, 88)),
         ("Tinggi", lambda x: trapezoid_up(x, 82, 92))]),
]


class GraphPanel(tk.Frame):
    """Frame yang menampung matplotlib figure (2×3 grid)."""

    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG, **kw)
        self.fig = Figure(figsize=(13, 6), facecolor=BG)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self._axes = None

    # ── API Publik ────────────────────────────────────────────────────────────

    def update(self, inputs: dict, fuzz: dict, z_star: float):
        """Gambar ulang semua subplot dengan data terbaru."""
        self.fig.clear()
        axes = self.fig.subplots(2, 3)

        vals   = [inputs["ipk"], inputs["prestasi"], inputs["org"], inputs["kehadiran"]]
        fuzz_v = [fuzz["ipk"],   fuzz["prestasi"],   fuzz["organisasi"], fuzz["kehadiran"]]

        for ax, (title, x_arr, xlabel, funcs), val in zip(
                axes.flat, INPUT_SPECS, vals):
            self._plot_mf(ax, x_arr, funcs, title, xlabel, val)

        # Output
        self._plot_mf(axes[1, 1], X_100,
                      [(n, fn) for n, fn in OUTPUT_MF],
                      "Output: Tingkat Prestasi", "Nilai z", z_star)

        # Panel info
        self._plot_info(axes[1, 2], inputs, fuzz, fuzz_v, z_star)

        self.fig.suptitle(
            f"Fungsi Keanggotaan  |  IPK={inputs['ipk']}  "
            f"Prestasi={inputs['prestasi']}  "
            f"Organisasi={inputs['org']}  Kehadiran={inputs['kehadiran']}%",
            fontsize=10, fontweight="bold", color="#1A1A2E",
        )
        self.fig.tight_layout(rect=[0, 0, 1, 0.93])
        self.canvas.draw()

    # ── Helper Private ────────────────────────────────────────────────────────

    def _plot_mf(self, ax, x_arr, funcs, title, xlabel, input_val):
        for (lbl, fn), color in zip(funcs, MF_COLORS):
            y = [fn(xi) for xi in x_arr]
            ax.plot(x_arr, y, label=lbl, color=color, linewidth=2)
            ax.fill_between(x_arr, y, alpha=0.07, color=color)
            mu = fn(input_val)
            if mu > 0.005:
                ax.plot(input_val, mu, "o", color=color, markersize=7, zorder=5)
                ax.plot([input_val, input_val], [0, mu],
                        color=color, linestyle=":", linewidth=1.2, alpha=0.7)

        ax.axvline(input_val, color=PRIMARY, linewidth=1.8,
                   linestyle="--", label=f"Input = {input_val}", zorder=4)
        ax.set_title(title, fontweight="bold", color="#1A1A2E", fontsize=9)
        ax.set_xlabel(xlabel, fontsize=8)
        ax.set_ylabel("μ(x)", fontsize=8)
        ax.legend(fontsize=7)
        ax.set_ylim(-0.05, 1.2)
        ax.set_facecolor("#F8FAFF")
        ax.grid(True, linestyle="--", alpha=0.35)
        for spine in ax.spines.values():
            spine.set_color(BORDER)

    def _plot_info(self, ax, inputs, fuzz, fuzz_v, z_star):
        ax.axis("off")
        names   = ["IPK", "Prestasi", "Organisasi", "Kehadiran"]
        in_vals = [inputs["ipk"], inputs["prestasi"], inputs["org"], inputs["kehadiran"]]
        text    = "Derajat Keanggotaan\n" + "─" * 24 + "\n"
        for name, val, d in zip(names, in_vals, fuzz_v):
            text += f"\n{name} = {val}\n"
            for k, v in d.items():
                if v > 0.005:
                    text += f"  {k.capitalize():8s}: {v:.3f}\n"
        text += f"\n{'─'*24}\nz* = {z_star:.4f}"
        ax.text(0.05, 0.95, text, transform=ax.transAxes,
                fontsize=8, verticalalignment="top", fontfamily="monospace",
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#EEF4FF",
                          edgecolor=PRIMARY, linewidth=1.2))
