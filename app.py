import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier

# 1. إعدادات الهوية البصرية لجامعة المجمعة
st.set_page_config(page_title="نظام جامعة المجمعة للذكاء الاصطناعي", layout="wide")

MU_LOGO = "https://www.mu.edu.sa/sites/default/files/2024-05/MU-Logo-New-2024.png"

# --- تنسيق الاحترافي CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; text-align: right; }
    .main-title { color: #004a87; text-align: center; font-weight: bold; padding: 15px; border-bottom: 3px solid #b7934b; margin-bottom: 30px; }
    .ai-card { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-right: 8px solid #b7934b; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# --- محرك تحليل البيانات والذكاء الاصطناعي ---
def run_ai_engine(df):
    try:
        # إعداد البيانات للتدريب
        X = df[['Grade', 'Attendance']]
        y = (df['Grade'] >= 60).astype(int) # تصنيف (ناجح/متعثر) بناءً على الدرجة
        
        # استخدام خوارزمية الغابة العشوائية (أقوى في التنبؤ الأكاديمي)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # حساب الاحتمالات وأهمية العوامل
        df['Success_Prob'] = model.predict_proba(X)[:, 1] * 100
        df['Decision'] = ["متوقع النجاح" if p >= 50 else "متوقع التعثر" for p in df['Success_Prob']]
        
        importances = model.feature_importances_
        return df, importances, True
    except:
        return df, [0.5, 0.5], False

# --- قاعدة بيانات تجريبية ---
users = {"admin": "123", "101": "std", "102": "std"}

# --- واجهة تسجيل الدخول ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.image(MU_LOGO, use_container_width=True)
        st.markdown("<h3 style='text-align:center;'>قسم تحليل البيانات والذكاء الاصطناعي</h3>", unsafe_allow_html=True)
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("تسجيل الدخول"):
            if u in users and users[u] == p:
                st.session_state.auth = True
                st.session_state.user = u
                st.rerun()
            else: st.error("بيانات خاطئة")
else:
    # --- لوحة التحكم الرئيسية ---
    st.sidebar.image(MU_LOGO, width=150)
    st.sidebar.markdown(f"**المستخدم:** {st.session_state.user}")
    st.sidebar.caption("🎓 مشروع تخرج - نموذج تجريبي")
    if st.sidebar.button("خروج"):
        st.session_state.auth = False
        st.rerun()

    st.markdown("<h2 class='main-title'>منصة التحليل الذكي للأداء الأكاديمي</h2>", unsafe_allow_html=True)

    file = st.file_uploader("تغذية النظام ببيانات الطلاب (Excel)", type=['xlsx'])
    
    if file:
        df_raw = pd.read_excel(file)
        df, feat_imp, status = run_ai_engine(df_raw)
        
        # عرض النتائج في تبويبات احترافية
        t1, t2, t3 = st.tabs(["📊 نظرة عامة", "🤖 تحليل الذكاء الاصطناعي", "📝 السجل التفصيلي"])
        
        with t1:
            m1, m2, m3 = st.columns(3)
            m1.metric("إجمالي الطلاب", len(df))
            m2.metric("متوسط الحضور", f"{df['Attendance'].mean():.1f}%")
            m3.metric("توقعات التعثر", len(df[df['Decision'] == "متوقع التعثر"]))
            
            fig = px.scatter(df, x="Attendance", y="Grade", color="Decision", 
                             title="توزيع الطلاب بناءً على الدرجات والحضور",
                             color_discrete_map={"متوقع النجاح": "#004a87", "متوقع التعثر": "#991b1b"})
            st.plotly_chart(fig, use_container_width=True)

        with t2:
            st.markdown("<div class='ai-card'><h4>🧠 منطق تحليل البيانات (AI Logic)</h4>"
                        "يوضح هذا القسم العوامل التي اعتمد عليها النظام في تصنيف الطلاب.</div>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**أهمية العوامل (Feature Importance):**")
                imp_data = pd.DataFrame({'العامل': ['الدرجات', 'الحضور'], 'التأثير': feat_imp})
                st.bar_chart(imp_data.set_index('العامل'))
            
            with col_b:
                st.write("**توزيع احتمالية النجاح:**")
                fig_hist = px.histogram(df, x="Success_Prob", nbins=10, color_discrete_sequence=['#b7934b'])
                st.plotly_chart(fig_hist, use_container_width=True)

        with t3:
            st.write("**قائمة التصنيف التنبؤي:**")
            st.dataframe(df[['Student_ID', 'Name', 'Grade', 'Attendance', 'Decision']], use_container_width=True)
            
            # رسالة تحذيرية ذكية تظهر في حال وجود تعثر
            if len(df[df['Decision'] == "متوقع التعثر"]) > 0:
                st.warning("⚠️ كشف النظام عن طلاب معرضين للتعثر؛ يوصى بتفعيل خطة التدخل المبكر.")

    else:
        st.info("الرجاء رفع ملف البيانات لبدء عملية التحليل الذكي.")
