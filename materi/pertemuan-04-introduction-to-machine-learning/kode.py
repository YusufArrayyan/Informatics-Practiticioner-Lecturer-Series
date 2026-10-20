# %% [markdown]
# # Pertemuan 4 — Introduction to Machine Learning
# **Studi Kasus:** Analitik Akademik Program Studi: Prediksi Kelulusan Tepat Waktu, Segmentasi Mahasiswa, dan Demo Empat Paradigma ML
#
# **Identitas**
# - Nama: Muhammad Yusuf Arrayyan
# - NPM: G1A024009
# - Program Studi: S1 Teknik Informatika, Universitas Bengkulu (UNIB)
# - Kegiatan: Informatics Practitioner Lecture Series
# - Narasumber: Dr. Tanzila Tahiddin, Senior Lecturer, Faculty of Computer and Mathematical Sciences, Universiti Teknologi MARA (UiTM), Malaysia (ejaan nama dan afiliasi dibaca dari catatan tulisan tangan; perlu dicek)
#
# > Data mahasiswa pada notebook ini **sintetis** dan tidak berasal dari individu nyata.
#
# ## Ringkasan Materi
# 1. **Machine learning (ML)** adalah cabang AI yang membuat komputer belajar pola dari data tanpa diprogram aturan secara eksplisit.
# 2. **Empat paradigma ML:**
#    - *Supervised*: belajar dari data berlabel (klasifikasi, regresi).
#    - *Unsupervised*: menemukan struktur pada data tanpa label (klaster, reduksi dimensi, deteksi anomali).
#    - *Semi-supervised*: memadukan sedikit data berlabel dengan banyak data tak berlabel.
#    - *Reinforcement*: agen belajar lewat interaksi dan *reward*.
# 3. **Siklus ML:** pengumpulan data → persiapan data → pelatihan → pengujian → evaluasi dan *deployment*.
# 4. Prinsip **Garbage In, Garbage Out**: kualitas data dan label menentukan kualitas model.
#
# ## Latar Belakang
# Program studi perguruan tinggi menyimpan data akademik mahasiswa (IPK per semester, kehadiran, SKS yang lulus, kegiatan di luar kuliah). Pengelola program studi ingin mengetahui **mahasiswa mana yang berisiko tidak lulus tepat waktu** sedini mungkin agar dosen wali dapat memberi pendampingan sebelum terlambat. Selain itu, pengelola ingin memahami **kelompok-kelompok mahasiswa** yang ada, memanfaatkan data yang **belum diberi label** (karena pelabelan mahal), dan melihat bagaimana sistem dapat belajar dari **umpan balik** (konsep reinforcement learning).
#
# Kasus ini dipilih karena satu kumpulan data yang sama dapat dipakai untuk memperagakan hampir seluruh paradigma ML dari materi, sehingga perbedaan tujuan dan keterbatasan tiap paradigma terlihat jelas dalam satu cerita.
#
# ## Rumusan Masalah
# 1. Seberapa baik fitur akademik awal memprediksi kelulusan tepat waktu, dan model mana yang paling cocok?
# 2. Seberapa besar kesalahan label menurunkan kinerja model (*Garbage In, Garbage Out*)?
# 3. Apakah terdapat kelompok mahasiswa yang berbeda secara alami tanpa memakai label?
# 4. Apakah data tak berlabel membantu ketika label hanya tersedia untuk 10% data?
# 5. Bagaimana agen belajar mencapai tujuan dengan reward?
#
# ## Tujuan
# 1. Membangun dan membandingkan tiga model klasifikasi dengan validasi silang, lalu menguji pada data terpisah.
# 2. Membandingkan hasil dengan *baseline* sederhana agar kinerja model dinilai secara jujur.
# 3. Mengukur dampak label tercemar terhadap akurasi.
# 4. Menerapkan K-Means, PCA, dan Isolation Forest.
# 5. Membandingkan Label Spreading dengan model yang hanya memakai label yang tersedia.
# 6. Mengimplementasikan Q-Learning pada *grid world*.
#
# ## Dasar Teori
# - **Klasifikasi:** memprediksi kategori (di sini lulus tepat waktu = 1 atau tidak = 0). Model yang dipakai: Logistic Regression (model linear, mudah ditafsirkan), Decision Tree (aturan bercabang), Random Forest (ansambel pohon).
# - **Validasi silang 5-fold:** data latih dibagi 5 bagian, bergantian 4 bagian untuk melatih dan 1 untuk menguji, sehingga estimasi kinerja lebih stabil.
# - **Metrik:** akurasi (proporsi benar), F1 (rata-rata harmonik presisi dan recall), matriks konfusi. **Baseline** mayoritas menunjukkan akurasi bila selalu menebak kelas terbanyak; model hanya berguna bila melampauinya.
# - **K-Means dan silhouette:** K-Means membagi data ke k klaster; skor silhouette (−1 sampai 1) mengukur seberapa jelas klaster terpisah. **PCA** memproyeksikan data ke sumbu yang menangkap varians terbesar. **Isolation Forest** menandai titik yang mudah "diisolasi" sebagai anomali.
# - **Label Spreading:** menyebarkan label dari titik berlabel ke tetangganya pada graf kesamaan.
# - **Q-Learning:** `Q(s,a) ← Q(s,a) + α [r + γ · max Q(s',a') − Q(s,a)]`, dengan α laju belajar, γ faktor diskon, dan strategi ε-greedy untuk menyeimbangkan eksplorasi dan eksploitasi.
#
# ## Dataset
# 800 mahasiswa sintetis (seed 42) dengan fitur:
# | Fitur | Arti |
# |---|---|
# | `ipk_s1`, `ipk_s2` | IPK semester 1 dan 2 |
# | `kehadiran_pct` | persentase kehadiran |
# | `jam_belajar_mgg` | jam belajar per minggu |
# | `kerja_paruh_waktu` | 1 bila bekerja paruh waktu |
# | `rasio_sks_lulus` | rasio SKS yang lulus |
# | `lulus_tepat` | **target**: 1 bila lulus tepat waktu |
#
# Target dibangkitkan dari fungsi logistik atas fitur ditambah keacakan, sehingga ada batas kemampuan prediksi (tidak mungkin 100%). Proporsi lulus tepat waktu sekitar **59,6%**.
#
# ## Metodologi
# 1. Eksplorasi data → 2. Supervised (3 model, CV 5-fold, uji, baseline, matriks konfusi) → 3. Eksperimen GIGO (label dibalik 0–40%, rata-rata 5 pengulangan) → 4. Unsupervised (K-Means, silhouette, PCA, Isolation Forest) → 5. Semi-supervised (10% label, 5 pengulangan) → 6. Reinforcement (Q-Learning 3.000 episode pada grid 5×5 dengan 4 sel bahaya).
#
# ## Implementasi
# Setiap kelompok keluaran diikuti sel **Interpretasi** (angka berdasarkan seed bawaan).

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
# ### Interpretasi: eksplorasi data
# - Rata-rata IPK semester 1 dan 2 sekitar 3,0; kehadiran rata-rata ±81%; jam belajar ±12 jam per minggu; ±29% mahasiswa bekerja paruh waktu.
# - **Sekitar 59,6% mahasiswa lulus tepat waktu**, sehingga kelas cukup seimbang. Ini penting untuk memilih metrik: pada data seimbang, akurasi masih bermakna tetapi harus dibandingkan dengan baseline.

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
# ### Interpretasi: supervised learning
# - **Baseline** (selalu menebak "lulus tepat waktu") menghasilkan akurasi uji **0,595**. Semua model melampauinya, jadi ada informasi yang berhasil dipelajari.
# - Hasil data uji: Logistic Regression akurasi **0,780** (F1 0,821), Decision Tree 0,770 (F1 0,810), Random Forest 0,755 (F1 0,798). F1 validasi silang masing-masing 0,823; 0,783; 0,804.
# - Model **paling sederhana (Logistic Regression) justru terbaik**. Karena target dibangkitkan dari hubungan hampir linear, model yang lebih kompleks tidak memberi keuntungan. Pelajaran: kompleksitas tidak otomatis lebih baik; pilih model sesuai struktur data.
# - Matriks konfusi (baris = aktual, kolom = prediksi): 55 benar-tidak-lulus, 26 salah-prediksi-lulus, 18 salah-prediksi-tidak-lulus, 101 benar-lulus. Dari 119 mahasiswa yang benar-benar lulus tepat waktu, 101 (±85%) tertangkap. Untuk pendampingan, kesalahan yang paling merugikan adalah **mahasiswa berisiko yang diprediksi aman** (26 kasus), sehingga ambang keputusan sebaiknya disesuaikan bila recall kelas berisiko lebih penting.

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
# ### Interpretasi: Garbage In, Garbage Out pada label
# - Akurasi Random Forest (rata-rata 5 pengacakan) pada label latih yang dibalik secara acak: 0% → **0,760**, 10% → 0,756, 20% → 0,753, 30% → 0,726, 40% → **0,697**.
# - Penurunan **tidak linear**: hampir datar hingga 20% label salah (Random Forest cukup tahan derau acak ringan), lalu menurun jelas pada 30–40%. Pada 40% label salah akurasi turun ±6 poin dan mendekati baseline 0,595.
# - Derau di sini acak. Kesalahan label yang **sistematis** (mis. satu kelompok selalu salah dilabeli) jauh lebih merusak. Maka audit kualitas label tetap wajib sebelum pelatihan.

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
# ### Interpretasi: unsupervised learning
# - Skor silhouette untuk k = 2 sampai 6 berkisar 0,186–0,215; **k = 3** dipilih (0,215, hampir sama dengan k = 2). Nilai ±0,2 tergolong rendah: segmen yang ditemukan **saling tumpang tindih**, bukan kelompok yang terpisah tegas. Hasil ini adalah alat bantu eksplorasi, bukan kebenaran mutlak.
# - Profil tiga segmen: **segmen 0** (301 mahasiswa) IPK ±2,55 dan hanya ±35% lulus tepat waktu → kelompok prioritas pendampingan; **segmen 1** (310) IPK ±3,30 dengan ±84% lulus tepat waktu; **segmen 2** (189) IPK ±3,14 dengan ±59%. Label `lulus_tepat` **tidak dipakai** untuk klaster, tetapi segmen yang terbentuk ternyata berkaitan kuat dengannya.
# - Nomor segmen bersifat sembarang (bergantung inisialisasi), yang bermakna adalah profilnya.
# - Dua komponen PCA menjelaskan **58,7%** varians (37,5% + 21,2%), cukup untuk visualisasi dua dimensi, tetapi sisa 41% informasi tidak terlihat pada plot. Titik bertanda merah adalah 5% data yang dianggap anomali oleh Isolation Forest; anomali berarti "tidak lazim", belum tentu "salah".

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
# ### Interpretasi: semi-supervised learning
# - Dengan hanya 10% label, model yang hanya memakai label itu (Logistic Regression) mencapai akurasi rata-rata **0,766**, sedangkan **Label Spreading 0,689**. Acuan dengan 100% label adalah 0,780.
# - Jadi pada data ini **memakai data tak berlabel tidak membantu, bahkan lebih buruk**. Penyebabnya: Label Spreading mengandalkan asumsi bahwa titik berdekatan memiliki label sama, padahal di data ini kelas tumpang tindih dan batas keputusannya linear.
# - Hasil ini dilaporkan apa adanya. Pelajaran: semi-supervised bukan jaminan peningkatan; selalu bandingkan dengan pembanding sederhana. Menariknya, model linear dengan hanya 10% label (0,766) sudah mendekati model dengan seluruh label (0,780), tanda bahwa jumlah label yang dibutuhkan relatif sedikit untuk struktur sesederhana ini.

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
# ### Interpretasi: reinforcement learning
# - Setelah 3.000 episode, agen menemukan jalur greedy dari (0,0) ke tujuan (4,4) dalam **8 langkah**, yaitu jarak terpendek yang mungkin pada grid 5×5, tanpa menginjak satu pun sel bahaya (X). Peta panah menunjukkan kebijakan yang dipelajari di setiap sel.
# - Perilaku ini muncul hanya dari reward (+10 tujuan, −10 bahaya, −1 per langkah) tanpa ada yang mengajarkan rute. **Desain reward menentukan perilaku**: tanpa penalti −1 per langkah, agen tidak punya alasan memilih rute terpendek.
# - Berbeda dengan paradigma lain, RL tidak butuh dataset awal, tetapi butuh lingkungan untuk berinteraksi (simulator atau dunia nyata).

