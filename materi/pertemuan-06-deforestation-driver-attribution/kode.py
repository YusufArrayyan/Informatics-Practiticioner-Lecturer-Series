# %% [markdown]
# # Pertemuan 6 — Attributing Direct Drivers to Deforestation Alerts with Satellite Imagery and AI
# **Studi kasus:** Sistem atribusi pemicu langsung deforestasi untuk Balai Penegakan Hukum Kehutanan di Bengkulu.
# Setiap poligon peringatan kehilangan kanopi diberi label pemicu: `Sawit_Industri`, `Pertanian_Rakyat`,
# `Tambang`, atau `Jalan_Penebangan`, agar patroli bisa diprioritaskan.
#
# Konsep dari materi:
# - Dari pertanyaan **"di mana"** ke **"mengapa"** (atribusi pemicu)
# - **Fusi multi-sensor:** optik Sentinel-2 (NDVI, NBR) + radar Sentinel-1 (VH, VH/VV) yang menembus awan
# - Fitur **morfologi poligon** (luas, elongasi) dan **deret waktu pascagangguan** (pemulihan NDVI)
# - Tantangan **class imbalance**
#
# > Data **sintetis** (rentang fitur dirancang berdasarkan karakteristik umum tiap pemicu). Akurasi di sini
# > tidak mencerminkan performa pada citra nyata. Penerapan nyata memakai data latih beranotasi ahli (mis. ForestNet)
# > dan validasi lapangan. Lokasi alert di bagian 7 adalah simulasi.

# %%
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, confusion_matrix, recall_score, f1_score

os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 110})
np.random.seed(42)
rng = np.random.default_rng(42)

# %% [markdown]
# ## 1. Dataset sintetis peringatan deforestasi
# Fitur: luas (ha), elongasi bentuk, penurunan NDVI & NBR (optik), backscatter VH & rasio VH/VV (radar),
# dan **pemulihan NDVI 90 hari** (fitur deret waktu).
# Catatan: kelas `Tambang` hanya menyatakan *bukaan tambang terdeteksi*; status legal/ilegal perlu dicek ke data izin (overlay IUP).

# %%
n = 250
def kelas(nama, luas, elong, ndvi, nbr, vh, ratio, pulih):
    u = lambda lo_hi: rng.uniform(lo_hi[0], lo_hi[1], n)
    return pd.DataFrame({"Luas_Hektare": u(luas), "Elongasi_Shape": u(elong), "NDVI_Drop": u(ndvi), "NBR_Drop": u(nbr),
                         "SAR_VH_dB": u(vh), "SAR_Ratio_VHVV": u(ratio), "NDVI_Pulih_90hr": u(pulih), "Driver": nama})

df = pd.concat([
    kelas("Sawit_Industri",   (15, 85),  (0.70, 0.95), (0.35, 0.60), (0.30, 0.55), (-17.5, -15.0), (0.35, 0.50), (0.10, 0.30)),
    kelas("Pertanian_Rakyat", (0.5, 3.2), (0.40, 0.75), (0.20, 0.45), (0.15, 0.40), (-15.5, -13.0), (0.45, 0.60), (0.25, 0.55)),
    kelas("Tambang",          (3, 25),   (0.50, 0.85), (0.65, 0.90), (0.60, 0.85), (-22.0, -18.5), (0.20, 0.35), (0.00, 0.08)),
    kelas("Jalan_Penebangan", (1.5, 12), (0.05, 0.28), (0.40, 0.70), (0.35, 0.65), (-18.0, -14.5), (0.30, 0.48), (0.05, 0.25)),
], ignore_index=True)

# Derau pengukuran sensor agar kelas saling tumpang-tindih (lebih realistis)
SIGMA = {"Luas_Hektare": 0.12, "Elongasi_Shape": 0.08, "NDVI_Drop": 0.08, "NBR_Drop": 0.08,
         "SAR_VH_dB": 1.4, "SAR_Ratio_VHVV": 0.05, "NDVI_Pulih_90hr": 0.07}
for kol, s in SIGMA.items():
    base = df[kol].copy()
    df[kol] = base * (1 + rng.normal(0, s, len(df))) if kol == "Luas_Hektare" else base + rng.normal(0, s, len(df))
df["Luas_Hektare"] = df["Luas_Hektare"].clip(lower=0.2)
df["Elongasi_Shape"] = df["Elongasi_Shape"].clip(0.01, 1.0)
df.round(4).to_csv("data/peringatan_deforestasi_sintetis.csv", index=False)
print(df["Driver"].value_counts().to_string())
print(df.groupby("Driver").mean(numeric_only=True).round(2).T)

# %% [markdown]
# ## 2. Pelatihan model atribusi (Random Forest) & evaluasi

