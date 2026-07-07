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
st.subheader("Mustaqil ta’lim natijalari, urinishlar va progress monitoringi")

st.info(
    "Bu sahifa talabalar mustaqil ta’lim topshiriqlari, AI baholash natijalari, "
    "rubrika asosidagi chizma ballari va qayta topshirish progressini tahlil qiladi."
)

st.divider()

students = get_students()
submissions = get_submissions()

students_count = len(students)
submissions_count = len(submissions)

if not submissions:
    st.warning("Hozircha analytics uchun topshiriq ma’lumotlari mavjud emas.")
    st.stop()

data = []

for row in submissions:
    data.append({
        "Submission ID": row["id"],
        "Student ID": row["student_id"],
        "Talaba": row["full_name"] if row["full_name"] else "Noma’lum",
        "Guruh": row["group_name"] if row["group_name"] else "Noma’lum",
        "Topshiriq": row["task_title"],
        "Urinish": row["attempt_number"] if row["attempt_number"] else 1,
        "AI ball": row["ai_score"] if row["ai_score"] is not None else 0,
        "Rubrika ball": row["rubric_score"] if row["rubric_score"] is not None else 0,
        "Texnik chizma balli": row["drawing_score"] if row["drawing_score"] is not None else 0,
        "Status": row["status"],
        "Fayl": row["file_name"] if row["file_name"] else "-",
        "Vaqt": row["created_at"]
    })

df = pd.DataFrame(data)

average_score = round(df["AI ball"].mean(), 1)
average_rubric = round(df["Rubrika ball"].mean(), 1)
average_drawing = round(df["Texnik chizma balli"].mean(), 1)

submitted_students_count = df["Student ID"].nunique()
not_submitted_count = max(students_count - submitted_students_count, 0)

total_attempts = len(df)
avg_attempts_per_student = round(total_attempts / submitted_students_count, 2) if submitted_students_count > 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Talabalar soni", students_count)

with col2:
    st.metric("Topshiriq yuborganlar", submitted_students_count)

with col3:
    st.metric("Topshiriq yubormaganlar", not_submitted_count)

with col4:
    st.metric("Umumiy urinishlar", total_attempts)

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric("O‘rtacha AI ball", f"{average_score}/100")

with col6:
    st.metric("O‘rtacha rubrika ball", f"{average_rubric}/100")

with col7:
    st.metric("O‘rtacha texnik chizma balli", f"{average_drawing}/100")

with col8:
    st.metric("Talabaga o‘rtacha urinish", avg_attempts_per_student)

st.divider()

st.markdown("## 1. Barcha topshiriqlar jadvali")

st.dataframe(
    df[
        [
            "Talaba",
            "Guruh",
            "Topshiriq",
            "Urinish",
            "AI ball",
            "Rubrika ball",
            "Texnik chizma balli",
            "Status",
            "Fayl",
            "Vaqt"
        ]
    ],
    use_container_width=True
)

st.divider()

st.markdown("## 2. Oxirgi natijalar bo‘yicha talaba holati")

latest_df = (
    df.sort_values(["Student ID", "Topshiriq", "Urinish"])
    .groupby(["Student ID", "Topshiriq"], as_index=False)
    .tail(1)
)

latest_table = latest_df[
    [
        "Talaba",
        "Guruh",
        "Topshiriq",
        "Urinish",
        "AI ball",
        "Rubrika ball",
        "Texnik chizma balli",
        "Status",
        "Vaqt"
    ]
].sort_values("AI ball", ascending=True)

st.dataframe(latest_table, use_container_width=True)

st.divider()

st.markdown("## 3. Urinishlar bo‘yicha progress tahlili")

progress_records = []

grouped = df.sort_values("Urinish").groupby(["Student ID", "Talaba", "Guruh", "Topshiriq"])

for (student_id, student_name, group_name, task_title), group in grouped:
    group = group.sort_values("Urinish")

    first_row = group.iloc[0]
    last_row = group.iloc[-1]

    first_score = first_row["AI ball"]
    last_score = last_row["AI ball"]
    growth = last_score - first_score

    first_rubric = first_row["Rubrika ball"]
    last_rubric = last_row["Rubrika ball"]
    rubric_growth = last_rubric - first_rubric

    first_drawing = first_row["Texnik chizma balli"]
    last_drawing = last_row["Texnik chizma balli"]
    drawing_growth = last_drawing - first_drawing

    if growth > 0:
        progress_status = "Yaxshilangan"
    elif growth == 0:
        progress_status = "O‘zgarmagan"
    else:
        progress_status = "Pasaygan"

    progress_records.append({
        "Talaba": student_name,
        "Guruh": group_name,
        "Topshiriq": task_title,
        "Urinishlar soni": len(group),
        "Birinchi AI ball": first_score,
        "Oxirgi AI ball": last_score,
        "AI o‘sish": growth,
        "Rubrika o‘sish": rubric_growth,
        "Texnik chizma o‘sish": drawing_growth,
        "Progress holati": progress_status
    })

progress_df = pd.DataFrame(progress_records)

if progress_df.empty:
    st.info("Progress tahlili uchun ma’lumot yetarli emas.")
else:
    st.dataframe(progress_df, use_container_width=True)

    improved_count = len(progress_df[progress_df["Progress holati"] == "Yaxshilangan"])
    unchanged_count = len(progress_df[progress_df["Progress holati"] == "O‘zgarmagan"])
    declined_count = len(progress_df[progress_df["Progress holati"] == "Pasaygan"])

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        st.metric("Yaxshilanganlar", improved_count)

    with col_p2:
        st.metric("O‘zgarmaganlar", unchanged_count)

    with col_p3:
        st.metric("Pasayganlar", declined_count)

    fig_progress_status = px.pie(
        progress_df,
        names="Progress holati",
        title="Progress holati bo‘yicha taqsimot"
    )

    st.plotly_chart(fig_progress_status, use_container_width=True)

