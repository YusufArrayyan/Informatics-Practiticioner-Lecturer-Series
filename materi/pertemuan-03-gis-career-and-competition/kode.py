# %% [markdown]
# # Pertemuan 3 — Career and Competition in Indonesia with GIS
# **Studi Kasus:** Penentuan Titik Evakuasi Tambahan di Zona Pesisir Rawan Tsunami dan Klasifikasi Tutupan Lahan
#
# **Identitas**
# - Nama: Muhammad Yusuf Arrayyan
# - NPM: G1A024009
# - Program Studi: S1 Teknik Informatika, Universitas Bengkulu (UNIB)
# - Kegiatan: Informatics Practitioner Lecture Series
# - Narasumber: praktisi GIS (nama pada catatan tulisan tangan kurang terbaca)
#
# > Lokasi, populasi, dan garis pantai pada notebook ini **sintetis** untuk mendemonstrasikan metode. Untuk keputusan kebencanaan nyata gunakan data resmi (BPBD, BIG, BMKG).
#
# ## Ringkasan Materi
# 1. **GIS (Sistem Informasi Geografis)** berkembang menjadi fondasi *Smart City*, logistik dan rantai pasok, serta layanan publik; GIS dipakai untuk analisis geografis dan optimasi lokasi.
# 2. Prospek **karier GIS di Indonesia** dan lanskap persaingannya: instansi pemerintah, industri, dan konsultan pemetaan.
# 3. Keterampilan yang didorong: perangkat open source profesional (**QGIS, PostGIS, GeoPandas**), pemrosesan data besar lewat **cloud computing (Google Earth Engine)**, dan integrasi **machine learning** seperti klasifikasi tutupan lahan.
# 4. Pesan: kompetensi data spasial makin dicari, dan perpaduan GIS dengan data science memberi keunggulan.
#
# ## Latar Belakang
# Kota Bengkulu berada di pesisir barat Sumatra yang menghadap Samudra Hindia, wilayah dengan sejarah gempa dan potensi tsunami. Salah satu aspek kesiapsiagaan adalah **ketersediaan titik evakuasi (shelter) yang dapat dijangkau penduduk dalam waktu singkat**. Pertanyaan praktisnya: kelurahan mana di zona pesisir yang belum terlayani, dan di mana sebaiknya shelter tambahan ditempatkan?
#
# Pertanyaan ini bersifat spasial: jawabannya bergantung pada jarak, populasi, dan letak garis pantai. Karena itu GIS menjadi alat yang tepat, dan keterampilan menjawabnya (jarak, *buffer*, cakupan layanan, optimasi lokasi) sejalan dengan kompetensi yang dibahas narasumber untuk karier GIS. Bagian kedua studi kasus mengambil keterampilan lain dari materi: **klasifikasi tutupan lahan** dari citra satelit multispektral dengan machine learning.
#
# ## Rumusan Masalah
# 1. Kelurahan mana yang berada di zona rawan dan berapa penduduknya?
# 2. Berapa persen penduduk zona rawan yang terlayani shelter eksisting dalam jarak jalan kaki?
# 3. Di mana lokasi shelter tambahan yang paling efektif menaikkan cakupan?
# 4. Bagaimana mengklasifikasikan tutupan lahan dari citra multispektral, dan kelas mana yang sulit dibedakan?
#
# ## Tujuan
# 1. Menerapkan operasi analisis spasial dasar: jarak, zona *buffer*, cakupan layanan.
# 2. Mengoptimalkan lokasi shelter baru dengan K-Means berbobot populasi.
# 3. Mengekspor hasil ke **GeoJSON** agar dapat dibuka di QGIS.
# 4. Mengklasifikasikan lima kelas tutupan lahan dengan Random Forest memakai indeks spektral NDVI, NDWI, dan NDBI.
#
# ## Dasar Teori
# - **Hukum pertama geografi (Tobler):** segala sesuatu saling berhubungan, tetapi yang berdekatan lebih berhubungan. Dasar logika bahwa jarak ke shelter memengaruhi keterjangkauan.
# - **Sistem koordinat:** koordinat lintang/bujur (WGS84) dikonversi ke meter dengan proyeksi lokal agar jarak bermakna dalam meter. Pada GeoPandas, CRS metrik yang sesuai untuk Bengkulu adalah **EPSG:32748** (UTM zona 48 selatan).
# - **Buffer dan cakupan layanan:** area dalam radius tertentu dari suatu titik. Kelurahan dianggap terlayani bila jarak ke shelter terdekat ≤ 1,5 km (asumsi ±20 menit berjalan kaki).
# - **K-Means berbobot:** mengelompokkan titik dengan bobot (populasi) sehingga pusat klaster tertarik ke area berpenduduk padat.
# - **Indeks spektral:** `NDVI = (NIR − Red)/(NIR + Red)` untuk vegetasi, `NDWI = (Green − NIR)/(Green + NIR)` untuk air, `NDBI = (SWIR − NIR)/(SWIR + NIR)` untuk lahan terbangun. Pada Sentinel-2: B2 biru, B3 hijau, B4 merah, B8 NIR, B11 SWIR.
#
# ## Dataset
# - **Kelurahan:** 45 titik sintetis (lat, lon, populasi, jarak ke pantai).
# - **Garis pantai:** garis lurus miring di sisi barat (penyederhanaan).
# - **Shelter eksisting:** 7 titik.
# - **Piksel tutupan lahan:** 300 sampel per kelas (Hutan, Sawit, Permukiman, Air, Lahan Terbuka) dengan reflektansi B2, B3, B4, B8, B11 dan derau pengukuran.
#
# ## Metodologi
# 1. Bangun data spasial dan hitung jarak ke pantai.
# 2. Tentukan zona rawan (≤ 3 km dari pantai) dan jarak ke shelter terdekat.
# 3. Hitung cakupan penduduk terlayani sebelum penambahan shelter.
# 4. Tempatkan 3 shelter baru dengan K-Means berbobot, lalu hitung ulang cakupan.
# 5. Petakan hasil dan ekspor GeoJSON; padanan GeoPandas bersifat opsional.
# 6. Klasifikasikan piksel dengan Random Forest dan evaluasi.
#
# ## Implementasi
# Angka pada sel **Interpretasi** berdasarkan seed bawaan.

