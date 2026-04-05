import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام التنبؤ الأكاديمي الذكي", layout="wide")

# --- ألوان رسمية ---
st.markdown("""
<style>
body {background-color: #e6f0fa;}
h1, h2, h3, h4 {color: #004a87;}
.stMetric {background-color: white !important; border: 2px solid #004a87; border-radius: 8px; padding: 10px;}
.stButton>button {background-color: #b7934b; color: white; border-radius: 8px; padding: 0.5em 1em;}
</style>
""", unsafe_allow_html=True)

# --- شعار الجامعة في المنتصف ---
def show_university_logo():
    st.markdown("""
        <div style='text-align:center;'>
            <img src='logo.png' width='180'>
            <p style='font-size:18px; color:#004a87; margin:2px 0;'>قسم تحليل البيانات والذكاء الاصطناعي</p>
            <p style='font-size:16px; color:#b7934b; margin:0;'>نسخة تجريبية</p>
        </div>
    """, unsafe_allow_html=True)

# --- قاعدة بيانات المستخدمين ---
users_db = {"admin": {"password": "123", "role": "teacher"}}
for i in range(101, 121):
    users_db[str(i)] = {"password": "std", "role": "student"}

# --- دالة تدريب AI ---
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
    st.markdown("<h2 style='text-align: center;'>🔐 تسجيل الدخول للنظام الذكي</h2>", unsafe_allow_html=True)
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
    st.title("👨‍🏫 لوحة تحكم المعلم (التحليل الذكي)")

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

            # Sidebar اختيار ما يظهر
            show_scatter = st.sidebar.checkbox("عرض Scatter Chart", True)
            show_pie = st.sidebar.checkbox("عرض Pie Chart", True)
            show_table = st.sidebar.checkbox("عرض الجدول التفصيلي", True)
            show_summary = st.sidebar.checkbox("عرض ملخص AI", True)

            # مؤشرات الأداء
            c1,c2,c3 = st.columns(3)
            c1.metric("إجمالي الطلاب", len(df))
            c2.metric("متوسط الدرجات", f"{df['Grade'].mean():.1f}%")
            c3.metric("طلاب في منطقة الخطر", len(df[df['Success_Probability']<50]))

            # الرسوم والجدول
            if show_scatter:
                fig_scatter = px.scatter(df, x="Attendance", y="Grade", color="AI_Status",
                                         size="Success_Probability", hover_name="Name",
                                         color_discrete_map={"ناجح متوقع":"#004a87","خطر تعثر":"#b7934b"},
                                         title="توزيع الطلاب حسب تنبؤات الذكاء الاصطناعي")
                st.plotly_chart(fig_scatter, use_container_width=True)

            if show_pie:
                status_counts = df['AI_Status'].value_counts()
                fig_pie = px.pie(names=status_counts.index, values=status_counts.values,
                                 color=status_counts.index,
                                 color_discrete_map={"ناجح متوقع":"#004a87","خطر تعثر":"#b7934b"},
                                 title="نسبة الطلاب (ناجح متوقع vs خطر تعثر)")
                st.plotly_chart(fig_pie, use_container_width=True)

            if show_table:
                df_display = df.copy()
                def color_prob_html(prob):
                    if prob>=75: color='#4CAF50'
                    elif prob>=50: color='#CDDC39'
                    else: color='#F44336'
                    return f'<span style="background-color:{color}; color:white; padding:2px 5px; border-radius:3px">{prob:.1f}%</span>'
                df_display['Success_Probability'] = df_display['Success_Probability'].apply(color_prob_html)
                st.subheader("📋 الجدول التفصيلي")
                st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)

            if show_summary:
                total_students = len(df)
                at_risk = len(df[df['Success_Probability']<50])
                passing = total_students - at_risk
                weak_subjects = df[['Math','Physics','Chemistry']].mean().sort_values().head(3).index.tolist()
                st.subheader("🤖 ملخص AI")
                st.write(f"✅ الطلاب المتوقع نجاحهم: {passing}")
                st.write(f"⚠️ الطلاب المعرضين للخطر: {at_risk}")
                st.write(f"📌 أكثر المواد ضعفًا: {', '.join(weak_subjects)}")
        else:
            st.error("الملف يجب أن يحتوي على جميع الأعمدة المطلوبة")

# --- واجهة الطالب ---
def student_dashboard():
    show_university_logo()
    st.title("🎓 ملف الطالب الشخصي")

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

            # Sidebar تحكم
            show_subjects = st.sidebar.checkbox("عرض درجات المواد", True)
            show_overall = st.sidebar.checkbox("عرض المعدل العام + التقدير", True)
            show_ai = st.sidebar.checkbox("عرض توقعات AI", True)
            show_plan = st.sidebar.checkbox("عرض خطة المذاكرة", True)

            if show_subjects:
                st.subheader("📚 درجاتك في المواد")
                st.dataframe(data[subject_cols])
                fig_bar = px.bar(x=subject_cols, y=[data[sub] for sub in subject_cols],
                                 labels={'x':'المادة','y':'الدرجة'},
                                 title="مستوى الطالب في كل مادة")
                st.plotly_chart(fig_bar, use_container_width=True)
                fig_pie = px.pie(names=subject_cols, values=[data[sub] for sub in subject_cols],
                                 title="نسبة كل مادة من مجموع درجاتك")
                st.plotly_chart(fig_pie, use_container_width=True)

            if show_overall:
                overall_percentage = student_row[subject_cols].mean(axis=1).iloc[0]
                if overall_percentage >= 90: grade_letter = "امتياز"
                elif overall_percentage >= 80: grade_letter = "جيد جدًا"
                elif overall_percentage >= 70: grade_letter = "جيد"
                elif overall_percentage >= 60: grade_letter = "مقبول"
                else: grade_letter = "ضعيف"
                st.subheader("📌 تقديرك العام")
                st.metric(label="المعدل العام", value=f"{overall_percentage:.1f}% - {grade_letter}")

            if show_ai:
                prob = data['Success_Probability']
                st.subheader("🤖 توقعات الذكاء الاصطناعي")
                st.metric("احتمالية النجاح المتوقعة", f"{prob:.1f}%")
                if prob<50: st.error("تنبيه: أنت في منطقة الخطر الأكاديمي!")
                else: st.success("أنت تسير في الطريق الصحيح للنجاح!")

            if show_plan:
                st.subheader("📅 خطة مذاكرة ذكية")
                plan = []
                weak_subjects = [sub for sub in subject_cols if data[sub]<60]
                if weak_subjects:
                    for sub in weak_subjects:
                        plan.append(f"📌 ركّز على مادة {sub} لمدة ساعة يوميًا")
                if data['Attendance']<75:
                    plan.append("📍 احرص على حضور جميع المحاضرات القادمة")
                if 'Engagement' in data and data['Engagement']<50:
                    plan.append("📍 شارك في الكلاس واسأل الأسئلة")
                if data['Success_Probability']<50:
                    plan.append("🔥 خصص 3-4 ساعات يوميًا للمذاكرة المكثفة")
                else:
                    plan.append("✅ استمر على نفس المستوى مع مراجعة يومية خفيفة")
                for p in plan: st.write(p)
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
