# %% [markdown]
# # Pertemuan 1 — Make Sense of Data with Analytics and AI
# **Studi Kasus:** Analitik Penjualan Jaringan UMKM Kuliner di Kota Bengkulu
#
# **Identitas**
# - Nama: Muhammad Yusuf Arrayyan
# - NPM: G1A024009
# - Program Studi: S1 Teknik Informatika, Universitas Bengkulu (UNIB)
# - Kegiatan: Informatics Practitioner Lecture Series
# - Narasumber: peneliti senior BRIN, pengelola tim High Performance Computing (nama pada catatan tulisan tangan kurang terbaca)
#
# > Seluruh data pada notebook ini **sintetis** (dibangkitkan program dengan seed tetap), bukan data usaha yang sebenarnya.
#
# ## Ringkasan Materi
# Narasumber membahas bagaimana data mentah diolah menjadi informasi dan akhirnya *insight* yang mendukung keputusan bisnis. Poin utama:
# 1. **CRISP-DM** (Cross-Industry Standard Process for Data Mining) sebagai kerangka kerja proyek data.
# 2. **Empat jenis analitik:** deskriptif (apa yang terjadi), diagnostik (mengapa terjadi), prediktif (apa yang akan terjadi), preskriptif (apa yang harus dilakukan).
# 3. **Persiapan data** adalah tahap penentu. Prinsipnya *Garbage In, Garbage Out*: data yang buruk menghasilkan analisis dan model yang buruk. Masalah umum: nilai kosong, duplikat, data tidak konsisten, dan anomali.
# 4. **Platform analitik berbasis workflow visual** (misalnya KNIME) mempermudah proses tersebut. Generative AI dapat membantu menyusun workflow, tetapi hasil akhir tetap dianalisis dan diputuskan manusia.
#
# ## Latar Belakang
# Usaha kuliner skala UMKM umumnya mencatat penjualan harian di kasir atau lembar kerja. Pemilik biasanya mengambil keputusan stok dan promosi berdasarkan perasaan, sehingga rawan **kelebihan stok** (bahan terbuang) atau **kehabisan stok** (penjualan hilang). Di sisi lain, data yang tersedia jarang bersih: ada nilai yang kosong, baris yang tercatat dua kali, penulisan nama produk yang berbeda-beda ("Nasi Goreng", "NASI GORENG "), dan angka yang salah ketik.
#
# Studi kasus ini mensimulasikan sebuah jaringan UMKM kuliner dengan 3 outlet dan 4 produk selama 1 Januari sampai 30 September 2026. Tujuannya menunjukkan alur lengkap CRISP-DM dan keempat jenis analitik pada data yang realistis (kotor), sekaligus **membuktikan secara empiris** bahwa kualitas data menentukan kualitas model.
#
# ## Rumusan Masalah
# 1. Bagaimana mengidentifikasi dan membersihkan masalah kualitas data penjualan?
# 2. Seberapa besar kualitas data memengaruhi akurasi model prediksi?
# 3. Bagaimana tren omzet tiap outlet, dan apa penyebab penurunan yang mencolok?
# 4. Berapa kebutuhan stok tiap produk untuk 7 hari ke depan?
# 5. Apakah diskon promosi layak dijalankan, dan pada besaran berapa?
#
# ## Tujuan
# 1. Menyiapkan data (profil, pembersihan, validasi hasil pembersihan).
# 2. Menerapkan keempat jenis analitik pada satu kasus yang sama.
# 3. Membuktikan prinsip *Garbage In, Garbage Out* dengan membandingkan dua model.
# 4. Menghasilkan rekomendasi keputusan yang dapat ditindaklanjuti pemilik usaha.
#
# ## Dasar Teori
# - **CRISP-DM** memiliki enam fase: *Business Understanding, Data Understanding, Data Preparation, Modeling, Evaluation, Deployment*. Notebook ini mencakup lima fase pertama dan menutup dengan rekomendasi (fase *Deployment* berupa tindakan bisnis).
# - **Deteksi outlier dengan IQR.** Nilai yang melebihi Q3 + 3 × (Q3 − Q1) dianggap pencilan ekstrem (aturan Tukey untuk *far out*) dan ditandai sebagai kosong sebelum diimputasi.
# - **Imputasi median per kelompok.** Nilai kosong diisi median untuk kombinasi produk dan akhir pekan, karena median tahan terhadap pencilan.
# - **Random Forest Regressor** adalah ansambel pohon keputusan yang memprediksi nilai numerik dengan merata-ratakan prediksi banyak pohon.
# - **MAE (Mean Absolute Error)** adalah rata-rata selisih mutlak antara prediksi dan nilai sebenarnya; makin kecil makin baik.
# - **Safety stock** `SS = z × σ × √n`. Dengan z = 1,28 (tingkat layanan ±90%), σ simpangan galat prediksi harian, dan n jumlah baris prediksi yang dijumlahkan.
# - **Laba kotor skenario diskon** = jumlah terjual × (harga × (1 − diskon) − biaya). Biaya produk diasumsikan 60% dari harga.
#
# ## Dataset
# | Kolom | Arti |
# |---|---|
# | `tanggal` | tanggal transaksi (273 hari) |
# | `outlet` | Pasar Minggu, Panorama, Padang Harapan |
# | `produk` | Nasi Goreng, Mie Ayam, Es Teh, Martabak |
# | `qty` | jumlah terjual per hari (target prediksi) |
# | `harga` | harga satuan (Rp) |
# | `promo` | 1 bila ada promo pada hari itu |
# | `hujan` | 1 bila hari hujan |
#
# Data benar berisi 273 hari × 3 outlet × 4 produk = **3.276 baris**. Faktor yang dibangun ke dalam data: akhir pekan menaikkan penjualan, promo menaikkan penjualan, hujan menurunkannya, outlet Panorama sedikit lebih ramai, dan **Panorama direnovasi 10–24 Juni 2026** (penjualan turun). Setelah itu data "dirusak": 4% nilai `qty` dikosongkan, 1% dikali 20 (salah input), 8% label produk ditulis huruf besar dengan spasi, dan 3% baris diduplikasi.
#
# ## Metodologi
# | Fase CRISP-DM | Bagian notebook |
# |---|---|
# | Business & Data Understanding | Bagian 1: membangkitkan data dan profil kualitas |
# | Data Preparation | Bagian 2: pembersihan dan validasi |
# | Analitik deskriptif, diagnostik | Bagian 3 dan 4 |
# | Modeling & Evaluation | Bagian 5: Model A (minimal) vs Model B (bersih), diuji pada data asli |
# | Aksi bisnis | Bagian 6: stok dan keputusan diskon |
#
# ## Implementasi
# Jalankan sel-sel berikut berurutan. Setiap kelompok hasil diikuti sel **Interpretasi** yang menjelaskan maknanya (angka berdasarkan seed bawaan).

