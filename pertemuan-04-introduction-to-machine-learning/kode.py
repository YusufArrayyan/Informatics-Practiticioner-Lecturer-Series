# %% [markdown]
# # Pertemuan 4 — Introduction to Machine Learning
# **Studi kasus:** Analitik akademik sebuah program studi: memprediksi kelulusan tepat waktu, menyegmentasi
# mahasiswa, memanfaatkan data berlabel yang sedikit, dan mendemokan pembelajaran berbasis *reward*.
#
# Empat paradigma dari materi, masing-masing satu demo:
# | Paradigma | Demo di notebook |
# |---|---|
# | Supervised | Klasifikasi kelulusan tepat waktu (Logistic Regression, Decision Tree, Random Forest) |
# | Unsupervised | Segmentasi mahasiswa (K-Means), reduksi dimensi (PCA), deteksi anomali (Isolation Forest) |
# | Semi-supervised | Label Spreading dengan hanya 10% data berlabel |
# | Reinforcement | Q-Learning agen di *grid world* |
#
# Siklus ML dari materi: pengumpulan data → persiapan data → pelatihan → pengujian → evaluasi/deployment.
# Prinsip **"Garbage In, Garbage Out"** diuji di bagian 2.
#
# > Data mahasiswa di sini **sintetis**, tidak berasal dari individu nyata.

# %%
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.semi_supervised import LabelSpreading

os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 110})
rng = np.random.default_rng(42)

# %% [markdown]
# ## 1. Pengumpulan data (sintetis) & eksplorasi

# %%
n = 800
ipk_s1 = np.clip(rng.normal(3.0, 0.5, n), 1.5, 4.0)
ipk_s2 = np.clip(ipk_s1 + rng.normal(0.05, 0.25, n), 1.5, 4.0)
kehadiran = np.clip(rng.normal(82, 12, n), 30, 100)
jam_belajar = np.clip(rng.normal(12, 5, n), 0, 35)
kerja_paruh_waktu = rng.binomial(1, 0.3, n)
sks_ratio = np.clip(0.5 * (ipk_s2 / 4) + 0.5 * (kehadiran / 100) + rng.normal(0, 0.1, n), 0.2, 1.0)

logit = (-15.3 + 2.6 * ipk_s2 + 0.06 * kehadiran + 0.10 * jam_belajar
         - 0.8 * kerja_paruh_waktu + 2.5 * sks_ratio)
p = 1 / (1 + np.exp(-logit))
lulus_tepat = (rng.random(n) < p).astype(int)

df = pd.DataFrame({"ipk_s1": ipk_s1, "ipk_s2": ipk_s2, "kehadiran_pct": kehadiran,
                   "jam_belajar_mgg": jam_belajar, "kerja_paruh_waktu": kerja_paruh_waktu,
                   "rasio_sks_lulus": sks_ratio, "lulus_tepat": lulus_tepat}).round(3)
df.to_csv("data/mahasiswa_sintetis.csv", index=False)
print(df.describe().round(2).T[["mean", "std", "min", "max"]])
print("\nProporsi lulus tepat waktu:", df["lulus_tepat"].mean().round(3))

