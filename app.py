import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# 1. إعدادات الصفحة الرسمية لجامعة المجمعة
st.set_page_config(page_title="نظام التنبؤ الأكاديمي الذكي - MU", layout="wide")

# الرابط المباشر لشعار جامعة المجمعة
MU_LOGO = "https://upload.wikimedia.org/wikipedia/ar/b/b5/Majmaah_University_Logo.png"

# --- تنسيق CSS احترافي (ألوان جامعة المجمعة الرسمية) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; text-align: right; }
    
    /* لون العنوان الرئيسي (أزرق جامعة المجمعة الرسمي) */
    .main-title { 
        color: #004a87; 
        text-align: center; 
        font-weight: bold; 
        padding: 20px; 
        border-bottom: 4px solid #b7934b; /* خط ذهبي */
        margin-bottom: 40px; 
    }
    
    /* إطار مخصص لبيانات عضو هيئة التدريس */
    .teacher-info-box {
        border: 2px solid #b7934b;
        padding: 15px;
        border-radius: 10px;
        background-color: #f0f4f8;
        text-align: center;
        color: #004a87;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    /* تنسيق الأزرار */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #004a87;
        color: white;
        height: 3em;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #b7934b;
        color: white;
    }
    
    /* تنسيق الحاويات والبطاقات */
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-right: 5px solid #b7934b;
    }
</style>
""", unsafe_allow_html=True)

# --- قاعدة بيانات المستخدمين المعتمدة ---
users_db = {
    "admin": {"password": "123", "role": "teacher", "name": "عضو هيئة التدريس"},
    "101": {"password": "std", "role": "student"},
    "102": {"password": "std", "role": "student"},
    "103": {"password": "std", "role": "student"},
    "104": {"password": "std", "role": "student"},
    "105": {"password": "std", "role": "student"}
}

# --- نظام معالجة البيانات والذكاء الاصطناعي ---
def train_ai_model(df):
    try:
        X = df[['Grade', 'Attendance']]
        y = (df['Grade'] >= 60).astype(int)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        df['Success_Probability'] = model.predict_proba(X)[:, 1] * 100
        df['AI_Status'] = ["حالة مستقرة" if p >= 50 else "يتطلب متابعة أكاديمية" for p in df['Success_Probability']]
        return df, True
    except:
        return df, False

# --- واجهة تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    col_logo1, col_logo2, col_logo3 = st.columns([1, 1, 1])
    with col_logo2:
        st.image(MU_LOGO, width=200)
    
    st.markdown("<h1 class='main-title'>قسم تحليل البيانات والذكاء الاصطناعي</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>نموذج تجريبي للتحليل الأكاديمي</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            user = st.text_input("اسم المستخدم أو الرقم الجامعي")
            pwd = st.text_input("كلمة المرور", type="password")
            submit = st.form_submit_button("دخول للنظام")
            if submit:
                if user in users_db and users_db[user]["password"] == pwd:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user
                    st.session_state['role'] = users_db[user]["role"]
                    st.rerun()
                else:
                    st.error("البيانات المدخلة غير صحيحة.")

else:
    # --- القائمة الجانبية الموحدة ---
    st.sidebar.image(MU_LOGO, width=150)
    
    # إطار خاص لعضو هيئة التدريس في القائمة الجانبية
    if st.session_state['role'] == "teacher":
        st.sidebar.markdown(f"""
        <div class="teacher-info-box">
            بوابة الإدارة الأكاديمية<br>
            المستخدم: {users_db['admin']['name']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.write(f"الرقم الجامعي: {st.session_state['user_id']}")
        
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- واجهة عضو هيئة التدريس ---
    if st.session_state['role'] == "teacher":
        st.markdown("<h2 class='main-title'>منصة التحليل والمراقبة الأكاديمية</h2>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("تحميل سجل بيانات الطلاب (Excel)", type=['xlsx'])
        
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            if all(col in df.columns for col in ['Student_ID', 'Name', 'Grade', 'Attendance']):
                df, _ = train_ai_model(df)
                st.session_state['data'] = df
                
                m1, m2, m3 = st.columns(3)
                m1.metric("إجمالي الطلاب", len(df))
                m2.metric("متوسط التحصيل الأكاديمي", f"{df['Grade'].mean():.1f}%")
                m3.metric("حالات التدخل المطلوبة", len(df[df['AI_Status'] == "يتطلب متابعة أكاديمية"]))
                
                tab1, tab2 = st.tabs(["التحليل البياني المتقدم", "سجل البيانات التفصيلي"])
                with tab1:
                    fig = px.scatter(df, x="Attendance", y="Grade", color="AI_Status",
                                     color_discrete_map={"حالة مستقرة": "#004a87", "يتطلب متابعة أكاديمية": "#b91c1c"},
                                     labels={"Attendance": "نسبة الحضور (%)", "Grade": "الدرجة النهائية (%)"})
                    st.plotly_chart(fig, use_container_width=True)
                with tab2:
                    st.dataframe(df[['Student_ID', 'Name', 'Grade', 'Attendance', 'AI_Status']], use_container_width=True)
            else:
                st.error("يرجى التأكد من أن ملف Excel يحتوي على الأعمدة المطلوبة.")

    # --- واجهة الطالب ---
    else:
        st.markdown("<h2 class='main-title'>بوابة التقرير الأكاديمي للطالب</h2>", unsafe_allow_html=True)
        
        if 'data' in st.session_state:
            df = st.session_state['data']
            student_data = df[df['Student_ID'].astype(str) == str(st.session_state['user_id'])]
            
            if not student_data.empty:
                row = student_data.iloc[0]
                st.markdown(f"### سجل الطالب: {row['Name']}")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("درجة الاختبار الحالية", f"{row['Grade']}%")
                with c2:
                    st.metric("نسبة حضور المحاضرات", f"{row['Attendance']}%")
                
                st.markdown("---")
                st.write("تحليل الحالة الأكاديمية بواسطة الذكاء الاصطناعي:")
                prob = row['Success_Probability']
                st.progress(int(prob))
                
                if prob < 50:
                    st.error("تنبيه: الحالة الأكاديمية الحالية تتطلب مراجعة المرشد الأكاديمي لتحسين النتائج.")
                else:
                    st.success("إشعار: المسار الأكاديمي الحالي مستقر ومطابق للمعايير المطلوبة.")
            else:
                st.warning("البيانات الخاصة برقمك الجامعي غير متوفرة في السجل الحالي.")
        else:
            st.info("النظام بانتظار رفع البيانات النهائية من قبل القسم المختص.")
