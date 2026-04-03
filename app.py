import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# إعداد الصفحة
st.set_page_config(page_title="نظام التحليل الأكاديمي", layout="wide")

# الشعار
MU_LOGO = "logo.png"

# --- CSS ---
st.markdown("""
<style>
html, body {
    text-align: right;
    font-family: 'Tajawal', sans-serif;
}

.center {
    text-align: center;
}

.main-header {
    text-align: center;
    color: #004a87;
    font-weight: bold;
    padding: 20px;
    border-bottom: 4px solid #b7934b;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# المستخدمين
users_db = {
    "admin": {"password": "123", "role": "teacher"},
    "101": {"password": "std", "role": "student"},
    "102": {"password": "std", "role": "student"},
    "103": {"password": "std", "role": "student"},
    "104": {"password": "std", "role": "student"},
    "105": {"password": "std", "role": "student"},
}

# --- AI ---
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
    
    # الشعار بالنص
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(MU_LOGO, width=200)
        st.markdown("<h2 class='center'>نظام التحليل الأكاديمي</h2>", unsafe_allow_html=True)
        st.markdown("<p class='center'>قسم تحليل البيانات والذكاء الاصطناعي</p>", unsafe_allow_html=True)
        st.markdown("<p class='center' style='color:gray;'>نموذج تجريبي</p>", unsafe_allow_html=True)

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

# --- بعد الدخول ---
else:
    st.sidebar.image(MU_LOGO, width=120)

    if st.sidebar.button("تسجيل خروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    # 👨‍🏫 الدكتور
    if st.session_state['role'] == "teacher":
        st.markdown("<div class='main-header'>لوحة تحكم الدكتور</div>", unsafe_allow_html=True)

        file = st.file_uploader("ارفع ملف Excel", type=['xlsx'])

        if file:
            df = pd.read_excel(file)

            if all(col in df.columns for col in ['Student_ID','Name','Grade','Attendance']):
                
                with st.spinner("جاري التحليل..."):
                    df = process_academic_analysis(df)

                st.session_state['data'] = df

                # مؤشرات
                col1, col2, col3 = st.columns(3)
                col1.metric("عدد الطلاب", len(df))
                col2.metric("المتوسط", f"{df['Grade'].mean():.1f}")
                col3.metric("عدد الحالات الخطرة", len(df[df['AI_Status']=="خطر"]))

                # Tabs بدل ما يكون الجدول تحت الرسم
                tab1, tab2 = st.tabs(["📊 الرسم البياني", "📋 الجدول"])

                with tab1:
                    fig = px.scatter(df, x="Attendance", y="Grade", color="AI_Status")
                    st.plotly_chart(fig, use_container_width=True)

                with tab2:
                    st.dataframe(df)

    # 👩‍🎓 الطالب
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