# %%
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 110})
rng = np.random.default_rng(7)

# %% [markdown]
# ## 1. Data spasial sintetis di sekitar Kota Bengkulu
# Koordinat disimpan dalam derajat (WGS84), lalu diproyeksikan ke meter (proyeksi lokal ekuirektangular)
# agar jarak dalam meter. Garis pantai disederhanakan sebagai garis lurus miring di sisi barat.

# %%
LAT0, LON0 = -3.80, 102.26
M_PER_DEG_LAT = 110_574.0
M_PER_DEG_LON = 111_320.0 * np.cos(np.radians(LAT0))

def ke_meter(lat, lon):
    return (np.asarray(lon) - LON0) * M_PER_DEG_LON, (np.asarray(lat) - LAT0) * M_PER_DEG_LAT

def ke_derajat(x, y):
    return LAT0 + np.asarray(y) / M_PER_DEG_LAT, LON0 + np.asarray(x) / M_PER_DEG_LON

# Garis pantai: dari (lat -3.70, lon 102.19) ke (lat -3.90, lon 102.24)
pantai_lat = np.array([-3.70, -3.90])
pantai_lon = np.array([102.19, 102.24])
px, py = ke_meter(pantai_lat, pantai_lon)

def jarak_ke_pantai(x, y):
    """Jarak titik ke segmen garis pantai (meter)."""
    a = np.array([px[0], py[0]]); b = np.array([px[1], py[1]])
    ab = b - a
    p = np.column_stack([x, y]) - a
    t = np.clip(p @ ab / (ab @ ab), 0, 1)
    proj = a + t[:, None] * ab
    return np.linalg.norm(np.column_stack([x, y]) - proj, axis=1)

n_kel = 45
lat_k = rng.uniform(-3.89, -3.71, n_kel)
lon_pantai = np.interp(lat_k, pantai_lat[::-1], pantai_lon[::-1])
lon_k = lon_pantai + rng.uniform(0.002, 0.075, n_kel)
kelurahan = pd.DataFrame({
    "kelurahan": [f"Kelurahan-{i+1:02d}" for i in range(n_kel)],
    "lat": lat_k, "lon": lon_k,
    "populasi": rng.lognormal(mean=8.3, sigma=0.5, size=n_kel).astype(int),
})
kelurahan["x"], kelurahan["y"] = ke_meter(kelurahan["lat"], kelurahan["lon"])
kelurahan["jarak_pantai_m"] = jarak_ke_pantai(kelurahan["x"], kelurahan["y"])

