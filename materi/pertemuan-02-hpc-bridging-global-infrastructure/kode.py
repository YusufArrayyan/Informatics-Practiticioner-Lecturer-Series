# %% [markdown]
# # Pertemuan 2 — Bridging Global Infrastructure to Address Local Challenge with HPC
# **Studi Kasus:** Simulasi Monte Carlo Risiko Banjir secara Serial dan Paralel
#
# **Identitas**
# - Nama: Muhammad Yusuf Arrayyan
# - NPM: G1A024009
# - Program Studi: S1 Teknik Informatika, Universitas Bengkulu (UNIB)
# - Kegiatan: Informatics Practitioner Lecture Series
# - Narasumber: Asst. Prof. Dr. Worawan Diaz Carballo, Thammasat University, Thailand (ejaan nama dari catatan tulisan tangan)
#
# > Model hujan pada notebook ini adalah **model mainan** untuk mendemonstrasikan komputasi paralel, bukan model hidrologi yang dikalibrasi.
#
# ## Ringkasan Materi
# 1. Di era AI dan data besar, **komputasi berkinerja tinggi (High Performance Computing, HPC)** menjadi penting untuk simulasi, pemodelan, dan pelatihan model AI skala besar yang tidak praktis dijalankan di komputer biasa.
# 2. Infrastruktur HPC global dapat dimanfaatkan untuk menjawab **masalah lokal**, misalnya sains iklim dan cuaca, pertanian, serta kesehatan, melalui akses bersama dan kolaborasi lintas negara.
# 3. Pengembangan kapasitas: pelatihan (*bootcamp*), kompetisi HPC-AI, dan kolaborasi regional ASEAN, termasuk gambaran superkomputer dunia dan infrastruktur nasional.
# 4. Pesan bagi mahasiswa: HPC bisa dipelajari bertahap, dimulai dari konsep paralelisme sebelum naik ke klaster dan kompetisi.
#
# ## Latar Belakang
# Bengkulu dan banyak daerah di Indonesia menghadapi risiko banjir akibat hujan ekstrem. Menaksir **peluang hujan ekstrem melampaui kapasitas drainase** membutuhkan simulasi *Monte Carlo*: ribuan hingga jutaan skenario badai dibangkitkan secara acak, lalu dihitung berapa persen yang menyebabkan banjir. Makin banyak skenario, makin stabil estimasinya, tetapi waktu hitung ikut membesar.
#
# Karakteristik pentingnya: tiap skenario **saling bebas**, sehingga pekerjaan ini disebut *embarrassingly parallel* dan sangat cocok dibagi ke banyak inti prosesor. Inilah jembatan antara konsep HPC dari narasumber dan masalah lokal: dengan membagi kerja, simulasi yang lama dapat diselesaikan jauh lebih cepat.
#
# ## Rumusan Masalah
# 1. Bagaimana mengestimasi peluang banjir dengan simulasi Monte Carlo?
# 2. Seberapa besar percepatan (*speedup*) yang diperoleh dengan membagi simulasi ke beberapa proses?
# 3. Apa yang membatasi percepatan tersebut (hukum Amdahl)?
# 4. Bagaimana perilaku sistem jika beban dan jumlah inti sama-sama dinaikkan (*weak scaling*)?
#
# ## Tujuan
# 1. Mengimplementasikan simulasi Monte Carlo serial dan paralel.
# 2. Mengukur speedup dan efisiensi, serta mengestimasi porsi paralel program.
# 3. Membedakan *strong scaling* dan *weak scaling*.
# 4. Mengekstrapolasi waktu hitung untuk simulasi yang jauh lebih besar.
#
# ## Dasar Teori
# - **Speedup** `S(p) = T1 / Tp`, dengan T1 waktu pada satu pekerja dan Tp waktu pada p pekerja. **Efisiensi** `E(p) = S(p) / p`.
# - **Hukum Amdahl:** `S(p) = 1 / ((1 − f) + f/p)`, dengan f porsi program yang dapat diparalelkan. Bagian serial (1 − f) membatasi percepatan maksimum menjadi `1/(1 − f)`, berapa pun jumlah intinya.
# - **Strong scaling:** beban total tetap, jumlah inti ditambah. **Weak scaling:** beban per inti tetap, sehingga beban total tumbuh bersama jumlah inti; idealnya waktu tetap konstan.
# - **Monte Carlo:** estimasi probabilitas dari proporsi kejadian pada banyak sampel acak; galat menurun sebanding 1/√N.
# - **multiprocessing (Python):** membuat banyak proses terpisah sehingga tidak dibatasi *Global Interpreter Lock*.
#
# ## Dataset dan Model
# Tidak ada dataset eksternal; data dibangkitkan oleh simulasi. Satu skenario adalah badai 72 jam:
# - intensitas badai ~ lognormal (σ = 0,6) sebagai pengali,
# - hujan per jam ~ gamma (shape 0,35; skala 9 mm),
# - banjir terjadi bila hujan **6 jam berturut-turut melebihi 150 mm** (ambang drainase asumsi).
#
# ## Metodologi
# 1. Fungsi `simulasi_chunk` menjalankan sebagian skenario pada satu proses.
# 2. `jalankan` membagi total skenario ke p pekerja dan mengukur waktu terbaik dari 3 percobaan.
# 3. Strong scaling: N tetap, p = 1, 2, … hingga jumlah inti tersedia.
# 4. Estimasi f dari hukum Amdahl, lalu bandingkan kurva teoritis dengan hasil ukur.
# 5. Weak scaling: N dikalikan p.
# 6. Ekstrapolasi waktu untuk 10 juta dan 100 juta skenario.
#
# ## Implementasi
# Waktu hitung bergantung pada mesin (jumlah inti, beban lain di sistem), sehingga angka pada sel **Interpretasi** di bawah adalah *contoh* dari satu kali jalan pada mesin 2 inti, bukan nilai tetap.

