from multi_record_ocr import (
    PageDescriptor,
    classify_page,
    detect_date,
    repair_page_dates,
    segment_descriptors,
)


def test_spanish_date_formats():
    assert detect_date("Fecha: 20/nov./2024") == "2024-11-20"
    assert detect_date("Playa del Carmen, Q. Roo a 8 de Noviembre de 2024") == "2024-11-08"
    assert detect_date("Fecha 29/ago./2023") == "2023-08-29"


def test_ecg_classification():
    d = classify_page(1, "ELECTROCARDIOGRAMA 12 derivaciones FC 72 bpm PR 160 ms QRS 86 ms QTc 410")
    assert d.kind == "diagnostic"
    assert d.study_type == "Electrocardiograma"
    assert not d.needs_detail


def test_lab_pages_require_detail():
    d = classify_page(2, "SIMILAB Fecha 08/11/2024 QUIMICA SANGUINEA 50 ELEMENTOS RESULTADOS VAL. REFERENCIA Glucosa 97 mg/dL")
    assert d.lab == "SimiLab"
    assert d.kind == "laboratory"
    assert d.study_type == "Química sanguínea"
    assert d.needs_detail


def test_conservative_date_inheritance_for_continuation():
    pages = [
        classify_page(1, "SIMILAB Fecha 08/11/2024 QUIMICA SANGUINEA 50 ELEMENTOS"),
        classify_page(2, "SIMILAB QUIMICA SANGUINEA 50 ELEMENTOS RESULTADOS VAL REFERENCIA"),
        classify_page(3, "SIMILAB Fecha 08/11/2024 QUIMICA SANGUINEA 50 ELEMENTOS"),
    ]
    repairs = repair_page_dates(pages)
    assert pages[1].date == "2024-11-08"
    assert pages[1].inherited_date
    assert repairs[0]["reason"] == "matching-neighbours"


def test_different_dates_do_not_merge():
    pages = [
        classify_page(1, "SIMILAB Fecha 08/11/2024 EXAMEN GENERAL DE ORINA"),
        classify_page(2, "SIMILAB Fecha 05/02/2024 EXAMEN GENERAL DE ORINA"),
    ]
    records = segment_descriptors(pages)
    assert len(records) == 2
    assert records[0]["date"] == "2024-11-08"
    assert records[1]["date"] == "2024-02-05"


def test_ultrasound_report_and_image_page_can_stay_together():
    report = classify_page(1, "SIMILAB 13 de febrero de 2024 ULTRASONIDO ABDOMINAL Hígado riñones conclusión")
    image = PageDescriptor(
        page=2,
        date="2024-02-13",
        kind="diagnostic",
        study_type="Ultrasonido abdominal",
        lab="SimiLab",
        text="Ultrasonido imágenes",
        needs_detail=False,
    )
    records = segment_descriptors([report, image])
    assert len(records) == 1
    assert records[0]["pages"] == [1, 2]
