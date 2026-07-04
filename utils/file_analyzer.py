from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image


def analyze_uploaded_file(file_path: str) -> dict:
    """
    Yuklangan faylni tahlil qiladi.
    PDF bo‘lsa matn ajratadi.
    Rasm bo‘lsa format, o‘lcham va umumiy ma’lumot qaytaradi.
    """

    path = Path(file_path)

    if not path.exists():
        return {
            "file_analysis": "Fayl topilmadi.",
            "extracted_text": ""
        }

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return analyze_pdf(path)

    if suffix in [".jpg", ".jpeg", ".png"]:
        return analyze_image(path)

    return {
        "file_analysis": f"{suffix} formatidagi fayl yuklangan. Hozircha bu format chuqur tahlil qilinmaydi.",
        "extracted_text": ""
    }


def analyze_pdf(path: Path) -> dict:
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
                f"Lekin PDF ichidan matn ajratilmadi. "
                f"Ehtimol, bu skaner qilingan PDF yoki rasm ko‘rinishidagi chizma. "
                f"Keyingi bosqichda bunday fayllar uchun OCR/chizma tahlili qo‘shiladi."
            )

        return {
            "file_analysis": file_analysis,
            "extracted_text": extracted_text
        }

    except Exception as e:
        return {
            "file_analysis": f"PDF tahlilida xatolik yuz berdi: {e}",
            "extracted_text": ""
        }


def analyze_image(path: Path) -> dict:
    try:
        with Image.open(path) as img:
            width, height = img.size
            image_format = img.format
            mode = img.mode

        file_analysis = (
            f"Rasm fayl tahlil qilindi.\n\n"
            f"Format: {image_format}\n"
            f"O‘lchami: {width} x {height} px\n"
            f"Rang rejimi: {mode}\n\n"
            f"Hozircha rasm ichidagi matn yoki chizma elementlari chuqur tahlil qilinmaydi. "
            f"Keyingi bosqichda OpenCV/OCR orqali chiziqlar, matnlar va chizma elementlarini ajratish qo‘shiladi."
        )

        return {
            "file_analysis": file_analysis,
            "extracted_text": ""
        }

    except Exception as e:
        return {
            "file_analysis": f"Rasm tahlilida xatolik yuz berdi: {e}",
            "extracted_text": ""
        }