from __future__ import annotations

import sys
from pathlib import Path
import pymupdf


def make_text_pdf(path: Path) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    rows = [
        (72, 110, "Prueba"), (280, 110, "Resultado"), (365, 110, "Unidad"), (455, 110, "Referencia"),
        (72, 150, "Glucosa"), (280, 150, "95"), (365, 150, "mg/dL"), (455, 150, "70 - 99"),
        (72, 185, "Creatinina"), (280, 185, "1.0"), (365, 185, "mg/dL"), (455, 185, "0.7 - 1.2"),
    ]
    page.insert_text((72, 65), "LABORATORIO CLINICO DE PRUEBA", fontsize=16)
    page.insert_text((72, 85), "Fecha de Registro: 16/08/2026", fontsize=11)
    for x, y, text in rows:
        page.insert_text((x, y), text, fontsize=13)
    doc.save(path)
    doc.close()


def make_uroculture_pdf(path: Path) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    y = 75
    for text in (
        "LABORATORIO CLINICO DE PRUEBA",
        "Fecha de Registro: 16/08/2026",
        "UROCULTIVO + CULTIVO",
        "CULTIVO",
        "---",
        "Sin",
        "desarrollo",
        "microbiano",
        "Método: Cultivo bacteriológico en medios específicos",
    ):
        page.insert_text((72, y), text, fontsize=13)
        y += 28
    doc.save(path)
    doc.close()


def make_scanned_pdf(text_pdf: Path, scanned_pdf: Path) -> None:
    src = pymupdf.open(text_pdf)
    pix = src[0].get_pixmap(matrix=pymupdf.Matrix(2.5, 2.5), alpha=False)
    image_bytes = pix.tobytes("png")
    src.close()
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    page.insert_image(page.rect, stream=image_bytes)
    doc.save(scanned_pdf)
    doc.close()


def main() -> int:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/codecafe-build-selftest")
    out.mkdir(parents=True, exist_ok=True)
    text_pdf = out / "embedded_text_test.pdf"
    scanned_pdf = out / "scanned_test.pdf"
    uroculture_pdf = out / "uroculture_test.pdf"
    make_text_pdf(text_pdf)
    make_scanned_pdf(text_pdf, scanned_pdf)
    make_uroculture_pdf(uroculture_pdf)
    print(text_pdf)
    print(scanned_pdf)
    print(uroculture_pdf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