# %%
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 110})

# %% [markdown]
# ## 1. Business & Data Understanding: membangkitkan data
# Data "kebenaran" (`df_true`) dibuat dulu, lalu dirusak secara terkontrol (`df_dirty`) agar kita bisa
# mengukur dampak data kotor terhadap model.

# %%
rng = np.random.default_rng(42)
tanggal = pd.date_range("2026-01-01", "2026-09-30", freq="D")
outlets = ["Pasar Minggu", "Panorama", "Padang Harapan"]
harga = {"Nasi Goreng": 15000, "Mie Ayam": 13000, "Es Teh": 5000, "Martabak": 20000}
dasar = {"Nasi Goreng": 30, "Mie Ayam": 25, "Es Teh": 45, "Martabak": 15}

rows = []
for t in tanggal:
    weekend = int(t.dayofweek >= 5)
    hujan = int(rng.random() < 0.35)
    for o in outlets:
        promo = int(rng.random() < 0.25)
        # Gangguan khusus outlet: Panorama sedang renovasi 10-24 Juni 2026
        renovasi = (o == "Panorama") and (pd.Timestamp("2026-06-10") <= t <= pd.Timestamp("2026-06-24"))
        for p, h in harga.items():
            lam = (dasar[p] * (1.35 if weekend else 1.0) * (1.25 if promo else 1.0)
                   * (0.80 if hujan else 1.0) * (1.10 if o == "Panorama" else 1.0)
                   * (0.55 if renovasi else 1.0))
            rows.append((t, o, p, int(rng.poisson(lam)), h, promo, hujan))

