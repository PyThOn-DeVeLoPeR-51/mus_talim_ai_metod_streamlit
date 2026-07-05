from pathlib import Path
from datetime import datetime

import cv2
import numpy as np

from utils.rubric_drawing_assessment import assess_drawing_by_rubric


def analyze_drawing_image(image_path: str) -> dict:
    """
    JPG/PNG chizma faylini OpenCV asosida boshlang‘ich tahlil qiladi.
    Natijada chizma sifati, chiziqlar soni, konturlar va overlay rasm yo‘lini qaytaradi.
    """

    path = Path(image_path)

    if not path.exists():
        return {
            "drawing_analysis": "Chizma fayli topilmadi.",
            "drawing_overlay_path": None,
            "drawing_score": None,
            "rubric_score": None,
            "rubric_feedback": None,
        }

    image = cv2.imread(str(path))

    if image is None:
        return {
            "drawing_analysis": "Rasmni OpenCV orqali o‘qib bo‘lmadi.",
            "drawing_overlay_path": None,
            "drawing_score": None,
            "rubric_score": None,
            "rubric_feedback": None,
        }

    height, width = image.shape[:2]
    total_pixels = width * height

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Tiniqlik bahosi: Laplacian variance
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Chizma chiziqlarini ajratish uchun threshold
    _, binary_inv = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    drawing_pixels = cv2.countNonZero(binary_inv)
    drawing_density = round((drawing_pixels / total_pixels) * 100, 2)

    # Edge detection
    edges = cv2.Canny(gray, 50, 150)

    # Hough lines
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=80,
        minLineLength=40,
        maxLineGap=10
    )

    horizontal_lines = 0
    vertical_lines = 0
    diagonal_lines = 0

    if lines is not None:
        for line in lines:
            coords = np.array(line).flatten()

            if len(coords) >= 4:
                x1, y1, x2, y2 = coords[:4].astype(int)

                dx = abs(x2 - x1)
                dy = abs(y2 - y1)

                if dy <= 5 and dx > 20:
                    horizontal_lines += 1
                elif dx <= 5 and dy > 20:
                    vertical_lines += 1
                else:
                    diagonal_lines += 1

    line_count = 0 if lines is None else len(lines)

    # Contours
    contours, _ = cv2.findContours(
        binary_inv,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    filtered_contours = [
        c for c in contours
        if cv2.contourArea(c) > 30
    ]

    contour_count = len(filtered_contours)

    # Chizma sifati bo‘yicha boshlang‘ich ball hisoblash

    # 1. Rasm o‘lchami — 15 ball
    if width >= 1200 and height >= 800:
        resolution_score = 15
    elif width >= 800 and height >= 600:
        resolution_score = 12
    elif width >= 600 and height >= 400:
        resolution_score = 8
    else:
        resolution_score = 4

    # 2. Tiniqlik — 20 ball
    if sharpness >= 250:
        sharpness_score = 20
    elif sharpness >= 120:
        sharpness_score = 16
    elif sharpness >= 80:
        sharpness_score = 12
    elif sharpness >= 40:
        sharpness_score = 7
    else:
        sharpness_score = 3

    # 3. Chizma zichligi — 20 ball
    if 1 <= drawing_density <= 25:
        density_score = 20
    elif 0.5 <= drawing_density < 1:
        density_score = 12
    elif 25 < drawing_density <= 35:
        density_score = 14
    elif drawing_density < 0.5:
        density_score = 5
    else:
        density_score = 8

    # 4. Chiziqlar soni — 25 ball
    if line_count >= 80:
        line_score = 25
    elif line_count >= 40:
        line_score = 21
    elif line_count >= 20:
        line_score = 16
    elif line_count >= 10:
        line_score = 10
    else:
        line_score = 4

    # 5. Konturlar soni — 20 ball
    if contour_count >= 30:
        contour_score = 20
    elif contour_count >= 15:
        contour_score = 16
    elif contour_count >= 7:
        contour_score = 11
    elif contour_count >= 3:
        contour_score = 7
    else:
        contour_score = 3

    drawing_score = (
            resolution_score
            + sharpness_score
            + density_score
            + line_score
            + contour_score
    )

    drawing_score = min(max(drawing_score, 0), 100)

    metrics = {
        "width": width,
        "height": height,
        "sharpness": sharpness,
        "drawing_density": drawing_density,
        "line_count": line_count,
        "contour_count": contour_count,
        "horizontal_lines": horizontal_lines,
        "vertical_lines": vertical_lines,
        "diagonal_lines": diagonal_lines,
    }

    rubric_result = assess_drawing_by_rubric(metrics)
    rubric_score = rubric_result["rubric_score"]
    rubric_feedback = rubric_result["rubric_feedback"]

    # Sifat bo‘yicha oddiy tavsiyalar
    recommendations = []

    if width < 800 or height < 600:
        recommendations.append(
            "Rasm o‘lchami kichik. Chizma aniq baholanishi uchun yuqoriroq sifatda yuklash tavsiya etiladi."
        )

    if sharpness < 80:
        recommendations.append(
            "Rasm xira ko‘rinadi. Telefon kamerasi bilan olingan bo‘lsa, chizmani yorug‘ joyda qayta suratga olish tavsiya etiladi."
        )
    else:
        recommendations.append(
            "Rasm tiniqligi boshlang‘ich tahlil uchun yetarli."
        )

    if drawing_density < 0.5:
        recommendations.append(
            "Chizmada chiziqlar juda kam aniqlanyapti. Fayl bo‘sh, juda xira yoki noto‘g‘ri yuklangan bo‘lishi mumkin."
        )
    elif drawing_density > 35:
        recommendations.append(
            "Chizma juda zich ko‘rinadi. Ortiqcha qorayish, fon shovqini yoki skaner sifati past bo‘lishi mumkin."
        )
    else:
        recommendations.append(
            "Chiziqlar zichligi me’yoriy diapazonda."
        )

    if line_count < 10:
        recommendations.append(
            "Aniqlangan to‘g‘ri chiziqlar soni kam. Proyeksion yoki texnik chizma elementlari yetarli ko‘rinmasligi mumkin."
        )
    else:
        recommendations.append(
            "Chizmada yetarli miqdorda chiziq elementlari aniqlandi."
        )

    if contour_count < 3:
        recommendations.append(
            "Konturlar soni kam. Detal yoki geometrik elementlar yetarli ajralmagan bo‘lishi mumkin."
        )
    else:
        recommendations.append(
            "Kontur elementlari aniqlandi."
        )

    # Overlay rasm yaratish
    overlay = image.copy()

    if lines is not None:
        for line in lines[:300]:
            coords = np.array(line).flatten()

            if len(coords) >= 4:
                x1, y1, x2, y2 = coords[:4].astype(int)
                cv2.line(
                    overlay,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    2
                )

    for contour in filtered_contours[:150]:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 10 and h > 10:
            cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), 2)

    output_dir = Path("outputs/overlays")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    overlay_path = output_dir / f"{timestamp}_{path.stem}_overlay.png"

    cv2.imwrite(str(overlay_path), overlay)

    drawing_analysis = (
            f"OpenCV asosida chizma texnik tahlili bajarildi.\n\n"
            f"Boshlang‘ich texnik chizma sifati balli: {drawing_score}/100\n\n"
            f"Rasm o‘lchami: {width} x {height} px\n"
            f"Chizma piksel zichligi: {drawing_density}%\n"
            f"Aniqlangan chiziqlar soni: {line_count}\n"
            f"Aniqlangan konturlar soni: {contour_count}\n"
            f"Rasm tiniqligi ko‘rsatkichi: {round(sharpness, 2)}\n\n"
            f"Chiziqlar yo‘nalishi:\n"
            f"- Gorizontal chiziqlar: {horizontal_lines}\n"
            f"- Vertikal chiziqlar: {vertical_lines}\n"
            f"- Qiya chiziqlar: {diagonal_lines}\n\n"
            f"Texnik ball tarkibi:\n"
            f"- Rasm o‘lchami: {resolution_score}/15\n"
            f"- Tiniqlik: {sharpness_score}/20\n"
            f"- Chizma zichligi: {density_score}/20\n"
            f"- Chiziqlar soni: {line_score}/25\n"
            f"- Konturlar soni: {contour_score}/20\n\n"
            f"Tavsiyalar:\n- " + "\n- ".join(recommendations)
    )

    return {
        "drawing_analysis": drawing_analysis,
        "drawing_overlay_path": str(overlay_path),
        "drawing_score": drawing_score,
        "rubric_score": rubric_score,
        "rubric_feedback": rubric_feedback
    }