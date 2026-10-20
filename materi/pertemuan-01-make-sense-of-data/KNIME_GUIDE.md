# Panduan KNIME — Pertemuan 1 (CRISP-DM + 4 jenis analitik)

> Panduan langkah demi langkah untuk membangun workflow di **KNIME Analytics Platform 5.x**. Berkas `.knwf`
> tidak disertakan karena harus diekspor dari aplikasi KNIME; ikuti urutan node di bawah, lalu ekspor lewat
> *File → Export KNIME Workflow* bila ingin menambahkannya ke repo. Nama node dapat sedikit berbeda antarversi.

Input: `data/penjualan_umkm_kotor.csv`

## A. Data Understanding & Preparation
1. **CSV Reader** → pilih berkas kotor. Pastikan kolom `tanggal` dibaca sebagai *Local Date*.
2. **Statistics** (atau *Data Explorer*) → lihat jumlah missing pada `qty` dan nilai unik `produk` (8 label, seharusnya 4).
3. **String Manipulation** pada `produk`: `capitalize(strip($produk$))` → "NASI GORENG " menjadi "Nasi Goreng".
4. **Duplicate Row Filter** → kolom kunci: `tanggal`, `outlet`, `produk`; pilih *Remove duplicate rows*.
5. **Date&Time Part Extractor** → ambil *Day of week* dan *Month*; **Rule Engine** untuk `weekend` (`$dow$ >= 6 => 1`, `TRUE => 0`).
6. **Numeric Outliers** → grup per `produk`, kolom `qty`, IQR multiplier 3; pilih *Replace outlier values with missing values*.
7. **Missing Value** → untuk `qty`, strategi *Median*. Untuk imputasi per kelompok, taruh di dalam **Group Loop Start / Loop End** dengan kelompok `produk` dan `weekend`.
8. **CSV Writer** → simpan sebagai `penjualan_umkm_bersih.csv` (bandingkan dengan keluaran Python).

## B. Analitik
**Deskriptif**
- **Math Formula**: `omzet = $qty$ * $harga$`
- **GroupBy** (kelompok: bulan, outlet; agregasi: Sum omzet) → **Pivoting** → **Line Plot**

**Diagnostik**
- **GroupBy** per pekan & outlet → **Math Formula** untuk z-score per outlet → **Sorter** (z menaik) untuk menemukan pekan anjlok.
- Hanya sertakan pekan dengan 7 hari (**Row Filter** pada jumlah hari) agar pekan parsial tidak terbaca sebagai anomali.
- **GroupBy** rata-rata `qty` menurut `promo`, `hujan`, `weekend` untuk membandingkan efek faktor.

**Prediktif**
1. **Row Splitter** (atau **Rule-based Row Filter**) → latih: `tanggal` < 2026-08-01, uji: sisanya.
2. **One to Many** pada `outlet` dan `produk` (one-hot).
3. **Random Forest Learner (Regression)** → target `qty`; **Random Forest Predictor (Regression)** pada data uji.
4. **Numeric Scorer** → baca *Mean absolute error*.
5. Ulangi dengan data yang hanya dibersihkan minimal (hapus missing) dan bandingkan MAE untuk membuktikan GIGO.

**Preskriptif**
- Buat tabel skenario 7 hari × outlet × produk (**Table Creator** atau **Cross Joiner**), jalankan predictor dengan `promo=0` dan `promo=1`.
- **GroupBy** jumlah prediksi per produk; **Math Formula** menambahkan safety stock `1.28 * sigma * sqrt(n)`.
- **Math Formula** untuk laba diskon: `qty * (harga*(1-d) - 0.6*harga)` pada beberapa nilai `d`.

## C. Variasi dengan AI (sesuai materi)
Gunakan asisten **K-AI** pada KNIME (bila tersedia di versi Anda) untuk menyarankan workflow, lalu **periksa sendiri** tiap node. AI membantu menyusun, manusia menyimpulkan.

## D. Alternatif cepat
Satu node **Python Script** dapat menjalankan isi `kode.py` bagian pembersihan bila Python terintegrasi di KNIME.
