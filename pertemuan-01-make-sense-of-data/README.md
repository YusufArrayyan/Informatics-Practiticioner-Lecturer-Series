# Pertemuan 1 — Make Sense of Data with Analytics and AI

[![Buka di Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/pertemuan-01-make-sense-of-data/notebook.ipynb)

**Narasumber:** peneliti senior BRIN dan pengelola tim High Performance Computing (nama pada catatan tulisan tangan kurang terbaca, mohon dilengkapi)
**Penyelenggara:** Program Studi S1 Teknik Informatika, Universitas Bengkulu

## Ringkasan materi
- Proses pengolahan data mengubah data mentah menjadi informasi, lalu *insight* yang menopang keputusan bisnis.
- Kerangka kerja **CRISP-DM** (Cross-Industry Standard Process for Data Mining) membimbing proses analitik. Materi menekankan **4 jenis analitik**:
  1. Deskriptif: apa yang terjadi?
  2. Diagnostik: mengapa terjadi?
  3. Prediktif: apa yang akan terjadi?
  4. Preskriptif: apa yang harus dilakukan?
- Tahap persiapan data menentukan kualitas hasil: prinsip **"Garbage In, Garbage Out"**. Masalah umum: *missing value*, duplikat, record tidak konsisten, dan anomali.
- Platform analitik berbasis alur kerja visual (seperti **KNIME**) menyederhanakan proses; integrasi Generative AI membantu menyusun workflow, tetapi hasil akhir tetap dianalisis dan diputuskan manusia.

## Studi kasus
**Analitik penjualan jaringan UMKM kuliner (3 outlet × 4 produk, Januari–September 2026).**
Pemilik usaha ingin tahu omzet, penyebab penurunan, kebutuhan stok minggu depan, dan apakah diskon promo layak. Data awalnya kotor (4% nilai kosong, 1% outlier salah input, 8% label tidak konsisten, 3% baris duplikat).

| Materi | Implementasi |
|---|---|
| CRISP-DM: data understanding | Profil kualitas data (missing, unik, duplikat) |
| Data preparation / GIGO | Standarisasi label, hapus duplikat, outlier IQR, imputasi median per kelompok; bukti empiris model A vs B |
| Analitik deskriptif | Omzet bulanan per outlet |
| Analitik diagnostik | Deteksi pekan anjlok (hanya pekan lengkap) dan uji peran promo/hujan/akhir pekan |
| Analitik prediktif | Random Forest memprediksi qty harian, diuji pada data asli Agustus–September |
| Analitik preskriptif | Rekomendasi stok 1–7 Oktober (dengan safety stock 90%) dan simulasi diskon |

## Cara menjalankan
- **Colab:** klik badge di atas, lalu *Runtime → Run all*. Data dibangkitkan otomatis.
- **Lokal:** `pip install -r ../requirements.txt` lalu `python kode.py` di folder ini.
- **KNIME:** ikuti [KNIME_GUIDE.md](KNIME_GUIDE.md). Data CSV siap pakai ada di `data/`.

## Hasil utama (seed tetap, hasil dapat direproduksi)
- Pembersihan memulihkan 3.276 baris asli dengan galat imputasi rata-rata 0,32 unit.
- Pekan anjlok terdalam: outlet Panorama, pekan 15 Juni 2026 (renovasi pada data sintetis); promo/hujan tidak menjelaskannya.
- Model dengan data dibersihkan penuh: MAE **4,71** vs **9,82** untuk pembersihan minimal (error turun ±52%).
- Skenario diskon: 5% memberi laba kotor tertinggi (15,3 juta Rp/pekan), 10% justru lebih rendah dari tanpa diskon. Asumsi: uplift volume tetap ×1,24 untuk semua kedalaman diskon, sehingga perlu uji A/B.

## Berkas
| Berkas | Isi |
|---|---|
| `notebook.ipynb`, `kode.py` | Implementasi (notebook dibuat otomatis dari `kode.py`) |
| `data/penjualan_umkm_kotor.csv` | Data mentah dengan masalah kualitas (input KNIME) |
| `data/penjualan_umkm_bersih.csv` | Hasil pembersihan |
| `output/*.png` | Grafik deskriptif dan perbandingan GIGO |

> Data seluruhnya sintetis.
