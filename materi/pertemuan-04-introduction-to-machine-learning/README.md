# Pertemuan 4 — Introduction to Machine Learning

[![Buka di Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/Pertemuan_4_Machine_Learning.ipynb)

**Narasumber:** Dr. Tanzila Tahiddin*, Senior Lecturer, Faculty of Computer and Mathematical Sciences, Universiti Teknologi MARA (UiTM), Malaysia
**Penyelenggara:** Program Studi S1 Teknik Informatika, Universitas Bengkulu
**Laporan studi kasus lengkap (latar belakang, rumusan masalah, tujuan, metodologi, hasil, kesimpulan):** [STUDI_KASUS.md](STUDI_KASUS.md)  
\* Ejaan nama dan afiliasi dibaca dari catatan tulisan tangan; mohon dicek.

## Ringkasan materi
- Pergeseran paradigma dari pemrograman tradisional (aturan eksplisit) ke **machine learning berbasis data**: model belajar pola dari data.
- Hubungan AI, Machine Learning (ML), dan Deep Learning (DL): ML bagian dari AI yang berfokus pada pembelajaran dari data; DL memakai jaringan saraf tiruan. Contoh algoritma: Decision Tree, SVM, hingga Deep Learning/NLP; contoh aplikasi: ChatGPT, Claude, Gemini.
- **Empat kategori ML:**
  1. *Supervised learning*: belajar dari data berlabel (klasifikasi spam, prediksi harga; regresi).
  2. *Unsupervised learning*: mencari pola pada data tanpa label (klasterisasi seperti K-Means, reduksi dimensi seperti PCA, deteksi anomali).
  3. *Reinforcement learning*: belajar lewat *trial and error* dengan reward dan penalti (mis. kendaraan otonom).
  4. *Semi-supervised learning*: sedikit data berlabel + banyak data tak berlabel untuk meningkatkan akurasi.
- **Siklus ML:** pengumpulan data, persiapan, pelatihan & pengujian, evaluasi, deployment. Prinsip **"Garbage In, Garbage Out"**: kualitas data menentukan kualitas model.

## Studi kasus
**Analitik akademik sebuah program studi** (data sintetis 800 mahasiswa): memprediksi kelulusan tepat waktu, menyegmentasi mahasiswa, bekerja dengan label sedikit, dan agen belajar berbasis reward.

| Paradigma | Implementasi |
|---|---|
| Supervised | Logistic Regression, Decision Tree, Random Forest + validasi silang, baseline, feature importance |
| GIGO | Label latih sengaja dirusak 0–40%, akurasi uji dirata-ratakan 5 kali |
| Unsupervised | K-Means (k dipilih silhouette), PCA 2D, Isolation Forest (5% anomali) |
| Semi-supervised | Label Spreading dengan 10% label vs Logistic Regression berlabel 10% |
| Reinforcement | Q-Learning di grid world 5×5 dengan zona bahaya |

## Cara menjalankan
- **Colab:** badge → *Run all*.
- **Lokal:** `python kode.py`.
- **KNIME:** [KNIME_GUIDE.md](KNIME_GUIDE.md).

## Hasil utama (seed tetap)
- Baseline tebakan mayoritas: akurasi 0,595. Logistic Regression terbaik pada uji: akurasi **0,78**, F1 **0,82**; Random Forest akurasi 0,755.
- GIGO: akurasi turun dari 0,76 (label bersih) menjadi 0,70 saat 40% label latih salah.
- K-Means: k = 2 dan 3 hampir sama (silhouette ≈ 0,215); dipilih k = 3. PCA 2 komponen menjelaskan 58,7% varians.
- Semi-supervised: pada data ini Label Spreading (rata-rata 0,69) **tidak mengalahkan** Logistic Regression berlabel 10% (0,77). Manfaat semi-supervised bergantung pada struktur data; hasil dilaporkan apa adanya.
- Q-Learning menemukan jalur 8 langkah ke tujuan dengan menghindari semua zona bahaya.

## Batasan
Data sintetis dan label dibangkitkan dari rumus yang kita tetapkan sendiri; akurasi tidak mencerminkan performa pada mahasiswa sungguhan. Penerapan nyata menuntut persetujuan data, uji keadilan (fairness), dan privasi.
