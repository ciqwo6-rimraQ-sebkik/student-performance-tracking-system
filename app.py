import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from io import BytesIO

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام التنبؤ الأكاديمي الذكي", layout="wide")

# --- ألوان رسمية ---
st.markdown("""
<style>
body {background-color: #fdf7e3;} 
h1, h2, h3, h4 {color: #b7934b;} 
.stButton>button {background-color:#b7934b; color:white; border-radius:8px; width:100%; padding:0.5em;}
.sidebar .sidebar-content {background-color: #004a87; color:white; border-radius:8px; padding:10px;}
.page-button {background-color:#6a6a6a; color:white; font-weight:bold; border-radius:8px; width:100%; padding:0.5em; margin-bottom:5px;}
.stMetric {background-color: white !important; border: 2px solid #004a87; border-radius: 8px; padding: 10px;}
</style>
""", unsafe_allow_html=True)

# --- شعار الجامعة ونسخة تجريبية ---
def show_university_logo():
    try:
        with open("logo.png", "rb") as f:
            logo_bytes = BytesIO(f.read())
        st.image(logo_bytes, width=180)
    except:
        st.warning("لم يتمكن النظام من تحميل شعار الجامعة")

    st.markdown("""
        <div style='text-align:center; margin-top:5px;'>
            <p style='font-size:16px; color:#333333; margin:2px 0; background-color:#b7934b; padding:3px 5px; border-radius:5px;'>نسخة تجريبية</p>
        </div>
    """, unsafe_allow_html=True)

# --- قاعدة بيانات المستخدمين ---
users_db = {"admin": {"password": "123", "role": "teacher"}}
for i in range(101, 121):
    users_db[str(i)] = {"password": "std", "role": "student"}

# --- تدريب AI ---
def train_ai_model(df):
    subject_cols = ['Math','Science','English','Physics','Chemistry','Biology','Computer']
    df['Grade'] = df[subject_cols].mean(axis=1)
    X = df[['Grade','Attendance']]
    y = (df['Grade'] >= 60).astype(int)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    df['Success_Probability'] = model.predict_proba(X)[:,1]*100
    df['AI_Status'] = ["ناجح متوقع" if p>=50 else "خطر تعثر" for p in df['Success_Probability']]
    return df