# Shelter eksisting: 7 titik acak di sekitar kelurahan terpilih
idx_shelter = rng.choice(n_kel, 7, replace=False)
shelter = kelurahan.loc[idx_shelter, ["lat", "lon"]].reset_index(drop=True)
shelter["lat"] += rng.normal(0, 0.002, 7)
shelter["lon"] += rng.normal(0, 0.002, 7)
shelter["nama"] = [f"Shelter-{i+1}" for i in range(7)]
shelter["x"], shelter["y"] = ke_meter(shelter["lat"], shelter["lon"])

kelurahan.drop(columns=["x", "y"]).to_csv("data/kelurahan_sintetis.csv", index=False)
print(kelurahan.describe().round(2).loc[["min", "max", "mean"], ["populasi", "jarak_pantai_m"]])

# %% [markdown]
# ## 2. Analisis spasial: zona rawan, jarak ke shelter, cakupan layanan
# - Zona rawan = jarak ke pantai ≤ 3 km
# - Terlayani = shelter terdekat ≤ 1,5 km (asumsi jarak tempuh jalan kaki ±20 menit)

# %%
RADIUS_ZONA_M = 3000
RADIUS_LAYANAN_M = 1500

def jarak_ke_terdekat(xk, yk, xs, ys):
    d = np.sqrt((xk[:, None] - xs[None, :]) ** 2 + (yk[:, None] - ys[None, :]) ** 2)
    return d.min(axis=1), d.argmin(axis=1)

kelurahan["rawan"] = kelurahan["jarak_pantai_m"] <= RADIUS_ZONA_M
kelurahan["jarak_shelter_m"], kelurahan["shelter_terdekat"] = jarak_ke_terdekat(
    kelurahan["x"].values, kelurahan["y"].values, shelter["x"].values, shelter["y"].values)
kelurahan["terlayani"] = kelurahan["jarak_shelter_m"] <= RADIUS_LAYANAN_M

def cakupan(df):
    rawan = df[df["rawan"]]
    return rawan.loc[rawan["terlayani"], "populasi"].sum() / rawan["populasi"].sum() * 100

print(f"Kelurahan di zona rawan : {kelurahan['rawan'].sum()} dari {n_kel}")
print(f"Penduduk zona rawan     : {kelurahan.loc[kelurahan['rawan'], 'populasi'].sum():,}")
print(f"Cakupan shelter eksisting (penduduk zona rawan terlayani): {cakupan(kelurahan):.1f}%")
kurang = kelurahan[kelurahan["rawan"] & ~kelurahan["terlayani"]].sort_values("populasi", ascending=False)
print("\nKelurahan rawan belum terlayani (5 populasi terbesar):")
print(kurang[["kelurahan", "populasi", "jarak_pantai_m", "jarak_shelter_m"]].head().round(0).to_string(index=False))

# %% [markdown]
# ### Interpretasi: kondisi awal
# - Dari 45 kelurahan, **14** berada di zona rawan (≤ 3 km dari pantai) dengan total sekitar **47.800 penduduk**.
# - Hanya **37,3%** penduduk zona rawan yang berada dalam 1,5 km dari shelter eksisting. Sisanya (±62,7%) belum terlayani.
# - Daftar kelurahan terbesar yang belum terlayani (mis. Kelurahan-30 dan Kelurahan-39 dengan populasi >6.000 jiwa) menjadi kandidat prioritas karena jumlah penduduk terdampak besar.

# %% [markdown]
# ## 3. Optimasi lokasi: K-Means berbobot populasi
# Titik shelter baru ditempatkan di pusat massa kelompok kelurahan yang belum terlayani, lalu
# di-*snap* ke kelurahan terdekat agar berada di area permukiman.

# %%
K_BARU = 3
km = KMeans(n_clusters=K_BARU, n_init=10, random_state=42)
km.fit(kurang[["x", "y"]], sample_weight=kurang["populasi"])
baru_xy = km.cluster_centers_
baru = []
for cx, cy in baru_xy:
    d = np.hypot(kelurahan["x"] - cx, kelurahan["y"] - cy)
    baru.append(kelurahan.loc[d.idxmin(), ["lat", "lon"]].values)
baru = pd.DataFrame(baru, columns=["lat", "lon"])
baru["nama"] = [f"Usulan-{i+1}" for i in range(K_BARU)]
baru["x"], baru["y"] = ke_meter(baru["lat"], baru["lon"])

