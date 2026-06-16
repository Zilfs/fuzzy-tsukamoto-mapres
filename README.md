# Sistem Penentuan Mahasiswa Berprestasi - Fuzzy Tsukamoto

Aplikasi desktop berbasis **Tkinter + Matplotlib** untuk menentukan tingkat prestasi mahasiswa (Cukup / Baik / Sangat Baik) menggunakan metode **Fuzzy Tsukamoto**, dengan 4 variabel input dan visualisasi grafik fungsi keanggotaan secara real-time.

---

## 1. Struktur Proyek

| File              | Fungsi                                                    |
| ----------------- | --------------------------------------------------------- |
| `main.py`         | Entry point, menjalankan aplikasi                         |
| `app.py`          | UI utama (window, tab, kartu input/hasil, tabel rule)     |
| `fuzzy_engine.py` | Logika fuzzy: fuzzifikasi, rule base, inferensi Tsukamoto |
| `graph_panel.py`  | Panel grafik Matplotlib ter-embed (tanpa jendela baru)    |
| `theme.py`        | Konstanta warna & font                                    |
| `widgets.py`      | Komponen UI reusable (`card`, `label`, `SliderInput`)     |

---

## 2. Requirement

- Python 3.8+
- Library eksternal: `numpy`, `matplotlib`
- `tkinter` - biasanya sudah bawaan Python (Windows/Mac). Di Linux kadang perlu install terpisah.

---

## 3. Instalasi (Clone & Setup)

### 3.1 Clone repository

```bash
git clone https://github.com/Zilfs/fuzzy-tsukamoto-mapres.git
cd fuzzy-tsukamoto-mapres
```

### 3.2 (Opsional) buat virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3.3 Install library yang dibutuhkan

```bash
pip install numpy matplotlib
```

### Khusus Linux, jika tkinter belum tersedia:

```bash
sudo apt install python3-tk
```

---

## 4. Menjalankan Aplikasi

```bash
python main.py
```

Window **"Sistem Fuzzy Tsukamoto - Mahasiswa Berprestasi"** akan terbuka, berisi 2 tab: **Kalkulator** dan **Grafik MF**.

---

## 5. Panduan Penggunaan

### 5.1 Tab "Kalkulator"

1. Atur 4 slider input di kartu kiri:
   - **IPK** (0–4, step 0.01)
   - **Prestasi Lomba** (0–100, step 1)
   - **Organisasi** (0–10, step 0.5)
   - **Kehadiran %** (0–100, step 1)
2. Klik tombol **"Hitung"**.
3. Hasil tampil di kartu kanan:
   - **Nilai z\*** (skor akhir hasil defuzzifikasi)
   - **Badge Kategori** (Cukup/Baik/Sangat Baik, warna otomatis sesuai `theme.py`)
   - **Progress bar** skor 0–100
   - **Derajat keanggotaan** tiap variabel input (mis. `IPK: Sedang: 0.65  Tinggi: 0.20`)
4. Di bawahnya, tabel **"Detail Rule & Inferensi"** menampilkan 12 rule fuzzy: nomor rule, nilai α (alpha predikat), kategori output, nilai z_i, dan % kontribusi tiap rule terhadap z\* (rule dengan α=0 ditandai abu-abu/tidak aktif, rule aktif di-highlight biru muda).

### 5.2 Tab "Grafik MF" (Menampilkan Grafik)

1. Setelah klik **"Hitung"** di tab Kalkulator.
2. Klik tab **"Grafik MF"** pada bagian atas notebook (tab tidak pindah otomatis - lihat catatan di bagian 7).
3. Akan tampil grid 2×3 (6 subplot):
   - 4 grafik fungsi keanggotaan input: **IPK, Prestasi Lomba, Organisasi, Kehadiran** - masing-masing menampilkan kurva Rendah/Sedang/Tinggi, garis vertikal putus-putus posisi nilai input, dan titik potong (α-cut) pada kurva yang aktif.
   - 1 grafik fungsi keanggotaan **Output** (Cukup/Baik/Sangat Baik) dengan garis vertikal di posisi z\*.
   - 1 panel info teks ringkasan seluruh derajat keanggotaan dan nilai z\* final.