# --- واجهة تسجيل الدخول ---
def login_page():
    show_university_logo()
    st.markdown("<h2 style='text-align:center; color:#004a87;'>قسم تحليل البيانات والذكاء الاصطناعي</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>🔐 تسجيل الدخول للنظام الذكي</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
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
    st.title("لوحة تحكم المعلم")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    file = st.file_uploader("ارفع ملف بيانات الطلاب (Excel/CSV)", type=['xlsx','csv'])
    if file:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        required_cols = ['Student_ID','Name','Attendance','Math','Science','English','Physics','Chemistry','Biology','Computer']
        if all(col in df.columns for col in required_cols):
            df = train_ai_model(df)
            st.session_state['data'] = df

            # --- إحصائيات سريعة ---
            total_students = len(df)
            avg_grade = df['Grade'].mean()
            at_risk = len(df[df['Success_Probability'] < 50])
            c1, c2, c3 = st.columns(3)
            c1.metric("إجمالي الطلاب", total_students)
            c2.metric("متوسط الدرجات", f"{avg_grade:.1f}%")
            c3.metric("طلاب في منطقة الخطر", at_risk)

            # --- Sidebar Navigation ---
            page = st.sidebar.radio("اختر القسم:", ["ملخص AI", "جدول الطلاب", "الرسوم البيانية"], index=0, format_func=lambda x: f"  {x}")
            if page == "ملخص AI":
                st.subheader("ملخص AI")
                weak_subjects = df[['Math','Physics','Chemistry']].mean().sort_values().head(3).index.tolist()
                st.write(f"الطلاب المتوقع نجاحهم: {total_students - at_risk}")
                st.write(f"الطلاب المعرضين للخطر: {at_risk}")
                st.write(f"أكثر المواد ضعفًا: {', '.join(weak_subjects)}")
            elif page == "جدول الطلاب":
                st.subheader("الجدول التفصيلي")
                df_display = df.copy()
                def color_prob_html(prob):
                    if prob>=75: color='#4CAF50'
                    elif prob>=50: color='#CDDC39'
                    else: color='#F44336'
                    return f'<span style="background-color:{color}; color:white; padding:2px 5px; border-radius:3px">{prob:.1f}%</span>'
                df_display['Success_Probability'] = df_display['Success_Probability'].apply(color_prob_html)
                st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
            elif page == "الرسوم البيانية":
                st.subheader("الرسوم البيانية")
                fig_scatter = px.scatter(df, x="Attendance", y="Grade", color="AI_Status",
                                         size="Success_Probability", hover_name="Name",
                                         color_discrete_map={"ناجح متوقع":"#004a87","خطر تعثر":"#b7934b"},
                                         title="توزيع الطلاب حسب AI")
                st.plotly_chart(fig_scatter, use_container_width=True)
                status_counts = df['AI_Status'].value_counts()
                fig_pie = px.pie(names=status_counts.index, values=status_counts.values,
                                 color=status_counts.index,
                                 color_discrete_map={"ناجح متوقع":"#004a87","خطر تعثر":"#b7934b"},
                                 title="نسبة الطلاب حسب الحالة")
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.error("الملف يجب أن يحتوي على جميع الأعمدة المطلوبة")

# --- واجهة الطالب ---
def student_dashboard():
    show_university_logo()
    st.title("ملف الطالب الشخصي")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    if 'data' in st.session_state:
        df = st.session_state['data']
        user_id = st.session_state['user_id']
        student_row = df[df['Student_ID'].astype(str)==str(user_id)]
        if not student_row.empty:
            data = student_row.iloc[0]
            subject_cols = ['Math','Science','English','Physics','Chemistry','Biology','Computer']

            # --- المعلومات الأساسية ---
            st.subheader(f"مرحباً بك، {data['Name']}")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**درجة الاختبار:** {data['Grade']:.1f}%")
                st.write(f"**نسبة الحضور:** {data['Attendance']}%")
            with col2:
                st.subheader("توقعات AI")
                prob = data['Success_Probability']
                st.metric("احتمالية النجاح", f"{prob:.1f}%")
                if prob<50: st.error("⚠️ أنت في منطقة الخطر الأكاديمي!")
                else: st.success("✅ أنت على الطريق الصحيح للنجاح!")

            # --- مخطط دائري صغير أسفل المعلومات مباشرة ---
            st.subheader("توزيع درجات المواد")
            fig_pie_inline = px.pie(names=subject_cols, values=[data[sub] for sub in subject_cols],
                                    title="توزيع درجات المواد")
            st.plotly_chart(fig_pie_inline, use_container_width=True)

            # --- Sidebar Navigation منفصلة ---
            page = st.sidebar.radio("اختر القسم:", ["درجات المواد", "المعدل العام والتقدير", "توقعات AI", "خطة المذاكرة", "مخطط دائري"], index=0)
            if page == "درجات المواد":
                st.subheader("درجات المواد")
                st.dataframe(data[subject_cols])
            elif page == "المعدل العام والتقدير":
                overall_percentage = student_row[subject_cols].mean(axis=1).iloc[0]
                if overall_percentage >= 90: grade_letter = "امتياز"
                elif overall_percentage >= 80: grade_letter = "جيد جدًا"
                elif overall_percentage >= 70: grade_letter = "جيد"
                elif overall_percentage >= 60: grade_letter = "مقبول"
                else: grade_letter = "ضعيف"
                st.subheader("تقديرك العام")
                st.metric(label="المعدل العام", value=f"{overall_percentage:.1f}% - {grade_letter}")
            elif page == "توقعات AI":
                st.subheader("توقعات الذكاء الاصطناعي")
                prob = data['Success_Probability']
                st.metric("احتمالية النجاح المتوقعة", f"{prob:.1f}%")
                if prob<50: st.error("تنبيه: أنت في منطقة الخطر الأكاديمي!")
                else: st.success("أنت تسير في الطريق الصحيح للنجاح!")
            elif page == "خطة المذاكرة":
                st.subheader("خطة المذاكرة الذكية")
                plan = []
                weak_subjects = [sub for sub in subject_cols if data[sub]<60]
                if weak_subjects:
                    for sub in weak_subjects:
                        plan.append(f"- ركّز على مادة {sub} لمدة ساعة يوميًا")
                if data['Attendance']<75:
                    plan.append("- احرص على حضور جميع المحاضرات القادمة")
                if 'Engagement' in data and data['Engagement']<50:
                    plan.append("- شارك في الكلاس واسأل الأسئلة")
                if data['Success_Probability']<50:
                    plan.append("- خصص 3-4 ساعات يوميًا للمذاكرة المكثفة")
                else:
                    plan.append("- استمر على نفس المستوى مع مراجعة يومية خفيفة")
                for p in plan: st.write(p)
            elif page == "مخطط دائري":
                st.subheader("مخطط توزيع درجات المواد")
                fig_pie = px.pie(names=subject_cols, values=[data[sub] for sub in subject_cols],
                                 title="توزيع درجاتك في المواد")
                st.plotly_chart(fig_pie, use_container_width=True)
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
    if st.session_state['role']=="teacher":
        teacher_dashboard()
    else:
        student_dashboard()