# %%
FITUR_OPTIK = ["NDVI_Drop", "NBR_Drop"]
FITUR_SAR = ["SAR_VH_dB", "SAR_Ratio_VHVV"]
FITUR_MORFO = ["Luas_Hektare", "Elongasi_Shape"]
FITUR_WAKTU = ["NDVI_Pulih_90hr"]
FITUR = FITUR_MORFO + FITUR_OPTIK + FITUR_SAR + FITUR_WAKTU

X, y = df[FITUR], df["Driver"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

rf = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42, n_jobs=-1).fit(X_tr, y_tr)
y_pred = rf.predict(X_te)
print(classification_report(y_te, y_pred, digits=3))

imp = pd.Series(rf.feature_importances_, index=FITUR).sort_values(ascending=False)
print("Kontribusi fitur (%):")
print((imp * 100).round(1).to_string())

# %% [markdown]
# ## 3. Mengapa fusi multi-sensor? Ablasi dengan tutupan awan
# Di hutan tropis, sebagian citra optik tertutup awan. Kita simulasikan **40% poligon** tanpa data optik (NaN),
# lalu bandingkan: optik saja, radar saja, dan fusi optik + radar (+ morfologi + deret waktu).
# Nilai optik yang hilang diisi median (imputasi sederhana).

# %%
X_awan = X.copy()
mask_awan = rng.random(len(X_awan)) < 0.40
X_awan.loc[mask_awan, FITUR_OPTIK] = np.nan
Xa_tr, Xa_te, ya_tr, ya_te = train_test_split(X_awan, y, test_size=0.20, random_state=42, stratify=y)

skenario = {
    "Optik saja (NDVI, NBR)":                FITUR_OPTIK,
    "Radar saja (VH, VH/VV)":                FITUR_SAR,
    "Fusi optik + radar":                    FITUR_OPTIK + FITUR_SAR,
    "Fusi + morfologi + deret waktu":        FITUR,
}
hasil = []
for nama, kolom in skenario.items():
    m = make_pipeline(SimpleImputer(strategy="median"),
                      RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42, n_jobs=-1))
    m.fit(Xa_tr[kolom], ya_tr)
    p = m.predict(Xa_te[kolom])
    hasil.append((nama, f1_score(ya_te, p, average="macro")))
abl = pd.DataFrame(hasil, columns=["fitur", "F1_macro"]).round(3)
print(abl.to_string(index=False))

print("Catatan: skor 1.0 pada baris terakhir terjadi karena fitur morfologi (luas, elongasi) memisahkan kelas hampir sempurna "
      "pada data sintetis. Pada data nyata, bentuk poligon saja jarang cukup; yang ingin ditunjukkan di sini adalah "
      "radar menjaga performa saat optik hilang.")
fig, ax = plt.subplots(figsize=(7, 3.4))
ax.barh(abl["fitur"], abl["F1_macro"], color=["#98A2B3", "#98A2B3", "#1570EF", "#1570EF"], height=0.55)
ax.invert_yaxis(); ax.set_xlim(0, 1)
for i, v in enumerate(abl["F1_macro"]):
    ax.text(v + 0.01, i, f"{v:.2f}", va="center", fontweight="bold")
ax.set_xlabel("F1 macro (dengan 40% poligon tertutup awan)")
ax.set_title("Nilai tambah fusi multi-sensor")
plt.tight_layout()
plt.savefig("output/06_ablasi_fusi_sensor.png", dpi=200)
plt.show()

# %% [markdown]
# ## 4. Tantangan class imbalance
# Di lapangan, tambang liar jauh lebih jarang daripada ladang kecil. Kita buat data latih dengan kelas `Tambang`
# hanya ±8% dan bandingkan **recall** kelas itu antara model biasa dan `class_weight="balanced"`.

# %%
tr = pd.concat([X_tr, y_tr], axis=1)
tambang_idx = tr[tr["Driver"] == "Tambang"].sample(frac=0.12, random_state=1).index
tr_imb = pd.concat([tr[tr["Driver"] != "Tambang"], tr.loc[tambang_idx]])
print("Distribusi kelas latih (tidak seimbang):")
print(tr_imb["Driver"].value_counts().to_string())

baris = []
for nama, cw in [("Tanpa penyeimbangan", None), ("class_weight='balanced'", "balanced")]:
    m = RandomForestClassifier(n_estimators=150, max_depth=8, class_weight=cw, random_state=42, n_jobs=-1)
    m.fit(tr_imb[FITUR], tr_imb["Driver"])
    p = m.predict(X_te)
    baris.append((nama, recall_score(y_te, p, labels=["Tambang"], average=None)[0], f1_score(y_te, p, average="macro")))