df_true = pd.DataFrame(rows, columns=["tanggal", "outlet", "produk", "qty", "harga", "promo", "hujan"])

# --- Merusak data secara terkontrol (meniru data nyata) ---
df_dirty = df_true.copy()
n = len(df_dirty)
df_dirty["qty"] = df_dirty["qty"].astype(float)
df_dirty.loc[rng.choice(n, int(0.04 * n), replace=False), "qty"] = np.nan          # missing value
idx_out = rng.choice(n, int(0.01 * n), replace=False)
df_dirty.loc[idx_out, "qty"] = df_dirty.loc[idx_out, "qty"] * 20                    # outlier salah input
idx_lbl = rng.choice(n, int(0.08 * n), replace=False)
df_dirty.loc[idx_lbl, "produk"] = df_dirty.loc[idx_lbl, "produk"].str.upper() + " "  # label tidak konsisten
dup = df_dirty.sample(int(0.03 * n), random_state=1)                                 # baris duplikat
df_dirty = pd.concat([df_dirty, dup]).sample(frac=1, random_state=2).reset_index(drop=True)

df_dirty.to_csv("data/penjualan_umkm_kotor.csv", index=False)
print("Baris data benar :", len(df_true))
print("Baris data kotor :", len(df_dirty))
print(df_dirty.head())

# %% [markdown]
# ### Profil kualitas data (Data Understanding)

# %%
profil = pd.DataFrame({
    "missing": df_dirty.isna().sum(),
    "pct_missing": (df_dirty.isna().mean() * 100).round(2),
    "n_unik": df_dirty.nunique(),
})
print(profil)
print("\nBaris duplikat penuh :", df_dirty.duplicated().sum())
print("Label produk mentah  :", sorted(df_dirty["produk"].unique()))

# %% [markdown]
# ### Interpretasi: profil kualitas data
# - Data kotor berisi **3.374 baris** (seharusnya 3.276). Ada 135 nilai `qty` kosong (4,0%), **98 baris duplikat penuh**, dan kolom `produk` memiliki **8 nilai unik padahal seharusnya 4** karena penulisan huruf besar/kecil dan spasi berbeda (mis. `'ES TEH '` dan `'Es Teh'`).
# - Profil nilai kosong **tidak menampakkan outlier** salah input (angka dikali 20), sehingga outlier perlu dideteksi dengan aturan statistik terpisah. Ini alasan profil data tidak boleh berhenti pada hitungan nilai kosong.

# %% [markdown]
# ## 2. Data Preparation: membersihkan data
# Urutan: standarisasi label → hapus duplikat → tandai outlier (IQR) → imputasi median per kelompok.

# %%
def bersihkan(df):
    d = df.copy()
    d["produk"] = d["produk"].str.strip().str.title()
    d = d.drop_duplicates(subset=["tanggal", "outlet", "produk"]).copy()
    d["weekend"] = (pd.to_datetime(d["tanggal"]).dt.dayofweek >= 5).astype(int)
    g = d.groupby("produk")["qty"]
    q1, q3 = g.transform(lambda s: s.quantile(0.25)), g.transform(lambda s: s.quantile(0.75))
    batas_atas = q3 + 3 * (q3 - q1)
    d["outlier"] = d["qty"] > batas_atas
    d.loc[d["outlier"], "qty"] = np.nan
    d["qty"] = d["qty"].fillna(d.groupby(["produk", "weekend"])["qty"].transform("median"))
    return d.drop(columns="outlier").sort_values(["tanggal", "outlet", "produk"]).reset_index(drop=True)

df_clean = bersihkan(df_dirty)
df_clean["tanggal"] = pd.to_datetime(df_clean["tanggal"])
df_clean.to_csv("data/penjualan_umkm_bersih.csv", index=False)

print("Baris setelah dibersihkan :", len(df_clean), "(target:", len(df_true), ")")
print("Missing tersisa           :", int(df_clean["qty"].isna().sum()))
cek = df_true.merge(df_clean[["tanggal", "outlet", "produk", "qty"]],
                    on=["tanggal", "outlet", "produk"], suffixes=("_asli", "_bersih"))
print("MAE qty hasil pembersihan vs data asli:", round(mean_absolute_error(cek["qty_asli"], cek["qty_bersih"]), 3))

