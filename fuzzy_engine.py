"""
fuzzy_engine.py  -  Logika Fuzzy Tsukamoto
"""
import numpy as np


# ── Fungsi Keanggotaan Dasar ──────────────────────────────────────────────────

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

def fuzzify_ipk(v):
    return {
        "rendah": trapezoid_down(v, 2.0, 2.75),
        "sedang": triangle(v, 2.5, 3.0, 3.5),
        "tinggi": trapezoid_up(v, 3.25, 3.75),
    }

def fuzzify_prestasi(v):
    return {
        "rendah": trapezoid_down(v, 30, 50),
        "sedang": triangle(v, 30, 55, 80),
        "tinggi": trapezoid_up(v, 65, 85),
    }

def fuzzify_organisasi(v):
    return {
        "rendah": trapezoid_down(v, 3, 5),
        "sedang": triangle(v, 3, 5, 8),
        "tinggi": trapezoid_up(v, 6, 9),
    }

def fuzzify_kehadiran(v):
    return {
        "rendah": trapezoid_down(v, 60, 75),
        "sedang": triangle(v, 65, 78, 88),
        "tinggi": trapezoid_up(v, 82, 92),
    }


# ── Fungsi Keanggotaan & Invers Output ───────────────────────────────────────

def z_cukup(z):       return trapezoid_down(z, 30, 50)
def z_baik(z):        return triangle(z, 30, 55, 80)
def z_sangat_baik(z): return trapezoid_up(z, 60, 100)

def invers_cukup(a):       return 50 - np.clip(a, 0, 1) * 20
def invers_baik(a):        return 30 + np.clip(a, 0, 1) * 25
def invers_sangat_baik(a): return 60 + np.clip(a, 0, 1) * 40

INVERS = {
    "cukup":       invers_cukup,
    "baik":        invers_baik,
    "sangat_baik": invers_sangat_baik,
}

OUTPUT_MF = [
    ("Cukup",       z_cukup),
    ("Baik",        z_baik),
    ("Sangat Baik", z_sangat_baik),
]


# ── Rule Base ────────────────────────────────────────────────────────────────

def apply_rules(ipk_f, prs_f, org_f, hdr_f):
    m = min
    return [
        (m(ipk_f["tinggi"], prs_f["tinggi"]),                    "sangat_baik"),
        (m(ipk_f["tinggi"], org_f["tinggi"]),                    "sangat_baik"),
        (m(ipk_f["tinggi"], hdr_f["tinggi"]),                    "sangat_baik"),
        (m(ipk_f["tinggi"], prs_f["rendah"]),                    "baik"),
        (m(ipk_f["sedang"], prs_f["tinggi"]),                    "baik"),
        (m(ipk_f["sedang"], prs_f["sedang"], hdr_f["sedang"]),   "baik"),
        (m(ipk_f["sedang"], org_f["sedang"]),                    "baik"),
        (m(ipk_f["sedang"], org_f["rendah"]),                    "cukup"),
        (m(ipk_f["rendah"], prs_f["rendah"]),                    "cukup"),
        (m(hdr_f["rendah"], prs_f["rendah"]),                    "cukup"),
        (m(ipk_f["rendah"], hdr_f["rendah"]),                    "cukup"),
        (m(ipk_f["sedang"], hdr_f["tinggi"], prs_f["sedang"]),   "baik"),
    ]


# ── Inferensi Tsukamoto ───────────────────────────────────────────────────────

def tsukamoto(ipk, prestasi, org, kehadiran):
    fuzz = {
        "ipk":        fuzzify_ipk(ipk),
        "prestasi":   fuzzify_prestasi(prestasi),
        "organisasi": fuzzify_organisasi(org),
        "kehadiran":  fuzzify_kehadiran(kehadiran),
    }

    rules        = apply_rules(fuzz["ipk"], fuzz["prestasi"], fuzz["organisasi"], fuzz["kehadiran"])
    total_alpha  = 0.0
    total_az     = 0.0
    rule_details = []

    for i, (alpha, label) in enumerate(rules, 1):
        z_i         = INVERS[label](alpha)
        total_az   += alpha * z_i
        total_alpha += alpha
        rule_details.append((i, alpha, label, z_i))

    z_star   = total_az / total_alpha if total_alpha > 0 else 0
    kategori = "Cukup" if z_star < 50 else ("Baik" if z_star < 75 else "Sangat Baik")

    return z_star, kategori, rule_details, fuzz
