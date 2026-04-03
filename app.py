import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام جامعة المجمعة للذكاء الاصطناعي", layout="wide")

# رابط شعار مستقر
MU_LOGO = "https://upload.wikimedia.org/wikipedia/ar/b/b5/Majmaah_University_Logo.png"

# --- تنسيق CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; text-align: right; }
    .main-title { color: #004a87; text-align: center; font-weight: bold; padding: 15px; border-bottom: 3px solid #b7934b; margin-bottom: 30px; }
    .ai-card { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-right: 8px solid #b7934b; }
</style>
""", unsafe_allow_html=True)

# --- قاعدة بيانات المستخدمين (من 101 إلى 105) ---
users_db = {
    "admin": {"password": "123", "role": "teacher", "display_name": "عضو هيئة التدريس"},
    "101": {"password": "std", "role": "student", "display_name": "الطالب: 101"},
    "102": {"password": "std", "role": "student", "display_name": "الطالب: 102"},
    "103": {"password": "std", "role": "student", "display_name": "الطالب: 103"},
    "104": {"password": "std", "role": "student", "display_name": "الطالب: 104"},
    "105": {"password": "std", "role": "student", "display_name": "الطالب: 105"}
}

# --- محرك التحليل ---
def run_ai_engine(df):
    try:
        X = df[['Grade', 'Attendance']]
        y = (df['Grade'] >= 60).astype(int)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        df['Success_Prob'] = model.predict_proba(X)[:, 1] * 100
        df['Decision'] = ["متوقع النجاح" if p >= 50 else "متوقع التعثر" for p in df['Success_Prob']]
        return df, model.feature_importances_, True
    except:
        return df, [0.5, 0.5], False

# --- إدارة الدخول ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.image(MU_LOGO, width=180)
        st.markdown("<h3 style='text-align:center;'>قسم تحليل البيانات والذكاء الاصطناعي</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:gray;'>نموذج تجريبي</p>", unsafe_allow_html=True)
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            if u in users_db and users_db[u]["password"] == p:
                st.session_state.auth = True
                st.session_state.user_id = u
                st.session_state.role = users_db[u]["role"]
                st.session_state.display_name = users_db[u]["display_name"]
                st.rerun()
            else: st.error("خطأ في البيانات")
else:
    # --- القائمة الجانبية ---
    st.sidebar.image(MU_LOGO, width=150)
    st.sidebar.write(f"👤 **المستخدم:** {st.session_state.display_name}")
    st.sidebar.caption("🎓 نموذج تجريبي")
    if st.sidebar.button("خروج"):
        st.session_state.auth = False
        st.rerun()

    # --- واجهة عضو هيئة التدريس (admin) ---
    if st.session_state.role == "teacher":
        st.markdown("<h2 class='main-title'>منصة التحليل الذكي للأداء الأكاديمي</h2>", unsafe_allow_html=True)
        file = st.file_uploader("تغذية النظام ببيانات الطلاب (Excel)", type=['xlsx'])
        if file:
            df_raw = pd.read_excel(file)
            df, feat_imp, status = run_ai_engine(df_raw)
            st.session_state['shared_data'] = df
            t1, t2 = st.tabs(["📊 التحليل العام", "🤖 تحليل الذكاء الاصطناعي"])
            with t1:
                st.dataframe(df[['Student_ID', 'Name', 'Grade', 'Attendance', 'Decision']], use_container_width=True)
            with t2:
                st.markdown("<div class='ai-card'><h4>🧠 تحليل البيانات والذكاء الاصطناعي</h4></div>", unsafe_allow_html=True)
                st.write("**أهمية العوامل:**")
                imp_df = pd.DataFrame({'العامل': ['الدرجات', 'الحضور'], 'التأثير': feat_imp})
                st.bar_chart(imp_df.set_index('العامل'))

    # --- واجهة الطالب ---
    else:
        st.markdown("<h2 class='main-title'>تقرير الأداء الأكاديمي الذكي</h2>", unsafe_allow_html=True)
        if 'shared_data' in st.session_state:
            df = st.session_state['shared_data']
            # البحث عن بيانات الطالب الحالي في الملف المرفوع
            student_data = df[df['Student_ID'].astype(str) == str(st.session_state.user_id)]
            
            if not student_data.empty:
                row = student_data.iloc[0]
                st.info(f"الدرجة: {row['Grade']}% | الحضور: {row['Attendance']}%")
                st.metric("احتمالية النجاح (AI)", f"{row['Success_Prob']:.1f}%")
                if row['Decision'] == "متوقع التعثر": st.error("⚠️ تنبيه بخصوص الأداء")
                else: st.success("✅ أداء مستقر")
            else:
                st.warning("عذراً، بياناتك غير موجودة في الملف المرفوع حالياً.")
        else:
            st.info("بانتظار قيام عضو هيئة التدريس برفع البيانات.")
