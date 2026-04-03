import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# 1. إعدادات الصفحة الرسمية لجامعة المجمعة
st.set_page_config(page_title="نظام جامعة المجمعة للتنبؤ الأكاديمي", layout="wide")

# الرابط المباشر الصحيح للشعار
MU_LOGO = "https://www.mu.edu.sa/sites/default/files/2024-05/MU-Logo-New-2024.png"

# --- تنسيق CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; text-align: right; }
    .main-title { color: #004a87; text-align: center; font-weight: bold; padding: 15px; border-bottom: 3px solid #b7934b; margin-bottom: 30px; }
    .stDataFrame { background-color: white; }
    .caption-text { text-align: center; color: #666; font-size: 0.9em; margin-top: -10px; margin-bottom: 20px; }
    .ai-box { background-color: #f0f7ff; padding: 20px; border-radius: 10px; border-right: 5px solid #004a87; margin-bottom: 20px; }
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

# --- محرك الذكاء الاصطناعي المطور ---
def train_ai_model(df):
    try:
        X = df[['Grade', 'Attendance']]
        y = (df['Grade'] >= 60).astype(int)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # التنبؤ بالاحتمالات والحالة
        df['Success_Probability'] = model.predict_proba(X)[:, 1] * 100
        df['AI_Status'] = ["متوقع النجاح" if p >= 50 else "متوقع التعثر" for p in df['Success_Probability']]
        
        # استخراج أهمية العوامل (Feature Importance) للشرح العلمي
        importances = model.feature_importances_
        feature_info = {'Grade': importances[0], 'Attendance': importances[1]}
        
        return df, feature_info, True
    except:
        return df, None, False

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

# --- واجهة المعلم (لوحة التحكم والتحليل) ---
def teacher_dashboard():
    st.sidebar.image(MU_LOGO, use_container_width=True)
    st.sidebar.caption("🎓 نموذج تجريبي - مشروع تخرج 2026")
    st.sidebar.markdown("---")
    if st.sidebar.button("خروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.markdown("<h2 class='main-title'>وحدة المراقبة الأكاديمية وتحليل البيانات</h2>", unsafe_allow_html=True)
    
    file = st.file_uploader("ارفع سجل الطلاب (Excel)", type=['xlsx'])
    if file:
        df_raw = pd.read_excel(file)
        df, feat_importance, success = train_ai_model(df_raw)
        st.session_state['data'] = df
        
        # 1. قسم المقاييس السريعة
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("عدد الطلاب", len(df))
        m2.metric("متوسط الدرجات", f"{df['Grade'].mean():.1f}%")
        m3.metric("نسبة الحضور", f"{df['Attendance'].mean():.1f}%")
        m4.metric("حالات التعثر", len(df[df['AI_Status'] == "متوقع التعثر"]))
        
        st.markdown("---")
        
        # 2. الأقسام الرئيسية
        tab1, tab2, tab3 = st.tabs(["📋 السجل الموحد", "📊 التحليل البياني", "🤖 ذكاء اصطناعي (AI Analysis)"])
        
        with tab1:
            st.dataframe(df.drop(columns=['Success_Probability']), use_container_width=True)
            
        with tab2:
            fig = px.scatter(df, x="Attendance", y="Grade", color="AI_Status",
                             title="علاقة الحضور بالدرجات وتوقعات النظام",
                             color_discrete_map={"متوقع النجاح": "#004a87", "متوقع التعثر": "#991b1b"})
            st.plotly_chart(fig, use_container_width=True)
            
        with tab3:
            st.markdown("<div class='ai-box'><h4>تحليل محرك التنبؤ (Random Forest Classifier)</h4>"
                        "يوضح هذا القسم كيف قام النموذج بتحليل البيانات لاتخاذ القرار.</div>", unsafe_allow_html=True)
            
            c_ai1, c_ai2 = st.columns(2)
            
            with c_ai1:
                st.write("**تأثير العوامل على النتيجة (Feature Importance):**")
                feat_df = pd.DataFrame(list(feat_importance.items()), columns=['العامل', 'الأهمية'])
                fig_feat = px.bar(feat_df, x='الأهمية', y='العامل', orientation='h', 
                                  color_discrete_sequence=['#b7934b'])
                st.plotly_chart(fig_feat, use_container_width=False)
                
            with c_ai2:
                st.write("**توزيع احتمالات النجاح بناءً على نموذج AI:**")
                fig_dist = px.histogram(df, x="Success_Probability", nbins=10, 
                                        color_discrete_sequence=['#004a87'],
                                        labels={'Success_Probability': 'نسبة الثقة في النجاح'})
                st.plotly_chart(fig_dist, use_container_width=False)

# --- واجهة الطالب ---
def student_dashboard():
    st.sidebar.image(MU_LOGO, use_container_width=True)
    st.sidebar.caption("🎓 نموذج تجريبي - مشروع تخرج 2026")
    if st.sidebar.button("خروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.markdown("<h2 class='main-title'>تقرير مؤشرات الأداء الأكاديمي</h2>", unsafe_allow_html=True)
    
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

# --- التشغيل ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if not st.session_state['logged_in']: login_page()
else:
    if st.session_state['role'] == "teacher": teacher_dashboard()
    else: student_dashboard()
