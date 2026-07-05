from pathlib import Path
from datetime import datetime

import fitz  # PyMuPDF
from PIL import Image

from utils.drawing_analyzer import analyze_drawing_image


def analyze_uploaded_file(file_path: str) -> dict:
    """
    Yuklangan faylni tahlil qiladi.
    PDF bo‘lsa: matn ajratadi + birinchi sahifani rasmga aylantirib OpenCV tahlil qiladi.
    Rasm bo‘lsa: format/o‘lcham + OpenCV chizma tahlili qiladi.
    """

    path = Path(file_path)

    if not path.exists():
        return {
            "file_analysis": "Fayl topilmadi.",
            "extracted_text": "",
            "drawing_overlay_path": None,
            "drawing_score": None
        }

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return analyze_pdf(path)

    if suffix in [".jpg", ".jpeg", ".png"]:
        return analyze_image(path)

    return {
        "file_analysis": f"{suffix} formatidagi fayl yuklangan. Hozircha bu format chuqur tahlil qilinmaydi.",
        "extracted_text": "",
        "drawing_overlay_path": None,
        "rubric_score": None,
        "rubric_feedback": None,
    }


def render_first_pdf_page_to_image(path: Path) -> str | None:
    """
    PDF birinchi sahifasini PNG rasmga aylantiradi.
    Keyin shu rasm OpenCV tahlilga beriladi.
    """

    try:
        output_dir = Path("outputs/pdf_pages")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"{timestamp}_{path.stem}_page1.png"

        doc = fitz.open(path)

        if len(doc) == 0:
            doc.close()
            return None

        page = doc[0]

        # 2x zoom — chizma aniqroq chiqishi uchun
        matrix = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=matrix, alpha=False)

        pix.save(str(output_path))

        doc.close()

        return str(output_path)

    except Exception:
        return None


def analyze_pdf(path: Path) -> dict:
    rubric_score = None
    rubric_feedback = None

    drawing_score = None
    extracted_text_parts = []

    try:
        doc = fitz.open(path)
        page_count = len(doc)

        for page in doc:
            text = page.get_text("text")
            if text:
                extracted_text_parts.append(text.strip())

        doc.close()

        extracted_text = "\n\n".join(extracted_text_parts).strip()

        if extracted_text:
            preview = extracted_text[:700]

            file_analysis = (
                f"PDF fayl tahlil qilindi.\n\n"
                f"Sahifalar soni: {page_count}\n"
                f"Ajratilgan matn uzunligi: {len(extracted_text)} belgi\n\n"
                f"Matndan qisqa parcha:\n{preview}"
            )
        else:
            file_analysis = (
                f"PDF fayl tahlil qilindi.\n\n"
                f"Sahifalar soni: {page_count}\n"
                f"PDF ichidan matn ajratilmadi. "
                f"Ehtimol, bu skaner qilingan PDF yoki rasm ko‘rinishidagi chizma."
            )

        rendered_image_path = render_first_pdf_page_to_image(path)

        drawing_overlay_path = None

        if rendered_image_path:
            drawing_result = analyze_drawing_image(rendered_image_path)
            rubric_score = drawing_result.get("rubric_score")
            rubric_feedback = drawing_result.get("rubric_feedback")

            file_analysis += (
                "\n\n"
                "PDF birinchi sahifasi rasmga aylantirildi va OpenCV orqali tahlil qilindi.\n\n"
                + drawing_result["drawing_analysis"]
            )

            drawing_overlay_path = drawing_result["drawing_overlay_path"]
            drawing_score = drawing_result.get("drawing_score")

        else:
            file_analysis += (
                "\n\n"
                "PDF sahifasini rasmga aylantirib bo‘lmadi. "
                "Shuning uchun OpenCV overlay yaratilmagan."
            )

        return {
            "file_analysis": file_analysis,
            "extracted_text": extracted_text,
            "drawing_overlay_path": drawing_overlay_path,
            "drawing_score": drawing_score,
            "rubric_score": rubric_score,
            "rubric_feedback": rubric_feedback,
        }


    except Exception as e:
        return {
            "file_analysis": f"PDF tahlilida xatolik yuz berdi: {e}",
            "extracted_text": "",
            "drawing_overlay_path": None,
            "rubric_score": None,
            "rubric_feedback": None,
        }


def analyze_image(path: Path) -> dict:
    try:
        with Image.open(path) as img:
            width, height = img.size
            image_format = img.format
            mode = img.mode

        base_analysis = (
            f"Rasm fayl tahlil qilindi.\n\n"
            f"Format: {image_format}\n"
            f"O‘lchami: {width} x {height} px\n"
            f"Rang rejimi: {mode}\n\n"
        )

        drawing_result = analyze_drawing_image(str(path))

        file_analysis = base_analysis + drawing_result["drawing_analysis"]

        return {
            "file_analysis": file_analysis,
            "extracted_text": "",
            "drawing_overlay_path": drawing_result["drawing_overlay_path"],
            "drawing_score": drawing_result["drawing_score"],
            "rubric_score": drawing_result.get("rubric_score"),
            "rubric_feedback": drawing_result.get("rubric_feedback"),
        }

    except Exception as e:
        return {
            "file_analysis": f"Rasm tahlilida xatolik yuz berdi: {e}",
            "extracted_text": "",
            "drawing_overlay_path": None
        }