semua_x = np.concatenate([shelter["x"], baru["x"]])
semua_y = np.concatenate([shelter["y"], baru["y"]])
kelurahan["jarak_shelter_baru_m"], _ = jarak_ke_terdekat(kelurahan["x"].values, kelurahan["y"].values, semua_x, semua_y)
kel_setelah = kelurahan.copy()
kel_setelah["terlayani"] = kel_setelah["jarak_shelter_baru_m"] <= RADIUS_LAYANAN_M

sebelum, sesudah = cakupan(kelurahan), cakupan(kel_setelah)
print(f"Cakupan sebelum : {sebelum:.1f}%")
print(f"Cakupan sesudah : {sesudah:.1f}% (+{K_BARU} shelter usulan, {sesudah - sebelum:+.1f} poin)")
print(baru[["nama", "lat", "lon"]].round(5).to_string(index=False))

# %% [markdown]
# ### Interpretasi: hasil optimasi lokasi
# - Penambahan **3 shelter usulan** menaikkan cakupan dari 37,3% menjadi **80,6%** (naik ±43 poin persentase).
# - Lokasi usulan dipilih dengan K-Means berbobot populasi lalu di-*snap* ke kelurahan terdekat agar berada di area permukiman, bukan di laut atau lahan kosong.
# - Ini usulan awal berbasis jarak. Keputusan nyata perlu mempertimbangkan kapasitas bangunan, ketinggian tanah, kondisi jalan, dan jalur evakuasi.

# %% [markdown]
# ## 4. Peta hasil + ekspor GeoJSON untuk QGIS

# %%
fig, ax = plt.subplots(figsize=(7, 7))
ax.plot(px, py, color="#1570EF", lw=3, label="Garis pantai (sintetis)")
rawan = kelurahan[kelurahan["rawan"]]
aman = kelurahan[~kelurahan["rawan"]]
ax.scatter(aman["x"], aman["y"], s=aman["populasi"] / 60, color="#D0D5DD", label="Kelurahan luar zona rawan")
ok = kel_setelah[kel_setelah["rawan"] & kel_setelah["terlayani"]]
ng = kel_setelah[kel_setelah["rawan"] & ~kel_setelah["terlayani"]]
ax.scatter(ok["x"], ok["y"], s=ok["populasi"] / 60, color="#27AE60", alpha=0.8, label="Rawan, terlayani")
ax.scatter(ng["x"], ng["y"], s=ng["populasi"] / 60, color="#D9383A", alpha=0.9, label="Rawan, belum terlayani")
ax.scatter(shelter["x"], shelter["y"], marker="^", s=120, color="#101828", label="Shelter eksisting")
ax.scatter(baru["x"], baru["y"], marker="*", s=300, color="#F39C12", edgecolor="#101828", label="Shelter usulan")
for _, r in baru.iterrows():
    ax.add_patch(plt.Circle((r["x"], r["y"]), RADIUS_LAYANAN_M, fill=False, ls="--", color="#F39C12"))
ax.set_aspect("equal")
ax.set_xlabel("x (m, relatif pusat)"); ax.set_ylabel("y (m)")
ax.set_title(f"Cakupan shelter di zona rawan: {sebelum:.0f}% → {sesudah:.0f}%")
ax.legend(frameon=False, fontsize=8, loc="upper right")
plt.tight_layout()
plt.savefig("output/03_peta_shelter.png", dpi=200)
plt.show()

def fitur_titik(row, props):
    return {"type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(row["lon"]), float(row["lat"])]},
            "properties": props}

fitur = []
for _, r in kel_setelah.iterrows():
    fitur.append(fitur_titik(r, {"jenis": "kelurahan", "nama": r["kelurahan"], "populasi": int(r["populasi"]),
                                 "rawan": bool(r["rawan"]), "terlayani_setelah_usulan": bool(r["terlayani"]),
                                 "jarak_shelter_m": round(float(r["jarak_shelter_baru_m"]), 1)}))
for _, r in shelter.iterrows():
    fitur.append(fitur_titik(r, {"jenis": "shelter_eksisting", "nama": r["nama"]}))
for _, r in baru.iterrows():
    fitur.append(fitur_titik(r, {"jenis": "shelter_usulan", "nama": r["nama"]}))
fitur.append({"type": "Feature",
              "geometry": {"type": "LineString", "coordinates": [[float(a), float(b)] for a, b in zip(pantai_lon, pantai_lat)]},
              "properties": {"jenis": "garis_pantai_sintetis"}})
