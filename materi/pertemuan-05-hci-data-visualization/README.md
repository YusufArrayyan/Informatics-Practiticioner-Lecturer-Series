# Pertemuan 5 — Human-Computer Interaction (HCI) & Data Visualization

[![Buka di Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YusufArrayyan/Informatics-Practiticioner-Lecturer-Series/blob/main/Pertemuan_5_HCI_Visualisasi_Data.ipynb)

**Narasumber:** Dr. Arafat Febriandirza, S.T., M.T.I. (Ketua Kelompok Riset Interaksi Manusia Komputer dan Visualisasi, Pusat Riset Sains Data dan Informasi, BRIN)
**Penyelenggara:** Program Studi S1 Teknik Informatika, Universitas Bengkulu
**Rekaman:** [YouTube, Informatika UNIB Official](https://www.youtube.com/live/5KhQm8OaYRM)

## Ringkasan materi
1. **Fondasi IMK:** siklus input → proses → output → feedback; evolusi antarmuka (kartu berlubang → CLI → GUI → NUI); prinsip *"You Are Not Your User"* dan **User-Centered Design**.
2. **Psikologi kognitif:** memori kerja terbatas (7 ± 2 unit), *recognition over recall*, tiga beban kognitif (intrinsic, germane, extraneous), dan *preattentive attributes* (<200 ms).
3. **Gestalt:** proximity, similarity, enclosure, continuity, closure, figure/ground.
4. **Konteks, aksesibilitas, etika:** WCAG (POUR), konteks fisik/sosial/teknis, penolakan *dark patterns*, grafik yang jujur.
5. **Metodologi:** siklus desain iteratif, prototipe low/high-fidelity, *Fail Early, Fail Cheap*, Heuristic Evaluation (Nielsen), Usability Testing, lima pilar Norman.
6. **Visualisasi data:** pemilihan grafik, **Tufte** (data-ink ratio, anti-chartjunk), dan **Shneiderman's Mantra**: *overview first, zoom and filter, then details-on-demand*.

## Studi kasus: HealthViz-HCI
Dinas Kesehatan Kota menolak dasbor lama karena beban kognitif ekstra (tabel panjang, grafik 3D, filter lambat). Persona: Kepala Bidang P2P, 45 tahun, memakai tablet saat rapat tanggap darurat, ingin melihat RS kritis dalam <5 detik.

| Prinsip | Implementasi |
|---|---|
| Shneiderman | KPI di atas (overview), filter kecamatan (zoom & filter), tooltip titik tren (details-on-demand) |
| Preattentive | Merah hanya untuk RS kritis (≥80%) dan lonjakan kasus |
| Tufte | Tanpa 3D/bayangan, label langsung, grid tipis |
| Gestalt | KPI dalam kartu (enclosure), warna status konsisten (similarity) |
| Norman | KPI **dihitung ulang** saat filter berubah (feedback); tinggi kontrol 44 px |
| WCAG | Audit kontras warna dan redundansi teks pada status |
| Etika | Demo *lie factor* sumbu terpotong vs jujur |

## Cara menjalankan
- **Colab:** badge → *Run all*. Dasbor HTML dibuat di `output/`; unduh lalu buka di browser (atau gunakan `IPython.display.HTML`).
- **Lokal:** `python kode.py` lalu buka `output/healthviz_dashboard_interactive.html`.
- **KNIME:** [KNIME_GUIDE.md](KNIME_GUIDE.md).

## Hasil utama
- BOR kota 77,3% (status Waspada); 2 dari 6 RS berstatus Kritis.
- **Audit kontras WCAG** terhadap latar putih: merah 4,59 (lulus), biru 4,57 (lulus), **oranye 2,19 dan hijau 2,87 gagal 3:1** untuk komponen grafis. Karena itu status selalu disertai teks, dan warna sebaiknya digelapkan pada versi produksi.
- *Lie factor* sumbu terpotong: perubahan data +5,6% tampak sebagai +200% (≈36 kali lipat).

## Perbedaan dari kode awal pada ringkasan kuliah
Kode ini mengembangkan versi awal dengan: nama/angka RS **fiktif** (agar tidak terbaca sebagai data fasilitas nyata), KPI yang ikut berubah saat filter, grafik tren interaktif, audit kontras WCAG, dan demo *lie factor*.

## Berkas
`kode.py` (notebook utama: `Pertemuan_5_HCI_Visualisasi_Data.ipynb` di akar repo), `data/*.csv`, `output/05_dasbor_statis.png`, `output/05_lie_factor.png`, `output/healthviz_dashboard_interactive.html`.