# %% [markdown]
# ### Interpretasi: hasil pembersihan
# - Jumlah baris kembali menjadi 3.276 sesuai data benar, dan tidak ada nilai kosong tersisa.
# - Karena kita memiliki data asli, hasil pembersihan bisa **divalidasi**: galat rata-rata imputasi hanya sekitar 0,32 unit per baris. Pada kasus nyata data asli tidak tersedia, sehingga validasi dilakukan dengan pemeriksaan wajar (rentang nilai, konsistensi antartabel) dan konfirmasi ke pemilik usaha.

# %% [markdown]
# ## 3. Analitik #1 — Deskriptif: apa yang terjadi?

# %%
df_clean["bulan"] = df_clean["tanggal"].dt.to_period("M").astype(str)
df_clean["omzet"] = df_clean["qty"] * df_clean["harga"]
omzet_bulanan = df_clean.groupby(["bulan", "outlet"])["omzet"].sum().unstack() / 1e6
print(omzet_bulanan.round(1))

ax = omzet_bulanan.plot(marker="o", figsize=(8, 3.8), color=["#1570EF", "#D9383A", "#667085"])
ax.set_ylabel("Omzet (juta Rp)")
ax.set_title("Omzet bulanan per outlet (data bersih)")
ax.grid(axis="y", linestyle=":", alpha=0.5)
plt.tight_layout()
plt.savefig("output/01_deskriptif_omzet_bulanan.png", dpi=200)
plt.show()

# %% [markdown]
# ### Interpretasi: analitik deskriptif
# - Omzet ketiga outlet berada pada kisaran 38–48 juta rupiah per bulan. Panorama umumnya tertinggi karena faktor outlet yang lebih ramai.
# - Pada **Juni** omzet Panorama turun tajam menjadi sekitar 35,8 juta, dibanding 47,8 juta (Mei) dan 48,2 juta (Juli). Grafik hanya memberi tahu *bahwa* terjadi penurunan, bukan *penyebabnya*. Itu tugas analitik diagnostik.

# %% [markdown]
# ## 4. Analitik #2 — Diagnostik: mengapa terjadi?
# Cari pekan dengan penurunan omzet terbesar per outlet, lalu uji apakah promo atau hujan menjelaskannya.

# %%
df_clean["pekan"] = df_clean["tanggal"].dt.to_period("W").dt.start_time
# Hanya pekan lengkap (7 hari) agar pekan parsial di awal/akhir data tidak terbaca sebagai "penurunan"
hari_per_pekan = df_clean.groupby("pekan")["tanggal"].nunique()
pekan_lengkap = hari_per_pekan[hari_per_pekan == 7].index
pekan = df_clean[df_clean["pekan"].isin(pekan_lengkap)].groupby(["pekan", "outlet"])["omzet"].sum().unstack()
z = (pekan - pekan.mean()) / pekan.std()
outlet_anomali = z.min().idxmin()
pekan_anomali = z[outlet_anomali].idxmin()
print(f"Penurunan terdalam: outlet {outlet_anomali}, pekan mulai {pekan_anomali.date()} (z = {z.loc[pekan_anomali, outlet_anomali]:.2f})")

pekan_data = df_clean[(df_clean["pekan"] == pekan_anomali)]
rata_hujan_normal = df_clean["hujan"].mean()
rata_promo_normal = df_clean["promo"].mean()
print(f"Proporsi hari hujan pekan itu : {pekan_data['hujan'].mean():.2f} (normal {rata_hujan_normal:.2f})")
print(f"Proporsi promo pekan itu      : {pekan_data[pekan_data['outlet']==outlet_anomali]['promo'].mean():.2f} (normal {rata_promo_normal:.2f})")

efek = pd.DataFrame({
    "faktor": ["Promo", "Hujan", "Akhir pekan"],
    "rata2_qty_ya": [df_clean.loc[df_clean[c] == 1, "qty"].mean() for c in ["promo", "hujan", "weekend"]],
    "rata2_qty_tidak": [df_clean.loc[df_clean[c] == 0, "qty"].mean() for c in ["promo", "hujan", "weekend"]],
})
efek["selisih_pct"] = ((efek["rata2_qty_ya"] / efek["rata2_qty_tidak"] - 1) * 100).round(1)
print(efek.round(2))
print("\nKesimpulan: promo dan hujan tidak cukup menjelaskan penurunan khas satu outlet; "
      "perlu investigasi lapangan (pada data ini penyebab sebenarnya adalah renovasi outlet).")

