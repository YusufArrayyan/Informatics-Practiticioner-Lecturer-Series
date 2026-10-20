# Panduan KNIME — Pertemuan 3 (analisis spasial + klasifikasi lahan)

> Panduan membangun workflow di **KNIME Analytics Platform 5.x**. Berkas `.knwf` tidak disertakan (harus diekspor dari
> aplikasi). Nama node dapat berbeda antarversi. KNIME juga punya ekstensi geospasial; panduan ini sengaja memakai
> node inti agar bisa diikuti tanpa ekstensi tambahan.

Input: `data/kelurahan_sintetis.csv` (kolom `lat`, `lon`, `populasi`, `jarak_pantai_m`) dan tabel shelter (buat dari `output/hasil_analisis.geojson` atau dengan **Table Creator**).

## A. Cakupan shelter (setara buffer + jarak terdekat)
1. **CSV Reader** untuk kelurahan; **Table Creator** untuk shelter (kolom `nama`, `lat`, `lon`).
2. **Cross Joiner** (kelurahan × shelter) → setiap pasangan kelurahan–shelter.
3. **Math Formula** jarak datar dalam meter (pendekatan lokal untuk area kecil):
   `sqrt( pow(($lat$ - $lat_s$) * 110574, 2) + pow(($lon$ - $lon_s$) * 111320 * cos(-3.80 * PI()/180), 2) )`
4. **GroupBy** per `kelurahan`, agregasi **Minimum** `jarak` → jarak shelter terdekat.
5. **Rule Engine**: `$jarak_pantai_m$ <= 3000 AND $jarak_min$ > 1500 => "Belum terlayani"`, `$jarak_pantai_m$ <= 3000 => "Terlayani"`, `TRUE => "Luar zona"`.
6. **GroupBy** (Sum `populasi` per status) → hitung persen cakupan dengan **Math Formula**.

## B. Lokasi shelter usulan
7. **Row Filter** kelurahan "Belum terlayani".
8. **k-Means** (k = 3) pada `lat`, `lon`. Untuk bobot populasi, gandakan baris sebanding `populasi` (mis. **Python Script** atau **Math Formula** + **Duplicate loop**), atau cukup gunakan hasil Python dari `kode.py`.
9. Pusat klaster → kandidat shelter. Ulangi langkah A dengan shelter eksisting + usulan untuk melihat peningkatan cakupan.

## C. Klasifikasi tutupan lahan
Input: `data/piksel_tutupan_lahan_sintetis.csv`.
1. **CSV Reader** → **Partitioning** (75/25, *stratified sampling* pada `kelas`).
2. **Random Forest Learner** (target `kelas`, fitur B2…B11, NDVI, NDWI, NDBI) → **Random Forest Predictor** → **Scorer**.
3. Baca *Accuracy* dan matriks konfusi (target sekitar 94% pada data ini).
4. **Table View / Bar Chart** untuk kepentingan fitur (keluaran *attribute statistics* dari learner).

## D. Visualisasi peta
Muat GeoJSON ke **QGIS** (lihat README) untuk peta cetak, atau gunakan **Scatter Plot** KNIME pada `lon`/`lat` dengan warna sesuai status.

## E. Ke arah karier
Pelajari pasangan alat dari materi: QGIS (desktop), PostGIS (basis data spasial), GeoPandas (skrip), Google Earth Engine (citra skala besar), dan KNIME/Python untuk otomasi alur.
