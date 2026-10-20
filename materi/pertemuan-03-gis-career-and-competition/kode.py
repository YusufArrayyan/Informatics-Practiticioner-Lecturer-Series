# %% [markdown]
# # Pertemuan 3 — Career and Competition in Indonesia with GIS
# **Studi kasus:** Penentuan lokasi titik evakuasi (shelter) tambahan untuk kelurahan di zona pesisir rawan tsunami,
# lalu klasifikasi tutupan lahan dengan *machine learning* dari citra multispektral.
#
# Keterampilan GIS yang disorot materi dan dipakai di sini:
# - Analisis spasial: jarak, *buffer*, cakupan layanan (setara operasi di **QGIS / PostGIS / GeoPandas**)
# - Pemrosesan data besar & klasifikasi tutupan lahan (setara alur **Google Earth Engine + ML**)
# - Ekspor **GeoJSON** agar hasil bisa dibuka langsung di QGIS
#
# > Lokasi, populasi, dan garis pantai pada notebook ini **sintetis** untuk demonstrasi metode,
# > bukan data kebencanaan resmi. Untuk keputusan nyata gunakan data BPBD/BIG.

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
# ## Ringkasan
# - Operasi inti GIS (jarak, buffer, cakupan, *snap*) dapat dijalankan sebagai kode dan hasilnya diekspor ke QGIS.
# - Optimasi sederhana (K-Means berbobot populasi) memberi usulan awal yang dapat dikaji pakar.
# - Klasifikasi tutupan lahan dengan ML membutuhkan data latih berlabel lapangan; pada kasus nyata,
#   ambil sampel dari Google Earth Engine dan validasi dengan survei lapangan.
# - Keterbatasan: jarak garis lurus bukan jarak tempuh jalan; model nyata perlu jaringan jalan, topografi, dan ketinggian.