# %% [markdown]
# ## Ringkasan
# - **Supervised** butuh label berkualitas; kesalahan label langsung menurunkan akurasi.
# - **Unsupervised** menemukan segmen & anomali tanpa label, tetapi interpretasi tetap tugas manusia.
# - **Semi-supervised** berguna saat label mahal; periksa selalu terhadap pembanding sederhana.
# - **Reinforcement** belajar lewat interaksi dan reward; desain reward menentukan perilaku agen.

# %% [markdown]
# ## Hasil dan Pembahasan (ringkasan)
# | Paradigma | Temuan utama |
# |---|---|
# | Supervised | Logistic Regression terbaik: akurasi uji 0,780 vs baseline 0,595 |
# | Garbage In, Garbage Out | Akurasi 0,760 (label bersih) → 0,697 (40% label salah) |
# | Unsupervised | k = 3 (silhouette ±0,215); satu segmen berisiko dengan ±35% lulus tepat waktu; PCA 2 komponen menangkap 58,7% varians |
# | Semi-supervised | Label Spreading 0,689 lebih rendah dari supervised 10% label (0,766) |
# | Reinforcement | Jalur 8 langkah optimal tanpa menginjak sel bahaya |
#
# ## Kesimpulan
# 1. Model sederhana yang sesuai struktur data bisa mengalahkan model kompleks; selalu bandingkan dengan baseline.
# 2. Kualitas label menentukan hasil: derau label ringan masih tertoleransi, derau besar menurunkan kinerja nyata.
# 3. Pembelajaran tanpa label menghasilkan segmen yang bermakna, tetapi kekuatan pemisahannya terbatas dan interpretasinya tugas manusia.
# 4. Semi-supervised hanya bermanfaat bila asumsi strukturnya terpenuhi.
# 5. Reinforcement learning belajar dari reward; merancang reward sama pentingnya dengan memilih algoritma.
#
# ## Keterbatasan
# - Data sintetis dengan hubungan yang kita tentukan sendiri; hasil tidak mewakili kondisi mahasiswa sebenarnya.
# - Satu pemisahan latih-uji (200 data uji) membuat selisih akurasi beberapa poin antarmodel belum tentu signifikan secara statistik.
# - Prediksi risiko akademik pada manusia membawa isu etika (label stigma, bias, privasi) yang tidak dibahas dalam kode.
# - Grid world RL sangat kecil dan deterministik.
#
# ## Saran Pengembangan
# - Memakai data akademik nyata yang dianonimkan dan disetujui kampus; menambahkan fitur seperti keaktifan LMS.
# - Menambahkan penjelasan model (koefisien, SHAP) dan kalibrasi probabilitas agar dosen wali dapat memahami alasan prediksi.
# - Menguji ketidakseimbangan kelas dan menyetel ambang keputusan sesuai biaya kesalahan.
# - Membangun alur yang sama di KNIME (Learner/Predictor, Scorer; lihat `KNIME_GUIDE.md`).
#
# ## Referensi
# > Rujukan di bawah adalah bacaan lanjutan. Periksa kembali penulisan, tahun, dan volume sebelum dikutip dalam laporan resmi.
# - Pedregosa, F., dkk. (2011). Scikit-learn: Machine Learning in Python. *JMLR*, 12, 2825–2830.
# - Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.
# - Watkins, C. J. C. H., & Dayan, P. (1992). Q-learning. *Machine Learning*, 8, 279–292.
# - Zhou, D., dkk. (2004). Learning with local and global consistency (Label Spreading). *NIPS 16*.
# - Rousseeuw, P. J. (1987). Silhouettes. *Journal of Computational and Applied Mathematics*, 20, 53–65.
# - Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation Forest. *IEEE ICDM*.
# - Materi Practitioner Lecture Series, Pertemuan 4 (catatan kuliah).
