# Panduan KNIME — Pertemuan 6 (atribusi pemicu deforestasi)

> Panduan membangun workflow di **KNIME Analytics Platform 5.x**. Berkas `.knwf` tidak disertakan (harus diekspor dari
> aplikasi). Nama node dapat berbeda antarversi.

Input: `data/peringatan_deforestasi_sintetis.csv` (kolom fitur + `Driver`).

## A. Eksplorasi
1. **CSV Reader** → **Statistics** (cek keseimbangan kelas `Driver`).
2. **Box Plot** / **Scatter Plot** `Luas_Hektare` vs `Elongasi_Shape` diwarnai `Driver` untuk melihat pemisahan morfologi.

## B. Pemodelan atribusi
1. **Partitioning** (80/20, *Stratified* pada `Driver`, seed tetap).
2. **Random Forest Learner** (target `Driver`, 150 pohon, *Max depth* 8) → **Random Forest Predictor**.
3. **Scorer** → akurasi, recall per kelas, matriks konfusi.
4. Kepentingan fitur dari statistik atribut keluaran learner → **Bar Chart**.

## C. Ablasi fusi sensor
1. Buat tiga cabang dengan **Column Filter**: (a) optik saja `NDVI_Drop`, `NBR_Drop`; (b) radar saja `SAR_VH_dB`, `SAR_Ratio_VHVV`; (c) gabungan.
2. Simulasikan awan: **Rule Engine/Math Formula** dengan angka acak (**Random Number Assigner**) → set kolom optik menjadi *missing* untuk ±40% baris.
3. **Missing Value** (median) pada kolom optik → learner/predictor/scorer per cabang → bandingkan *F-measure* rata-rata makro.

## D. Class imbalance
1. **Row Splitter/Row Filter** untuk mengurangi baris `Tambang` pada data latih.
2. Bandingkan model biasa dengan data diseimbangkan ulang memakai **SMOTE** (bila tersedia) atau **Equal Size Sampling**. Pantau **recall** kelas Tambang pada Scorer.

## E. Inferensi dan prioritas patroli
1. **Table Creator** untuk poligon alert baru (kolom sama dengan fitur).
2. **Random Forest Predictor** (aktifkan *Append individual class probabilities*).
3. **Rule Engine**: `MAXIMUM probabilitas < 0.6 => "VERIFIKASI citra resolusi tinggi"`, kelas Tambang/Jalan_Penebangan ⇒ "PRIORITAS 1", lainnya ⇒ "PRIORITAS 2".

## F. Menuju citra nyata
Ekspor atribut poligon dari Google Earth Engine (CSV/GeoJSON), baca dengan **CSV Reader**; untuk klasifikasi langsung pada gambar gunakan ekstensi *KNIME Deep Learning* atau Python (PyTorch) dengan U-Net/CNN. Selalu validasi lapangan dan tumpang-susun dengan data izin sebelum tindakan hukum.