# %% [markdown]
# ### Interpretasi: analitik diagnostik
# - Penurunan terdalam terdeteksi pada outlet **Panorama, pekan yang dimulai 15 Juni 2026** (z-score sekitar −3,75). Analisis hanya memakai pekan lengkap 7 hari agar pekan parsial di ujung data tidak terbaca sebagai anomali palsu.
# - Pada pekan itu proporsi hari promo **0,57** (normal 0,27), jadi justru lebih tinggi dari biasanya, sedangkan proporsi hari hujan **0,43** (normal 0,38), hanya sedikit di atas normal. Promo menaikkan penjualan, jadi promo tidak menjelaskan penurunan; hujan terlalu kecil perannya.
# - Efek faktor secara umum: akhir pekan sekitar +38%, promo sekitar +23%, hujan sekitar −19% terhadap rata-rata penjualan. Karena penurunan Panorama bersifat khas satu outlet, dugaan yang masuk akal adalah **gangguan operasional** (pada data sintetis ini memang renovasi). Diagnostik memberi hipotesis; konfirmasinya tetap lewat investigasi lapangan.

# %% [markdown]
# ## 5. Analitik #3 — Prediktif + bukti "Garbage In, Garbage Out"
# Dua model dilatih pada data yang sama dengan kualitas berbeda, lalu diuji pada **data asli (kebenaran)**
# periode Agustus–September 2026.
# - **Model A (minimal):** hanya membuang baris kosong; outlier & duplikat dibiarkan (label sudah distandarkan).
# - **Model B (bersih):** memakai hasil seluruh langkah pembersihan.

# %%
fitur_kategori = ["outlet", "produk"]

def siapkan_x(d):
    d = d.copy()
    d["tanggal"] = pd.to_datetime(d["tanggal"])
    d["dow"] = d["tanggal"].dt.dayofweek
    d["bulan_ke"] = d["tanggal"].dt.month
    return pd.get_dummies(d[["dow", "bulan_ke", "promo", "hujan"] + fitur_kategori], columns=fitur_kategori)

batas = pd.Timestamp("2026-08-01")
test = df_true[df_true["tanggal"] >= batas]
X_test_raw = siapkan_x(test)
y_test = test["qty"].values

minimal = df_dirty.copy()
minimal["produk"] = minimal["produk"].str.strip().str.title()
minimal["tanggal"] = pd.to_datetime(minimal["tanggal"])
minimal = minimal.dropna(subset=["qty"])
train_a = minimal[minimal["tanggal"] < batas]
train_b = df_clean[df_clean["tanggal"] < batas]

hasil = {}
for nama, tr in [("A: minimal (hapus NaN saja)", train_a), ("B: bersih penuh", train_b)]:
    Xtr = siapkan_x(tr)
    model = RandomForestRegressor(n_estimators=120, min_samples_leaf=3, random_state=42, n_jobs=-1)
    model.fit(Xtr, tr["qty"])
    Xte = X_test_raw.reindex(columns=Xtr.columns, fill_value=0)
    pred = model.predict(Xte)
    hasil[nama] = mean_absolute_error(y_test, pred)
    if nama.startswith("B"):
        model_terbaik = model
        kolom_model = Xtr.columns

hasil_df = pd.Series(hasil, name="MAE (unit/baris)").round(3)
print(hasil_df)
perbaikan = (1 - hasil_df.iloc[1] / hasil_df.iloc[0]) * 100
print(f"\nPerubahan error model B dibanding A: {perbaikan:+.1f}% (positif = B lebih baik)")

fig, ax = plt.subplots(figsize=(6, 3.2))
ax.bar(["A: minimal", "B: bersih penuh"], hasil_df.values, color=["#667085", "#1570EF"], width=0.5)
for i, v in enumerate(hasil_df.values):
    ax.text(i, v + 0.02, f"{v:.2f}", ha="center", fontweight="bold")
ax.set_ylabel("MAE pada data uji asli")
ax.set_title("Kualitas data memengaruhi kualitas model")
plt.tight_layout()
plt.savefig("output/02_prediktif_garbage_in_out.png", dpi=200)
plt.show()

