import streamlit as st

from utils.db import add_student, add_submission
from utils.assessment import assess_student_answer

st.set_page_config(
    page_title="Talaba paneli",
    page_icon="👨‍🎓",
    layout="wide"
)

st.title("👨‍🎓 Talaba paneli")
st.subheader("Mustaqil ta’lim diagnostikasi va individual o‘quv rejasi")

st.info(
    "Bu sahifada talaba dastlabki diagnostikadan o‘tadi, "
    "AI tomonidan tavsiya qilingan mustaqil ta’lim rejasini oladi "
    "va topshiriqlarni bajaradi."
)

st.divider()

st.markdown("## 1. Talaba ma’lumotlari")

col1, col2 = st.columns(2)

with col1:
    full_name = st.text_input("F.I.Sh.")
    group = st.text_input("Guruh")

with col2:
    subject = st.selectbox(
        "Fan",
        [
            "Muhandislik grafikasi",
            "Kompyuter grafikasi",
            "Dasturlash asoslari",
            "Sun’iy intellekt asoslari"
        ]
    )

    weekly_hours = st.slider(
        "Haftasiga mustaqil ta’lim uchun ajratadigan vaqtingiz",
        min_value=1,
        max_value=20,
        value=6
    )

st.divider()

st.markdown("## 2. Diagnostika savollari")

q1 = st.radio(
    "1. Ushbu fan bo‘yicha bilim darajangiz qanday?",
    ["Boshlang‘ich", "O‘rta", "Yaxshi", "Juda yaxshi"]
)

q2 = st.radio(
    "2. Mustaqil ta’lim topshiriqlarini bajarishda qaysi holat sizga ko‘proq mos?",
    [
        "Aniq ko‘rsatma bo‘lsa yaxshi bajaraman",
        "Namuna bo‘lsa tushunaman",
        "Mustaqil izlanib bajara olaman",
        "Loyiha asosida ishlashni yoqtiraman"
    ]
)

q3 = st.radio(
    "3. Qaysi turdagi topshiriq sizga qulay?",
    [
        "Matnli topshiriq",
        "Amaliy loyiha",
        "Chizma yoki grafik ish",
        "Test va savol-javob",
        "Aralash topshiriq"
    ]
)

q4 = st.text_area(
    "4. Ushbu fan bo‘yicha qaysi mavzularda qiynalasiz?"
)

st.divider()

if st.button("🤖 AI mustaqil ta’lim rejasini yaratish"):
    student_id = add_student(
        full_name=full_name,
        group_name=group,
        subject=subject,
        weekly_hours=weekly_hours,
        knowledge_level=q1,
        learning_style=q2,
        task_type=q3,
        difficult_topics=q4
    )

    st.session_state["student_id"] = student_id

    st.success("Talaba diagnostikasi yakunlandi. Quyida individual reja shakllantirildi.")

    st.markdown("## 3. 4 haftalik individual mustaqil ta’lim rejasi")

    st.markdown(f"""
    **Talaba:** {full_name if full_name else "Noma’lum"}  
    **Guruh:** {group if group else "Noma’lum"}  
    **Fan:** {subject}  
    **Haftalik vaqt:** {weekly_hours} soat  
    **Bilim darajasi:** {q1}

    ### 1-hafta
    - Mavzu: Fanning asosiy tushunchalarini takrorlash
    - Vazifa: Asosiy terminlar bo‘yicha qisqa konspekt tayyorlash
    - Natija: Talaba asosiy tushunchalarni izohlab bera oladi

    ### 2-hafta
    - Mavzu: Amaliy topshiriqlarni bajarish algoritmi
    - Vazifa: Berilgan namunani tahlil qilish
    - Natija: Talaba topshiriqni bosqichma-bosqich bajarish tartibini tushunadi

    ### 3-hafta
    - Mavzu: Mustaqil amaliy ish
    - Vazifa: O‘z yechimini ishlab chiqish va izohlash
    - Natija: Talaba mustaqil fikr asosida ish bajaradi

    ### 4-hafta
    - Mavzu: Yakuniy mini-loyiha
    - Vazifa: Amaliy natijani himoya qilish
    - Natija: Talaba bajargan ishini tushuntirib, xatolarini tahlil qiladi
    """)

st.divider()

st.markdown("## 4. Topshiriq yuklash")

answer = st.text_area("Topshiriq bo‘yicha javobingizni yozing")

uploaded_file = st.file_uploader(
    "Fayl yuklash",
    type=["pdf", "png", "jpg", "jpeg", "docx"]
)

if st.button("Topshiriqni yuborish"):
    if "student_id" not in st.session_state:
        st.error("Avval AI mustaqil ta’lim rejasini yarating.")
    elif not answer.strip() and uploaded_file is None:
        st.error("Avval javob yozing yoki fayl yuklang.")
    else:
        file_name = uploaded_file.name if uploaded_file else None

        assessment_result = assess_student_answer(
            answer_text=answer,
            subject=subject
        )

        add_submission(
            student_id=st.session_state["student_id"],
            task_title="1-mustaqil ta’lim topshirig‘i",
            answer_text=answer,
            file_name=file_name,
            ai_score=assessment_result["score"],
            ai_feedback=assessment_result["feedback"],
            status=assessment_result["status"]
        )

        st.success("Topshiriq baholandi va SQLite bazaga saqlandi.")

        st.markdown("## 🤖 AI feedback")
        st.metric("AI ball", f"{assessment_result['score']}/100")
        st.info(assessment_result["feedback"])