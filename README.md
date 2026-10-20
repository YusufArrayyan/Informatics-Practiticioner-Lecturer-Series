# Informatics Practitioner Lecturer Series: Studi Kasus & Implementasi

**Nama:** Muhammad Yusuf Arrayyan  
**NPM:** G1A024009  
**Program Studi:** S1 Teknik Informatika, Universitas Bengkulu (UNIB)

Kumpulan studi kasus, implementasi kode (Python/Google Colab), dan panduan workflow **KNIME** dari 6 pertemuan *Practitioner Lecture Series*.

## Notebook utama (Google Colab)
Buka langsung di Colab, lalu *Runtime → Run all*. Data dibangkitkan otomatis oleh notebook.

| # | Topik | Notebook | Materi lengkap |
|---|---|---|---|
| 1 | Make Sense of Data with Analytics and AI | [`Pertemuan_1_Analytics_and_AI.ipynb`](Pertemuan_1_Analytics_and_AI.ipynb) [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/Pertemuan_1_Analytics_and_AI.ipynb) | [materi/pertemuan-01-make-sense-of-data](materi/pertemuan-01-make-sense-of-data) |
| 2 | Bridging Global Infrastructure to Address Local Challenge with HPC | [`Pertemuan_2_HPC.ipynb`](Pertemuan_2_HPC.ipynb) [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/Pertemuan_2_HPC.ipynb) | [materi/pertemuan-02-hpc-bridging-global-infrastructure](materi/pertemuan-02-hpc-bridging-global-infrastructure) |
| 3 | Career and Competition in Indonesia with GIS | [`Pertemuan_3_GIS.ipynb`](Pertemuan_3_GIS.ipynb) [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/Pertemuan_3_GIS.ipynb) | [materi/pertemuan-03-gis-career-and-competition](materi/pertemuan-03-gis-career-and-competition) |
| 4 | Introduction to Machine Learning | [`Pertemuan_4_Machine_Learning.ipynb`](Pertemuan_4_Machine_Learning.ipynb) [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/Pertemuan_4_Machine_Learning.ipynb) | [materi/pertemuan-04-introduction-to-machine-learning](materi/pertemuan-04-introduction-to-machine-learning) |
| 5 | HCI & Data Visualization | [`Pertemuan_5_HCI_Visualisasi_Data.ipynb`](Pertemuan_5_HCI_Visualisasi_Data.ipynb) [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/Pertemuan_5_HCI_Visualisasi_Data.ipynb) | [materi/pertemuan-05-hci-data-visualization](materi/pertemuan-05-hci-data-visualization) |
| 6 | Attributing Direct Drivers to Deforestation Alerts | [`Pertemuan_6_Deforestasi_Satelit_AI.ipynb`](Pertemuan_6_Deforestasi_Satelit_AI.ipynb) [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/Pertemuan_6_Deforestasi_Satelit_AI.ipynb) | [materi/pertemuan-06-deforestation-driver-attribution](materi/pertemuan-06-deforestation-driver-attribution) |

## Struktur repo
```
README.md
requirements.txt
Pertemuan_1 … Pertemuan_6 (.ipynb)   <- notebook utama
materi/
  pertemuan-0X-…/                     <- per pertemuan
    README.md        ringkasan materi, studi kasus, hasil
    KNIME_GUIDE.md   panduan workflow KNIME
    kode.py          sumber kode (dasar pembuatan notebook)
    data/  output/   dataset sintetis & hasil
  tools/build_notebooks.py
```

## Menjalankan
- **Colab:** klik badge di tabel di atas.
- **Lokal:** `pip install -r requirements.txt`, lalu `cd materi/pertemuan-01-make-sense-of-data && python kode.py`.
- Setelah mengubah `kode.py`, bangun ulang notebook dengan `python materi/tools/build_notebooks.py`.

## Catatan
- **Semua data sintetis** (dibangkitkan program, seed tetap). Nama rumah sakit pada pertemuan 5 fiktif. Hasil numerik tidak mencerminkan performa pada data nyata.
- Berkas workflow KNIME (`.knwf`) belum disertakan; panduan node per node ada di tiap `KNIME_GUIDE.md`.
- Pertemuan 2 mengukur waktu komputasi sehingga hasilnya berbeda antarmesin.
- Nama narasumber pertemuan 1–4 dibaca dari catatan tulisan tangan dan perlu dicek.
