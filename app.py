import tkinter as tk
from tkinter import ttk, messagebox

from theme import (BG, CARD, PRIMARY, ACCENT, BORDER,
                   TEXT, SUBTEXT, FONT_TITLE, FONT_SMALL,
                   FONT_RESULT, FONT_VALUE, KATEGORI_COLOR)
from widgets import card, label, SliderInput
from graph_panel import GraphPanel
from fuzzy_engine import tsukamoto


class FuzzyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Fuzzy Tsukamoto - Mahasiswa Berprestasi")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._build_ui()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_header()

        # Notebook: tab Kalkulator & tab Grafik
        nb = ttk.Notebook(self)
        nb.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)

        # Tab 1 - Kalkulator
        tab_calc = tk.Frame(nb, bg=BG)
        tab_calc.columnconfigure(0, weight=1)
        tab_calc.columnconfigure(1, weight=1)
        tab_calc.rowconfigure(1, weight=1)
        nb.add(tab_calc, text="Kalkulator")

        self._build_input_card(tab_calc)
        self._build_result_card(tab_calc)
        self._build_rule_table(tab_calc)

        # Tab 2 - Grafik (embedded)
        tab_graph = tk.Frame(nb, bg=BG)
        tab_graph.columnconfigure(0, weight=1)
        tab_graph.rowconfigure(0, weight=1)
        nb.add(tab_graph, text="Grafik MF")

        self.graph_panel = GraphPanel(tab_graph)
        self.graph_panel.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self._nb = nb

    def _build_header(self):
        hdr = tk.Frame(self, bg=PRIMARY)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.columnconfigure(0, weight=1)

        tk.Label(hdr, text="Sistem Penentuan Mahasiswa Berprestasi",
                 font=FONT_TITLE, fg="white", bg=PRIMARY, pady=14
                 ).grid(row=0, column=0)

    # ── Kartu Input ───────────────────────────────────────────────────────────

    def _build_input_card(self, parent):
        c = card(parent)
        c.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=8)
        c.columnconfigure(0, weight=1)

        label(c, "  Data Input Mahasiswa",
              font=("Segoe UI", 11, "bold"), color=PRIMARY
              ).grid(row=0, column=0, sticky="w", pady=(12, 4))
        tk.Frame(c, height=1, bg=BORDER).grid(row=1, column=0, sticky="ew", padx=12)

        configs = [
            ("IPK", 0, 4, 0.01),
            ("Prestasi Lomba", 0, 100, 1),
            ("Organisasi", 0, 10, 0.5),
            ("Kehadiran (%)", 0, 100, 1),
        ]
        self.sliders = []
        for i, (txt, lo, hi, res) in enumerate(configs):
            s = SliderInput(c, txt, lo, hi, res)
            s.grid(row=i + 2, column=0, sticky="ew", padx=16, pady=6)
            self.sliders.append(s)

        tk.Button(
            c, text="  Hitung & Tampilkan Grafik  ",
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

        label(c, "Hasil Penilaian",
              font=("Segoe UI", 11, "bold"), color=PRIMARY
              ).grid(row=0, column=0, sticky="w", pady=(12, 4))
        tk.Frame(c, height=1, bg=BORDER).grid(row=1, column=0, sticky="ew", padx=12)

        z_frame = tk.Frame(c, bg=BG, pady=10)
        z_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(12, 4))
        label(z_frame, "Nilai z*", font=FONT_SMALL, color=SUBTEXT).pack(anchor="w")
        self.lbl_z = label(z_frame, "-", font=("Segoe UI", 18, "bold"), color=TEXT)
        self.lbl_z.pack(anchor="w")

        badge_frame = tk.Frame(c, bg=CARD)
        badge_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=4)
        label(badge_frame, "Kategori", font=FONT_SMALL, color=SUBTEXT).pack(anchor="w")
        self.badge = tk.Label(badge_frame, text="-",
                              font=FONT_RESULT, fg=SUBTEXT, bg=CARD)
        self.badge.pack(anchor="w", pady=(2, 0))

        label(c, "Skor Prestasi (0-100)", font=FONT_SMALL,
              color=SUBTEXT).grid(row=4, column=0, sticky="w", padx=16, pady=(12, 2))
        bar_bg = tk.Frame(c, bg=BORDER, height=16)
        bar_bg.grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 12))
        bar_bg.grid_propagate(False)
        self.progress_bar = tk.Frame(bar_bg, bg=SUBTEXT, height=16)
        self.progress_bar.place(x=0, y=0, relheight=1, relwidth=0)
        self.lbl_pct = label(c, "", font=FONT_SMALL, color=SUBTEXT)
        self.lbl_pct.grid(row=6, column=0, sticky="w", padx=16)

        label(c, "  Derajat Keanggotaan Input",
              font=("Segoe UI", 10, "bold"), color=PRIMARY
              ).grid(row=7, column=0, sticky="w", pady=(16, 4))
        tk.Frame(c, height=1, bg=BORDER).grid(row=8, column=0, sticky="ew", padx=12)

        self.fuzz_labels = {}
        for i, (display, key) in enumerate(
                [("IPK", "ipk"), ("Prestasi", "prestasi"),
                 ("Organisasi", "organisasi"), ("Kehadiran", "kehadiran")]):
            row_f = tk.Frame(c, bg=CARD)
            row_f.grid(row=9 + i, column=0, sticky="ew", padx=16, pady=2)
            label(row_f, f"{display}:", font=FONT_SMALL, color=SUBTEXT).pack(side="left")
            lbl = label(row_f, "-", font=FONT_SMALL, color=TEXT)
            lbl.pack(side="left", padx=(6, 0))
            self.fuzz_labels[key] = lbl

    # ── Tabel Rule ────────────────────────────────────────────────────────────

    def _build_rule_table(self, parent):
        c = card(parent)
        c.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=8)
        c.columnconfigure(0, weight=1)

        label(c, "  Detail Rule & Inferensi",
              font=("Segoe UI", 11, "bold"), color=PRIMARY
              ).grid(row=0, column=0, sticky="w", pady=(12, 4))
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

        cols = ("Rule", "Alpha", "Output", "z_i", "Kontribusi")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                                 height=12, style="Custom.Treeview")
        for col, w in zip(cols, [50, 100, 130, 100, 120]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        sb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

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

        # Hasil
        self.lbl_z.config(text=f"{z:.4f}")
        color = KATEGORI_COLOR.get(kat, SUBTEXT)
        self.badge.config(text=kat, fg=color)
        self.progress_bar.place(relwidth=z / 100)
        self.progress_bar.config(bg=color)
        self.lbl_pct.config(text=f"{z:.1f} / 100")

        # Fuzzifikasi
        def fmt(d):
            return "  ".join(
                f"{k.capitalize()}: {v:.2f}" for k, v in d.items() if v > 0.01
            ) or "-"
        for key, lbl in self.fuzz_labels.items():
            lbl.config(text=fmt(fuzz[key]))

        # Tabel
        for row in self.tree.get_children():
            self.tree.delete(row)
        total_alpha = sum(r[1] for r in rules)
        for r in rules:
            kontribusi = f"{(r[1]/total_alpha*100):.1f}%" if total_alpha > 0 else "-"
            tag = "active" if r[1] > 0 else "inactive"
            self.tree.insert("", "end", tags=(tag,), values=(
                f"R{r[0]}", f"{r[1]:.4f}",
                r[2].replace("_", " ").title(),
                f"{r[3]:.4f}", kontribusi,
            ))
        self.tree.tag_configure("active",   background="#EEF4FF")
        self.tree.tag_configure("inactive", foreground=SUBTEXT)

        # Update grafik & pindah ke tab Grafik
        inputs = {"ipk": ipk, "prestasi": prestasi, "org": org, "kehadiran": kehadiran}
        self.graph_panel.update(inputs, fuzz, z)
        self._nb.select(1)   # otomatis pindah ke tab Grafik
