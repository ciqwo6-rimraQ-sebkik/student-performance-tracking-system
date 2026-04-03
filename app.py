import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# 1. إعدادات الصفحة الرسمية لجامعة المجمعة
st.set_page_config(page_title="نظام جامعة المجمعة للتنبؤ الأكاديمي", layout="wide")

# الرابط المباشر الصحيح للشعار
MU_LOGO = "https://www.mu.edu.sa/sites/default/files/2024-05/MU-Logo-New-2024.png"

# --- تنسيق CSS لإلغاء تدرج الألوان وجعل الواجهة رسمية ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; text-align: right; }
    
    .main-title { color: #004a87; text-align: center; font-weight: bold; padding: 15px; border-bottom: 3px solid #b7934b; margin-bottom: 30px; }
    
    /* جعل الجدول أبيض رسمي بدون تدرجات ألوان */
    .stDataFrame { background-color: white; }
    
    /* إخفاء القوائم غير الرسمية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* تنسيق النصوص الفرعية */
    .caption-text { text-align: center; color: #666; font-size: 0.9em; margin-top: -10px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- قاعدة بيانات المستخدمين ---
users_db = {
    "admin": {"password": "123", "role": "teacher"},
    "101": {"password": "std", "role": "student"},
    "102": {"password": "std", "role": "student"},
    "103": {"password": "std", "role": "student"},
    "104": {"password": "std", "role": "student"},
    "105": {"password": "std", "role": "student"}
}

# --- محرك الذكاء الاصطناعي ---
def train_ai_model(df):
    try:
        X = df[['Grade', 'Attendance']]
        y = (df['Grade'] >= 60).astype(int)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        df['Success_Probability'] = model.predict_proba(X)[:, 1] * 100
        df['AI_Status'] = ["متوقع النجاح" if p >= 50 else "متوقع التعثر" for p in df['Success_Probability']]
        return df, True
    except:
        return df, False

# --- واجهة تسجيل الدخول ---
def login_page():
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        st.image(MU_LOGO, use_container_width=True)
        st.markdown("<p class='caption-text'>مشروع تخرج - قسم علوم الحاسب</p>", unsafe_allow_html=True)
        
    st.markdown("<h2 class='main-title'>نظام التحليل التنبؤي للأداء الأكاديمي</h2>", unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3 = st.columns([1, 1.2, 1])
    with col_f2:
        with st.form("login_form"):
            u = st.text_input("الرقم الجامعي / اسم المستخدم")
            p = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("دخول للنظام"):
                if u in users_db and users_db[u]["password"] == p:
                    st.session_state.update({'logged_in': True, 'user_id': u, 'role': users_db[u]["role"]})
                    st.rerun()
                else:
                    st.error("خطأ في بيانات الدخول")

# --- واجهة المعلم ---
def teacher_dashboard():
    st.sidebar.image(MU_LOGO, use_container_width=True)
    st.sidebar.caption("🎓 نموذج تجريبي - مشروع تخرج 2026")
    st.sidebar.markdown("---")
    if st.sidebar.button("خروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.markdown("<h2 class='main-title'>وحدة المراقبة الأكاديمية (أعضاء هيئة التدريس)</h2>", unsafe_allow_html=True)
    
    file = st.file_uploader("ارفع سجل الطلاب (Excel)", type=['xlsx'])
    if file:
        df = pd.read_excel(file)
        df, _ = train_ai_model(df)
        st.session_state['data'] = df
        
        m1, m2, m3 = st.columns(3)
        m1.metric("عدد الطلاب", len(df))
        m2.metric("متوسط الدرجات", f"{df['Grade'].mean():.1f}%")
        m3.metric("حالات التعثر المحتملة", len(df[df['AI_Status'] == "متوقع التعثر"]))
        
        st.markdown("---")
        t1, t2 = st.tabs(["📊 التحليل التنبؤي", "📋 السجل الرقمي الموحد"])
        with t1:
            fig = px.scatter(df, x="Attendance", y="Grade", color="AI_Status",
                             color_discrete_map={"متوقع النجاح": "#004a87", "متوقع التعثر": "#991b1b"})
            st.plotly_chart(fig, use_container_width=True)
        with t2:
            st.dataframe(df.drop(columns=['Success_Probability']), use_container_width=True)

# --- واجهة الطالب ---
def student_dashboard():
    st.sidebar.image(MU_LOGO, use_container_width=True)
    st.sidebar.caption("🎓 نموذج تجريبي - مشروع تخرج 2026")
    if st.sidebar.button("خروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.markdown("<h2 class='main-title'>تقرير مؤشرات الأداء الأكاديمي للفصل الحالي</h2>", unsafe_allow_html=True)
    
    if 'data' in st.session_state:
        df = st.session_state['data']
        res = df[df['Student_ID'].astype(str) == str(st.session_state['user_id'])]
        
        if not res.empty:
            row = res.iloc[0]
            st.markdown(f"#### الطالب: {row['Name']}")
            
            c1, c2 = st.columns(2)
            c1.info(f"الدرجة الحالية: {row['Grade']}%")
            c2.info(f"نسبة الحضور: {row['Attendance']}%")
            
            prob = row['Success_Probability']
            st.metric("احتمالية النجاح المقدرة (AI)", f"{prob:.1f}%")
            
            if row['AI_Status'] == "متوقع التعثر":
                st.error("⚠️ تنبيه: يشير تحليل النظام إلى انخفاض في مؤشرات الأداء، يُنصح بمراجعة المرشد الأكاديمي لوضع خطة تحسين عاجلة.")
            else:
                st.success("✅ إشعار: بناءً على تحليل البيانات الحالية، يُظهر الطالب أداءً أكاديمياً متميزاً ومستقراً يتوافق مع معايير النجاح.")
        else:
            st.warning("البيانات غير متوفرة في النظام حالياً.")
    else:
        st.info("بانتظار تحديث البيانات من قبل القسم المختص.")

# --- إدارة الجلسة ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if not st.session_state['logged_in']: login_page()
else:
    if st.session_state['role'] == "teacher": teacher_dashboard()
    else: student_dashboard()
