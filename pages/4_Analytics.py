import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import get_students, get_submissions


st.set_page_config(
    page_title="Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Learning Analytics")
st.subheader("Mustaqil ta’lim jarayonini real ma’lumotlar asosida tahlil qilish")

st.info(
    "Bu sahifa SQLite bazadagi talabalar va topshiriqlar natijalarini tahlil qiladi. "
    "O‘qituvchi talabalar faolligi, o‘rtacha ball, past natijalar va xavf guruhini ko‘rishi mumkin."
)

st.divider()

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
    st.metric("Topshiriq yuborganlar", submissions_count)

with col3:
    st.metric("Topshiriq yubormaganlar", not_submitted_count)

with col4:
    st.metric("O‘rtacha AI ball", f"{average_score}%")

st.divider()

if not submissions:
    st.warning("Hozircha analytics uchun topshiriq ma’lumotlari yetarli emas.")
else:
    submissions_data = [
        {
            "Talaba": row["full_name"],
            "Guruh": row["group_name"],
            "Topshiriq": row["task_title"],
            "AI ball": row["ai_score"],
            "Status": row["status"],
            "Vaqt": row["created_at"]
        }
        for row in submissions
    ]

    df = pd.DataFrame(submissions_data)

    st.markdown("## 1. Topshiriqlar natijalari jadvali")
    st.dataframe(df, use_container_width=True)

    st.divider()

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        fig1 = px.bar(
            df,
            x="Talaba",
            y="AI ball",
            color="Status",
            title="Talabalar bo‘yicha AI baholash natijalari"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        status_count = df["Status"].value_counts().reset_index()
        status_count.columns = ["Status", "Soni"]

        fig2 = px.pie(
            status_count,
            names="Status",
            values="Soni",
            title="Topshiriqlar statusi bo‘yicha taqsimot"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    st.markdown("## 2. Xavf guruhidagi talabalar")

    risk_df = df[df["AI ball"] < 56]

    if risk_df.empty:
        st.success("Hozircha xavf guruhidagi talaba aniqlanmadi.")
    else:
        st.warning("Quyidagi talabalar bilan individual ishlash tavsiya etiladi:")

        risk_table = risk_df.copy()
        risk_table["Tavsiya"] = risk_table["AI ball"].apply(
            lambda score: "Qayta topshirish va individual maslahat kerak"
            if score < 30
            else "Qo‘shimcha material berish va qayta ishlash tavsiya etiladi"
        )

        st.dataframe(risk_table, use_container_width=True)

    st.divider()

    st.markdown("## 3. Guruhlar bo‘yicha o‘rtacha natija")

    group_df = df.groupby("Guruh", as_index=False)["AI ball"].mean()
    group_df["AI ball"] = group_df["AI ball"].round(1)

    fig3 = px.bar(
        group_df,
        x="Guruh",
        y="AI ball",
        title="Guruhlar bo‘yicha o‘rtacha AI ball"
    )

    st.plotly_chart(fig3, use_container_width=True)