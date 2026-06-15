"""
Sistem Fuzzy Tsukamoto - Penentuan Mahasiswa Berprestasi
Input : IPK, Prestasi Lomba, Organisasi, Kehadiran
Output: Tingkat Prestasi (Cukup, Baik, Sangat Baik)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt


# ── Fungsi Keanggotaan Input ──────────────────────────────────────────────────

def trapezoid_down(x, a, b):
    if x <= a: return 1.0
    if x >= b: return 0.0
    return (b - x) / (b - a)

def triangle(x, a, b, c):
    if x <= a or x >= c: return 0.0
    if x <= b: return (x - a) / (b - a)
    return (c - x) / (c - b)

def trapezoid_up(x, a, b):
    if x <= a: return 0.0
    if x >= b: return 1.0
    return (x - a) / (b - a)


# ── Fuzzifikasi ───────────────────────────────────────────────────────────────

def fuzzify_ipk(ipk):
    return {
        "rendah": trapezoid_down(ipk, 2.0, 2.75),
        "sedang": triangle(ipk, 2.5, 3.0, 3.5),
        "tinggi": trapezoid_up(ipk, 3.25, 3.75),
    }

def fuzzify_prestasi(prestasi):
    return {
        "rendah": trapezoid_down(prestasi, 30, 50),
        "sedang": triangle(prestasi, 30, 55, 80),
        "tinggi": trapezoid_up(prestasi, 65, 85),
    }

def fuzzify_organisasi(org):
    return {
        "rendah": trapezoid_down(org, 3, 5),
        "sedang": triangle(org, 3, 5, 8),
        "tinggi": trapezoid_up(org, 6, 9),
    }

def fuzzify_kehadiran(hadir):
    return {
        "rendah": trapezoid_down(hadir, 60, 75),
        "sedang": triangle(hadir, 65, 78, 88),
        "tinggi": trapezoid_up(hadir, 82, 92),
    }


# ── Fungsi Keanggotaan Output ─────────────────────────────────────────────────

def z_cukup(z):      return trapezoid_down(z, 30, 50)
def z_baik(z):       return triangle(z, 30, 55, 80)
def z_sangat_baik(z):return trapezoid_up(z, 60, 100)

def invers_cukup(alpha):       return 50 - np.clip(alpha, 0, 1) * 20
def invers_baik(alpha):        return 30 + np.clip(alpha, 0, 1) * 25
def invers_sangat_baik(alpha): return 60 + np.clip(alpha, 0, 1) * 40


# ── 12 Rule Fuzzy ────────────────────────────────────────────────────────────

def apply_rules(ipk_f, prestasi_f, org_f, hadir_f):
    return [
        (min(ipk_f["tinggi"], prestasi_f["tinggi"]),                    "sangat_baik"),  # R1
        (min(ipk_f["tinggi"], org_f["tinggi"]),                         "sangat_baik"),  # R2
        (min(ipk_f["tinggi"], hadir_f["tinggi"]),                       "sangat_baik"),  # R3
        (min(ipk_f["tinggi"], prestasi_f["rendah"]),                    "baik"),         # R4
        (min(ipk_f["sedang"], prestasi_f["tinggi"]),                    "baik"),         # R5
        (min(ipk_f["sedang"], prestasi_f["sedang"], hadir_f["sedang"]), "baik"),         # R6
        (min(ipk_f["sedang"], org_f["sedang"]),                         "baik"),         # R7
        (min(ipk_f["sedang"], org_f["rendah"]),                         "cukup"),        # R8
        (min(ipk_f["rendah"], prestasi_f["rendah"]),                    "cukup"),        # R9
        (min(hadir_f["rendah"], prestasi_f["rendah"]),                  "cukup"),        # R10
        (min(ipk_f["rendah"], hadir_f["rendah"]),                       "cukup"),        # R11
        (min(ipk_f["sedang"], hadir_f["tinggi"], prestasi_f["sedang"]), "baik"),         # R12
    ]


# ── Inferensi & Defuzzifikasi Tsukamoto ──────────────────────────────────────

INVERS = {
    "cukup":       invers_cukup,
    "baik":        invers_baik,
    "sangat_baik": invers_sangat_baik,
}

def tsukamoto(ipk, prestasi, org, kehadiran):
    ipk_f      = fuzzify_ipk(ipk)
    prestasi_f = fuzzify_prestasi(prestasi)
    org_f      = fuzzify_organisasi(org)
    hadir_f    = fuzzify_kehadiran(kehadiran)

    rules        = apply_rules(ipk_f, prestasi_f, org_f, hadir_f)
    total_alpha  = 0.0
    total_az     = 0.0
    rule_details = []

    for i, (alpha, label) in enumerate(rules, 1):
        z_i       = INVERS[label](alpha)
        total_az  += alpha * z_i
        total_alpha += alpha
        rule_details.append((i, alpha, label, z_i))

    z_star   = total_az / total_alpha if total_alpha > 0 else 0
    kategori = "Cukup" if z_star < 50 else ("Baik" if z_star < 75 else "Sangat Baik")

    return z_star, kategori, rule_details, {
        "ipk": ipk_f, "prestasi": prestasi_f,
        "organisasi": org_f, "kehadiran": hadir_f
    }


# ── Konstanta Warna & Font ────────────────────────────────────────────────────

BG        = "#F0F4FF"
CARD      = "#FFFFFF"
PRIMARY   = "#3B5BDB"
ACCENT    = "#4DABF7"
SUCCESS   = "#2F9E44"
WARNING   = "#E67700"
DANGER    = "#C92A2A"
TEXT      = "#1A1A2E"
SUBTEXT   = "#6B7280"
BORDER    = "#DEE2F0"

FONT_TITLE  = ("Segoe UI", 16, "bold")
FONT_LABEL  = ("Segoe UI", 10)
FONT_VALUE  = ("Segoe UI", 10, "bold")
FONT_RESULT = ("Segoe UI", 22, "bold")
FONT_SMALL  = ("Segoe UI", 9)

KATEGORI_COLOR = {
    "Cukup":       WARNING,
    "Baik":        SUCCESS,
    "Sangat Baik": PRIMARY,
    "–":           SUBTEXT,
}


# ── Komponen Helper ───────────────────────────────────────────────────────────

def card(parent, **kwargs):
    """Frame putih dengan border tipis, seperti kartu."""
    return tk.Frame(parent, bg=CARD, relief="flat",
                    highlightbackground=BORDER, highlightthickness=1, **kwargs)

def label(parent, text, font=FONT_LABEL, color=TEXT, **kwargs):
    return tk.Label(parent, text=text, font=font, fg=color, bg=parent["bg"], **kwargs)


# ── Widget Slider Input ───────────────────────────────────────────────────────

class SliderInput(tk.Frame):
    """Baris input: Label | Slider | Nilai angka."""

    def __init__(self, parent, text, from_, to, resolution, **kwargs):
        super().__init__(parent, bg=CARD, **kwargs)
        self.var = tk.DoubleVar(value=from_)

        label(self, text, font=FONT_LABEL, color=SUBTEXT).grid(
            row=0, column=0, sticky="w", padx=(0, 12))

        self.slider = tk.Scale(
            self, from_=from_, to=to, resolution=resolution,
            orient="horizontal", variable=self.var,
            length=260, showvalue=False,
            bg=CARD, fg=PRIMARY, troughcolor=BORDER,
            activebackground=ACCENT, highlightthickness=0,
            command=self._on_change,
        )
        self.slider.grid(row=0, column=1)

        self.val_lbl = tk.Label(
            self, textvariable=self.var,
            font=FONT_VALUE, fg=PRIMARY, bg=CARD, width=6, anchor="e"
        )
        self.val_lbl.grid(row=0, column=2, padx=(8, 0))

    def _on_change(self, _):
        pass  # nilai sudah sync lewat DoubleVar

    def get(self):
        return self.var.get()


# ── Aplikasi Utama ────────────────────────────────────────────────────────────

class FuzzyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Fuzzy Tsukamoto – Mahasiswa Berprestasi")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._build_ui()
        self.minsize(640, 700)

    # ── Layout Utama ──────────────────────────────────────────────────────────

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        # Header
        self._build_header()

        # Dua kolom: Input (kiri) & Hasil (kanan)
        body = tk.Frame(self, bg=BG)
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        self._build_input_card(body)
        self._build_result_card(body)

        # Tabel rule (full width)
        self._build_rule_table(body)

        # Tombol grafik
        self._build_footer()

    def _build_header(self):
        hdr = tk.Frame(self, bg=PRIMARY)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.columnconfigure(0, weight=1)

        tk.Label(hdr, text="🎓  Sistem Mahasiswa Berprestasi",
                 font=FONT_TITLE, fg="white", bg=PRIMARY,
                 pady=14).grid(row=0, column=0)
        tk.Label(hdr, text="Fuzzy Inference System — Metode Tsukamoto",
                 font=FONT_SMALL, fg=ACCENT, bg=PRIMARY,
                 pady=0).grid(row=1, column=0)
        tk.Frame(hdr, height=6, bg=ACCENT).grid(row=2, column=0, sticky="ew")

    # ── Kartu Input ───────────────────────────────────────────────────────────

    def _build_input_card(self, parent):
        c = card(parent)
        c.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=8)
        c.columnconfigure(0, weight=1)

        label(c, "  Data Input Mahasiswa", font=("Segoe UI", 11, "bold"),
              color=PRIMARY).grid(row=0, column=0, sticky="w", pady=(12, 4))
        tk.Frame(c, height=1, bg=BORDER).grid(row=1, column=0, sticky="ew", padx=12)

        configs = [
            ("IPK",            0,   4,   0.01),
            ("Prestasi Lomba", 0, 100,   1),
            ("Organisasi",     0,  10,   0.5),
            ("Kehadiran (%)",  0, 100,   1),
        ]
        self.sliders = []
        for i, (txt, lo, hi, res) in enumerate(configs):
            s = SliderInput(c, txt, lo, hi, res)
            s.grid(row=i + 2, column=0, sticky="ew", padx=16, pady=6)
            self.sliders.append(s)

        tk.Button(
            c, text="  Hitung Prestasi  ",
            font=("Segoe UI", 10, "bold"),
            bg=PRIMARY, fg="white", relief="flat",
            activebackground=ACCENT, activeforeground="white",
            cursor="hand2", pady=8,
            command=self._calculate,
        ).grid(row=len(configs) + 2, column=0, pady=16, padx=16, sticky="ew")

    # ── Kartu Hasil ───────────────────────────────────────────────────────────

    def _build_result_card(self, parent):
        c = card(parent)
        c.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=8)
        c.columnconfigure(0, weight=1)

        label(c, "  Hasil Penilaian", font=("Segoe UI", 11, "bold"),
              color=PRIMARY).grid(row=0, column=0, sticky="w", pady=(12, 4))
        tk.Frame(c, height=1, bg=BORDER).grid(row=1, column=0, sticky="ew", padx=12)

        # Nilai z*
        z_frame = tk.Frame(c, bg=BG, pady=10)
        z_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(12, 4))
        label(z_frame, "Nilai z*", font=FONT_SMALL, color=SUBTEXT).pack(anchor="w")
        self.lbl_z = label(z_frame, "–", font=("Segoe UI", 18, "bold"), color=TEXT)
        self.lbl_z.pack(anchor="w")

        # Badge kategori
        badge_frame = tk.Frame(c, bg=CARD)
        badge_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=4)
        label(badge_frame, "Kategori", font=FONT_SMALL, color=SUBTEXT).pack(anchor="w")

        self.badge = tk.Label(
            badge_frame, text="–",
            font=FONT_RESULT, fg=SUBTEXT, bg=CARD,
        )
        self.badge.pack(anchor="w", pady=(2, 0))

        # Indikator bar (progress visual)
        label(c, "Skor Prestasi (0–100)", font=FONT_SMALL,
              color=SUBTEXT).grid(row=4, column=0, sticky="w", padx=16, pady=(12, 2))

        bar_bg = tk.Frame(c, bg=BORDER, height=16)
        bar_bg.grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 12))
        bar_bg.columnconfigure(0, weight=1)
        bar_bg.grid_propagate(False)

        self.progress_bar = tk.Frame(bar_bg, bg=SUBTEXT, height=16)
        self.progress_bar.place(x=0, y=0, relheight=1, relwidth=0)

        self.lbl_pct = label(c, "", font=FONT_SMALL, color=SUBTEXT)
        self.lbl_pct.grid(row=6, column=0, sticky="w", padx=16)

        # Info fuzzifikasi singkat
        label(c, "  Derajat Keanggotaan Input",
              font=("Segoe UI", 10, "bold"), color=PRIMARY).grid(
                  row=7, column=0, sticky="w", pady=(16, 4))
        tk.Frame(c, height=1, bg=BORDER).grid(row=8, column=0, sticky="ew", padx=12)

        self.fuzz_labels = {}
        fuzz_names = [("IPK", "ipk"), ("Prestasi", "prestasi"),
                      ("Organisasi", "organisasi"), ("Kehadiran", "kehadiran")]
        for i, (display, key) in enumerate(fuzz_names):
            row_f = tk.Frame(c, bg=CARD)
            row_f.grid(row=9 + i, column=0, sticky="ew", padx=16, pady=2)
            label(row_f, f"{display}:", font=FONT_SMALL, color=SUBTEXT).pack(side="left")
            lbl = label(row_f, "–", font=FONT_SMALL, color=TEXT)
            lbl.pack(side="left", padx=(6, 0))
            self.fuzz_labels[key] = lbl

    # ── Tabel Rule ────────────────────────────────────────────────────────────

    def _build_rule_table(self, parent):
        c = card(parent)
        c.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=8)
        c.columnconfigure(0, weight=1)

        label(c, "  Detail Rule & Inferensi",
              font=("Segoe UI", 11, "bold"), color=PRIMARY).grid(
                  row=0, column=0, sticky="w", pady=(12, 4))
        tk.Frame(c, height=1, bg=BORDER).grid(row=1, column=0, sticky="ew", padx=12)

        tbl_frame = tk.Frame(c, bg=CARD)
        tbl_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=8)
        tbl_frame.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                         background=CARD, fieldbackground=CARD,
                         foreground=TEXT, rowheight=26,
                         font=FONT_SMALL, borderwidth=0)
        style.configure("Custom.Treeview.Heading",
                         background=PRIMARY, foreground="white",
                         font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Custom.Treeview", background=[("selected", ACCENT)])

        cols = ("Rule", "Alpha (α)", "Output", "z_i", "Kontribusi")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                                  height=12, style="Custom.Treeview")

        widths = [50, 100, 130, 100, 120]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        scrollbar = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    # ── Footer ────────────────────────────────────────────────────────────────

    def _build_footer(self):
        footer = tk.Frame(self, bg=BG)
        footer.grid(row=2, column=0, pady=(0, 16))

        tk.Button(
            footer, text="📊  Tampilkan Grafik Fungsi Keanggotaan",
            font=("Segoe UI", 10), bg=CARD, fg=PRIMARY,
            relief="flat", highlightbackground=PRIMARY, highlightthickness=1,
            activebackground=BG, cursor="hand2", padx=16, pady=8,
            command=self._show_graph,
        ).pack()

    # ── Logika Hitung ─────────────────────────────────────────────────────────

    def _calculate(self):
        try:
            ipk       = self.sliders[0].get()
            prestasi  = self.sliders[1].get()
            org       = self.sliders[2].get()
            kehadiran = self.sliders[3].get()
        except tk.TclError as e:
            messagebox.showerror("Input Error", str(e))
            return

        z, kat, rules, fuzz = tsukamoto(ipk, prestasi, org, kehadiran)

        # Update hasil
        self.lbl_z.config(text=f"{z:.4f}")
        color = KATEGORI_COLOR.get(kat, SUBTEXT)
        self.badge.config(text=kat, fg=color)

        # Progress bar
        pct = z / 100
        self.progress_bar.place(relwidth=pct)
        self.progress_bar.config(bg=color)
        self.lbl_pct.config(text=f"{z:.1f} / 100")

        # Update fuzzifikasi
        def fmt(d):
            return "  ".join(
                f"{k.capitalize()}: {v:.2f}"
                for k, v in d.items() if v > 0.01
            ) or "–"

        for key, lbl in self.fuzz_labels.items():
            lbl.config(text=fmt(fuzz[key]))

        # Update tabel
        for row in self.tree.get_children():
            self.tree.delete(row)

        total_alpha = sum(r[1] for r in rules)
        for r in rules:
            kontribusi = f"{(r[1]/total_alpha*100):.1f}%" if total_alpha > 0 else "–"
            tag = "active" if r[1] > 0 else "inactive"
            self.tree.insert("", "end", tags=(tag,), values=(
                f"R{r[0]}",
                f"{r[1]:.4f}",
                r[2].replace("_", " ").title(),
                f"{r[3]:.4f}",
                kontribusi,
            ))

        self.tree.tag_configure("active",   background="#EEF4FF")
        self.tree.tag_configure("inactive", foreground=SUBTEXT)

        self._last_fuzz = fuzz

    # ── Grafik MF ─────────────────────────────────────────────────────────────

    def _show_graph(self):
        if not hasattr(self, "_last_fuzz"):
            messagebox.showinfo("Info", "Tekan 'Hitung Prestasi' terlebih dahulu.")
            return

        fig, axes = plt.subplots(2, 3, figsize=(13, 6))
        fig.patch.set_facecolor("#F0F4FF")
        fig.suptitle("Fungsi Keanggotaan – Sistem Fuzzy Tsukamoto",
                     fontsize=13, fontweight="bold", color="#1A1A2E")

        COLORS = ["#C92A2A", "#E67700", "#2F9E44"]

        def plot_mf(ax, x, funcs, title, xlabel):
            for (lbl, fn), color in zip(funcs, COLORS):
                y = [fn(xi) for xi in x]
                ax.plot(x, y, label=lbl, color=color, linewidth=2)
                ax.fill_between(x, y, alpha=0.08, color=color)
            ax.set_title(title, fontweight="bold", color="#1A1A2E")
            ax.set_xlabel(xlabel, fontsize=9)
            ax.set_ylabel("μ(x)", fontsize=9)
            ax.legend(fontsize=8)
            ax.set_ylim(-0.05, 1.15)
            ax.set_facecolor("#F8FAFF")
            ax.grid(True, linestyle="--", alpha=0.4)
            for spine in ax.spines.values():
                spine.set_color(BORDER)

        x_ipk = np.linspace(0, 4, 300)
        x_100 = np.linspace(0, 100, 300)
        x_org = np.linspace(0, 10, 300)

        plot_mf(axes[0,0], x_ipk, [
            ("Rendah", lambda x: trapezoid_down(x, 2.0, 2.75)),
            ("Sedang", lambda x: triangle(x, 2.5, 3.0, 3.5)),
            ("Tinggi", lambda x: trapezoid_up(x, 3.25, 3.75)),
        ], "IPK", "Nilai IPK")

        plot_mf(axes[0,1], x_100, [
            ("Rendah", lambda x: trapezoid_down(x, 30, 50)),
            ("Sedang", lambda x: triangle(x, 30, 55, 80)),
            ("Tinggi", lambda x: trapezoid_up(x, 65, 85)),
        ], "Prestasi Lomba", "Skor Prestasi")

        plot_mf(axes[0,2], x_org, [
            ("Rendah", lambda x: trapezoid_down(x, 3, 5)),
            ("Sedang", lambda x: triangle(x, 3, 5, 8)),
            ("Tinggi", lambda x: trapezoid_up(x, 6, 9)),
        ], "Organisasi", "Skor Keterlibatan")

        plot_mf(axes[1,0], x_100, [
            ("Rendah", lambda x: trapezoid_down(x, 60, 75)),
            ("Sedang", lambda x: triangle(x, 65, 78, 88)),
            ("Tinggi", lambda x: trapezoid_up(x, 82, 92)),
        ], "Kehadiran", "% Kehadiran")

        plot_mf(axes[1,1], x_100, [
            ("Cukup",       z_cukup),
            ("Baik",        z_baik),
            ("Sangat Baik", z_sangat_baik),
        ], "Output: Tingkat Prestasi", "Nilai z")

        axes[1,2].axis("off")
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = FuzzyApp()
    app.mainloop()