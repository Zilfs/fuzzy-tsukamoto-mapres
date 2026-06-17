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

## 8. Dokumentasi Percobaan

### Percobaan 1 (Kategori Cukup)

![](doc-image/kalkulator-percobaan1.png)
![](doc-image/graf-percobaan1.png)

#### 1. Kondisi Input Mahasiswa

Nilai tegas (_crisp_) yang dimasukkan ke dalam sistem melalui slider adalah sebagai berikut:

- **IPK = 3.13** (Berada di kategori **Sedang** dengan derajat keanggotaan $\mu = 0.740$, dan sudah mulai menyentuh area kurva Tinggi tetapi masih bernilai sangat kecil/mendekati $0.00$).
- **Prestasi Lomba = 25.0** (Berada mutlak di kategori **Rendah** dengan derajat keanggotaan $\mu = 1.000$).
- **Organisasi = 2.5** (Berada mutlak di kategori **Rendah** dengan derajat keanggotaan $\mu = 1.000$).
- **Kehadiran = 24.0%** (Berada mutlak di kategori **Rendah** dengan derajat keanggotaan $\mu = 1.000$).

#### 2. Analisis Inferensi (Aturan yang Aktif)

Dari total 12 aturan yang ada pada sistem, hanya ada **2 aturan** yang aktif (memiliki nilai $ lpha$-predikat $> 0$) karena dipicu oleh kondisi nilai input di atas:

- **Rule 8 (R8):** `IF IPK Sedang AND Organisasi Rendah THEN Cukup`
  - Nilai $ lpha$-predikat = $\min(\mu	ext{IPK\_Sedang}, \mu	ext{Org\_Rendah}) = \min(0.74, 1.00) = \mathbf{0.7400}$.
  - Nilai implikasi tegas individual ($z_8$) = **35.2000**.
  - Aturan ini memberikan kontribusi sebesar **42.5%** terhadap hasil akhir.
- **Rule 10 (R10):** `IF Kehadiran Rendah AND Prestasi Rendah THEN Cukup`
  - Nilai $ lpha$-predikat = $\min(\mu	ext{Hdr\_Rendah}, \mu	ext{Prs\_Rendah}) = \min(1.00, 1.00) = \mathbf{1.0000}$.
  - Nilai implikasi tegas individual ($z_{10}$) = **30.0000**.
  - Aturan ini menjadi dominan dengan kontribusi sebesar **57.5%** terhadap hasil akhir.

#### 3. Hasil Akhir Defuzzifikasi

Melalui perhitungan rata-rata berbobot (_weighted average_) dari aturan-aturan yang aktif:

$$z^* = rac{(0.7400 	imes 35.2000) + (1.0000 	imes 30.0000)}{0.7400 + 1.0000} = \mathbf{32.2115}$$

Sistem mengeluarkan nilai akhir tegas **32.2115** yang secara otomatis diklasifikasikan ke dalam kategori **Cukup** (karena nilai $z^* < 50$).

**Kesimpulan Percobaan:** Meskipun mahasiswa memiliki pencapaian akademik yang lumayan baik (IPK 3.13 berada di tingkat Sedang), skor akhir prestasinya anjlok ke kategori **Cukup** akibat nilai parameter non-akademik (Prestasi Lomba, Organisasi) serta tingkat Kehadiran yang sangat rendah (bernilai maksimal di kurva Rendah).

---

### Percobaan 2 (Kategori Baik)

![](doc-image/kalkulator-percobaan2.png)
![](doc-image/graf-percobaan2.png)

#### 1. Kondisi Input Mahasiswa

Nilai tegas (_crisp_) yang dimasukkan ke dalam sistem melalui slider adalah sebagai berikut:

- **IPK = 3.49** (Berada di dua kurva: Kategori **Tinggi** dengan $\mu = 0.480$ dan kategori **Sedang** dengan $\mu = 0.020$).
- **Prestasi Lomba = 76.0** (Berada di dua kurva: Kategori **Tinggi** dengan $\mu = 0.550$ dan kategori **Sedang** dengan $\mu = 0.160$).
- **Organisasi = 7.0** (Berada di dua kurva: Kategori **Tinggi** dengan $\mu = 0.333$ dan kategori **Sedang** dengan $\mu = 0.333$).
- **Kehadiran = 78.0%** (Berada mutlak di kategori **Sedang** dengan derajat keanggotaan $\mu = 1.000$).

#### 2. Analisis Inferensi (Aturan yang Aktif)

Kombinasi nilai input yang bersinggungan di beberapa kurva keanggotaan ini memicu aktifnya **5 aturan** sekaligus (memiliki nilai $ lpha$-predikat $> 0$):

- **Rule 1 (R1):** `IF IPK Tinggi AND Prestasi Tinggi THEN Sangat Baik`
  - Nilai $ lpha$-predikat = $\min(0.48, 0.55) = \mathbf{0.4800}$.
  - Nilai tegas individual ($z_1$) = **79.2000**. Aturan ini berkontribusi paling besar yaitu **55.0%**.