with open("output/hasil_analisis.geojson", "w", encoding="utf-8") as f:
    json.dump({"type": "FeatureCollection", "features": fitur}, f)
print("GeoJSON tersimpan: output/hasil_analisis.geojson (buka di QGIS: Layer > Add Layer > Add Vector Layer)")

# %% [markdown]
# ### Interpretasi: peta dan interoperabilitas
# - Peta menampilkan kelurahan rawan yang terlayani (hijau), yang belum terlayani (merah), shelter eksisting (segitiga), dan shelter usulan (bintang) beserta radius layanan 1,5 km.
# - Berkas **GeoJSON** dapat dibuka di QGIS (*Layer → Add Layer → Add Vector Layer*) dan dikelompokkan berdasarkan atribut `jenis`. Ini contoh bagaimana hasil analisis kode dibawa ke perangkat GIS desktop yang dibahas materi.

# %% [markdown]
# ### Opsional: padanan GeoPandas
# Sel ini hanya berjalan bila `geopandas` terpasang (sudah tersedia di Google Colab). Operasi *buffer* 1,5 km
# dilakukan pada CRS metrik **EPSG:32748** (UTM zona 48 selatan, yang mencakup Bengkulu).

# %%
try:
    import geopandas as gpd
    g = gpd.read_file("output/hasil_analisis.geojson")
    sh = g[g["jenis"].isin(["shelter_eksisting", "shelter_usulan"])].to_crs(32748)
    area_km2 = sh.geometry.buffer(RADIUS_LAYANAN_M).unary_union.area / 1e6
    print(f"Luas gabungan buffer layanan {RADIUS_LAYANAN_M} m (GeoPandas): {area_km2:.2f} km²")
except ImportError:
    print("geopandas tidak terpasang; sel opsional dilewati.")

# %% [markdown]
# ## 5. Klasifikasi tutupan lahan dari citra multispektral (setara alur GEE + ML)
# Sampel piksel sintetis (reflektansi Sentinel-2: B2, B3, B4, B8, B11) untuk 5 kelas.
# Fitur turunan: NDVI, NDWI, NDBI.

# %%
kelas = {
    #             B2    B3    B4    B8    B11
    "Hutan":        (0.03, 0.05, 0.03, 0.40, 0.15),
    "Sawit":        (0.04, 0.07, 0.05, 0.33, 0.18),
    "Permukiman":   (0.09, 0.11, 0.13, 0.22, 0.25),
    "Air":          (0.05, 0.07, 0.04, 0.02, 0.01),
    "Lahan_Terbuka": (0.10, 0.13, 0.17, 0.24, 0.32),
}
baris = []
for nama, mu in kelas.items():
    x = np.clip(rng.normal(mu, 0.025, size=(300, 5)), 0.001, None)
    d = pd.DataFrame(x, columns=["B2", "B3", "B4", "B8", "B11"])
    d["kelas"] = nama
    baris.append(d)
piksel = pd.concat(baris, ignore_index=True)
piksel["NDVI"] = (piksel["B8"] - piksel["B4"]) / (piksel["B8"] + piksel["B4"])
piksel["NDWI"] = (piksel["B3"] - piksel["B8"]) / (piksel["B3"] + piksel["B8"])
piksel["NDBI"] = (piksel["B11"] - piksel["B8"]) / (piksel["B11"] + piksel["B8"])
piksel.to_csv("data/piksel_tutupan_lahan_sintetis.csv", index=False)

fitur_ml = ["B2", "B3", "B4", "B8", "B11", "NDVI", "NDWI", "NDBI"]
Xtr, Xte, ytr, yte = train_test_split(piksel[fitur_ml], piksel["kelas"], test_size=0.25,
                                      random_state=42, stratify=piksel["kelas"])
rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1).fit(Xtr, ytr)
pred = rf.predict(Xte)
print(classification_report(yte, pred, digits=3))

labels = sorted(piksel["kelas"].unique())
cm = pd.DataFrame(confusion_matrix(yte, pred, labels=labels), index=labels, columns=labels)
print("Matriks konfusi:\n", cm)
print("\nKepentingan fitur:")
print(pd.Series(rf.feature_importances_, index=fitur_ml).sort_values(ascending=False).round(3).to_string())

