# Pertemuan 6 — Attributing Direct Drivers to Deforestation Alerts with Satellite Imagery and AI

[![Buka di Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/Pertemuan_6_Deforestasi_Satelit_AI.ipynb)

**Narasumber:** Dr. Bart Slagter (Laboratory of Geo-Information Science and Remote Sensing, Wageningen University & Research)
**Penyelenggara:** Program Studi S1 Teknik Informatika, Universitas Bengkulu
**Waktu:** Senin, 19 Oktober 2026, 14.00 WIB
**Rekaman:** [YouTube, Informatika UNIB Official](https://www.youtube.com/live/OFLzys5FYqg)

## Ringkasan materi
1. **Dari "di mana" ke "mengapa":** sistem peringatan (Hansen, GLAD, RADD) tahu *di mana* dan *kapan* tutupan pohon hilang, tetapi tidak *mengapa*. Atribusi pemicu penting untuk penegakan hukum dan kepatuhan rantai pasok (mis. EUDR).
2. **Multi-sensor:** optik (Sentinel-2) terganggu awan di tropis; radar SAR C-band (Sentinel-1) menembus awan dan sensitif terhadap struktur kanopi (backscatter VV/VH), dasar sistem RADD.
3. **Taksonomi pemicu langsung** (delapan kategori): pertanian skala besar, pertanian rakyat, penebangan selektif, infrastruktur, pertambangan, kebakaran, bencana alam, dinamika sungai.
4. **Deep learning & deret waktu:** satu citra "sebelum-sesudah" tidak cukup; dinamika pascagangguan (pemulihan vs penanaman teratur) menjadi petunjuk. Arsitektur: CNN, U-Net/ResNet, transformer temporal; komputasi di Google Earth Engine; data acuan ForestNet.
5. **Operasional di Global Forest Watch** bersama WRI: peringatan disertai atribut pemicu.
6. **Relevansi Indonesia dan peluang riset:** class imbalance, Edge AI untuk drone/gawai, dasbor untuk polisi hutan.

## Studi kasus
Balai Penegakan Hukum Kehutanan di Bengkulu menerima ratusan peringatan kehilangan kanopi tiap bulan, tetapi personel terbatas dan sering salah sasaran. Dibangun pipeline atribusi empat kelas: `Sawit_Industri`, `Pertanian_Rakyat`, `Tambang`, `Jalan_Penebangan`.

| Konsep materi | Implementasi |
|---|---|
| Fitur optik | NDVI_Drop, NBR_Drop |
| Fitur radar | SAR_VH_dB, SAR_Ratio_VHVV |
| Morfologi poligon | Luas (ha), elongasi |
| Deret waktu pascagangguan | NDVI_Pulih_90hr |
| Fusi multi-sensor + awan | Ablasi dengan 40% poligon tertutup awan |
| Class imbalance | Kelas Tambang dikurangi ±88% pada data latih; bandingkan `class_weight` |
| Dari model ke patroli | Rekomendasi berbasis probabilitas, keyakinan rendah → verifikasi |

## Cara menjalankan
- **Colab:** badge → *Run all*.
- **Lokal:** `python kode.py`.
- **KNIME:** [KNIME_GUIDE.md](KNIME_GUIDE.md).

## Hasil utama (data sintetis, seed tetap)
- Akurasi uji 99,5% (data mudah dipisahkan; **bukan** perkiraan performa pada citra nyata).
- Ablasi dengan 40% poligon tertutup awan (F1 macro): optik saja **0,54**, radar saja **0,71**, fusi optik+radar **0,72**, fusi + morfologi + deret waktu **1,00**. Skor 1,00 terutama karena morfologi sintetis sangat membedakan; pesan yang valid adalah radar menjaga performa saat optik hilang.
- Class imbalance: pada data sintetis yang mudah ini recall Tambang tetap 0,98 tanpa penyeimbangan (0,92 dengan `balanced`), sehingga dampaknya kecil; pada data nyata biasanya jauh lebih besar.

## Catatan penting
- Kelas **Tambang** hanya berarti bukaan tambang terdeteksi. Legal/ilegal ditentukan lewat tumpang-susun dengan data perizinan (mis. IUP), bukan oleh citra.
- Lokasi alert di bagian inferensi adalah **simulasi**. Prediksi model adalah petunjuk prioritas, bukan bukti hukum.
- Untuk citra nyata: gunakan data latih beranotasi ahli, validasi lapangan, dan arsitektur CNN/U-Net/Transformer sebagaimana dibahas materi; Random Forest di sini adalah *baseline* tabular.

## Berkas
`kode.py` (notebook utama: `Pertemuan_6_Deforestasi_Satelit_AI.ipynb` di akar repo), `data/peringatan_deforestasi_sintetis.csv`, `output/06_ablasi_fusi_sensor.png`, `output/06_evaluasi_model.png`.
