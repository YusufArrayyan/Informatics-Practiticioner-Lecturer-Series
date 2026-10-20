# %% [markdown]
# # Pertemuan 5 — Human-Computer Interaction (HCI) & Data Visualization
# **Studi kasus:** HealthViz-HCI, dasbor pemantauan keterisian tempat tidur (BOR) rumah sakit dan tren kasus DBD
# untuk Dinas Kesehatan Kota.
#
# Prinsip dari materi yang diterapkan:
# - **Shneiderman's Mantra:** overview first → zoom & filter → details-on-demand
# - **Tufte:** data-ink ratio tinggi, tanpa *chartjunk*
# - **Preattentive attributes:** warna merah hanya untuk kondisi kritis
# - **Gestalt:** proximity, similarity, enclosure (kartu)
# - **Norman & WCAG:** feedback langsung, redundansi warna + teks, kontras terukur
# - **Ethical design:** sumbu grafik jujur (demo *lie factor*)
#
# > Nama rumah sakit dan angka hunian di sini **fiktif** untuk demonstrasi, bukan data riil fasilitas kesehatan.

# %%
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)
np.random.seed(42)

# %% [markdown]
# ## 1. Data sintetis

# %%
hospital_data = {
    "Nama_RS": ["RS Contoh A", "RS Contoh B", "RS Contoh C", "RS Contoh D", "RS Contoh E", "RS Contoh F"],
    "Wilayah": ["Gading Cempaka", "Ratu Agung", "Teluk Segara", "Ratu Samban", "Selebar", "Gading Cempaka"],
    "Total_Bed": [320, 150, 110, 95, 140, 80],
    "Bed_Terisi": [285, 102, 82, 86, 92, 45],
}
df_rs = pd.DataFrame(hospital_data)
df_rs["BOR_Persen"] = df_rs["Bed_Terisi"] / df_rs["Total_Bed"] * 100

def tentukan_status(bor):
    """Status + warna preattentive: merah hanya untuk kritis."""
    if bor >= 80.0:
        return "Kritis", "#D9383A"
    elif bor >= 70.0:
        return "Waspada", "#F39C12"
    return "Aman", "#27AE60"

df_rs["Status"], df_rs["Warna"] = zip(*df_rs["BOR_Persen"].apply(tentukan_status))

dates = pd.date_range(start="2026-09-20", periods=30, freq="D")
trend_cases = np.random.poisson(lam=18, size=30)
trend_cases[22:26] += np.array([15, 22, 28, 20])   # lonjakan DBD
df_trend = pd.DataFrame({"Tanggal": dates, "Kasus_Baru": trend_cases})

df_rs.to_csv("data/bor_rumah_sakit_sintetis.csv", index=False)
df_trend.to_csv("data/kasus_dbd_harian_sintetis.csv", index=False)
print(df_rs[["Nama_RS", "Wilayah", "Total_Bed", "Bed_Terisi", "BOR_Persen", "Status"]].round(1).to_string(index=False))

total_bed = int(df_rs["Total_Bed"].sum())
total_terisi = int(df_rs["Bed_Terisi"].sum())
bor_kota = total_terisi / total_bed * 100
rs_kritis = int((df_rs["Status"] == "Kritis").sum())
print(f"\nBOR kota {bor_kota:.1f}% | RS kritis: {rs_kritis}")

# %% [markdown]
# ## 2. Dasbor statis: Overview first + Tufte + Gestalt

# %%
fig, (ax_kpi, ax_bar, ax_line) = plt.subplots(3, 1, figsize=(11, 13),
                                              gridspec_kw={"height_ratios": [0.8, 2.2, 2.0]})
fig.patch.set_facecolor("#F8F9FA")

# Panel 1: kartu KPI (Gestalt: enclosure + proximity)
ax_kpi.axis("off")
status_kota, warna_kota = tentukan_status(bor_kota)
kpis = [
    ("TOTAL BED TERISI / KAPASITAS", f"{total_terisi:,} / {total_bed:,}", "#2C3E50", 0.02),
    ("RATA-RATA BOR KOTA", f"{bor_kota:.1f}%  ({status_kota})", warna_kota, 0.36),
    ("RS STATUS KRITIS (≥80%)", f"{rs_kritis} Rumah Sakit", "#D9383A" if rs_kritis else "#27AE60", 0.70),
]
for judul, nilai, warna, x0 in kpis:
    ax_kpi.add_patch(patches.FancyBboxPatch((x0, 0.1), 0.28, 0.8, boxstyle="round,pad=0.03",
                                            fc="white", ec="#D0D5DD", lw=1.5))
    ax_kpi.text(x0 + 0.14, 0.65, judul, fontsize=9, fontweight="bold", color="#667085", ha="center")
    ax_kpi.text(x0 + 0.14, 0.30, nilai, fontsize=15, fontweight="bold", color=warna, ha="center")

