import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from io import BytesIO
import requests

# 1. إعدادات الصفحة العامة
st.set_page_config(page_title="نظام التنبؤ الأكاديمي الذكي", layout="wide")

# --- تحميل شعار الجامعة من GitHub كملف ---
LOGO_FILE_URL = "https://github.com/USERNAME/REPO/raw/main/logo.png"  # ضع رابط الملف هنا

def show_university_logo():
    # تحميل الملف من GitHub
    try:
        response = requests.get(LOGO_FILE_URL)
        logo_bytes = BytesIO(response.content)
        st.image(logo_bytes, width=180)
    except:
        st.warning("لم يتمكن النظام من تحميل شعار الجامعة")

    # النصوص تحت الشعار
    st.markdown("""
        <div style='text-align:center; margin-top:5px;'>
            <p style='font-size:18px; color:#004a87; margin:2px 0;'>قسم تحليل البيانات والذكاء الاصطناعي</p>
            <p style='font-size:16px; color:#b7934b; margin:0;'>نسخة تجريبية</p>
        </div>
    """, unsafe_allow_html=True)

# --- قاعدة بيانات مستخدمين تجريبية ---
users_db = {
    "admin": {"password": "123", "role": "teacher"},
    "101": {"password": "std", "role": "student"},
    "102": {"password": "std", "role": "student"},
    "103": {"password": "std", "role": "student"},
    "104": {"password": "std", "role": "student"},
    "105": {"password": "std", "role": "student"}
}

# --- دالة تدريب الذكاء الاصطناعي ---
def train_ai_model(df):
    X = df[['Grade', 'Attendance']]
    y = (df['Grade'] >= 60).astype(int)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    df['Success_Probability'] = model.predict_proba(X)[:, 1] * 100
    df['AI_Status'] = ["ناجح متوقع" if p >= 50 else "خطر تعثر" for p in df['Success_Probability']]
    return df

# --- واجهة تسجيل الدخول ---
def login_page():
    show_university_logo()
    st.markdown("<h2 style='text-align: center;'>🔐 تسجيل الدخول للنظام الذكي</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            user = st.text_input("اسم المستخدم / الرقم الجامعي")
            pwd = st.text_input("كلمة المرور", type="password")
            submit = st.form_submit_button("دخول")
            if submit:
                if user in users_db and users_db[user]["password"] == pwd:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user
                    st.session_state['role'] = users_db[user]["role"]
                    st.rerun()
                else:
                    st.error("بيانات الدخول غير صحيحة")

# --- واجهة المعلم ---
def teacher_dashboard():
    show_university_logo()
    st.title("👨‍🏫 لوحة تحكم المعلم (التحليل الذكي)")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['logged_in'] = False
        st.rerun()
    
    file = st.file_uploader("ارفع ملف بيانات الطلاب (Excel/CSV)", type=['xlsx', 'csv'])
    if file:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        if all(col in df.columns for col in ['Student_ID', 'Name', 'Grade', 'Attendance']):
            df = train_ai_model(df)
            st.session_state['data'] = df
            c1, c2, c3 = st.columns(3)
            c1.metric("إجمالي الطلاب", len(df))
            c2.metric("متوسط الدرجات", f"{df['Grade'].mean():.1f}%")
            c3.metric("طلاب في منطقة الخطر", len(df[df['Success_Probability'] < 50]))
            
            t1, t2 = st.tabs(["📊 تحليل البيانات", "📋 الجدول التفصيلي"])
            with t1:
                fig = px.scatter(df, x="Attendance", y="Grade", color="AI_Status",
                                 size="Success_Probability", hover_name="Name",
                                 title="توزيع الطلاب حسب تنبؤات الذكاء الاصطناعي",
                                 color_discrete_map={"ناجح متوقع":"#004a87","خطر تعثر":"#b7934b"})
                st.plotly_chart(fig, use_container_width=True)
            with t2:
                # تلوين الاحتمالية مباشرة بدون matplotlib
                def color_prob(val):
                    if val >= 75:
                        color = '#4CAF50'  # أخضر داكن
                    elif val >= 50:
                        color = '#CDDC39'  # أصفر فاتح
                    else:
                        color = '#F44336'  # أحمر
                    return f'background-color: {color}; color: white; text-align:center'
                
                styled_df = df[['Student_ID','Name','Grade','Attendance','Success_Probability','AI_Status']].style.applymap(color_prob, subset=['Success_Probability'])
                st.dataframe(styled_df)
        else:
            st.error("الملف يجب أن يحتوي على الأعمدة: Student_ID, Name, Grade, Attendance")

# --- واجهة الطالب ---
def student_dashboard():
    show_university_logo()
    st.title("🎓 ملف الطالب الشخصي")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['logged_in'] = False
        st.rerun()
    
    user_id = st.session_state['user_id']
    if 'data' in st.session_state:
        df = st.session_state['data']
        student_row = df[df['Student_ID'].astype(str) == str(user_id)]
        if not student_row.empty:
            data = student_row.iloc[0]
            st.success(f"مرحباً بك يا {data['Name']}")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("أداؤك الحالي")
                st.write(f"**درجة الاختبار:** {data['Grade']}%")
                st.write(f"**نسبة الحضور:** {data['Attendance']}%")
                st.progress(int(data['Grade']))
            with col2:
                st.subheader("توقعات الذكاء الاصطناعي")
                prob = data['Success_Probability']
                st.metric("احتمالية النجاح المتوقعة", f"{prob:.1f}%")
                if prob < 50:
                    st.error("تنبيه: أنت في منطقة الخطر الأكاديمي!")
                else:
                    st.success("أنت تسير في الطريق الصحيح للنجاح!")
        else:
            st.warning("عذراً، لم يتم العثور على بياناتك في الملف الذي رفعه المعلم.")
    else:
        st.info("انتظر حتى يقوم المعلم برفع النتائج والتحليلات.")

# --- إدارة الجلسة ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login_page()
else:
    if st.session_state['role'] == "teacher":
        teacher_dashboard()
    else:
        student_dashboard()
