"""Bangun STUDI_KASUS.md (laporan tanpa kode) tiap pertemuan dari sel markdown di kode.py.

Jalankan dari akar repo:  python materi/tools/build_studi_kasus.py
Sumber tunggal tetap kode.py: ubah narasi di sana, lalu jalankan build_notebooks.py dan skrip ini.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
NOTEBOOK = {1: "Pertemuan_1_Analytics_and_AI.ipynb", 2: "Pertemuan_2_HPC.ipynb",
            3: "Pertemuan_3_GIS.ipynb", 4: "Pertemuan_4_Machine_Learning.ipynb",
            5: "Pertemuan_5_HCI_Visualisasi_Data.ipynb", 6: "Pertemuan_6_Deforestasi_Satelit_AI.ipynb"}
REPO = "YusufArrayyan/Informatics-Practiticioner-Lecturer-Series"


def markdown_cells(path):
    out = []
    for blok in re.split(r"(?m)^(?=# %%)", path.read_text(encoding="utf-8")):
        if not blok.startswith("# %% [markdown]"):
            continue
        baris = blok.split("\n")[1:]
        out.append("\n".join(b[2:] if b.startswith("# ") else b.lstrip("#") for b in baris).strip("\n"))
    return out


def main():
    for kode in sorted((ROOT / "materi").glob("pertemuan-*/kode.py")):
        folder = kode.parent
        nomor = int(folder.name.split("-")[1])
        sel = markdown_cells(kode)
        bagian = []
        for s in sel:
            s = s.replace("Jalankan sel-sel berikut berurutan. Setiap kelompok hasil diikuti sel **Interpretasi** yang menjelaskan maknanya (angka berdasarkan seed bawaan).",
                          "Seluruh kode ada di `kode.py` dan notebook utama; di bawah ini hasil dan interpretasinya (angka berdasarkan seed bawaan).")
            bagian.append(s)
        gambar = sorted((folder / "output").glob("*.png"))
        lampiran = ["## Lampiran: Gambar Hasil"]
        for g in gambar:
            lampiran.append(f"**{g.stem}**\n\n![{g.stem}](output/{g.name})\n")
        if len(lampiran) == 1:
            lampiran = []
        nb = NOTEBOOK[nomor]
        kepala = (f"> Laporan studi kasus ini dihasilkan otomatis dari narasi di `kode.py`. "
                  f"Kode lengkap: [`{nb}`](../../{nb}) "
                  f"([buka di Colab](https://colab.research.google.com/github/{REPO}/blob/main/{nb})) "
                  f"dan [`kode.py`](kode.py). Panduan KNIME: [`KNIME_GUIDE.md`](KNIME_GUIDE.md).\n")
        isi = bagian[0] + "\n\n" + kepala + "\n" + "\n\n".join(bagian[1:])
        if lampiran:
            isi += "\n\n" + "\n\n".join(lampiran)
        (folder / "STUDI_KASUS.md").write_text(isi.rstrip() + "\n", encoding="utf-8")
        print(folder.name, "-> STUDI_KASUS.md")


if __name__ == "__main__":
    main()
