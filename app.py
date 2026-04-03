import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# --- إعداد الصفحة ---
st.set_page_config(page_title="نظام التحليل الأكاديمي", layout="wide")

# --- الشعار ---
MU_LOGO = "logo.png"

# --- CSS لتنسيق احترافي ---
st.markdown("""
<style>
html, body {
    font-family: 'Tajawal', sans-serif;
    text-align: right;
    background-color: white;
    padding: 0px;
    margin: 0px;
}

/* إطار الصفحة */
.main-container {
    border: 2px solid #004a87;
    border-radius: 15px;
    padding: 20px;
    margin: 20px auto;
    max-width: 900px;
}

/* الشعار */
.logo-container {
    text-align: center;
    margin-bottom: 10px;
}
.logo-container img {
    width: 180px;
    display: block;
    margin-left: auto;
    margin-right: auto;
}

/* العناوين */
.main-header {
    text-align: center;
    color: #004a87;
    font-weight: bold;
    font-size: 28px;
    margin-bottom: 5px;
    border-bottom: 3px solid #b7934b;
    padding-bottom: 10px;
}

/* نصوص تحت الشعار */
.sub-header {
    text-align: center;
    color: gray;
    margin-bottom: 20px;
}

/* خانات الطالب */
.metric-box {
    background-color: #f2f6fb;
    border: 1px solid #004a87;
    border-radius: 10px;
    padding: 15px;
    text-align: center;
    margin-bottom: 10px;
}

/* ألوان الرسم البياني */
.stable {color: #004a87; font-weight: bold;}  /* أزرق */
.danger {color: #b7934b; font-weight: bold;} /* ذهبي */
</style>
""", unsafe_allow_html=True)

# --- قاعدة المستخدمين ---
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
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='logo-container'>
        <img src='{MU_LOGO}' alt='Logo'>
    </div>
    <h2 class='main-header'>نظام التحليل الأكاديمي</h2>
    <p class='sub-header'>قسم تحليل البيانات والذكاء الاصطناعي</p>
    <p class='sub-header'>نموذج تجريبي</p>
    """, unsafe_allow_html=True)

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
    st.markdown("</div>", unsafe_allow_html=True)

# --- بعد تسجيل الدخول ---
else:
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='logo-container'>
        <img src='{MU_LOGO}' alt='Logo'>
    </div>
    <h2 class='main-header'>نظام التحليل الأكاديمي</h2>
    <p class='sub-header'>قسم تحليل البيانات والذكاء الاصطناعي</p>
    <p class='sub-header'>نموذج تجريبي</p>
    """, unsafe_allow_html=True)

    st.sidebar.image(MU_LOGO, width=120)
    if st.sidebar.button("تسجيل خروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    # 👨‍🏫 الدكتور
    if st.session_state['role'] == "teacher":
        st.markdown("<h3 class='stable'>تسجيل عضو هيئة تدريس</h3>", unsafe_allow_html=True)
        file = st.file_uploader("ارفع ملف Excel", type=['xlsx'])

        if file:
            df = pd.read_excel(file)
            if all(col in df.columns for col in ['Student_ID','Name','Grade','Attendance']):
                with st.spinner("جاري التحليل..."):
                    df = process_academic_analysis(df)
                st.session_state['data'] = df

                col1, col2, col3 = st.columns(3)
                col1.metric("عدد الطلاب", len(df))
                col2.metric("المتوسط", f"{df['Grade'].mean():.1f}")
                col3.metric("عدد الحالات الخطرة", len(df[df['AI_Status']=="خطر"]))

                tab1, tab2 = st.tabs(["📊 الرسم البياني", "📋 الجدول"])
                with tab1:
                    fig = px.scatter(
                        df,
                        x="Attendance",
                        y="Grade",
                        color="AI_Status",
                        color_discrete_map={"مستقر": "#004a87", "خطر": "#b7934b"},
                        hover_data=['Name','Grade','Attendance','Success_Probability']
                    )
                    fig.update_layout(title="تحليل أداء الطلاب", xaxis_title="الحضور", yaxis_title="الدرجة")
                    st.plotly_chart(fig, use_container_width=True)
                with tab2:
                    st.dataframe(df)

    # 👩‍🎓 الطالب
    else:
        if 'data' in st.session_state:
            df = st.session_state['data']
            student = df[df['Student_ID'].astype(str) == str(st.session_state['user_id'])]

            if not student.empty:
                s = student.iloc[0]
                col1, col2, col3 = st.columns(3)
                col1.metric("الدرجة", s['Grade'])
                col2.metric("الحضور", s['Attendance'])
                col3.metric("نسبة النجاح", f"{s['Success_Probability']:.1f}%")

                st.progress(int(s['Success_Probability']))

                if s['Success_Probability'] < 50:
                    st.error("مستواك يحتاج تحسين")
                else:
                    st.success("أداء ممتاز 👏")
            else:
                st.warning("لا توجد بيانات")
        else:
            st.info("بانتظار رفع البيانات من الدكتور")
    st.markdown("</div>", unsafe_allow_html=True)