# Panel 2: bar chart BOR (data-ink tinggi, label langsung)
y_pos = np.arange(len(df_rs))
bars = ax_bar.barh(y_pos, df_rs["BOR_Persen"], color=df_rs["Warna"], height=0.55, edgecolor="none")
ax_bar.set_facecolor("#FFFFFF")
ax_bar.set_yticks(y_pos)
ax_bar.set_yticklabels(df_rs["Nama_RS"], fontsize=10, fontweight="bold", color="#1D2939")
ax_bar.invert_yaxis()
ax_bar.set_xlim(0, 105)
ax_bar.set_xlabel("Bed Occupancy Rate (%)", fontsize=10, fontweight="bold", color="#475467")
ax_bar.set_title("Tingkat Keterisian Tempat Tidur (BOR) per Rumah Sakit (data fiktif)",
                 fontsize=12, fontweight="bold", color="#101828", pad=12)
ax_bar.axvline(x=80, color="#D9383A", linestyle="--", linewidth=1.5, alpha=0.7)
ax_bar.text(80.5, len(df_rs) - 0.7, "Ambang kritis (80%)", color="#D9383A", fontsize=8, fontweight="bold")
for sp in ["top", "right"]:
    ax_bar.spines[sp].set_visible(False)
for sp in ["left", "bottom"]:
    ax_bar.spines[sp].set_color("#D0D5DD")
ax_bar.xaxis.grid(True, linestyle=":", alpha=0.6, color="#E4E7EC")
for bar, st in zip(bars, df_rs["Status"]):
    w = bar.get_width()
    ax_bar.text(w + 1.2, bar.get_y() + bar.get_height() / 2, f"{w:.1f}%  {st}",
                va="center", fontsize=9, fontweight="bold", color="#344054")   # teks = redundansi warna

# Panel 3: tren harian + sorot anomali
ax_line.set_facecolor("#FFFFFF")
ax_line.plot(df_trend["Tanggal"], df_trend["Kasus_Baru"], color="#1570EF", linewidth=2.2, label="Kasus baru harian")
anomali = df_trend[df_trend["Kasus_Baru"] >= 30]
ax_line.scatter(anomali["Tanggal"], anomali["Kasus_Baru"], color="#D9383A", s=65, zorder=5, label="Lonjakan (≥30 kasus)")
ax_line.set_title("Tren Kasus DBD Harian, 30 Hari Terakhir (data fiktif)", fontsize=12, fontweight="bold", color="#101828", pad=12)
ax_line.set_ylabel("Pasien masuk", fontsize=10, fontweight="bold", color="#475467")
for sp in ["top", "right"]:
    ax_line.spines[sp].set_visible(False)
for sp in ["left", "bottom"]:
    ax_line.spines[sp].set_color("#D0D5DD")
ax_line.yaxis.grid(True, linestyle=":", alpha=0.6, color="#E4E7EC")
ax_line.legend(frameon=False, loc="upper left", fontsize=9)