# %% [markdown]
# ### Interpretasi: prediktif dan Garbage In, Garbage Out
# - Dua model memakai algoritma dan data sumber yang sama, hanya kualitas persiapan datanya berbeda, lalu diuji pada **data asli** periode Agustus–September.
# - Model A (hanya membuang baris kosong, outlier dan duplikat dibiarkan) memiliki MAE sekitar **9,82**, sedangkan Model B (pembersihan penuh) sekitar **4,71**. Galat turun kira-kira **52%**.
# - Pencilan ×20 menyeret model ke nilai yang tidak masuk akal. Bukti ini menegaskan pesan materi: **investasi terbesar ada pada kualitas data, bukan sekadar memilih algoritma yang canggih**.

# %% [markdown]
# ## 6. Analitik #4 — Preskriptif: apa yang harus dilakukan?
# (a) Berapa stok per produk untuk 7 hari ke depan (1–7 Oktober 2026)?
# (b) Apakah diskon promo layak dijalankan? (asumsi biaya produk 60% dari harga)

# %%
tgl_depan = pd.date_range("2026-10-01", periods=7, freq="D")
skenario = pd.DataFrame([(t, o, p) for t in tgl_depan for o in outlets for p in harga],
                        columns=["tanggal", "outlet", "produk"])
skenario["hujan"] = 0

def prediksi(df_skenario, promo_val):
    s = df_skenario.copy()
    s["promo"] = promo_val
    X = siapkan_x(s).reindex(columns=kolom_model, fill_value=0)
    return model_terbaik.predict(X)

skenario["qty_tanpa_promo"] = prediksi(skenario, 0)
skenario["qty_promo"] = prediksi(skenario, 1)

# (a) Stok: prediksi + safety stock 90% service level (z = 1.28)
resid = pd.Series(y_test - model_terbaik.predict(X_test_raw.reindex(columns=kolom_model, fill_value=0)))
sigma = resid.std()
stok = skenario.groupby("produk")["qty_tanpa_promo"].agg(["sum", "count"])
stok["safety_stock"] = 1.28 * sigma * np.sqrt(stok["count"])
stok["rekomendasi_stok"] = np.ceil(stok["sum"] + stok["safety_stock"]).astype(int)
print("Rekomendasi stok 1–7 Oktober 2026 (porsi/unit):")
print(stok[["sum", "safety_stock", "rekomendasi_stok"]].round(1))

# (b) Kelayakan promo: uplift hasil model, margin = harga*(1-diskon) - 0.6*harga
uplift = skenario["qty_promo"].sum() / skenario["qty_tanpa_promo"].sum()
print(f"\nUplift volume akibat promo menurut model: x{uplift:.2f}")
skenario["harga"] = skenario["produk"].map(harga)
opsi = []
for diskon in [0.0, 0.05, 0.10, 0.15]:
    qty = skenario["qty_tanpa_promo"].sum() * (1 if diskon == 0 else uplift)
    laba_unit = (skenario["harga"] * (1 - diskon) - 0.6 * skenario["harga"]).mean()
    opsi.append((f"{int(diskon*100)}%", round(qty * laba_unit / 1e6, 3)))
opsi = pd.DataFrame(opsi, columns=["diskon", "laba_kotor_juta_Rp"])
print(opsi)
terbaik = opsi.loc[opsi["laba_kotor_juta_Rp"].idxmax(), "diskon"]
print(f"\nRekomendasi: diskon {terbaik}. Catatan: uplift dianggap tetap untuk semua kedalaman diskon "
      "(asumsi penyederhanaan); uji A/B sebelum diterapkan.")

