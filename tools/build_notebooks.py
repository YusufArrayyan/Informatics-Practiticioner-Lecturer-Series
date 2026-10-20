"""Mengubah kode.py (format '# %%' / '# %% [markdown]') di tiap folder pertemuan menjadi notebook.ipynb untuk Google Colab.

Jalankan dari akar repo:  python tools/build_notebooks.py
"""
import json
import re
from pathlib import Path

REPO = "YusufArrayyan/Informatics-Practiticioner-Lecturer-Series"
ROOT = Path(__file__).resolve().parent.parent


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


def to_notebook(cells, path):
    badge = (f"[![Buka di Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
             f"(https://colab.research.google.com/github/{REPO}/blob/main/{path})")
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
    for src in sorted(ROOT.glob("pertemuan-*/kode.py")):
        folder = src.parent.name
        cells = parse(src.read_text(encoding="utf-8"))
        nomor = int(folder.split("-")[1])
        # 1) notebook di dalam folder pertemuan
        nb = to_notebook(cells, f"{folder}/notebook.ipynb")
        out = src.parent / "notebook.ipynb"
        out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
        # 2) notebook utama di akar repo (nama mudah ditemukan)
        nama_root = f"studi_kasus_dan_implementasi_lecture_series_pertemuan_{nomor}.ipynb"
        nb_root = to_notebook(cells, nama_root)
        (ROOT / nama_root).write_text(json.dumps(nb_root, ensure_ascii=False, indent=1), encoding="utf-8")
        n_code = sum(c["cell_type"] == "code" for c in nb["cells"])
        print(f"{folder}: {len(nb['cells'])} sel ({n_code} kode) -> {out.name} + {nama_root}")


if __name__ == "__main__":
    main()
