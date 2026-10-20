# Panduan KNIME — Pertemuan 2 (komputasi paralel)

> Panduan membangun workflow di **KNIME Analytics Platform 5.x**. Berkas `.knwf` tidak disertakan (harus diekspor dari
> aplikasi). Nama node dapat berbeda antarversi.

KNIME mengeksekusi cabang workflow secara paralel sesuai jumlah thread dan memiliki mekanisme *chunk loop* untuk memecah tabel. Idenya sama dengan `multiprocessing` pada Python.

## A. Membuat tabel skenario
1. **Table Creator / Counting Loop Start** → hasilkan tabel `id_skenario` 1…N (mulai N = 100.000).
2. **Math Formula** untuk intensitas badai (lognormal): gunakan **Random Number Assigner** atau **Python Script** untuk membuat kolom `intensitas`.

## B. Simulasi per baris
3. Per skenario, hasilkan hujan 72 jam dan hitung maksimum jendela 6 jam. Cara termudah: node **Python Script** berisi fungsi `simulasi_chunk` dari `kode.py`, dengan `n` = jumlah baris pada chunk dan keluaran `banjir` (jumlah kejadian).

## C. Paralelisasi
4. Letakkan langkah 3 di antara **Parallel Chunk Start** dan **Parallel Chunk End** (kategori *Workflow Control → Parallel Chunk Loop*; bila tidak ada, pasang lewat *File → Install KNIME Extensions*).
5. Atur jumlah chunk = jumlah inti CPU (mis. 1, 2, 4).
6. **GroupBy** (Sum `banjir`) → **Math Formula** `prob = sum / N`.

## D. Mengukur speedup
7. Catat waktu eksekusi tiap konfigurasi (indikator waktu pada node atau *Timer Info*).
8. Hitung `speedup = T1 / Tp` dan `efisiensi = speedup / p` dengan **Math Formula**, lalu **Line Plot** untuk speedup vs jumlah chunk.
9. Estimasi porsi paralel: `f = (1 - 1/S) / (1 - 1/p)` (hukum Amdahl) dengan Math Formula.

## E. Catatan
- Pada mesin dengan sedikit inti, speedup terbatas dan overhead pemecahan tabel terlihat jelas, ini justru inti pelajaran Amdahl.
- Untuk beban sebenarnya, kerjakan simulasi di Python (lihat `kode.py`) dan gunakan KNIME untuk orkestrasi serta visualisasi hasil.
