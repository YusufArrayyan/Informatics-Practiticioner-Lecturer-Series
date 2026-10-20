# Informatics Practitioner Lecturer Series: Studi Kasus & Implementasi

Kumpulan studi kasus, implementasi kode (Python/Google Colab), dan panduan workflow **KNIME** dari 6 pertemuan *Practitioner Lecture Series* Program Studi S1 Teknik Informatika, Universitas Bengkulu (UNIB).

Setiap folder pertemuan berisi:
- `README.md`: ringkasan materi, studi kasus, pemetaan materi → implementasi, dan hasil utama
- `notebook.ipynb`: notebook Google Colab (dibuat otomatis dari `kode.py`)
- `KNIME_GUIDE.md`: panduan membangun workflow KNIME langkah demi langkah
- `data/`: dataset sintetis (siap dipakai di KNIME) dan `output/`: grafik/hasil

| # | Topik | Narasumber | Studi kasus | Colab |
|---|---|---|---|---|
| 1 | [Make Sense of Data with Analytics and AI](pertemuan-01-make-sense-of-data) | Peneliti senior BRIN* | Analitik penjualan UMKM kuliner: CRISP-DM, 4 jenis analitik, bukti GIGO | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/pertemuan-01-make-sense-of-data/notebook.ipynb) |
| 2 | [Bridging Global Infrastructure to Address Local Challenge with HPC](pertemuan-02-hpc-bridging-global-infrastructure) | Asst. Prof. Dr. Worawan Diaz Carballo* | Simulasi Monte Carlo banjir serial vs paralel, hukum Amdahl | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/pertemuan-02-hpc-bridging-global-infrastructure/notebook.ipynb) |
| 3 | [Career and Competition in Indonesia with GIS](pertemuan-03-gis-career-and-competition) | Praktisi GIS* | Lokasi shelter tsunami + klasifikasi tutupan lahan | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/pertemuan-03-gis-career-and-competition/notebook.ipynb) |
| 4 | [Introduction to Machine Learning](pertemuan-04-introduction-to-machine-learning) | Dr. Tanzila Tahiddin* (UiTM) | 4 paradigma ML pada analitik akademik | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/pertemuan-04-introduction-to-machine-learning/notebook.ipynb) |
| 5 | [HCI & Data Visualization](pertemuan-05-hci-data-visualization) | Dr. Arafat Febriandirza (BRIN) | Dasbor HealthViz-HCI: Shneiderman, Tufte, Gestalt, WCAG | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/pertemuan-05-hci-data-visualization/notebook.ipynb) |
| 6 | [Attributing Direct Drivers to Deforestation Alerts](pertemuan-06-deforestation-driver-attribution) | Dr. Bart Slagter (WUR) | Atribusi pemicu deforestasi: fusi Sentinel-1/2 | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/pertemuan-06-deforestation-driver-attribution/notebook.ipynb) |

\* Nama/afiliasi pada pertemuan 1–4 dibaca dari catatan tulisan tangan; beberapa kurang terbaca. Mohon dicek dan dilengkapi.

## Menjalankan
```bash
pip install -r requirements.txt
cd pertemuan-01-make-sense-of-data && python kode.py
```
Atau buka notebook di Colab lewat badge. Setelah mengubah `kode.py`, bangun ulang notebook dengan `python tools/build_notebooks.py`.

## Catatan
- **Semua data sintetis** (dibangkitkan program, seed tetap). Nama rumah sakit pada pertemuan 5 fiktif. Hasil numerik tidak mencerminkan performa pada data nyata.
- Berkas workflow KNIME (`.knwf`) tidak disertakan karena harus diekspor dari aplikasi KNIME; panduan node per node tersedia di tiap `KNIME_GUIDE.md`.
- Pertemuan 2 mengukur waktu komputasi sehingga hasilnya berbeda antarmesin.

## Ringkasan materi
Catatan ringkas kuliah (format 1 lembar) tersedia pada ringkasan di tiap README pertemuan.