4. Judul figure menampilkan ringkasan nilai input yang sedang digunakan.
5. Setiap kali tombol "Hitung" ditekan ulang di tab Kalkulator, grafik di tab ini ikut ter-update otomatis - cukup klik kembali tab "Grafik MF" untuk melihat hasil terbaru.

---

## 6. Logika Fuzzy Tsukamoto

### 6.1 Variabel & Himpunan Fuzzy Input

| Variabel           | Rendah          | Sedang               | Tinggi          |
| ------------------ | --------------- | -------------------- | --------------- |
| IPK (0–4)          | turun 2.0->2.75 | segitiga 2.5–3.0–3.5 | naik 3.25->3.75 |
| Prestasi (0–100)   | turun 30->50    | segitiga 30–55–80    | naik 65->85     |
| Organisasi (0–10)  | turun 3->5      | segitiga 3–5–8       | naik 6->9       |
| Kehadiran (0–100%) | turun 60->75    | segitiga 65–78–88    | naik 82->92     |

### 6.2 Variabel Output (skor 0–100) & Fungsi Invers (Tsukamoto)

| Kategori    | Bentuk MF         | Invers (untuk z_i) |
| ----------- | ----------------- | ------------------ |
| Cukup       | turun 30->50      | z = 50 − 20·α      |
| Baik        | segitiga 30–55–80 | z = 30 + 25·α      |
| Sangat Baik | naik 60->100      | z = 60 + 40·α      |

### 6.3 Basis Rule (12 Rule, operator AND = min)

| #   | Kondisi                                         | Output      |
| --- | ----------------------------------------------- | ----------- |
| R1  | IPK Tinggi ∧ Prestasi Tinggi                    | Sangat Baik |
| R2  | IPK Tinggi ∧ Organisasi Tinggi                  | Sangat Baik |
| R3  | IPK Tinggi ∧ Kehadiran Tinggi                   | Sangat Baik |
| R4  | IPK Tinggi ∧ Prestasi Rendah                    | Baik        |
| R5  | IPK Sedang ∧ Prestasi Tinggi                    | Baik        |
| R6  | IPK Sedang ∧ Prestasi Sedang ∧ Kehadiran Sedang | Baik        |
| R7  | IPK Sedang ∧ Organisasi Sedang                  | Baik        |
| R8  | IPK Sedang ∧ Organisasi Rendah                  | Cukup       |
| R9  | IPK Rendah ∧ Prestasi Rendah                    | Cukup       |
| R10 | Kehadiran Rendah ∧ Prestasi Rendah              | Cukup       |
| R11 | IPK Rendah ∧ Kehadiran Rendah                   | Cukup       |
| R12 | IPK Sedang ∧ Kehadiran Tinggi ∧ Prestasi Sedang | Baik        |

### 6.4 Defuzzifikasi & Kategori Akhir

```
z* = Σ(αᵢ × zᵢ) / Σ(αᵢ)
```

- z\* < 50 -> **Cukup**
- 50 ≤ z\* < 75 -> **Baik**
- z\* ≥ 75 -> **Sangat Baik**

---

## 7. Fitur & Catatan Teknis Lain

- **Tema konsisten** (`theme.py`): kartu putih dengan border tipis, warna primer biru, badge kategori berwarna otomatis (Cukup=oranye, Baik=hijau, Sangat Baik=biru).
- **Komponen reusable** (`widgets.py`): `card()` untuk panel, `label()` untuk teks, `SliderInput` (label + slider + nilai angka berjalan).
- **Tabel rule custom** menggunakan `ttk.Treeview` dengan style `clam`, baris aktif di-highlight.
- **Grafik ter-embed**, bukan jendela popup baru, sehingga performa lebih ringan dan UI menyatu.
- **Catatan**: baris `self._nb.select(1)` di `app.py` (untuk auto-pindah ke tab Grafik setelah klik Hitung) sedang **di-nonaktifkan (di-comment)**. Jika ingin tab berpindah otomatis, hapus tanda `#` pada baris tersebut di akhir method `_calculate()`.
