"""Membuat notebook utama (di akar repo) dari materi/pertemuan-*/kode.py.

Jalankan dari mana saja:  python materi/tools/build_notebooks.py
"""
import json
import re
from pathlib import Path

REPO = "YusufArrayyan/Informatics-Practiticioner-Lecturer-Series"
ROOT = Path(__file__).resolve().parent.parent.parent
NAMA = {
    1: "Pertemuan_1_Analytics_and_AI.ipynb",
    2: "Pertemuan_2_HPC.ipynb",
    3: "Pertemuan_3_GIS.ipynb",
    4: "Pertemuan_4_Machine_Learning.ipynb",
    5: "Pertemuan_5_HCI_Visualisasi_Data.ipynb",
    6: "Pertemuan_6_Deforestasi_Satelit_AI.ipynb",
}


def parse(text):
    cells, mode, buf = [], None, []

    def flush():
        if mode is None:
            return
        lines = list(buf)
        while lines and not lines[-1].strip():
            lines.pop()
        while lines and not lines[0].strip():
            lines.pop(0)
        if not lines:
            return
        if mode == "markdown":
            lines = [re.sub(r"^# ?", "", ln) for ln in lines]
        cells.append((mode, lines))

    for line in text.splitlines():
        if line.startswith("# %%"):
            flush()
            buf = []
            mode = "markdown" if "[markdown]" in line else "code"
        else:
            buf.append(line)
    flush()
    return cells


def to_notebook(cells, nama):
    badge = (f"[![Buka di Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
             f"(https://colab.research.google.com/github/{REPO}/blob/main/{nama})")
    nb_cells = [{"cell_type": "markdown", "metadata": {}, "source": [badge]}]
    for mode, lines in cells:
        src = [ln + "\n" for ln in lines[:-1]] + [lines[-1]]
        if mode == "markdown":
            nb_cells.append({"cell_type": "markdown", "metadata": {}, "source": src})
        else:
            nb_cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src})
    return {
        "cells": nb_cells,
        "metadata": {
            "colab": {"provenance": []},
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }


def main():
    for src in sorted((ROOT / "materi").glob("pertemuan-*/kode.py")):
        nomor = int(src.parent.name.split("-")[1])
        nb = to_notebook(parse(src.read_text(encoding="utf-8")), NAMA[nomor])
        out = ROOT / NAMA[nomor]
        out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{src.parent.name} -> {out.name} ({len(nb['cells'])} sel)")


if __name__ == "__main__":
    main()