st.divider()

st.markdown("## 4. Grafik tahlillar")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig_scores = px.bar(
        latest_df.sort_values("AI ball", ascending=False),
        x="Talaba",
        y="AI ball",
        color="Status",
        title="Talabalar bo‘yicha oxirgi AI ball"
    )
    st.plotly_chart(fig_scores, use_container_width=True)

with col_chart2:
    status_count = latest_df["Status"].value_counts().reset_index()
    status_count.columns = ["Status", "Soni"]

    fig_status = px.pie(
        status_count,
        names="Status",
        values="Soni",
        title="Oxirgi natijalar statusi"
    )
    st.plotly_chart(fig_status, use_container_width=True)

col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    fig_attempts = px.histogram(
        df,
        x="Urinish",
        title="Urinishlar soni bo‘yicha taqsimot",
        nbins=10
    )
    st.plotly_chart(fig_attempts, use_container_width=True)

with col_chart4:
    fig_score_distribution = px.histogram(
        latest_df,
        x="AI ball",
        nbins=10,
        title="Oxirgi AI ballar taqsimoti"
    )
    st.plotly_chart(fig_score_distribution, use_container_width=True)

st.divider()

st.markdown("## 5. Guruhlar bo‘yicha tahlil")

group_analysis = latest_df.groupby("Guruh", as_index=False).agg({
    "AI ball": "mean",
    "Rubrika ball": "mean",
    "Texnik chizma balli": "mean",
    "Student ID": "nunique"
})

group_analysis = group_analysis.rename(columns={
    "AI ball": "O‘rtacha AI ball",
    "Rubrika ball": "O‘rtacha rubrika ball",
    "Texnik chizma balli": "O‘rtacha texnik chizma balli",
    "Student ID": "Talabalar soni"
})

group_analysis["O‘rtacha AI ball"] = group_analysis["O‘rtacha AI ball"].round(1)
group_analysis["O‘rtacha rubrika ball"] = group_analysis["O‘rtacha rubrika ball"].round(1)
group_analysis["O‘rtacha texnik chizma balli"] = group_analysis["O‘rtacha texnik chizma balli"].round(1)

st.dataframe(group_analysis, use_container_width=True)

fig_group = px.bar(
    group_analysis,
    x="Guruh",
    y="O‘rtacha AI ball",
    title="Guruhlar bo‘yicha o‘rtacha AI ball"
)

st.plotly_chart(fig_group, use_container_width=True)

st.divider()

st.markdown("## 6. Xavf guruhidagi talabalar")

risk_df = latest_df[latest_df["AI ball"] < 56].copy()

if risk_df.empty:
    st.success("Hozircha xavf guruhidagi talaba aniqlanmadi.")
else:
    risk_df["Tavsiya"] = risk_df["AI ball"].apply(
        lambda score: "Individual maslahat, qayta topshirish va rubrika bo‘yicha ishlash kerak"
        if score < 40
        else "Qo‘shimcha material berish va qayta topshirish tavsiya etiladi"
    )

    st.warning("Quyidagi talabalar bilan individual ishlash tavsiya etiladi:")

    st.dataframe(
        risk_df[
            [
                "Talaba",
                "Guruh",
                "Topshiriq",
                "Urinish",
                "AI ball",
                "Rubrika ball",
                "Texnik chizma balli",
                "Status",
                "Tavsiya"
            ]
        ],
        use_container_width=True
    )

st.divider()

st.markdown("## 7. Rubrika va texnik chizma ballari solishtiruvi")

col_r1, col_r2 = st.columns(2)

with col_r1:
    fig_rubric = px.scatter(
        latest_df,
        x="Rubrika ball",
        y="AI ball",
        color="Status",
        hover_name="Talaba",
        title="Rubrika ball va umumiy AI ball bog‘liqligi"
    )
    st.plotly_chart(fig_rubric, use_container_width=True)

with col_r2:
    fig_drawing = px.scatter(
        latest_df,
        x="Texnik chizma balli",
        y="AI ball",
        color="Status",
        hover_name="Talaba",
        title="Texnik chizma balli va umumiy AI ball bog‘liqligi"
    )
    st.plotly_chart(fig_drawing, use_container_width=True)

st.divider()

st.markdown("## 8. Ilmiy-metodik xulosa")

if not progress_df.empty:
    avg_growth = round(progress_df["AI o‘sish"].mean(), 1)
    max_growth = progress_df["AI o‘sish"].max()
    min_growth = progress_df["AI o‘sish"].min()

    st.success(
        f"Urinishlar bo‘yicha o‘rtacha o‘sish {avg_growth} ballni tashkil etdi. "
        f"Eng yuqori o‘sish {max_growth} ball, eng past o‘zgarish {min_growth} ball. "
        f"Bu ko‘rsatkichlar AI feedback, rubrika asosida baholash va qayta topshirish mexanizmining "
        f"talabalar mustaqil ta’lim faoliyatiga ta’sirini tahlil qilish uchun ishlatiladi."
    )
else:
    st.info(
        "Ilmiy-metodik xulosa chiqarish uchun kamida 2 ta urinishga ega topshiriqlar bo‘lishi kerak."
    )