# %% [markdown]
# ### Interpretasi: analitik preskriptif
# - **Stok 1–7 Oktober 2026** (prediksi + safety stock): Es Teh ±1.101, Nasi Goreng ±733, Mie Ayam ±613, Martabak ±376 porsi/unit untuk seluruh outlet. Produk dengan permintaan tinggi memerlukan stok terbesar, dan safety stock melindungi dari lonjakan di atas prediksi.
# - **Diskon:** model menaksir promo menaikkan volume sekitar ×1,24. Dengan biaya produk 60% dari harga, laba kotor mingguan: tanpa diskon ±14,18 juta; diskon 5% ±15,34 juta (**naik ±8%**); diskon 10% ±13,15 juta; diskon 15% ±10,96 juta. Artinya diskon kecil menguntungkan, tetapi diskon besar justru menggerus laba karena kenaikan volume tidak sebanding dengan pemotongan margin.
# - **Catatan penting:** analisis mengasumsikan kenaikan volume tetap ×1,24 untuk semua besaran diskon. Dalam praktik, diskon yang lebih besar bisa menaikkan volume lebih besar. Karena itu hasil ini dipakai sebagai hipotesis yang **diuji dengan A/B test** sebelum diterapkan.

# %% [markdown]
# ## Ringkasan
# | Jenis analitik | Pertanyaan | Hasil di notebook |
# |---|---|---|
# | Deskriptif | Apa yang terjadi? | Omzet bulanan per outlet |
# | Diagnostik | Mengapa? | Penurunan outlet tertentu bukan akibat promo/hujan |
# | Prediktif | Apa yang akan terjadi? | Prediksi qty harian (Random Forest) |
# | Preskriptif | Apa yang dilakukan? | Rekomendasi stok & kelayakan diskon |

# %% [markdown]
# ## Hasil dan Pembahasan (ringkasan)
# | Analitik | Temuan |
# |---|---|
# | Persiapan data | Data kotor (4% kosong, 1% outlier, 8% label tidak konsisten, 3% duplikat) pulih ke 3.276 baris dengan galat imputasi ±0,32 |
# | Deskriptif | Omzet outlet 38–48 juta per bulan; Panorama turun tajam pada Juni |
# | Diagnostik | Penurunan khas satu outlet (pekan 15 Juni), bukan akibat promo atau hujan |
# | Prediktif | MAE 4,71 (data bersih) vs 9,82 (pembersihan minimal): galat turun ±52% |
# | Preskriptif | Rekomendasi stok per produk; diskon 5% paling menguntungkan di antara opsi yang diuji |
#
# ## Kesimpulan
# 1. Alur CRISP-DM dan empat jenis analitik dapat dijalankan end-to-end pada satu kasus nyata-sintetis, dari data kotor sampai rekomendasi keputusan.
# 2. Kualitas data menentukan kualitas model: pembersihan penuh menurunkan galat prediksi sekitar separuhnya.
# 3. Analitik deskriptif menunjukkan *apa*, diagnostik memberi hipotesis *mengapa*, prediktif menaksir *apa yang akan terjadi*, dan preskriptif mengubahnya menjadi *tindakan*. Keempatnya saling melengkapi.
# 4. Keputusan akhir tetap berada di tangan manusia: model memberi rekomendasi, bukan perintah.
#
# ## Keterbatasan
# - Data sintetis dibangun dari rumus yang kita tetapkan, sehingga model "menemukan" pola yang memang ditanam. Performa pada data usaha sungguhan akan berbeda.
# - Cakupan waktu hanya 9 bulan, tanpa efek musiman tahunan (Ramadan, libur panjang).
# - Analisis diskon mengandalkan asumsi biaya produk dan kenaikan volume yang tetap.
#
# ## Saran Pengembangan
# - Menambahkan fitur harga pesaing, cuaca nyata (BMKG), dan kalender hari besar.
# - Mencoba model deret waktu (mis. gradient boosting dengan fitur lag) dan membandingkannya dengan Random Forest.
# - Menyusun workflow yang sama di **KNIME** (lihat `KNIME_GUIDE.md`) agar pemilik usaha dapat mengulang analisis tanpa menulis kode.
# - Menjalankan A/B test promo sebelum keputusan diskon.
#
# ## Referensi
# > Rujukan di bawah adalah bacaan lanjutan. Periksa kembali penulisan, tahun, dan volume sebelum dikutip dalam laporan resmi.
# - Chapman, P., dkk. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS Inc.
# - Breiman, L. (2001). Random Forests. *Machine Learning*, 45(1), 5–32.
# - Pedregosa, F., dkk. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
# - Tukey, J. W. (1977). *Exploratory Data Analysis*. Addison-Wesley.
# - Materi Practitioner Lecture Series, Pertemuan 1 (catatan kuliah).
