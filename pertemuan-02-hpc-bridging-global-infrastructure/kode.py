# %% [markdown]
# # Pertemuan 2 — Bridging Global Infrastructure to Address Local Challenge with HPC
# **Studi kasus:** Simulasi Monte Carlo risiko banjir (curah hujan ekstrem) untuk satu daerah tangkapan air,
# dijalankan **serial vs paralel**. Tujuannya menunjukkan alasan HPC dipakai untuk masalah lokal: jutaan skenario
# perlu dihitung dalam waktu singkat.
#
# Konsep dari materi yang didemokan:
# - Pembagian kerja ke banyak inti (*parallel computing*)
# - *Speedup* dan *efficiency*
# - **Hukum Amdahl**: bagian serial membatasi percepatan
# - *Strong scaling* (beban tetap) vs *weak scaling* (beban tumbuh bersama jumlah inti)
#
# > Parameter hujan di bawah adalah **model mainan** untuk demonstrasi komputasi, bukan model hidrologi terkalibrasi.

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
# ## Ringkasan
# - Masalah *embarrassingly parallel* (skenario saling bebas) cocok untuk HPC.
# - Speedup nyata < ideal karena bagian serial (pembagian tugas, pengumpulan hasil, overhead proses).
# - Hukum Amdahl memberi batas atas percepatan; strong vs weak scaling menjawab pertanyaan berbeda.
