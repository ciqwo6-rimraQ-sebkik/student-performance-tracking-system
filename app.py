import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# 1. إعدادات الصفحة الهوية البصرية
st.set_page_config(page_title="نظام جامعة المجمعة للذكاء الاصطناعي", layout="wide")

# رابط شعار جامعة المجمعة
MU_LOGO = "https://upload.wikimedia.org/wikipedia/ar/b/b5/Majmaah_University_Logo.png"

# --- تنسيق واجهة المستخدم بألوان الجامعة الرسمية ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    /* الخط العام والخلفية */
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        text-align: right;
        background-color: #fcfcfc;
    }
    
    /* العناوين الرئيسية */
    .main-title {
        color: #004a87; /* أزرق جامعة المجمعة */
        text-align: center;
        font-weight: bold;
        padding: 20px;
        border-bottom: 4px solid #b7934b; /* ذهبي جامعة المجمعة */
        margin-bottom: 40px;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* إطار خاص لبيانات عضو هيئة التدريس */
    .teacher-frame {
        padding: 15px;
        border: 2px solid #b7934b;
        border-radius: 12px;
        background-color: #f0f4f8;
        margin-bottom: 20px;
        text-align: center;
        color: #004a87;
        font-weight: bold;
    }
    
    /* بطاقات تحليل الذكاء الاصطناعي */
    .ai-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-right: 10px solid #004a87;
        border-left: 1px solid #dee2e6;
        border-top: 1px solid #dee2e6;
        border-bottom: 1px solid #dee2e6;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.05);
    }
    
    /* تنسيق الأزرار */
    .stButton>button {
        background-color: #004a87;
        color: white;
        border-radius: 8px;
        border: none;
        width: 100%;
        height: 45px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #b7934b;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- قاعدة بيانات المستخدمين النظام ---
users_db = {
    "admin": {"password": "123", "role": "teacher", "display_name": "عضو هيئة التدريس"},
    "101": {"password": "std", "role": "student", "display_name": "الطالب رقم 101"},
    "102": {"password": "std", "role": "student", "display_name": "الطالب رقم 102"},
    "103": {"password": "std", "role": "student", "display_name": "الطالب رقم 103"},
    "104": {"password": "std", "role": "student", "display_name": "الطالب رقم 104"},
    "105": {"password": "std", "role": "student", "display_name": "الطالب رقم 105"}
}

# --- نظام معالجة البيانات والذكاء الاصطناعي ---
def run_ai_engine(df):
    try:
        X = df[['Grade', 'Attendance']]
        y = (df['Grade'] >= 60).astype(int)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        df['Success_Prob'] = model.predict_proba(X)[:, 1] * 100
        df['Decision'] = ["حالة مستقرة" if p >= 50 else "يحتاج متابعة أكاديمية" for p in df['Success_Prob']]
        return df, model.feature_importances_, True
    except:
        return df, [0.5, 0.5], False

# --- إدارة جلسة تسجيل الدخول ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image(MU_LOGO, width=200)
        st.markdown("<h3 style='text-align:center; color:#004a87;'>قسم تحليل البيانات والذكاء الاصطناعي</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#b7934b; font-weight:bold;'>نموذج تجريبي</p>", unsafe_allow_html=True)
        
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        
        if st.button("تسجيل الدخول"):
            if username in users_db and users_db[username]["password"] == password:
                st.session_state.auth = True
                st.session_state.user_id = username
                st.session_state.role = users_db[username]["role"]
                st.session_state.display_name = users_db[username]["display_name"]
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة، يرجى المحاولة مرة أخرى")
else:
    # --- القائمة الجانبية (Sidebar) ---
    st.sidebar.image(MU_LOGO, width=150)
    
    # وضع إطار حول اسم المستخدم إذا كان عضو هيئة تدريس
    if st.session_state.role == "teacher":
        st.sidebar.markdown(f"""
        <div class="teacher-frame">
            الحساب الحالي:<br>
            {st.session_state.display_name}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.write(f"المستخدم: {st.session_state.display_name}")
        
    st.sidebar.caption("نظام التحليل الأكاديمي الذكي")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.auth = False
        st.rerun()

    # --- واجهة عضو هيئة التدريس ---
    if st.session_state.role == "teacher":
        st.markdown("<h2 class='main-title'>منصة التحليل الذكي للأداء الأكاديمي بجامعة المجمعة</h2>", unsafe_allow_html=True)
        
        st.markdown("<h4>تحميل سجلات الطلاب</h4>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("يرجى اختيار ملف بيانات الطلاب بصيغة Excel", type=['xlsx'])
        
        if uploaded_file:
            df_raw = pd.read_excel(uploaded_file)
            df, feature_importance, status = run_ai_engine(df_raw)
            st.session_state['shared_data'] = df
            
            tab1, tab2 = st.tabs(["قائمة بيانات الطلاب", "نتائج تحليل الذكاء الاصطناعي"])
            
            with tab1:
                st.write("النتائج التفصيلية المسجلة:")
                st.dataframe(df[['Student_ID', 'Name', 'Grade', 'Attendance', 'Decision']], use_container_width=True)
            
            with tab2:
                st.markdown("<div class='ai-card'><h4>تحليل العوامل المؤثرة على الأداء</h4>", unsafe_allow_html=True)
                st.write("توضيح مدى تأثير كل عامل في التنبؤ بالحالة الأكاديمية للطالب:")
                
                importance_data = pd.DataFrame({
                    'العوامل الأساسية': ['معدل الدرجات', 'نسبة الحضور'],
                    'درجة التأثير': feature_importance
                })
                
                fig = px.bar(importance_data, x='العوامل الأساسية', y='درجة التأثير', 
                             color_discrete_sequence=['#b7934b'])
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # --- واجهة الطالب ---
    else:
        st.markdown("<h2 class='main-title'>بوابة الطالب - تقرير الأداء الأكاديمي</h2>", unsafe_allow_html=True)
        
        if 'shared_data' in st.session_state:
            df = st.session_state['shared_data']
            current_student = df[df['Student_ID'].astype(str) == str(st.session_state.user_id)]
            
            if not current_student.empty:
                data = current_student.iloc[0]
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("درجة الاختبار", f"{data['Grade']}%")
                with col_b:
                    st.metric("نسبة حضور المحاضرات", f"{data['Attendance']}%")
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.write("تقدير النظام الأكاديمي المبني على الذكاء الاصطناعي:")
                st.progress(int(data['Success_Prob']))
                st.write(f"احتمالية النجاح المقدرة: {data['Success_Prob']:.1f}%")
                
                if data['Decision'] == "يحتاج متابعة أكاديمية":
                    st.error("تنبيه: تشير تحليلات النظام إلى ضرورة تحسين الأداء الأكاديمي في الفترة القادمة")
                else:
                    st.success("إشعار: مستوى الأداء الأكاديمي الحالي مستقر وضمن النطاق الآمن")
            else:
                st.warning("لم يتم العثور على بيانات خاصة برقمك الجامعي في السجل الحالي")
        else:
            st.info("النظام في انتظار رفع البيانات من قبل الإدارة الأكاديمية")
