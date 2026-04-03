import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# 1. إعدادات الصفحة الرسمية لجامعة المجمعة
st.set_page_config(page_title="نظام التنبؤ الأكاديمي الذكي - MU", layout="wide")

# الرابط الجديد المباشر لشعار جامعة المجمعة
MU_LOGO = "https://www.mu.edu.sa/sites/default/files/2024-05/MU-Logo-New-2024.png"

# --- تنسيق CSS احترافي (الهوية البصرية لجامعة المجمعة) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; text-align: right; }
    
    /* لون العناوين (أزرق جامعة المجمعة الرسمي) */
    .main-title { 
        color: #004a87; 
        text-align: center; 
        font-weight: bold; 
        padding: 20px; 
        border-bottom: 4px solid #b7934b; /* خط ذهبي رفيع */
        margin-bottom: 40px; 
    }
    
    /* تنسيق الأزرار والقوائم */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #004a87;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    
    /* إخفاء العلامات غير الرسمية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* تنسيق الحاويات */
    .stMetric {
        background-color: #f8fafc;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- قاعدة بيانات المستخدمين (تشمل جميع الأرقام المطلوبة) ---
users_db = {
    "admin": {"password": "123", "role": "teacher", "name": "عضو هيئة التدريس"},
    "101": {"password": "std", "role": "student"},
    "102": {"password": "std", "role": "student"},
    "103": {"password": "std", "role": "student"},
    "104": {"password": "std", "role": "student"},
    "105": {"password": "std", "role": "student"}
}

# --- نموذج الذكاء الاصطناعي (Random Forest Classifier) ---
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
def login_page():
    # عرض الشعار في المنتصف فوق نموذج الدخول
    col_logo1, col_logo2, col_logo3 = st.columns([1, 1, 1])
    with col_logo2:
        st.image(MU_LOGO, use_container_width=True)
    
    st.markdown("<h1 class='main-title'>نظام التحليل الأكاديمي والتنبؤ المبكر</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("<p style='text-align:center; font-weight:bold;'>تسجيل الدخول للمنسوبين</p>", unsafe_allow_html=True)
            user = st.text_input("اسم المستخدم / الرقم الجامعي")
            pwd = st.text_input("كلمة المرور", type="password")
            submit = st.form_submit_button("دخول للنظام")
            if submit:
                if user in users_db and users_db[user]["password"] == pwd:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user
                    st.session_state['role'] = users_db[user]["role"]
                    st.rerun()
                else:
                    st.error("البيانات المدخلة غير مرتبطة بسجل مستخدم نشط.")

# --- لوحة التحكم الخاصة بالمعلم ---
def teacher_dashboard():
    st.sidebar.image(MU_LOGO, width=160)
    st.sidebar.markdown("---")
    st.sidebar.info(f"المستخدم: {users_db['admin']['name']}")
    
    st.markdown("<h2 class='main-title'>وحدة المراقبة الأكاديمية الذكية</h2>", unsafe_allow_html=True)
    
    if st.sidebar.button("تسجيل الخروج الآمن"):
        st.session_state['logged_in'] = False
        st.rerun()

    uploaded_file = st.file_uploader("يرجى تحميل سجل الدرجات (ملف Excel)", type=['xlsx'])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        if all(col in df.columns for col in ['Student_ID', 'Name', 'Grade', 'Attendance']):
            df, _ = train_ai_model(df)
            st.session_state['data'] = df
            
            # عرض المقاييس الأساسية
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("عدد الطلاب المسجلين", len(df))
            m2.metric("متوسط التحصيل الأكاديمي", f"{df['Grade'].mean():.1f}%")
            m3.metric("نسبة الحضور العامة", f"{df['Attendance'].mean():.1f}%")
            m4.metric("حالات التدخل المقترحة", len(df[df['Success_Probability'] < 50]))
            
            st.markdown("---")
            
            tab1, tab2 = st.tabs(["📊 التحليل البياني المستند للـ AI", "📋 السجل الرقمي الموحد"])
            with tab1:
                fig = px.scatter(df, x="Attendance", y="Grade", color="AI_Status",
                                 size="Success_Probability", hover_name="Name",
                                 color_discrete_map={"حالة مستقرة": "#004a87", "يتطلب متابعة أكاديمية": "#b91c1c"},
                                 labels={"Attendance": "الحضور (%)", "Grade": "الدرجة (%)"})
                st.plotly_chart(fig, use_container_width=True)
            with tab2:
                st.dataframe(df.drop(columns=['Success_Probability']).style.background_gradient(cmap='Blues', subset=['Grade']), use_container_width=True)
        else:
            st.error("خطأ في بنية البيانات: تأكد من تطابق أسماء الأعمدة في الملف.")

# --- لوحة التقرير الخاص بالطالب ---
def student_dashboard():
    st.sidebar.image(MU_LOGO, width=150)
    st.sidebar.markdown(f"**الرقم الجامعي:** {st.session_state['user_id']}")
    
    st.markdown("<h2 class='main-title'>بوابة التقرير الأكاديمي الذكي</h2>", unsafe_allow_html=True)
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    if 'data' in st.session_state:
        df = st.session_state['data']
        student_data = df[df['Student_ID'].astype(str) == str(st.session_state['user_id'])]
        
        if not student_data.empty:
            row = student_data.iloc[0]
            st.markdown(f"### تقرير الطالب المعتمد: {row['Name']}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"📌 الدرجة الحالية: {row['Grade']}%")
                st.info(f"📅 نسبة الحضور: {row['Attendance']}%")
            with c2:
                prob = row['Success_Probability']
                st.metric("احتمالية النجاح (تقدير النظام)", f"{prob:.1f}%")
                if prob < 50:
                    st.error("⚠️ إشعار: يتطلب أداؤك الأكاديمي الحالي مراجعة المرشد المختص لضمان الاستدامة.")
                else:
                    st.success("✅ إشعار: أداء الطالب ضمن المسار الأكاديمي المستقر والمعتمد.")
        else:
            st.warning("عذراً، لم تكتمل عملية مزامنة بياناتك مع السجل الحالي بعد.")
    else:
        st.info("النظام بانتظار اعتماد البيانات النهائية من قبل الشؤون الأكاديمية.")

# --- إدارة الجلسة والتشغيل الموحد ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login_page()
else:
    if st.session_state['role'] == "teacher":
        teacher_dashboard()
    else:
        student_dashboard()
