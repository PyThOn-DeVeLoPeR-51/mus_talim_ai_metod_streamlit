def assess_drawing_by_rubric(metrics: dict) -> dict:
    """
    OpenCV texnik ko‘rsatkichlarini pedagogik rubrikaga aylantiradi.
    Bu baholash hozircha boshlang‘ich avtomatik baholashdir.
    """

    width = metrics.get("width", 0)
    height = metrics.get("height", 0)
    sharpness = metrics.get("sharpness", 0)
    drawing_density = metrics.get("drawing_density", 0)
    line_count = metrics.get("line_count", 0)
    contour_count = metrics.get("contour_count", 0)
    horizontal_lines = metrics.get("horizontal_lines", 0)
    vertical_lines = metrics.get("vertical_lines", 0)
    diagonal_lines = metrics.get("diagonal_lines", 0)

    # 1. Chizma tozaligi — 20 ball
    if 1 <= drawing_density <= 25 and sharpness >= 120:
        cleanliness_score = 20
    elif 0.5 <= drawing_density <= 35 and sharpness >= 80:
        cleanliness_score = 15
    elif drawing_density < 0.5:
        cleanliness_score = 7
    else:
        cleanliness_score = 10

    # 2. Kontur va asosiy chiziqlar — 20 ball
    if line_count >= 80 and contour_count >= 20:
        contour_line_score = 20
    elif line_count >= 40 and contour_count >= 10:
        contour_line_score = 16
    elif line_count >= 20 and contour_count >= 5:
        contour_line_score = 11
    else:
        contour_line_score = 6

    # 3. Proyeksion elementlar — 20 ball
    # Texnik/proyeksion chizmalarda gorizontal va vertikal chiziqlar muhim.
    projection_lines = horizontal_lines + vertical_lines

    if projection_lines >= 40:
        projection_score = 20
    elif projection_lines >= 20:
        projection_score = 16
    elif projection_lines >= 10:
        projection_score = 10
    else:
        projection_score = 5

    # 4. Chizma joylashuvi va kompozitsiyasi — 20 ball
    if width >= 1000 and height >= 700 and 1 <= drawing_density <= 25:
        composition_score = 20
    elif width >= 800 and height >= 600:
        composition_score = 15
    elif width >= 600 and height >= 400:
        composition_score = 10
    else:
        composition_score = 6

    # 5. Tekshirishga yaroqlilik — 20 ball
    if sharpness >= 150 and line_count >= 40:
        checkability_score = 20
    elif sharpness >= 80 and line_count >= 20:
        checkability_score = 15
    elif sharpness >= 40 and line_count >= 10:
        checkability_score = 10
    else:
        checkability_score = 5

    rubric_score = (
        cleanliness_score
        + contour_line_score
        + projection_score
        + composition_score
        + checkability_score
    )

    rubric_score = min(max(rubric_score, 0), 100)

    feedback = (
        f"Rubrika asosida chizma baholandi.\n\n"
        f"Umumiy rubrika balli: {rubric_score}/100\n\n"
        f"Mezonlar bo‘yicha natija:\n"
        f"1. Chizma tozaligi: {cleanliness_score}/20\n"
        f"2. Kontur va asosiy chiziqlar: {contour_line_score}/20\n"
        f"3. Proyeksion elementlar: {projection_score}/20\n"
        f"4. Chizma joylashuvi va kompozitsiyasi: {composition_score}/20\n"
        f"5. Tekshirishga yaroqlilik: {checkability_score}/20\n\n"
        f"Texnik ko‘rsatkichlar:\n"
        f"- Aniqlangan chiziqlar soni: {line_count}\n"
        f"- Aniqlangan konturlar soni: {contour_count}\n"
        f"- Gorizontal chiziqlar: {horizontal_lines}\n"
        f"- Vertikal chiziqlar: {vertical_lines}\n"
        f"- Qiya chiziqlar: {diagonal_lines}\n"
        f"- Chizma zichligi: {drawing_density}%\n"
        f"- Tiniqlik ko‘rsatkichi: {round(sharpness, 2)}\n\n"
        f"Izoh: bu baholash chizmaning texnik sifati va proyeksion elementlari "
        f"mavjudligini boshlang‘ich avtomatik tahlil qiladi. Keyingi bosqichlarda "
        f"o‘lcham chiziqlari, markaz chiziqlari, qirqim/kesim va proyeksiya mosligi "
        f"alohida model orqali chuqurroq baholanadi."
    )

    return {
        "rubric_score": rubric_score,
        "rubric_feedback": feedback,
        "rubric_parts": {
            "cleanliness_score": cleanliness_score,
            "contour_line_score": contour_line_score,
            "projection_score": projection_score,
            "composition_score": composition_score,
            "checkability_score": checkability_score,
        }
    }