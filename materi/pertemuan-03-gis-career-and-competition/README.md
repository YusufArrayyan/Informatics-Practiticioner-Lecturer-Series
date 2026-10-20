# Pertemuan 3 — Career and Competition in Indonesia with GIS

[![Buka di Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/Pertemuan_3_GIS.ipynb)

**Narasumber:** praktisi GIS (nama pada catatan tulisan tangan kurang terbaca, mohon dilengkapi)
**Penyelenggara:** Program Studi S1 Teknik Informatika, Universitas Bengkulu

## Ringkasan materi
- Perkembangan GIS (Sistem Informasi Geografis) dan perannya sebagai fondasi **Smart City**, logistik/rantai pasok, dan layanan publik; GIS dipakai untuk analisis geografis dan optimasi lokasi.
- Prospek karier GIS di Indonesia dan lanskap persaingannya, termasuk peluang di instansi pemerintah, industri, dan konsultan pemetaan.
- Keterampilan yang didorong: perangkat lunak open source profesional (**QGIS, PostGIS, GeoPandas**), pemrosesan data besar lewat **cloud computing (Google Earth Engine)**, serta integrasi **machine learning** (mis. klasifikasi tutupan lahan).
- Pesan: kompetensi data spasial makin dicari, dan perpaduan GIS + data science memberi keunggulan.

## Studi kasus
**Penentuan titik evakuasi tambahan di zona pesisir rawan tsunami, Kota Bengkulu** (data sintetis), dilanjutkan **klasifikasi tutupan lahan** dari citra multispektral.

| Keterampilan materi | Implementasi |
|---|---|
| Analisis spasial (jarak, buffer, cakupan layanan) | Zona rawan ≤ 3 km dari pantai; kelurahan terlayani bila shelter ≤ 1,5 km |
| Optimasi lokasi | K-Means berbobot populasi pada kelurahan belum terlayani, lalu *snap* ke permukiman |
| Interoperabilitas QGIS | Ekspor `output/hasil_analisis.geojson` |
| GeoPandas | Sel opsional: buffer pada EPSG:32748 (UTM 48S) |
| GEE + ML | Klasifikasi 5 kelas lahan (Hutan, Sawit, Permukiman, Air, Lahan Terbuka) dengan NDVI/NDWI/NDBI dan Random Forest |

## Cara menjalankan
- **Colab:** badge → *Run all*. Sel GeoPandas berjalan otomatis (sudah terpasang di Colab).
- **Lokal:** `python kode.py`. GeoPandas opsional; tanpa itu sel opsional dilewati.
- **KNIME:** [KNIME_GUIDE.md](KNIME_GUIDE.md).

## Hasil utama
- 14 dari 45 kelurahan berada di zona rawan (±47.800 penduduk); cakupan shelter eksisting hanya **37,3%**.
- Dengan 3 shelter usulan, cakupan naik menjadi **80,6%** (+43,3 poin).
- Klasifikasi tutupan lahan: akurasi **94,4%** pada data uji; kesalahan terbesar antara Hutan↔Sawit dan Permukiman↔Lahan Terbuka (spektral mirip).

## Visual di QGIS
`Layer → Add Layer → Add Vector Layer` → pilih `output/hasil_analisis.geojson`. Gunakan atribut `jenis` (`kelurahan`, `shelter_eksisting`, `shelter_usulan`, `garis_pantai_sintetis`) untuk *categorized symbology*.

## Lanjutan: mengambil data Sentinel-2 dari Google Earth Engine (contoh, tidak dijalankan di notebook)
```python
import ee
ee.Initialize(project="PROJECT_ID_ANDA")
roi = ee.Geometry.Rectangle([102.15, -3.92, 102.35, -3.68])
s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
      .filterBounds(roi).filterDate("2026-01-01", "2026-09-30")
      .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20)).median())
ndvi = s2.normalizedDifference(["B8", "B4"]).rename("NDVI")
```
Cuplikan ini **belum diuji** di sini (membutuhkan akun dan proyek Earth Engine).

## Batasan
Lokasi, populasi, dan garis pantai **sintetis**; jarak memakai garis lurus (bukan jaringan jalan). Keputusan nyata membutuhkan data resmi (BPBD/BIG), jaringan jalan, dan topografi.
