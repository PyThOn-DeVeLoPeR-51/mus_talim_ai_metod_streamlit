import streamlit as st

st.set_page_config(
    page_title="AI Mentor",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Mentor")
st.subheader("Talabani tayyor javob bilan emas, yo‘naltiruvchi savollar bilan o‘qitish")

st.warning(
    "AI Mentorning vazifasi talabaga tayyor javob berish emas, "
    "balki uni mustaqil fikrlashga yo‘naltirishdir."
)

st.divider()

st.markdown("## 1. Talaba savoli")

student_question = st.text_area(
    "Savolingizni yozing",
    placeholder="Masalan: Proyeksion chizmada asosiy ko‘rinishni qanday tanlayman?"
)

if st.button("AI Mentor javobini olish"):
    if student_question.strip():
        st.success("AI Mentor javobi:")

        st.markdown("""
        Siz savolni to‘g‘ri qo‘ydingiz. Avval tayyor javobga shoshilmaymiz.

        O‘ylab ko‘ring:

        1. Berilgan topshiriqda asosiy obyekt qaysi?
        2. Uni qaysi tomondan ko‘rsatsangiz, shakli eng aniq bilinadi?
        3. Frontal, gorizontal va profil ko‘rinishlar orasidagi bog‘lanish saqlanganmi?
        4. Siz tanlagan asosiy ko‘rinish boshqa ko‘rinishlarni qurishga yordam beradimi?

        Endi javobingizni 3-4 gapda asoslab yozing. Shundan keyin keyingi bosqichga o‘tamiz.
        """)
    else:
        st.error("Avval savol yozing.")

st.divider()

st.markdown("## 2. AI baholash rubrikasi namunasi")

st.markdown("""
| Mezon | Ball | Izoh |
|---|---:|---|
| Mavzuni tushunish | 30 | Talaba asosiy tushunchalarni to‘g‘ri izohlaydi |
| Amaliy qo‘llash | 30 | Talaba bilimni topshiriqda qo‘llay oladi |
| Mustaqil fikr | 20 | Talaba o‘z tahlilini beradi |
| Xulosa | 20 | Talaba natijani umumlashtira oladi |
""")