FITUR = ["ipk_s1", "ipk_s2", "kehadiran_pct", "jam_belajar_mgg", "kerja_paruh_waktu", "rasio_sks_lulus"]
X, y = df[FITUR], df["lulus_tepat"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

# %% [markdown]
# ## 2. Supervised Learning: klasifikasi kelulusan tepat waktu
# Tiga model dibandingkan dengan validasi silang 5-fold pada data latih lalu diuji pada data uji.

# %%
model_set = {
    "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "Decision Tree (depth 4)": DecisionTreeClassifier(max_depth=4, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42, n_jobs=-1),
}
base_mayoritas = max(y_te.mean(), 1 - y_te.mean())
print(f"Baseline (selalu menebak kelas mayoritas): akurasi uji = {base_mayoritas:.3f}")
hasil = []
for nama, m in model_set.items():
    cv = cross_val_score(m, X_tr, y_tr, cv=5, scoring="f1").mean()
    m.fit(X_tr, y_tr)
    pred = m.predict(X_te)
    hasil.append((nama, cv, accuracy_score(y_te, pred), f1_score(y_te, pred)))
tabel = pd.DataFrame(hasil, columns=["model", "F1_cv5", "akurasi_uji", "F1_uji"]).round(3)
print(tabel.to_string(index=False))

terbaik = tabel.loc[tabel["F1_uji"].idxmax(), "model"]
print("\nModel terbaik pada data uji:", terbaik)
print("Matriks konfusi (baris=aktual, kolom=prediksi):\n", confusion_matrix(y_te, model_set[terbaik].predict(X_te)))

rf = model_set["Random Forest"]
imp = pd.Series(rf.feature_importances_, index=FITUR).sort_values()
fig, ax = plt.subplots(figsize=(6, 3.4))
ax.barh(imp.index, imp.values, color="#1570EF", height=0.55)
ax.set_title("Fitur yang paling memengaruhi prediksi (Random Forest)")
ax.set_xlabel("Kepentingan fitur")
plt.tight_layout()
plt.savefig("output/04_supervised_feature_importance.png", dpi=200)
plt.show()

# %% [markdown]
# ### Eksperimen "Garbage In, Garbage Out": label tercemar
# Sebagian label latih sengaja dibalik (kesalahan input), lalu model diuji pada label uji yang benar.

# %%
rows = []
for noise in [0.0, 0.1, 0.2, 0.3, 0.4]:
    akurasi = []
    for ulang in range(5):   # rata-rata 5 pengacakan agar hasil stabil
        r = np.random.default_rng(100 + ulang)
        y_noisy = y_tr.copy()
        flip = r.random(len(y_noisy)) < noise
        y_noisy[flip] = 1 - y_noisy[flip]
        m = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42, n_jobs=-1).fit(X_tr, y_noisy)
        akurasi.append(accuracy_score(y_te, m.predict(X_te)))
    rows.append((f"{int(noise*100)}%", float(np.mean(akurasi))))
gigo = pd.DataFrame(rows, columns=["label_salah", "akurasi_uji"]).round(3)
print(gigo.to_string(index=False))

fig, ax = plt.subplots(figsize=(5.5, 3.2))
ax.plot(gigo["label_salah"], gigo["akurasi_uji"], marker="o", color="#D9383A")
ax.set_xlabel("Proporsi label latih yang salah"); ax.set_ylabel("Akurasi pada data uji")
ax.set_title("Kualitas label menentukan kualitas model")
ax.grid(axis="y", linestyle=":", alpha=0.5)
plt.tight_layout()
plt.savefig("output/04_garbage_in_garbage_out.png", dpi=200)
plt.show()

# %% [markdown]
# ## 3. Unsupervised Learning: segmentasi, PCA, anomali
# Label `lulus_tepat` **tidak dipakai**. Model mencari struktur sendiri dari fitur.

# %%
Xs = StandardScaler().fit_transform(X)
sil = {k: silhouette_score(Xs, KMeans(n_clusters=k, n_init=10, random_state=42).fit_predict(Xs)) for k in range(2, 7)}
k_best = max(sil, key=sil.get)
print("Silhouette per k:", {k: round(v, 3) for k, v in sil.items()}, "-> k terbaik =", k_best)

df["segmen"] = KMeans(n_clusters=k_best, n_init=10, random_state=42).fit_predict(Xs)
profil = df.groupby("segmen")[FITUR + ["lulus_tepat"]].mean().round(2)
profil["jumlah"] = df["segmen"].value_counts().sort_index()
print(profil)

pca = PCA(n_components=2)
Z = pca.fit_transform(Xs)
print("Varians dijelaskan PCA 2 komponen:", pca.explained_variance_ratio_.round(3), "total", pca.explained_variance_ratio_.sum().round(3))

iso = IsolationForest(contamination=0.05, random_state=42).fit(Xs)
df["anomali"] = iso.predict(Xs) == -1

fig, ax = plt.subplots(figsize=(6.5, 4.5))
sc = ax.scatter(Z[:, 0], Z[:, 1], c=df["segmen"], cmap="tab10", s=18, alpha=0.75)
ax.scatter(Z[df["anomali"], 0], Z[df["anomali"], 1], facecolors="none", edgecolors="#D9383A", s=70, label="Anomali (5%)")
ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
ax.set_title(f"Segmentasi mahasiswa (k={k_best}) pada ruang PCA")
ax.legend(frameon=False)
plt.tight_layout()
plt.savefig("output/04_unsupervised_pca_segmen.png", dpi=200)
plt.show()

# %% [markdown]
# ## 4. Semi-supervised Learning: hanya 10% data berlabel
# Label Spreading memanfaatkan struktur data tak berlabel. Pembanding: Logistic Regression yang hanya memakai data berlabel.
# Hasil dilaporkan apa adanya; manfaat semi-supervised bergantung pada struktur data.