- **Rule 2 (R2):** `IF IPK Tinggi AND Organisasi Tinggi THEN Sangat Baik`
  - Nilai $ lpha$-predikat = $\min(0.48, 0.333) = \mathbf{0.3333}$.
  - Nilai tegas individual ($z_2$) = **73.3333**. Kontribusi aturan ini adalah **38.2%**.
- **Rule 5, 6, dan 7 (R5, R6, R7):** Ketiganya menghasilkan output **Baik** dengan nilai $ lpha$-predikat masing-masing sebesar **0.0200** dan nilai tegas individual ($z_i$) sebesar **30.5000**. Masing-masing aturan ini memberikan kontribusi kecil sebesar **2.3%** terhadap hasil akhir.

#### 3. Hasil Akhir Defuzzifikasi

Melalui perhitungan rata-rata berbobot (_weighted average_) dari kelima aturan yang aktif tersebut:

$$z^* = rac{(0.4800 	imes 79.2000) + (0.3333 	imes 73.3333) + 3 	imes (0.0200 	imes 30.5000)}{0.4800 + 0.3333 + 0.0200 + 0.0200 + 0.0200} = \mathbf{73.6150}$$

Sistem mengeluarkan nilai akhir tegas **73.6150** yang secara otomatis diklasifikasikan ke dalam kategori **Baik** (karena berada di rentang $50 \le z^* < 75$).

**Kesimpulan Percobaan:** Berbeda dengan percobaan sebelumnya, mahasiswa ini menunjukkan performa yang seimbang dan unggul di seluruh parameter. Komponen akademik (IPK 3.49) dan non-akademik (Prestasi Lomba 76 dan Organisasi 7) mayoritas sudah menyentuh domain kurva Tinggi, sehingga mendorong nilai akhir melonjak signifikan ke angka **73.6150 (Kategori Baik)** dan hampir mendekati batas kategori Sangat Baik.

---

### Percobaan 3 (Kategori Sangat Baik)

![](doc-image/kalkulator-percobaan3.png)
![](doc-image/graf-percobaan3.png)

#### 1. Kondisi Input Mahasiswa

Nilai tegas (_crisp_) yang dimasukkan ke dalam sistem melalui slider adalah sebagai berikut:

- **IPK = 3.86** (Berada mutlak di kategori **Tinggi** dengan derajat keanggotaan $\mu = 1.000$).
- **Prestasi Lomba = 88.0** (Berada mutlak di kategori **Tinggi** dengan derajat keanggotaan $\mu = 1.000$).
- **Organisasi = 9.2** (Berada mutlak di kategori **Tinggi** dengan derajat keanggotaan $\mu = 1.000$).
- **Kehadiran = 94.0%** (Berada mutlak di kategori **Tinggi** dengan derajat keanggotaan $\mu = 1.000$).

#### 2. Analisis Inferensi (Aturan yang Aktif)

Kondisi nilai input yang seluruhnya berada di level maksimal (kurva Tinggi) ini memicu aktifnya **3 aturan** yang mengarah langsung pada hasil performa terbaik:

- **Rule 1 (R1):** `IF IPK Tinggi AND Prestasi Tinggi THEN Sangat Baik`
  - Nilai $ lpha$-predikat = $\min(1.00, 1.00) = \mathbf{1.0000}$.
  - Nilai tegas individual ($z_1$) = **100.0000**. Aturan ini memegang kontribusi sebesar **33.3%**.
- **Rule 2 (R2):** `IF IPK Tinggi AND Organisasi Tinggi THEN Sangat Baik`
  - Nilai $ lpha$-predikat = $\min(1.00, 1.00) = \mathbf{1.0000}$.
  - Nilai tegas individual ($z_2$) = **100.0000**. Aturan ini juga berkontribusi sebesar **33.3%**.
- **Rule 3 (R3):** `IF IPK Tinggi AND Kehadiran Tinggi THEN Sangat Baik`
  - Nilai $ lpha$-predikat = $\min(1.00, 1.00) = \mathbf{1.0000}$.
  - Nilai tegas individual ($z_3$) = **100.0000**. Aturan ini melengkapi bobot dengan kontribusi sebesar **33.3%**.

#### 3. Hasil Akhir Defuzzifikasi

Melalui perhitungan rata-rata berbobot (_weighted average_) dari ketiga aturan dominan yang aktif tersebut:

$$z^* = rac{(1.0000 	imes 100.0000) + (1.0000 	imes 100.0000) + (1.0000 	imes 100.0000)}{1.0000 + 1.0000 + 1.0000} = \mathbf{100.0000}$$

Sistem mengeluarkan nilai akhir tegas **100.0000** yang secara otomatis diklasifikasikan ke dalam kategori **Sangat Baik** (karena nilai $z^* \ge 75$).

**Kesimpulan Percobaan:** Percobaan kali ini merepresentasikan profil mahasiswa dengan pencapaian sempurna di semua lini. Karena seluruh parameter input (akademik, prestasi, organisasi, dan kehadiran) berada di puncak kurva Tinggi dengan derajat keanggotaan penuh ($\mu = 1.00$), basis aturan menghasilkan nilai invers output maksimal ($z_i = 100$). Hasilnya, sistem memberikan skor mutlak **100.0000 (Kategori Sangat Baik)** dengan visualisasi grafik output yang menyentuh batas paling kanan.
