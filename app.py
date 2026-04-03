import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# 1. إعدادات الصفحة الرسمية للهوية البصرية لجامعة المجمعة
st.set_page_config(page_title="نظام جامعة المجمعة للتحليل الأكاديمي", layout="wide")

# الرابط المباشر لشعار جامعة المجمعة
MU_LOGO = "https://upload.wikimedia.org/wikipedia/ar/b/b5/Majmaah_University_Logo.png"

# --- تصميم الواجهة باستخدام CSS الرسمي (أزرق وكحلي وذهبي) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    /* الخطوط والخلفية العامة */
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        text-align: right;
        background-color: #fcfcfc;
    }
    
    /* العنوان الرئيسي المعتمد */
    .main-header {
        color: #004a87; /* أزرق الجامعة */
        text-align: center;
        font-weight: bold;
        padding: 25px;
        border-bottom: 5px solid #b7934b; /* ذهبي الجامعة */
        margin-bottom: 40px;
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* إطار خاص لبيانات عضو هيئة التدريس */
    .teacher-profile-container {
        border: 2px solid #b7934b;
        padding: 20px;
        border-radius: 12px;
        background-color: #f8f9fa;
        text-align: center;
        color: #004a87;
        font-weight: bold;
        margin-bottom: 25px;
    }
    
    /* تنسيق الحاويات والبطاقات */
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-right: 6px solid #004a87;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* تنسيق الأزرار */
    .stButton>button {
        background-color: #004a87;
        color: white;
        border-radius: 6px;
        border: none;
        width: 100%;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #b7934b;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- قاعدة بيانات المستخدمين (تشمل الطلاب من 101 إلى 105) ---
users_db = {
    "admin": {"password": "123", "role": "teacher", "full_name": "عضو هيئة التدريس"},
    "101": {"password": "std", "role": "student"},
    "102": {"password": "std", "role": "student"},
    "103": {"password": "std", "role": "student"},
    "104": {"password": "std", "role": "student"},
    "105": {"password": "std", "role": "student"}
}

# --- محرك التحليل الذكي للأداء الأكاديمي ---
def process_academic_analysis(df):
    try:
        X = df[['Grade', 'Attendance']]
        y = (df['Grade'] >= 60).astype(int)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        df['Success_Probability'] = model.predict_proba(X)[:, 1] * 100
        df['AI_Status'] = ["حالة مستقرة" if p >= 50 else "يتطلب تدخل أكاديمي" for p in df['Success_Probability']]
        return df, True
    except:
        return df, False

# --- إدارة جلسة تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        st.image(MU_LOGO, width=220)
        st.markdown("<h2 style='text-align: center; color: #004a87;'>منصة التحليل الأكاديمي الذكي</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #b7934b;'>قسم تحليل البيانات والذكاء الاصطناعي - نموذج تجريبي</p>", unsafe_allow_html=True)
        
        with st.form("login_section"):
            u_id = st.text_input("اسم المستخدم أو الرقم الجامعي")
            u_pwd = st.text_input("كلمة المرور المعتمدة", type="password")
            login_btn = st.form_submit_button("تسجيل الدخول للنظام")
            if login_btn:
                if u_id in users_db and users_db[u_id]["password"] == u_pwd:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = u_id
                    st.session_state['role'] = users_db[u_id]["role"]
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة، يرجى التحقق من الرقم السري")

else:
    # --- القائمة الجانبية (Sidebar) ---
    st.sidebar.image(MU_LOGO, width=160)
    
    if st.session_state['role'] == "teacher":
        st.sidebar.markdown(f"""
        <div class="teacher-profile-container">
            بوابة الإدارة الأكاديمية<br>
            المستخدم: {users_db['admin']['full_name']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.write(f"الرقم الجامعي الحالي: {st.session_state['user_id']}")
        
    if st.sidebar.button("خروج من النظام"):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- واجهة عضو هيئة التدريس ---
    if st.session_state['role'] == "teacher":
        st.markdown("<div class='main-header'>لوحة تحكم إدارة البيانات الأكاديمية</div>", unsafe_allow_html=True)
        
        data_file = st.file_uploader("رفع سجل الطلاب السنوي (بصيغة Excel)", type=['xlsx'])
        
        if data_file:
            df = pd.read_excel(data_file)
            if all(col in df.columns for col in ['Student_ID', 'Name', 'Grade', 'Attendance']):
                df, _ = process_academic_analysis(df)
                st.session_state['shared_data'] = df
                
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("عدد الطلاب المسجلين", len(df))
                col_m2.metric("متوسط التحصيل الدراسي", f"{df['Grade'].mean():.1f}%")
                col_m3.metric("حالات التدخل المقترحة", len(df[df['AI_Status'] == "يتطلب تدخل أكاديمي"]))
                
                tab_viz, tab_data = st.tabs(["تحليل المسارات الأكاديمية", "السجل الرقمي الكامل"])
                with tab_viz:
                    fig = px.scatter(df, x="Attendance", y="Grade", color="AI_Status",
                                     color_discrete_map={"حالة مستقرة": "#004a87", "يتطلب تدخل أكاديمي": "#b91c1c"},
                                     labels={"Attendance": "نسبة الحضور (%)", "Grade": "التحصيل الدراسي (%)"})
                    st.plotly_chart(fig, use_container_width=True)
                with tab_data:
                    st.dataframe(df[['Student_ID', 'Name', 'Grade', 'Attendance', 'AI_Status']], use_container_width=True)
            else:
                st.error("يرجى التأكد من مطابقة أعمدة الملف المرفوع للمعايير المطلوبة")

    # --- واجهة الطالب ---
    else:
        st.markdown("<div class='main-header'>بوابة الطالب - تقرير الأداء الأكاديمي</div>", unsafe_allow_html=True)
        
        if 'shared_data' in st.session_state:
            df = st.session_state['shared_data']
            current_student = df[df['Student_ID'].astype(str) == str(st.session_state['user_id'])]
            
            if not current_student.empty:
                info = current_student.iloc[0]
                st.markdown(f"### السجل الأكاديمي للطالب: {info['Name']}")
                
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.metric("الدرجة العلمية الحالية", f"{info['Grade']}%")
                with col_stat2:
                    st.metric("نسبة حضور المحاضرات", f"{info['Attendance']}%")
                
                st.markdown("---")
                st.write("تقدير الذكاء الاصطناعي لمستوى الاستمرارية:")
                success_rate = info['Success_Probability']
                st.progress(int(success_rate))
                
                if success_rate < 50:
                    st.error("تنبيه رسمي: مستوى التحصيل الدراسي الحالي يتطلب مراجعة القسم لضمان النجاح.")
                else:
                    st.success("إشعار: مستوى الأداء الأكاديمي الحالي مستقر ومطابق لخطط النجاح.")
            else:
                st.warning("البيانات المرتبطة برقمك الجامعي غير متوفرة في السجل المرفوع حالياً.")
        else:
            st.info("النظام بانتظار اعتماد النتائج النهائية من قبل الإدارة الأكاديمية.")