plt.tight_layout()
plt.savefig("output/05_dasbor_statis.png", dpi=200, facecolor=fig.get_facecolor(), bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 3. Audit aksesibilitas: kontras warna (WCAG, prinsip *Perceivable*)
# Rasio kontras warna grafis terhadap latar putih. WCAG 2.1 meminta ≥ 3:1 untuk komponen grafis dan ≥ 4,5:1 untuk teks biasa.

# %%
def luminans(hex_):
    r, g, b = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def kontras(a, b="#FFFFFF"):
    la, lb = sorted([luminans(a), luminans(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)

audit = pd.DataFrame({"status": ["Kritis", "Waspada", "Aman", "Biru tren"],
                      "warna": ["#D9383A", "#F39C12", "#27AE60", "#1570EF"]})
audit["kontras_vs_putih"] = audit["warna"].apply(kontras).round(2)
audit["lulus_grafis_3:1"] = audit["kontras_vs_putih"] >= 3
audit["lulus_teks_4.5:1"] = audit["kontras_vs_putih"] >= 4.5
print(audit.to_string(index=False))
print("\nTemuan: warna yang gagal 3:1 perlu digelapkan, dan status tidak boleh hanya mengandalkan warna "
      "(dasbor ini selalu menambahkan label teks, mendukung pengguna buta warna merah-hijau).")

# %% [markdown]
# ## 4. Ethical design: demo *lie factor* (sumbu terpotong)
# Dua grafik memakai data yang sama. Sumbu terpotong membuat selisih kecil tampak dramatis.

# %%
minggu = ["Pekan lalu", "Pekan ini"]
bor_minggu = [72.0, 76.0]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.6))
a1.bar(minggu, bor_minggu, color=["#98A2B3", "#D9383A"], width=0.5)
a1.set_ylim(70, 77)
a1.set_title("MENYESATKAN: sumbu mulai dari 70", fontsize=10, color="#B42318", fontweight="bold")
a2.bar(minggu, bor_minggu, color=["#98A2B3", "#1570EF"], width=0.5)
a2.set_ylim(0, 100)
a2.set_title("JUJUR: sumbu mulai dari 0", fontsize=10, color="#027A48", fontweight="bold")
for a in (a1, a2):
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
    a.set_ylabel("BOR kota (%)")
    for i, v in enumerate(bor_minggu):
        a.text(i, v + 0.3 if a is a1 else v + 1.5, f"{v:.0f}%", ha="center", fontweight="bold")
plt.tight_layout()
plt.savefig("output/05_lie_factor.png", dpi=200)
plt.show()
tinggi_a1 = (bor_minggu[1] - 70) / (bor_minggu[0] - 70)
tinggi_a2 = bor_minggu[1] / bor_minggu[0]
print(f"Perubahan data sebenarnya: {tinggi_a2 - 1:+.1%} | tinggi batang tampak berubah {tinggi_a1 - 1:+.0%} "
      f"pada sumbu terpotong (lie factor ≈ {(tinggi_a1 - 1) / (tinggi_a2 - 1):.0f}).")

# %% [markdown]
# ## 5. Dasbor web interaktif (Zoom & Filter + Details-on-Demand)
# File HTML mandiri tanpa dependensi. Saat filter kecamatan diubah, **kartu KPI ikut dihitung ulang** (prinsip *feedback* Norman).
# Hover pada titik grafik tren menampilkan rincian per tanggal (*details-on-demand*).

# %%
def svg_tren(df, w=900, h=240, pl=44, pr=16, pt=14, pb=30):
    n = len(df)
    ymax = int(np.ceil(df["Kasus_Baru"].max() * 1.1 / 10) * 10)
    xs = [pl + i * (w - pl - pr) / (n - 1) for i in range(n)]
    ys = [h - pb - v / ymax * (h - pt - pb) for v in df["Kasus_Baru"]]
    garis = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Tren kasus DBD harian 30 hari" style="width:100%;height:auto">']
    for tick in range(0, ymax + 1, 10):
        y = h - pb - tick / ymax * (h - pt - pb)
        out.append(f'<line x1="{pl}" x2="{w-pr}" y1="{y:.1f}" y2="{y:.1f}" stroke="#EAECF0" stroke-width="1"/>'
                   f'<text x="{pl-6}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="#667085">{tick}</text>')
    for i in (0, n // 2, n - 1):
        out.append(f'<text x="{xs[i]:.1f}" y="{h-8}" text-anchor="middle" font-size="11" fill="#667085">{df["Tanggal"].iloc[i].strftime("%d %b")}</text>')
    out.append(f'<polyline points="{garis}" fill="none" stroke="#1570EF" stroke-width="2.2"/>')
    for x, y, (_, r) in zip(xs, ys, df.iterrows()):
        anom = r["Kasus_Baru"] >= 30
        if anom:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#D9383A"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="transparent" tabindex="0">'
                   f'<title>{r["Tanggal"].strftime("%d %b %Y")}: {int(r["Kasus_Baru"])} kasus{" (lonjakan)" if anom else ""}</title></circle>')
    out.append("</svg>")
    return "\n".join(out)

baris_html = []
for _, r in df_rs.iterrows():
    kls = {"Kritis": "badge-kritis", "Waspada": "badge-waspada", "Aman": "badge-aman"}[r["Status"]]
    baris_html.append(f'''
        <tr data-wilayah="{r['Wilayah']}" data-terisi="{r['Bed_Terisi']}" data-total="{r['Total_Bed']}" data-status="{r['Status']}">
          <td><strong>{r['Nama_RS']}</strong></td>
          <td>{r['Wilayah']}</td>
          <td>{r['Bed_Terisi']} / {r['Total_Bed']}</td>
          <td><div class="bar-wrap"><div class="bar-bg"><div class="bar-fill" style="width:{r['BOR_Persen']:.1f}%;background:{r['Warna']}"></div></div>
              <span class="bar-val">{r['BOR_Persen']:.1f}%</span></div></td>
          <td><span class="badge {kls}">{r['Status']}</span></td>
        </tr>''')

opsi_wilayah = "\n".join(f'<option value="{w}">{w}</option>' for w in sorted(df_rs["Wilayah"].unique()))

TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HealthViz-HCI: Dasbor Kesiapsiagaan Fasilitas Kesehatan</title>
<style>
  * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  body { background:#F8F9FA; margin:0; padding:24px; color:#1D2939; }
  h1 { margin:0 0 6px; font-size:24px; color:#101828; }
  .sub { margin:0 0 20px; color:#667085; font-size:14px; }
  .kpi-container { display:flex; flex-wrap:wrap; gap:16px; margin-bottom:20px; }
  .kpi-card { flex:1 1 220px; background:#fff; padding:18px; border-radius:12px; border:1px solid #EAECF0; }
  .kpi-title { font-size:12px; font-weight:700; color:#667085; text-transform:uppercase; margin-bottom:6px; }
  .kpi-value { font-size:26px; font-weight:800; color:#101828; }
  .c-kritis { color:#B42318; } .c-waspada { color:#B54708; } .c-aman { color:#027A48; }
  .filter { background:#fff; padding:14px 18px; border-radius:10px; border:1px solid #EAECF0; margin-bottom:20px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
  .filter label { font-size:14px; font-weight:600; color:#344054; }
  .filter select { padding:10px 12px; border-radius:6px; border:1px solid #98A2B3; font-size:15px; background:#fff; min-height:44px; }
  .card { background:#fff; padding:20px; border-radius:12px; border:1px solid #EAECF0; margin-bottom:20px; }
  .card h2 { margin:0 0 8px; font-size:16px; }
  table { width:100%; border-collapse:collapse; }
  th, td { padding:12px 14px; text-align:left; font-size:14px; border-bottom:1px solid #F2F4F7; }
  th { background:#F9FAFB; color:#475467; font-weight:600; }
  .bar-wrap { display:flex; align-items:center; gap:8px; }
  .bar-bg { background:#F2F4F7; border-radius:4px; height:12px; width:100%; min-width:80px; overflow:hidden; }
  .bar-fill { height:100%; border-radius:4px; }
  .bar-val { font-weight:700; font-size:12px; white-space:nowrap; }
  .badge { padding:4px 8px; border-radius:6px; font-size:12px; font-weight:700; display:inline-block; }
  .badge-kritis { background:#FEF3F2; color:#B42318; } .badge-waspada { background:#FFFAEB; color:#B54708; } .badge-aman { background:#ECFDF3; color:#027A48; }
  .note { font-size:12px; color:#667085; margin-top:8px; }
  circle:focus { outline: 2px solid #101828; }
</style>
</head>
<body>
<h1>HealthViz-HCI: Dasbor Monitoring Rumah Sakit Kota</h1>
<p class="sub">Contoh dengan data fiktif. Dirancang dengan Shneiderman's Mantra, Tufte (data-ink), Gestalt, dan WCAG.</p>

<!-- 1. OVERVIEW FIRST -->
<div class="kpi-container" aria-live="polite">
  <div class="kpi-card"><div class="kpi-title">Bed terisi / kapasitas</div><div class="kpi-value" id="kpiKapasitas">__TERISI__ / __TOTAL__</div></div>
  <div class="kpi-card"><div class="kpi-title">Rata-rata BOR</div><div class="kpi-value __KELAS_BOR__" id="kpiBor">__BOR__%</div></div>
  <div class="kpi-card"><div class="kpi-title">RS status kritis (≥80%)</div><div class="kpi-value __KELAS_KRITIS__" id="kpiKritis">__KRITIS__ RS</div></div>
</div>

<!-- 2. ZOOM & FILTER -->
<div class="filter">
  <label for="filterWilayah">Saring berdasarkan kecamatan:</label>
  <select id="filterWilayah">
    <option value="SEMUA">Seluruh kota</option>
    __OPSI__
  </select>
</div>

<!-- 3. DETAILS-ON-DEMAND -->
<div class="card">
  <h2>Kapasitas ruang rawat inap per rumah sakit</h2>
  <table id="tabelRS">
    <thead><tr><th>Rumah sakit</th><th>Kecamatan</th><th>Bed terisi / total</th><th style="width:28%">Keterisian (BOR)</th><th>Status</th></tr></thead>
    <tbody>__BARIS__</tbody>
  </table>
</div>

<div class="card">
  <h2>Tren kasus DBD harian, 30 hari terakhir</h2>
  __SVG__
  <p class="note">Titik merah = lonjakan (≥30 kasus). Arahkan kursor atau fokuskan dengan papan ketik pada titik untuk melihat rincian.</p>
</div>

<script>
  function kelasStatus(bor) { return bor >= 80 ? "c-kritis" : (bor >= 70 ? "c-waspada" : "c-aman"); }
  function perbarui() {
    var pilihan = document.getElementById("filterWilayah").value;
    var terisi = 0, total = 0, kritis = 0;
    document.querySelectorAll("#tabelRS tbody tr").forEach(function (tr) {
      var tampil = (pilihan === "SEMUA" || tr.getAttribute("data-wilayah") === pilihan);
      tr.style.display = tampil ? "" : "none";
      if (tampil) {
        terisi += parseInt(tr.getAttribute("data-terisi"));
        total += parseInt(tr.getAttribute("data-total"));
        if (tr.getAttribute("data-status") === "Kritis") kritis += 1;
      }
    });
    var bor = total > 0 ? terisi / total * 100 : 0;
    document.getElementById("kpiKapasitas").textContent = terisi + " / " + total;
    var elBor = document.getElementById("kpiBor");
    elBor.textContent = bor.toFixed(1) + "%";
    elBor.className = "kpi-value " + kelasStatus(bor);
    var elK = document.getElementById("kpiKritis");
    elK.textContent = kritis + " RS";
    elK.className = "kpi-value " + (kritis > 0 ? "c-kritis" : "c-aman");
  }
  document.getElementById("filterWilayah").addEventListener("change", perbarui);
  perbarui();
</script>
</body>
</html>
"""

kelas = lambda bor: "c-kritis" if bor >= 80 else ("c-waspada" if bor >= 70 else "c-aman")
html = (TEMPLATE.replace("__TERISI__", str(total_terisi)).replace("__TOTAL__", str(total_bed))
        .replace("__BOR__", f"{bor_kota:.1f}").replace("__KELAS_BOR__", kelas(bor_kota))
        .replace("__KRITIS__", str(rs_kritis)).replace("__KELAS_KRITIS__", "c-kritis" if rs_kritis else "c-aman")
        .replace("__OPSI__", opsi_wilayah).replace("__BARIS__", "".join(baris_html))
        .replace("__SVG__", svg_tren(df_trend)))
with open("output/healthviz_dashboard_interactive.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Dasbor interaktif tersimpan: output/healthviz_dashboard_interactive.html (buka di browser)")

# %% [markdown]
# ## 6. Evaluasi usability (Heuristic Evaluation Nielsen, ringkas)
# | Heuristik | Penerapan di HealthViz-HCI | Status |
# |---|---|---|
# | Visibility of system status | KPI selalu tampil & berubah saat filter | ✔ |
# | Recognition over recall | Label teks pada status, tanpa legenda tersembunyi | ✔ |
# | Consistency | Warna status sama di bar, badge, dan KPI | ✔ |
# | Error prevention | Filter berupa pilihan tertutup | ✔ |
# | Aesthetic & minimalist | Tanpa 3D, bayangan, atau grid pekat | ✔ |
# | Accessibility | Redundansi teks; kontras diaudit; kontrol dapat dioperasikan papan ketik | ⚠ oranye & hijau gagal 3:1 pada audit; perlu digelapkan |
#
# Langkah berikut yang disarankan materi: **usability testing** dengan persona (Kepala Bidang P2P) pada skenario
# "temukan RS kritis dalam <5 detik" dan ukur *success rate* serta waktu tugas.