# %% [markdown]
# ### Interpretasi: klasifikasi tutupan lahan
# - Akurasi pada data uji sekitar **94,4%**. Kelas **Air** terpisah sempurna karena reflektansi NIR dan SWIR-nya sangat rendah.
# - Kesalahan terbesar terjadi pada pasangan **Hutan ↔ Sawit** (spektral keduanya mirip: sama-sama vegetasi lebat) dan **Permukiman ↔ Lahan Terbuka** (sama-sama tidak bervegetasi). Pada citra nyata, pembeda yang sering ditambahkan adalah **deret waktu** (pola musiman/panen) dan **tekstur** atau bentuk lahan.
# - Fitur yang paling berpengaruh adalah B11 (SWIR) dan B8 (NIR), karena keduanya paling membedakan vegetasi, air, dan tanah terbuka.

# %% [markdown]
# ## Ringkasan
# - Operasi inti GIS (jarak, buffer, cakupan, *snap*) dapat dijalankan sebagai kode dan hasilnya diekspor ke QGIS.
# - Optimasi sederhana (K-Means berbobot populasi) memberi usulan awal yang dapat dikaji pakar.
# - Klasifikasi tutupan lahan dengan ML membutuhkan data latih berlabel lapangan; pada kasus nyata,
#   ambil sampel dari Google Earth Engine dan validasi dengan survei lapangan.
# - Keterbatasan: jarak garis lurus bukan jarak tempuh jalan; model nyata perlu jaringan jalan, topografi, dan ketinggian.

# %% [markdown]
# ## Hasil dan Pembahasan (ringkasan)
# | Analisis | Temuan |
# |---|---|
# | Zona rawan | 14 dari 45 kelurahan, ±47.800 penduduk |
# | Cakupan awal | 37,3% penduduk zona rawan terlayani shelter ≤ 1,5 km |
# | Setelah 3 shelter usulan | 80,6% (naik ±43 poin) |
# | Klasifikasi lahan | Akurasi ±94,4%; Hutan↔Sawit dan Permukiman↔Lahan Terbuka paling sering tertukar |
#
# ## Kesimpulan
# 1. Analisis spasial dasar (jarak, buffer, cakupan) dapat menunjukkan celah layanan secara kuantitatif.
# 2. Optimasi sederhana dengan K-Means berbobot populasi memberi usulan lokasi yang efektif sebagai titik awal diskusi.
# 3. Hasil analisis dapat dibawa ke QGIS lewat GeoJSON, sehingga kode dan perangkat GIS saling melengkapi.
# 4. Klasifikasi tutupan lahan dengan ML bekerja baik pada kelas yang spektralnya berbeda dan kesulitan pada kelas yang spektralnya mirip.
# 5. Kombinasi GIS dan data science, seperti ditekankan narasumber, membuka banyak peluang karier.
#
# ## Keterbatasan
# - Data sintetis dan garis pantai disederhanakan menjadi garis lurus.
# - Jarak memakai garis lurus, bukan jarak tempuh di jaringan jalan; kapasitas shelter dan topografi tidak dimodelkan.
# - Klasifikasi memakai piksel tunggal sintetis tanpa konteks spasial dan tanpa validasi lapangan.
#
# ## Saran Pengembangan
# - Memakai data nyata: batas kelurahan (BPS/BIG), jaringan jalan (OpenStreetMap), data tsunami dari BNPB/BMKG, dan DEM.
# - Menghitung jarak jaringan jalan dan *service area* dengan PostGIS atau `osmnx`.
# - Mengambil citra Sentinel-2 dari Google Earth Engine dan melatih model dengan sampel lapangan; mencoba CNN/U-Net.
# - Mengemas hasil menjadi peta web interaktif (mis. Folium).
#
# ## Referensi
# > Rujukan di bawah adalah bacaan lanjutan. Periksa kembali penulisan, tahun, dan volume sebelum dikutip dalam laporan resmi.
# - Tobler, W. R. (1970). A computer movie simulating urban growth in the Detroit region. *Economic Geography*, 46, 234–240.
# - Rouse, J. W., dkk. (1974). Monitoring vegetation systems in the Great Plains with ERTS (NDVI).
# - McFeeters, S. K. (1996). The use of the Normalized Difference Water Index (NDWI). *International Journal of Remote Sensing*, 17(7).
# - Zha, Y., Gao, J., & Ni, S. (2003). Use of normalized difference built-up index. *International Journal of Remote Sensing*, 24(3).
# - Gorelick, N., dkk. (2017). Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment*, 202, 18–27.
# - Dokumentasi QGIS, GeoPandas, dan Copernicus Sentinel-2.
# - Materi Practitioner Lecture Series, Pertemuan 3 (catatan kuliah).