# %%
import os
import time
import multiprocessing as mp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 110})

CPU = os.cpu_count() or 1
print("Jumlah inti CPU tersedia:", CPU)

# %% [markdown]
# ## 1. Model simulasi (satu "pekerja")
# Tiap skenario = badai 72 jam. Banjir terjadi bila curah hujan 6 jam berturut-turut melebihi ambang drainase.

# %%
AMBANG_MM_6JAM = 150.0  # kapasitas drainase (mm per 6 jam), asumsi demonstrasi

def simulasi_chunk(args):
    """Menjalankan n skenario dengan seed tertentu, mengembalikan jumlah kejadian banjir."""
    seed, n = args
    rng = np.random.default_rng(seed)
    banjir = 0
    sisa = n
    while sisa > 0:
        m = min(5000, sisa)
        intensitas = rng.lognormal(mean=0.0, sigma=0.6, size=(m, 1))   # kekuatan badai
        hujan = rng.gamma(shape=0.35, scale=9.0, size=(m, 72)) * intensitas
        c = np.cumsum(hujan, axis=1)
        r6 = c[:, 6:] - c[:, :-6]
        banjir += int((r6.max(axis=1) > AMBANG_MM_6JAM).sum())
        sisa -= m
    return banjir

def jalankan(n_total, n_pekerja, seed=2026, ulang=3):
    """Membagi n_total skenario ke n_pekerja proses; waktu = terbaik dari `ulang` percobaan (mengurangi noise)."""
    per = [n_total // n_pekerja] * n_pekerja
    per[0] += n_total - sum(per)
    tugas = [(seed + i, k) for i, k in enumerate(per)]
    waktu_terbaik, hasil = float("inf"), None
    for _ in range(ulang):
        t0 = time.perf_counter()
        if n_pekerja == 1:
            hasil = [simulasi_chunk(tugas[0])]
        else:
            with mp.Pool(n_pekerja) as pool:
                hasil = pool.map(simulasi_chunk, tugas)
        waktu_terbaik = min(waktu_terbaik, time.perf_counter() - t0)
    return sum(hasil) / n_total, waktu_terbaik

# %% [markdown]
# ## 2. Strong scaling: beban tetap, inti ditambah

# %%
N_TOTAL = int(os.environ.get("HPC_N_TOTAL", 600_000))
pekerja = sorted({1, 2, 4, min(8, CPU)} | {CPU if CPU <= 8 else 8})
pekerja = [p for p in pekerja if p <= max(CPU, 2)]
print("Jumlah pekerja yang diuji:", pekerja)

baris = []
for p in pekerja:
    prob, t = jalankan(N_TOTAL, p)
    baris.append((p, t, prob))
    print(f"{p:>2} pekerja | waktu {t:6.2f} s | P(banjir) = {prob:.4%}")

strong = pd.DataFrame(baris, columns=["pekerja", "waktu_s", "prob_banjir"])
t1 = strong.loc[strong["pekerja"] == 1, "waktu_s"].iloc[0]
strong["speedup"] = t1 / strong["waktu_s"]
strong["efisiensi"] = strong["speedup"] / strong["pekerja"]
strong.to_csv("data/hasil_strong_scaling.csv", index=False)
print(strong.round(3))

# %% [markdown]
# ### Interpretasi: strong scaling
# - **Peluang banjir** hasil simulasi sekitar 4,6% (4,62% dengan 1 pekerja, 4,60% dengan 2 pekerja). Nilainya hampir sama karena yang berubah hanya cara pembagian kerja, bukan modelnya. Selisih kecil muncul karena setiap pekerja memakai seed yang berbeda.
# - Pada contoh jalan di mesin 2 inti, waktu turun dari ±2,40 detik (1 pekerja) menjadi ±1,22 detik (2 pekerja): speedup ±1,96× dan efisiensi ±0,98. Hasilnya mendekati ideal (2×) tetapi tidak sempurna karena ada biaya membuat proses dan mengumpulkan hasil.
# - **Angka waktu bergantung pada mesin** dan beban sistem saat dijalankan. Di Colab atau laptop lain hasilnya akan berbeda; yang konsisten adalah polanya: waktu turun dan efisiensi sedikit di bawah 1.

# %% [markdown]
# ## 3. Hukum Amdahl: estimasi porsi paralel
# $S(p) = \dfrac{1}{(1-f) + f/p}$ dengan $f$ = porsi program yang dapat diparalelkan.
# Dari tiap pengukuran dengan $p>1$: $f = \dfrac{1 - 1/S}{1 - 1/p}$.

# %%
uji = strong[strong["pekerja"] > 1]
f_est = float(np.clip(((1 - 1 / uji["speedup"]) / (1 - 1 / uji["pekerja"])).mean(), 0, 1)) if len(uji) else float("nan")
print(f"Estimasi porsi paralel f = {f_est:.3f}")
if f_est < 1:
    print(f"Batas speedup teoritis (p -> tak hingga) = {1 / (1 - f_est):.1f}x")

p_kurva = np.arange(1, max(strong['pekerja']) * 2 + 1)
amdahl = 1 / ((1 - f_est) + f_est / p_kurva)

fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(p_kurva, p_kurva, "--", color="#98A2B3", label="Ideal (linear)")
ax.plot(p_kurva, amdahl, color="#D9383A", label=f"Amdahl (f={f_est:.2f})")
ax.scatter(strong["pekerja"], strong["speedup"], color="#1570EF", zorder=5, s=60, label="Terukur")
ax.set_xlabel("Jumlah pekerja (proses)")
ax.set_ylabel("Speedup")
ax.set_title("Strong scaling: simulasi Monte Carlo banjir")
ax.legend(frameon=False)
ax.grid(linestyle=":", alpha=0.5)
plt.tight_layout()
plt.savefig("output/02_strong_scaling_amdahl.png", dpi=200)
plt.show()

# %% [markdown]
# ### Interpretasi: hukum Amdahl
# - Porsi paralel f yang terestimasi sekitar 0,98 pada contoh jalan. Artinya hanya ±2% program bersifat serial (pembagian tugas, pembuatan proses, penggabungan hasil).
# - Batas percepatan teoritis `1/(1 − f)` sekitar 45,8× berapa pun jumlah inti. Inilah inti hukum Amdahl: **menambah inti memberi hasil yang makin menurun jika ada bagian serial**, sehingga mengurangi bagian serial sama pentingnya dengan menambah perangkat keras.
# - Estimasi f dihitung dari satu titik data (p = 2) sehingga sangat sensitif terhadap derau pengukuran waktu. Pada eksekusi lain nilainya bisa berkisar sekitar 0,9–1,0. Jalankan di mesin dengan lebih banyak inti untuk estimasi yang lebih andal.

# %% [markdown]
# ## 4. Weak scaling: beban tumbuh sebanding jumlah inti
# Idealnya waktu tetap konstan. Efisiensi = $T_1 / T_p$.

# %%
BASE = N_TOTAL // 3
baris = []
for p in pekerja:
    _, t = jalankan(BASE * p, p)
    baris.append((p, BASE * p, t))
weak = pd.DataFrame(baris, columns=["pekerja", "skenario", "waktu_s"])
weak["efisiensi_weak"] = weak["waktu_s"].iloc[0] / weak["waktu_s"]
weak.to_csv("data/hasil_weak_scaling.csv", index=False)
print(weak.round(3))

# %% [markdown]
# ### Interpretasi: weak scaling
# - Pada weak scaling, beban per inti tetap (200.000 skenario per pekerja), sehingga waktu idealnya konstan. Pada contoh jalan, 1 pekerja dengan 200.000 skenario memerlukan ±0,76 detik dan 2 pekerja dengan 400.000 skenario ±0,88 detik: **efisiensi weak scaling ±0,86**.
# - Efisiensi di bawah 1 mencerminkan overhead (pembuatan proses, pengumpulan hasil). Pada klaster nyata, **komunikasi antarnode** dan I/O menjadi penyebab utama.

# %% [markdown]
# ## 5. Apa artinya untuk masalah lokal?
# Dengan kecepatan hasil di atas, kita bisa menghitung perkiraan waktu untuk simulasi yang jauh lebih besar.

# %%
t_per_skenario = t1 / N_TOTAL
for target in [10_000_000, 100_000_000]:
    serial = target * t_per_skenario
    paralel = serial / strong["speedup"].max()
    print(f"{target:>11,} skenario | serial ≈ {serial/60:7.1f} menit | "
          f"{int(strong['pekerja'].max())} inti ≈ {paralel/60:7.1f} menit")
print("\nCatatan: pada klaster HPC sungguhan, jumlah inti ratusan hingga ribuan dan kendala utama "
      "bergeser ke komunikasi antarnode serta I/O.")

# %% [markdown]
# ### Interpretasi: dari lokal ke skala HPC
# - Simulasi 10 juta skenario memerlukan ±0,7 menit secara serial dan ±0,3 menit dengan 2 inti; 100 juta skenario ±6,7 menit serial dan ±3,4 menit dengan 2 inti (ekstrapolasi dari waktu terukur).
# - Model nyata (resolusi tinggi, banyak variabel) bisa ribuan kali lebih berat. Pembagian kerja ke ratusan atau ribuan inti pada klaster HPC mengubah waktu hitung dari hari menjadi jam.
# - Itulah makna "menjembatani infrastruktur global untuk tantangan lokal": daerah dapat menjalankan simulasi besar tanpa memiliki superkomputer sendiri, asalkan memahami cara membagi pekerjaan.

# %% [markdown]
# ## Ringkasan
# - Masalah *embarrassingly parallel* (skenario saling bebas) cocok untuk HPC.
# - Speedup nyata < ideal karena bagian serial (pembagian tugas, pengumpulan hasil, overhead proses).
# - Hukum Amdahl memberi batas atas percepatan; strong vs weak scaling menjawab pertanyaan berbeda.

# %% [markdown]
# ## Hasil dan Pembahasan (ringkasan)
# | Aspek | Temuan |
# |---|---|
# | Estimasi peluang banjir | ±4,6%, konsisten pada semua konfigurasi pekerja |
# | Strong scaling | Speedup ±1,96× pada 2 inti (efisiensi ±0,98); makin banyak inti, efisiensi makin turun karena bagian serial |
# | Hukum Amdahl | Porsi paralel ±0,98 membatasi speedup maksimum teoritis ±46× (sensitif terhadap derau waktu) |
# | Weak scaling | Efisiensi ±0,86 pada 2 inti; turun oleh overhead |
#
# ## Kesimpulan
# 1. Simulasi Monte Carlo yang saling bebas sangat cocok diparalelkan dan memberi percepatan nyata.
# 2. Percepatan dibatasi bagian serial program (hukum Amdahl), sehingga hasil tidak pernah sepenuhnya linear.
# 3. Strong dan weak scaling menjawab pertanyaan berbeda: "seberapa cepat beban tetap selesai" vs "seberapa besar beban yang dapat ditangani".
# 4. Konsep ini menjadi dasar memanfaatkan infrastruktur HPC untuk masalah lokal seperti risiko bencana.
#
# ## Keterbatasan
# - Percobaan berjalan pada satu mesin dengan memori bersama; klaster sungguhan memiliki komunikasi jaringan antarnode.
# - Hasil waktu bervariasi antarmesin dan antarjalan karena beban sistem lain.
# - Model hujan sangat disederhanakan; hasilnya tidak untuk keputusan mitigasi nyata.
#
# ## Saran Pengembangan
# - Mengganti model mainan dengan model hidrologi sederhana yang dikalibrasi data curah hujan (BMKG).
# - Mencoba `mpi4py` atau Dask untuk membagi kerja antarmesin, lalu menjalankannya di klaster kampus atau layanan HPC nasional/regional.
# - Mengikuti pelatihan dan kompetisi HPC-AI seperti yang disebut narasumber.
# - Menyusun workflow paralel di KNIME dengan *Parallel Chunk Start/End* (lihat `KNIME_GUIDE.md`).
#
# ## Referensi
# > Rujukan di bawah adalah bacaan lanjutan. Periksa kembali penulisan, tahun, dan volume sebelum dikutip dalam laporan resmi.
# - Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. *AFIPS Spring Joint Computer Conference*.
# - Gustafson, J. L. (1988). Reevaluating Amdahl's Law. *Communications of the ACM*, 31(5), 532–533.
# - Metropolis, N., & Ulam, S. (1949). The Monte Carlo method. *Journal of the American Statistical Association*, 44(247), 335–341.
# - Dokumentasi Python: modul `multiprocessing`.
# - Materi Practitioner Lecture Series, Pertemuan 2 (catatan kuliah).
