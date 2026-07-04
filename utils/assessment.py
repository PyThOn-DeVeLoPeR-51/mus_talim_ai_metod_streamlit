def assess_student_answer(answer_text: str, subject: str = "Muhandislik grafikasi"):
    """
    Talaba javobini oddiy rubrika asosida baholash.
    Keyingi bosqichda bu modulga haqiqiy LLM API ulanadi.
    """

    if not answer_text or not answer_text.strip():
        return {
            "score": 0,
            "status": "Qayta ishlash kerak",
            "feedback": "Javob matni kiritilmagan. Talaba topshiriq bo‘yicha izohli javob yozishi kerak."
        }

    text = answer_text.lower()
    word_count = len(text.split())

    engineering_keywords = [
        "chizma",
        "proyeksiya",
        "proyeksion",
        "ko‘rinish",
        "korinish",
        "frontal",
        "gorizontal",
        "profil",
        "o‘lcham",
        "olcham",
        "detal",
        "kesim",
        "qirqim",
        "kontur",
        "masshtab",
        "markaz",
        "chiziq",
        "grafika"
    ]

    independent_thinking_keywords = [
        "menimcha",
        "xulosa",
        "tahlil",
        "sabab",
        "natija",
        "taqqoslash",
        "fikrimcha",
        "amaliy",
        "bosqich"
    ]

    practical_keywords = [
        "misol",
        "amaliy",
        "bajarish",
        "chizish",
        "tekshirish",
        "aniqlash",
        "solishtirish",
        "hisoblash",
        "joylashtirish"
    ]

    conclusion_keywords = [
        "xulosa",
        "yakun",
        "natijada",
        "shunday qilib",
        "demak"
    ]

    # 1. Mavzuni tushunish — 30 ball
    matched_engineering = [kw for kw in engineering_keywords if kw in text]
    understanding_score = min(len(matched_engineering) * 4, 30)

    # 2. Amaliy qo‘llash — 30 ball
    matched_practical = [kw for kw in practical_keywords if kw in text]
    practical_score = min(len(matched_practical) * 6, 30)

    # 3. Mustaqil fikr — 20 ball
    matched_independent = [kw for kw in independent_thinking_keywords if kw in text]
    independent_score = min(len(matched_independent) * 5, 20)

    # 4. Xulosa — 20 ball
    matched_conclusion = [kw for kw in conclusion_keywords if kw in text]
    conclusion_score = min(len(matched_conclusion) * 10, 20)

    # Javob uzunligi bo‘yicha kichik bonus
    length_bonus = 0
    if word_count >= 80:
        length_bonus = 10
    elif word_count >= 50:
        length_bonus = 6
    elif word_count >= 30:
        length_bonus = 3

    total_score = understanding_score + practical_score + independent_score + conclusion_score + length_bonus
    total_score = min(total_score, 100)

    if total_score >= 86:
        status = "A’lo"
    elif total_score >= 71:
        status = "Yaxshi"
    elif total_score >= 56:
        status = "Qoniqarli"
    else:
        status = "Qayta ishlash kerak"

    feedback_parts = []

    feedback_parts.append(f"Umumiy ball: {total_score}/100.")
    feedback_parts.append(f"Holat: {status}.")

    if understanding_score < 18:
        feedback_parts.append(
            "Mavzuni tushuntirish qismi yetarli emas. Javobda asosiy tushunchalar, terminlar va ularning mazmuni ko‘proq yoritilishi kerak."
        )
    else:
        feedback_parts.append(
            "Mavzuni tushunish qismi yaxshi yoritilgan."
        )

    if practical_score < 18:
        feedback_parts.append(
            "Amaliy qo‘llash qismi kuchsiz. Javobda real chizma, proyeksiya, detal yoki bajarish bosqichlari bilan bog‘liq misol keltirish tavsiya qilinadi."
        )
    else:
        feedback_parts.append(
            "Amaliy qo‘llash bo‘yicha javobda yetarli elementlar mavjud."
        )

    if independent_score < 12:
        feedback_parts.append(
            "Mustaqil fikr yetarli ko‘rinmayapti. Talaba o‘z tahlili, sababi va shaxsiy xulosasini aniqroq yozishi kerak."
        )
    else:
        feedback_parts.append(
            "Javobda mustaqil fikr va tahlil elementlari mavjud."
        )

    if conclusion_score < 10:
        feedback_parts.append(
            "Xulosa qismi kuchsiz. Javob oxirida umumlashtiruvchi xulosa berish tavsiya etiladi."
        )
    else:
        feedback_parts.append(
            "Xulosa qismi mavjud."
        )

    if word_count < 30:
        feedback_parts.append(
            "Javob juda qisqa. Mustaqil ta’lim topshirig‘i uchun kamida 50–80 so‘zli izohli javob yozish maqsadga muvofiq."
        )

    feedback = "\n\n".join(feedback_parts)

    return {
        "score": total_score,
        "status": status,
        "feedback": feedback
    }