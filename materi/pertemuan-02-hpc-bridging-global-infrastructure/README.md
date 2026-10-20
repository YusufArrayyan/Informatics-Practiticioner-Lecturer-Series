# Pertemuan 2 — Bridging Global Infrastructure to Address Local Challenge with HPC

[![Buka di Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/Pertemuan_2_HPC.ipynb)

**Narasumber:** Asst. Prof. Dr. Worawan Diaz Carballo, Thammasat University, Thailand*
**Penyelenggara:** Program Studi S1 Teknik Informatika, Universitas Bengkulu
\* Ejaan nama dibaca dari catatan tulisan tangan; mohon dicek.

## Ringkasan materi
- Era AI dan data besar membuat komputasi berkinerja tinggi (**HPC**) menjadi penting: simulasi, pemodelan, dan pelatihan model AI skala besar tidak praktis di komputer biasa.
- HPC global dimanfaatkan untuk masalah **lokal** nyata (contoh yang dibahas: sains iklim dan cuaca, pertanian, kesehatan/obat) lewat akses ke infrastruktur bersama.
- Pengembangan kapasitas: pelatihan (*bootcamp*), kompetisi HPC-AI, dan kolaborasi regional ASEAN, termasuk gambaran superkomputer dunia dan infrastruktur nasional (mis. Thailand).
- Pesan bagi mahasiswa: HPC dapat dipelajari bertahap dari konsep paralelisme, lalu naik ke klaster dan kompetisi.

## Studi kasus
**Simulasi Monte Carlo risiko banjir untuk satu daerah tangkapan air**, dijalankan serial vs paralel. Menjawab pertanyaan: "berapa peluang hujan ekstrem melampaui kapasitas drainase?" Estimasi akurat membutuhkan jutaan skenario, sehingga percepatan paralel relevan.

| Konsep materi | Implementasi |
|---|---|
| Paralelisme (embarrassingly parallel) | `multiprocessing.Pool` membagi skenario ke banyak proses |
| Speedup & efisiensi | Tabel dan grafik strong scaling |
| Batas percepatan (hukum Amdahl) | Estimasi porsi paralel *f* dan kurva teoritis |
| Strong vs weak scaling | Dua eksperimen terpisah |
| Dari lokal ke skala HPC | Ekstrapolasi waktu untuk 10 juta dan 100 juta skenario |

## Cara menjalankan
- **Colab:** badge di atas → *Run all*. Colab biasanya menyediakan 2 inti CPU, sehingga hasil memperlihatkan p = 1 dan 2.
- **Lokal:** `python kode.py`. Variabel lingkungan `HPC_N_TOTAL` mengatur jumlah skenario (default 600.000).
- **KNIME:** [KNIME_GUIDE.md](KNIME_GUIDE.md).

## Hasil (contoh satu kali jalan di mesin 2 inti; **berbeda antarmesin dan antarjalan**)
- Peluang banjir terestimasi ≈ 4,6% pada kedua konfigurasi (hasil statistik konsisten, ±0,02 poin karena seed berbeda per pekerja).
- Speedup 2 pekerja ≈ 1,8× (efisiensi ≈ 0,9). Estimasi *f* ≈ 0,9 → batas teoritis beberapa kali lipat saja.
- Waktu diukur sebagai yang terbaik dari 3 percobaan untuk mengurangi noise, tetapi pada mesin bersama variasi tetap ada.

## Berkas
| Berkas | Isi |
|---|---|
| `kode.py` (notebook utama: `Pertemuan_2_HPC.ipynb` di akar repo) | Implementasi |
| `data/hasil_strong_scaling.csv`, `data/hasil_weak_scaling.csv` | Hasil pengukuran jalan terakhir |
| `output/02_strong_scaling_amdahl.png` | Grafik speedup vs Amdahl |

## Batasan
Model hujan adalah **model mainan** untuk demonstrasi komputasi, bukan model hidrologi terkalibrasi. Pada klaster HPC sungguhan, komunikasi antarnode dan I/O menjadi kendala utama; demo ini hanya satu mesin (memori bersama).
