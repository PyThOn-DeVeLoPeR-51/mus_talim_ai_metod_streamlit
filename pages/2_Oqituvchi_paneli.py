import streamlit as st
import pandas as pd

from utils.db import get_students, get_submissions, add_task

st.set_page_config(
    page_title="O‘qituvchi paneli",
    page_icon="👨‍🏫",
    layout="wide"
)

st.title("👨‍🏫 O‘qituvchi paneli")
st.subheader("Talabalar mustaqil ta’lim faoliyatini monitoring qilish")

st.info(
    "Bu sahifada o‘qituvchi talabalar faoliyati, topshiriqlar holati, "
    "AI baholash natijalari va xavf guruhidagi talabalarni ko‘radi."
)

st.divider()

st.markdown("## 1. Umumiy ko‘rsatkichlar")

students = get_students()
submissions = get_submissions()

students_count = len(students)
submissions_count = len(submissions)
not_submitted_count = max(students_count - submissions_count, 0)

if submissions_count > 0:
    average_score = round(
        sum(row["ai_score"] for row in submissions) / submissions_count,
        1
    )
else:
    average_score = 0


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Talabalar soni", students_count)

with col2:
    st.metric("Topshiriq bajarganlar", submissions_count)

with col3:
    st.metric("Bajarmaganlar", not_submitted_count)

with col4:
    st.metric("O‘rtacha ball", f"{average_score}%")


st.divider()

st.markdown("## 2. Bazadagi talabalar ro‘yxati")

students = get_students()

if students:
    students_data = [
        {
            "ID": row["id"],
            "Talaba": row["full_name"],
            "Guruh": row["group_name"],
            "Fan": row["subject"],
            "Haftalik vaqt": row["weekly_hours"],
            "Bilim darajasi": row["knowledge_level"],
            "Yaratilgan vaqt": row["created_at"]
        }
        for row in students
    ]

    df_students = pd.DataFrame(students_data)
    st.dataframe(df_students, use_container_width=True)
else:
    st.warning("Hozircha bazada talaba mavjud emas.")

#df = pd.DataFrame(data)

#st.dataframe(df, use_container_width=True)

st.divider()

st.markdown("## 3. Topshiriqlar natijalari")

submissions = get_submissions()

if submissions:
    submissions_data = [
        {
            "ID": row["id"],
            "Talaba": row["full_name"],
            "Guruh": row["group_name"],
            "Topshiriq": row["task_title"],
            "Fayl": row["file_name"],
            "AI ball": row["ai_score"],
            "Status": row["status"],
            "Vaqt": row["created_at"]
        }
        for row in submissions
    ]

    df_submissions = pd.DataFrame(submissions_data)
    st.dataframe(df_submissions, use_container_width=True)

    st.markdown("### 🤖 AI feedbackni batafsil ko‘rish")

    submission_options = {
        f"{row['full_name']} | {row['task_title']} | {row['created_at']}": row
        for row in submissions
    }

    selected_submission_label = st.selectbox(
        "Talaba topshirig‘ini tanlang",
        list(submission_options.keys())
    )

    selected_submission = submission_options[selected_submission_label]

    st.info(selected_submission["ai_feedback"])

    with st.expander("Talaba javobini ko‘rish"):
        st.write(selected_submission["answer_text"])

    if selected_submission["file_name"]:
        st.caption(f"Yuklangan fayl: {selected_submission['file_name']}")

    if selected_submission["file_path"]:
        st.code(selected_submission["file_path"])

    if selected_submission["file_analysis"]:
        with st.expander("📎 Fayl tahlilini ko‘rish"):
            st.info(selected_submission["file_analysis"])

    if selected_submission["extracted_text"]:
        with st.expander("📄 PDFdan ajratilgan to‘liq matn"):
            st.write(selected_submission["extracted_text"])

    if selected_submission["drawing_overlay_path"]:
        with st.expander("🖼 OpenCV overlay natijasi"):
            st.image(
                selected_submission["drawing_overlay_path"],
                caption="Aniqlangan chiziqlar va konturlar",
                use_container_width=True
            )

else:
    st.warning("Hozircha topshiriq yuborilmagan.")

task_title = st.text_input("Topshiriq nomi")
task_description = st.text_area("Topshiriq tavsifi")
deadline = st.date_input("Topshiriq muddati")

rubric = st.text_area(
    "Baholash mezonlari",
    value="""1. Mavzuni tushunish - 30 ball
2. Amaliy bajarish - 30 ball
3. Mustaqil fikr - 20 ball
4. Xulosa va izoh - 20 ball"""
)

if st.button("Topshiriq yaratish"):
    if not task_title.strip():
        st.error("Topshiriq nomini kiriting.")
    else:
        add_task(
            title=task_title,
            description=task_description,
            deadline=deadline,
            rubric=rubric
        )

        st.success("Topshiriq SQLite bazaga saqlandi.")