imb = pd.DataFrame(baris, columns=["strategi", "recall_Tambang", "F1_macro"]).round(3)
print(imb.to_string(index=False))
print("\nRecall kelas langka krusial: tambang yang terlewat berarti perambahan tidak tertangani.")
print("Catatan: pada data sintetis yang mudah dipisahkan ini dampak ketidakseimbangan kecil, dan pembobotan bisa "
      "menukar sedikit presisi dengan recall. Pada citra nyata (kelas tumpang-tindih) dampaknya biasanya jauh lebih besar.")

# %% [markdown]
# ## 5. Matriks konfusi & kontribusi fitur

# %%
labels = sorted(y.unique())
cm = confusion_matrix(y_te, y_pred, labels=labels)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
cax = ax1.matshow(cm, cmap="Blues", alpha=0.85)
fig.colorbar(cax, ax=ax1, fraction=0.046, pad=0.04)
ax1.set_xticks(range(len(labels))); ax1.set_yticks(range(len(labels)))
ax1.set_xticklabels(labels, rotation=35, ha="left", fontsize=9, fontweight="bold")
ax1.set_yticklabels(labels, fontsize=9, fontweight="bold")
ax1.set_title("Matriks konfusi atribusi pemicu", fontsize=12, fontweight="bold", pad=20)
ax1.set_xlabel("Prediksi model", fontweight="bold", labelpad=10); ax1.set_ylabel("Kondisi aktual", fontweight="bold")
for i in range(len(labels)):
    for j in range(len(labels)):
        ax1.text(j, i, str(cm[i, j]), ha="center", va="center",
                 color="black" if cm[i, j] < cm.max() / 2 else "white", fontweight="bold")

ax2.barh(imp.index, imp.values * 100, color="#1570EF", height=0.55)
ax2.invert_yaxis()
ax2.set_title("Kontribusi fitur (%)", fontsize=12, fontweight="bold", pad=15)
ax2.set_xlabel("Kepentingan fitur (%)", fontweight="bold")
for i, v in enumerate(imp.values * 100):
    ax2.text(v + 0.3, i, f"{v:.1f}%", va="center", fontsize=9, fontweight="bold")
plt.tight_layout()
plt.savefig("output/06_evaluasi_model.png", dpi=200, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 6. Inferensi pada peringatan baru (SIMULASI) + prioritas patroli
# Rekomendasi memakai **probabilitas** dan ambang keyakinan: prediksi dengan keyakinan rendah diarahkan ke verifikasi
# citra resolusi tinggi, bukan langsung ke tindakan lapangan.

# %%
alert_baru = pd.DataFrame([
    # Luas, Elongasi, NDVI_Drop, NBR_Drop, VH, VH/VV, NDVI_Pulih
    [42.5, 0.88, 0.48, 0.42, -16.2, 0.41, 0.18],
    [3.2, 0.12, 0.55, 0.49, -16.8, 0.38, 0.12],
    [9.1, 0.65, 0.78, 0.72, -20.5, 0.26, 0.03],
], columns=FITUR_MORFO + FITUR_OPTIK + FITUR_SAR + FITUR_WAKTU)[FITUR]
lokasi = ["Alert simulasi A (penyangga hutan lindung)", "Alert simulasi B (koridor di dalam hutan)", "Alert simulasi C (bantaran sungai)"]

prob = rf.predict_proba(alert_baru)
pred = rf.classes_[prob.argmax(axis=1)]
PRIORITAS_1 = {"Tambang", "Jalan_Penebangan"}
for i in range(len(alert_baru)):
    yakin = prob[i].max() * 100
    print(f"{lokasi[i]}")
    print(f"  -> Pemicu terdeteksi : {pred[i]}  (keyakinan {yakin:.1f}%)")
    if yakin < 60:
        aksi = "VERIFIKASI: keyakinan rendah, cek citra resolusi tinggi sebelum menerjunkan tim"
    elif pred[i] in PRIORITAS_1:
        aksi = "PRIORITAS 1: koordinasikan tim penegakan hukum untuk verifikasi lapangan (cek izin/IUP)"
    else:
        aksi = "PRIORITAS 2: pantau dengan citra resolusi tinggi"
    print(f"  -> Rekomendasi       : {aksi}\n")

# %% [markdown]
# ## Ringkasan
# - Atribusi pemicu mengubah peringatan "di mana & kapan" menjadi informasi "mengapa", sehingga patroli lebih terarah.
# - Radar menjaga performa saat optik tertutup awan; fusi dan fitur deret waktu menambah daya pembeda.
# - Class imbalance perlu ditangani (bobot kelas, resampling) dan dievaluasi lewat recall kelas langka.
# - Prediksi model = **petunjuk prioritas**, bukan bukti hukum: butuh verifikasi lapangan dan data perizinan.
# - Arah riset lanjutan dari materi: Edge AI untuk drone/gawai, CNN/U-Net/Transformer pada citra asli, serta dasbor
#   yang ramah polisi hutan (lihat Pertemuan 5).
