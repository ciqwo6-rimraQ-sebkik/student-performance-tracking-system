import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# إعداد الصفحة
st.set_page_config(page_title="نظام جامعة المجمعة للتحليل الأكاديمي", layout="wide")

# الشعار (ملف محلي داخل المجلد)
MU_LOGO = "logo.png"

# --- تصميم CSS ---
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif;
    text-align: right;
    background-color: #fcfcfc;
}

.main-header {
    color: #004a87;
    text-align: center;
    font-weight: bold;
    padding: 25px;
    border-bottom: 5px solid #b7934b;
    margin-bottom: 40px;
    background-color: #ffffff;
    border-radius: 8px;
}

.teacher-box {
    border: 2px solid #b7934b;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    color: #004a87;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# قاعدة المستخدمين
users_db = {
    "admin": {"password": "123", "role": "teacher", "full_name": "عضو هيئة التدريس"},
    "101": {"password": "std", "role": "student"},
    "102": {"password": "std", "role": "student"},
    "103": {"password": "std", "role": "student"},
}

# --- تحليل البيانات ---
def process_academic_analysis(df):
    X = df[['Grade', 'Attendance']]
    y = (df['Grade'] >= 60).astype(int)

    model = RandomForestClassifier()
    model.fit(X, y)

    df['Success_Probability'] = model.predict_proba(X)[:, 1] * 100
    df['AI_Status'] = ["مستقر" if p >= 50 else "خطر" for p in df['Success_Probability']]

    return df

# --- تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.image(MU_LOGO, width=200)

    st.markdown("<h2 style='text-align: center; color:#004a87;'>منصة التحليل الأكاديمي</h2>", unsafe_allow_html=True)

    with st.form("login"):
        user = st.text_input("اسم المستخدم")
        pwd = st.text_input("كلمة المرور", type="password")
        btn = st.form_submit_button("تسجيل الدخول")

        if btn:
            if user in users_db and users_db[user]["password"] == pwd:
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = user
                st.session_state['role'] = users_db[user]["role"]
                st.rerun()
            else:
                st.error("بيانات غير صحيحة")

# --- بعد تسجيل الدخول ---
else:
    st.sidebar.image(MU_LOGO, width=120)

    if st.sidebar.button("تسجيل خروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    # 👨‍🏫 واجهة الدكتور
    if st.session_state['role'] == "teacher":
        st.markdown("<div class='main-header'>لوحة التحكم</div>", unsafe_allow_html=True)

        file = st.file_uploader("ارفع ملف Excel", type=['xlsx'])

        if file:
            df = pd.read_excel(file)

            if all(col in df.columns for col in ['Student_ID','Name','Grade','Attendance']):
                with st.spinner("جاري التحليل..."):
                    df = process_academic_analysis(df)

                st.success("تم التحليل بنجاح ✅")

                st.session_state['data'] = df

                col1, col2, col3 = st.columns(3)
                col1.metric("عدد الطلاب", len(df))
                col2.metric("المتوسط", f"{df['Grade'].mean():.1f}")
                col3.metric("حالات الخطر", len(df[df['AI_Status']=="خطر"]))

                fig = px.scatter(df, x="Attendance", y="Grade", color="AI_Status")
                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(df)

                # تحميل البيانات
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("تحميل النتائج", csv, "students.csv")

            else:
                st.error("الأعمدة غير صحيحة")

    # 👩‍🎓 واجهة الطالب
    else:
        st.markdown("<div class='main-header'>تقرير الطالب</div>", unsafe_allow_html=True)

        if 'data' in st.session_state:
            df = st.session_state['data']

            student = df[df['Student_ID'].astype(str) == str(st.session_state['user_id'])]

            if not student.empty:
                s = student.iloc[0]

                st.metric("الدرجة", s['Grade'])
                st.metric("الحضور", s['Attendance'])

                st.progress(int(s['Success_Probability']))

                if s['Success_Probability'] < 50:
                    st.error("مستواك يحتاج تحسين")
                else:
                    st.success("أداء ممتاز 👏")

            else:
                st.warning("لا توجد بيانات")
        else:
            st.info("بانتظار رفع البيانات من الدكتور")