# %%
sc_ = StandardScaler().fit(X_tr)
Xtr_s, Xte_s = sc_.transform(X_tr), sc_.transform(X_te)

hasil_semi = []
for seed in range(5):
    r = np.random.default_rng(seed)
    n_lab = int(0.10 * len(y_tr))
    idx_lab = r.choice(len(y_tr), n_lab, replace=False)
    y_part = np.full(len(y_tr), -1)
    y_part[idx_lab] = y_tr.values[idx_lab]
    sup = LogisticRegression(max_iter=1000).fit(Xtr_s[idx_lab], y_tr.values[idx_lab])
    semi = LabelSpreading(kernel="knn", n_neighbors=10).fit(Xtr_s, y_part)
    hasil_semi.append((accuracy_score(y_te, sup.predict(Xte_s)), accuracy_score(y_te, semi.predict(Xte_s))))
hs = pd.DataFrame(hasil_semi, columns=["supervised_10pct_label", "label_spreading_10pct_label"])
print(hs.round(3))
print("\nRata-rata 5 pengulangan:\n", hs.mean().round(3).to_string())
print(f"Acuan: Logistic Regression dengan 100% label = {tabel.loc[0, 'akurasi_uji']:.3f}")

# %% [markdown]
# ## 5. Reinforcement Learning: Q-Learning di grid world 5×5
# Agen (misal robot pengantar logistik) belajar dari **reward**: +10 mencapai tujuan, −10 masuk zona bahaya, −1 tiap langkah.

# %%
UKURAN = 5
START, GOAL = (0, 0), (4, 4)
BAHAYA = {(1, 2), (2, 2), (3, 1), (3, 3)}
AKSI = [(-1, 0), (1, 0), (0, -1), (0, 1)]   # atas, bawah, kiri, kanan
SIMBOL = ["↑", "↓", "←", "→"]

def langkah(s, a):
    r, c = s[0] + AKSI[a][0], s[1] + AKSI[a][1]
    if not (0 <= r < UKURAN and 0 <= c < UKURAN):
        return s, -2, False
    s2 = (r, c)
    if s2 == GOAL:
        return s2, 10, True
    if s2 in BAHAYA:
        return s2, -10, True
    return s2, -1, False

Q = np.zeros((UKURAN, UKURAN, 4))
alpha, gamma, eps = 0.2, 0.95, 0.2
total_reward = []
rl = np.random.default_rng(0)
for ep in range(3000):
    s, selesai, tot = START, False, 0
    for _ in range(100):
        a = rl.integers(4) if rl.random() < eps else int(np.argmax(Q[s]))
        s2, r, selesai = langkah(s, a)
        Q[s][a] += alpha * (r + gamma * (0 if selesai else Q[s2].max()) - Q[s][a])
        s, tot = s2, tot + r
        if selesai:
            break
    total_reward.append(tot)

print("Kebijakan hasil belajar (G=tujuan, X=bahaya):")
for r in range(UKURAN):
    print(" ".join("G" if (r, c) == GOAL else "X" if (r, c) in BAHAYA else SIMBOL[int(np.argmax(Q[r, c]))]
                   for c in range(UKURAN)))

s, jalur = START, [START]
for _ in range(20):
    s, _, selesai = langkah(s, int(np.argmax(Q[s])))
    jalur.append(s)
    if selesai:
        break
print("\nJalur greedy:", jalur)
print("Mencapai tujuan:", jalur[-1] == GOAL)

ma = pd.Series(total_reward).rolling(100).mean()
fig, ax = plt.subplots(figsize=(6, 3.2))
ax.plot(ma, color="#1570EF")
ax.set_xlabel("Episode"); ax.set_ylabel("Reward rata-rata (jendela 100)")
ax.set_title("Kurva belajar Q-Learning")
ax.grid(axis="y", linestyle=":", alpha=0.5)
plt.tight_layout()
plt.savefig("output/04_reinforcement_kurva_belajar.png", dpi=200)
plt.show()

# %% [markdown]
# ## Ringkasan
# - **Supervised** butuh label berkualitas; kesalahan label langsung menurunkan akurasi.
# - **Unsupervised** menemukan segmen & anomali tanpa label, tetapi interpretasi tetap tugas manusia.
# - **Semi-supervised** berguna saat label mahal; periksa selalu terhadap pembanding sederhana.
# - **Reinforcement** belajar lewat interaksi dan reward; desain reward menentukan perilaku agen.
