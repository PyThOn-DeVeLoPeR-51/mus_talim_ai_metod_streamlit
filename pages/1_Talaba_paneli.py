import streamlit as st

import pandas as pd
import plotly.express as px

from pathlib import Path
from datetime import datetime

from utils.db import (
    add_student,
    add_submission,
    get_submissions_by_student,
    get_next_attempt_number,
    get_student_progress
)
from utils.assessment import assess_student_answer
from utils.file_analyzer import analyze_uploaded_file


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
        file_path = None

        if uploaded_file is not None:
            upload_dir = Path("uploads/submissions")
            upload_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_file_name = f"{timestamp}_{uploaded_file.name}"
            saved_path = upload_dir / safe_file_name

            with open(saved_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            file_path = str(saved_path)

        file_analysis = None
        extracted_text = None
        drawing_overlay_path = None
        drawing_score = None
        rubric_score = None
        rubric_feedback = None

        if file_path:
            file_result = analyze_uploaded_file(file_path)
            file_analysis = file_result.get("file_analysis")
            extracted_text = file_result.get("extracted_text")
            drawing_overlay_path = file_result.get("drawing_overlay_path")
            drawing_score = file_result.get("drawing_score")
            rubric_score = file_result.get("rubric_score")
            rubric_feedback = file_result.get("rubric_feedback")


        combined_answer = answer

        if extracted_text:
            combined_answer = f"{answer}\n\nPDF fayldan ajratilgan matn:\n{extracted_text}"

        assessment_result = assess_student_answer(
            answer_text=combined_answer,
            subject=subject
        )

        text_score = assessment_result["score"]
        final_score = text_score
        final_feedback = assessment_result["feedback"]
        final_status = assessment_result["status"]

        main_drawing_score = rubric_score if rubric_score is not None else drawing_score
        if main_drawing_score is not None:
            if answer.strip():
                final_score = round((main_drawing_score * 0.7) + (text_score * 0.3))
                final_feedback = (
                    f"Umumiy AI ball: {final_score}/100.\n\n"
                    f"Rubrika asosidagi chizma balli: "
                    f"{rubric_score if rubric_score is not None else '-'} /100.\n"
                    f"Boshlang‘ich texnik chizma sifati balli: "
                    f"{drawing_score if drawing_score is not None else '-'} /100.\n"
                    f"Matnli javob balli: {text_score}/100.\n\n"
                    f"Yakuniy AI ball hisobida rubrika asosidagi chizma bahosi 70%, "
                    f"matnli izoh 30% ulushda hisoblandi.\n\n"
                    f"{assessment_result['feedback']}"
                )
            else:
                final_score = drawing_score

                final_feedback = (
                    f"Umumiy AI ball: {final_score}/100.\n\n"
                    f"Baholash asosan yuklangan chizma asosida shakllantirildi.\n"
                    f"Rubrika asosidagi chizma balli: "
                    f"{rubric_score if rubric_score is not None else '-'} /100.\n"
                    f"Boshlang‘ich texnik chizma sifati balli: "
                    f"{drawing_score if drawing_score is not None else '-'} /100.\n\n"
                    f"Talaba qisqa izoh ham yozsa, baholash yanada to‘liqroq bo‘ladi."
                )

            if final_score >= 86:
                final_status = "A’lo"
            elif final_score >= 71:
                final_status = "Yaxshi"
            elif final_score >= 56:
                final_status = "Qoniqarli"
            else:
                final_status = "Qayta ishlash kerak"

        task_title = "1-mustaqil ta’lim topshirig‘i"

        attempt_number = get_next_attempt_number(
            student_id=st.session_state["student_id"],
            task_title=task_title
        )

        add_submission(
            student_id=st.session_state["student_id"],
            task_title="1-mustaqil ta’lim topshirig‘i",
            answer_text=answer,
            file_name=file_name,
            file_path=file_path,
            file_analysis=file_analysis,
            extracted_text=extracted_text,
            drawing_overlay_path=drawing_overlay_path,
            drawing_score=drawing_score,
            rubric_score=rubric_score,
            rubric_feedback=rubric_feedback,
            ai_score=final_score,
            ai_feedback=final_feedback,
            status=final_status,
            attempt_number=attempt_number
        )

        st.success(f"Topshiriq baholandi va SQLite bazaga saqlandi. Bu {attempt_number}-urinish.")


st.divider()

st.markdown("## 📚 Mening topshiriqlarim va natijalarim")

if "student_id" not in st.session_state:
    st.info("Natijalarni ko‘rish uchun avval talaba ma’lumotlarini kiriting va AI mustaqil ta’lim rejasini yarating.")
else:
    my_submissions = get_submissions_by_student(st.session_state["student_id"])

    if not my_submissions:
        st.warning("Siz hali topshiriq yubormagansiz.")
    else:
        result_table = [
            {
                "ID": row["id"],
                "Topshiriq": row["task_title"],
                "Urinish": f"{row['attempt_number']}-urinish",
                "AI ball": row["ai_score"],
                "Rubrika ball": row["rubric_score"] if row["rubric_score"] is not None else "-",
                "Texnik chizma balli": row["drawing_score"] if row["drawing_score"] is not None else "-",
                "Status": row["status"],
                "Fayl": row["file_name"] if row["file_name"] else "-",
                "Vaqt": row["created_at"],
            }
            for row in my_submissions
        ]

        st.dataframe(result_table, use_container_width=True)

        st.markdown("### 🔍 Batafsil natijani ko‘rish")

        submission_options = {
            f"{row['task_title']} | {row['attempt_number']}-urinish | AI ball: {row['ai_score']} | {row['created_at']}": row
            for row in my_submissions
        }

        selected_label = st.selectbox(
            "Topshiriqni tanlang",
            list(submission_options.keys()),
            key="student_submission_select"
        )

        selected = submission_options[selected_label]

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.metric("Umumiy AI ball", f"{selected['ai_score']}/100")

        with col_b:
            if selected["rubric_score"] is not None:
                st.metric("Rubrika ball", f"{selected['rubric_score']}/100")
            else:
                st.metric("Rubrika ball", "-")

        with col_c:
            if selected["drawing_score"] is not None:
                st.metric("Texnik chizma balli", f"{selected['drawing_score']}/100")
            else:
                st.metric("Texnik chizma balli", "-")

        st.metric("Urinish", f"{selected['attempt_number']}-urinish")

        st.markdown("### 🤖 AI feedback")
        st.info(selected["ai_feedback"])

        if selected["rubric_feedback"]:
            with st.expander("📋 Rubrika bo‘yicha batafsil tahlil", expanded=True):
                st.info(selected["rubric_feedback"])

        if selected["file_analysis"]:
            with st.expander("📎 Faylning texnik tahlili"):
                st.info(selected["file_analysis"])

        if selected["answer_text"]:
            with st.expander("✍️ Mening yozgan javobim"):
                st.write(selected["answer_text"])

        if selected["extracted_text"]:
            with st.expander("📄 PDFdan ajratilgan matn"):
                st.write(selected["extracted_text"])

        if selected["file_name"]:
            st.caption(f"Yuklangan fayl: {selected['file_name']}")

        if selected["drawing_overlay_path"]:
            st.markdown("### 🖼 OpenCV overlay natijasi")
            st.image(
                selected["drawing_overlay_path"],
                caption="Aniqlangan chiziqlar va konturlar",
                use_container_width=True
            )


st.divider()

st.markdown("## 📈 Mening progressim")

if "student_id" not in st.session_state:
    st.info("Progressni ko‘rish uchun avval talaba ma’lumotlarini kiriting.")
else:
    progress_rows = get_student_progress(
        student_id=st.session_state["student_id"],
        task_title="1-mustaqil ta’lim topshirig‘i"
    )

    if len(progress_rows) < 2:
        st.info("Progressni ko‘rish uchun kamida 2 ta urinish kerak.")
    else:
        progress_data = [
            {
                "Urinish": row["attempt_number"],
                "AI ball": row["ai_score"],
                "Rubrika ball": row["rubric_score"] if row["rubric_score"] is not None else 0,
                "Texnik chizma balli": row["drawing_score"] if row["drawing_score"] is not None else 0,
                "Status": row["status"],
                "Vaqt": row["created_at"],
            }
            for row in progress_rows
        ]

        progress_df = pd.DataFrame(progress_data)

        st.dataframe(progress_df, use_container_width=True)

        first_score = progress_df.iloc[0]["AI ball"]
        last_score = progress_df.iloc[-1]["AI ball"]
        growth = last_score - first_score

        col_p1, col_p2, col_p3 = st.columns(3)

        with col_p1:
            st.metric("Birinchi urinish", f"{first_score}/100")

        with col_p2:
            st.metric("Oxirgi urinish", f"{last_score}/100")

        with col_p3:
            st.metric("O‘sish", f"{growth:+}/100")

        if growth > 0:
            st.success(
                f"Sizning natijangiz {growth} ballga yaxshilangan. "
                f"Bu AI feedback asosida qayta ishlash ijobiy ta’sir qilganini ko‘rsatadi."
            )
        elif growth == 0:
            st.warning(
                "Natija o‘zgarmagan. Keyingi urinishda rubrika bo‘yicha tavsiyalarni aniqroq bajarish tavsiya etiladi."
            )
        else:
            st.error(
                f"Natija {abs(growth)} ballga pasaygan. "
                f"Chizma sifati, rubrika mezonlari va matnli izohni qayta ko‘rib chiqish kerak."
            )

        st.markdown("### 📊 Urinishlar bo‘yicha o‘sish grafigi")

        fig_progress = px.line(
            progress_df,
            x="Urinish",
            y="AI ball",
            markers=True,
            title="AI ballning urinishlar bo‘yicha o‘zgarishi"
        )

        st.plotly_chart(fig_progress, use_container_width=True)
