# Panduan KNIME — Pertemuan 5 (dasbor interaktif, Shneiderman's Mantra)

> Panduan membangun workflow di **KNIME Analytics Platform 5.x**. Berkas `.knwf` tidak disertakan (harus diekspor dari
> aplikasi). Nama node dapat berbeda antarversi.

Input: `data/bor_rumah_sakit_sintetis.csv`, `data/kasus_dbd_harian_sintetis.csv`

## A. Persiapan data
1. **CSV Reader** untuk kedua berkas.
2. **Rule Engine** pada `BOR_Persen`: `$BOR_Persen$ >= 80 => "Kritis"`, `$BOR_Persen$ >= 70 => "Waspada"`, `TRUE => "Aman"` → kolom `Status`.
3. **Color Manager** pada `Status`: Kritis `#D9383A`, Waspada `#F39C12`, Aman `#27AE60` (merah hanya untuk kritis = preattentive).
4. **Math Formula** untuk anomali tren: `$Kasus_Baru$ >= 30`.

## B. Komponen dasbor (Overview first)
KNIME 5 memakai **Components** dengan *widget* dan *view* sebagai dasbor.
1. Kartu KPI: **GroupBy** (Sum `Bed_Terisi`, Sum `Total_Bed`) → **Math Formula** BOR kota; **Rule Engine** untuk status → tampilkan dengan **Text Output** atau **Tile View**.
2. Bar chart BOR: **Bar Chart** (horizontal), warna dari Color Manager, tampilkan label nilai, matikan grid berlebih (data-ink tinggi).
3. Tren: **Line Plot** pada `Tanggal` vs `Kasus_Baru`; tandai anomali dengan warna merah melalui **Color Manager** di kolom anomali.

## C. Zoom & Filter
1. Bungkus langkah B dalam sebuah **Component** (Ctrl/Cmd+Shift+... atau klik kanan → *Create Component*).
2. Di dalamnya tambahkan **Single Selection Widget** (daftar kecamatan + "Seluruh kota") atau **Value Selection Widget**.
3. **Row Filter** dengan variabel alur dari widget → semua view (KPI, bar chart, tabel) otomatis mengikuti pilihan (*feedback* langsung).

## D. Details-on-demand
Pada view KNIME (**Bar Chart**, **Line Plot**), arahkan kursor untuk *tooltip*; tambahkan kolom `Nama_RS`, `Wilayah`, `Bed_Terisi` pada pengaturan tooltip. Tambahkan **Table View** sebagai rincian.

## E. Aksesibilitas & evaluasi
- Pastikan label teks pada status, bukan hanya warna.
- Gunakan palet kontras ≥3:1 untuk grafis (lihat audit di README, oranye dan hijau perlu digelapkan).
- Uji dengan skenario persona: "temukan RS kritis <5 detik", catat *success rate* dan waktu (usability testing).

## F. Distribusi
Component dapat dibagikan sebagai *composite view* di **KNIME Hub/Business Hub**; untuk berbagi cepat tanpa server, gunakan dasbor HTML hasil `kode.py`.
