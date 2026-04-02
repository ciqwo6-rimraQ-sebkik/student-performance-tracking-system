import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# إعداد الصفحة
st.set_page_config(page_title="نظام متابعة أداء الطلاب", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1f4e79;'>نظام متابعة أداء الطلاب</h1>", unsafe_allow_html=True)
st.markdown("---")

# تحميل البيانات
df = pd.read_excel("students.xlsx")

# حساب مستوى الخطر
def calculate_risk(row):
    if row["Grade"] < 60 or row["Attendance"] < 60:
        return "High"
    elif row["Grade"] < 75:
        return "Medium"
    else:
        return "Low"

df["Risk Level"] = df.apply(calculate_risk, axis=1)

# مؤشرات
total_students = len(df)
high_risk = len(df[df["Risk Level"] == "High"])
medium_risk = len(df[df["Risk Level"] == "Medium"])
low_risk = len(df[df["Risk Level"] == "Low"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("عدد الطلاب", total_students)
col2.metric("High Risk", high_risk)
col3.metric("Medium Risk", medium_risk)
col4.metric("Low Risk", low_risk)

# تلوين الجدول
def highlight_risk(val):
    if val == "High":
        return "background-color: #ffcccc"
    elif val == "Medium":
        return "background-color: #fff3cd"
    elif val == "Low":
        return "background-color: #d4edda"
    return ""

st.dataframe(df.style.applymap(highlight_risk, subset=["Risk Level"]))

# رسم بياني
fig, ax = plt.subplots()
ax.pie(
    [high_risk, medium_risk, low_risk],
    labels=["High", "Medium", "Low"],
    autopct='%1.1f%%'
)
st.pyplot(fig)