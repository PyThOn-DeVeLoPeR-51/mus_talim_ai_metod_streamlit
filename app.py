import streamlit as st
from utils.db import init_db

init_db()

st.set_page_config(
    page_title="AI-Mustaqil",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI-Mustaqil")
st.subheader("Kredit-modul tizimida talabalar mustaqil ta’limini tashkil etish platformasi")

st.markdown("""
Ushbu platforma talabalar mustaqil ta’limini:

- individual rejalashtirish;
- AI mentor orqali yo‘naltirish;
- topshiriqlarni baholash;
- o‘qituvchi tomonidan monitoring qilish;
- learning analytics asosida tahlil qilish

uchun ishlab chiqilmoqda.
""")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.info("👨‍🎓 Talaba paneli")
    st.write("Diagnostika, mustaqil ta’lim rejasi, topshiriqlar va AI feedback.")

with col2:
    st.success("👨‍🏫 O‘qituvchi paneli")
    st.write("Talabalar faolligi, topshiriqlar, baholash va monitoring.")

with col3:
    st.warning("🤖 AI Mentor")
    st.write("Talabaga yo‘naltiruvchi savollar, tavsiyalar va baholash mezonlari.")

st.divider()

st.markdown("### Loyiha holati")
st.progress(10)
st.caption("1-bosqich: Streamlit MVP skeleti yaratildi.")