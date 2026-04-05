import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from io import BytesIO

# 1. إعدادات الصفحة العامة
st.set_page_config(page_title="نظام التنبؤ الأكاديمي الذكي", layout="wide")

# --- رابط شعار الجامعة ---
LOGO_FILE_URL = "https://github.com/USERNAME/REPO/raw/main/logo.png"  # ضع الرابط الصحيح هنا

def show_university_logo():
    try:
        st.image(LOGO_FILE_URL, width=180)
    except:
        st.warning("لم يتمكن النظام من تحميل شعار الجامعة")

    st.markdown("""
        <div style='text-align:center; margin-top:5px;'>
            <p style='font-size:18px; color:#004a87; margin:2px 0;'>قسم تحليل البيانات والذكاء الاصطناعي</p>
            <p style='font-size:16px; color:#b7934b; margin:0;'>نسخة تجريبية</p>
        </div>
    """, unsafe_allow_html=True)

# --- قاعدة بيانات المستخدمين ---
users_db = {"admin": {"password": "123", "role": "teacher"}}
for i in range(101, 121):
    users_db[str(i)] = {"password": "std", "role": "student"}

# --- الأعمدة للمواد ---
subject_cols = ['Math','Science','English','Physics','Chemistry','Biology','Computer']

# --- تدريب الذكاء الاصطناعي ---
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
        
        # حساب المعدل التلقائي
        if all(sub in df.columns for sub in subject_cols):
            df['Grade'] = df[subject_cols].mean(axis=1)
        
        if all(col in df.columns for col in ['Student_ID', 'Name', 'Grade', 'Attendance']):
            df = train_ai_model(df)
            st.session_state['data'] = df

            # مؤشرات الأداء
            c1, c2, c3 = st.columns(3)
            c1.metric("إجمالي الطلاب", len(df))
            c2.metric("متوسط الدرجات", f"{df['Grade'].mean():.1f}%")
            c3.metric("طلاب في منطقة الخطر", len(df[df['Success_Probability'] < 50]))

            # Tabs للتحليل
            t1, t2 = st.tabs(["📊 تحليل البيانات", "📋 الجدول التفصيلي"])
            with t1:
                fig = px.scatter(df, x="Attendance", y="Grade", color="AI_Status",
                                 size="Success_Probability", hover_name="Name",
                                 title="توزيع الطلاب حسب تنبؤات الذكاء الاصطناعي",
                                 color_discrete_map={"ناجح متوقع":"#004a87","خطر تعثر":"#b7934b"})
                st.plotly_chart(fig, use_container_width=True)
            
            with t2:
                st.subheader("الجدول التفصيلي")
                def color_prob_html(prob):
                    if prob >= 75:
                        color = '#4CAF50'
                    elif prob >= 50:
                        color = '#CDDC39'
                    else:
                        color = '#F44336'
                    return f'<span style="background-color:{color}; color:white; padding:2px 5px; border-radius:3px">{prob:.1f}%</span>'
                
                df_display = df.copy()
                df_display['Success_Probability'] = df_display['Success_Probability'].apply(color_prob_html)
                st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)

            # Pie Chart لحالات الطلاب
            st.subheader("🥧 توزيع حالات الطلاب")
            status_counts = df['AI_Status'].value_counts()
            fig_pie = px.pie(
                names=status_counts.index,
                values=status_counts.values,
                title="نسبة الطلاب (ناجح متوقع vs خطر تعثر)",
                color=status_counts.index,
                color_discrete_map={"ناجح متوقع": "#004a87","خطر تعثر": "#b7934b"}
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            # الطلاب المعرضين للخطر
            st.subheader("🚨 الطلاب المعرضين للخطر (تنبيه مبكر)")
            at_risk = df[df['Success_Probability'] < 50]
            if not at_risk.empty:
                st.warning(f"عدد الطلاب المعرضين للخطر: {len(at_risk)}")
                st.dataframe(at_risk[['Student_ID','Name','Grade','Attendance','Success_Probability']])
            else:
                st.success("🎉 لا يوجد طلاب في منطقة الخطر!")
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

            # درجات المواد
            st.subheader("📚 درجاتك في المواد")
            st.dataframe(data[subject_cols])

            # Bar Chart
            st.subheader("📊 تحليل درجاتك")
            y_values = [data[sub] for sub in subject_cols]
            fig_bar = px.bar(
                x=subject_cols,
                y=y_values,
                labels={'x':'المادة','y':'الدرجة'},
                title="مستوى الطالب في كل مادة"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # Pie Chart
            st.subheader("🥧 توزيع درجاتك")
            fig_pie = px.pie(
                names=subject_cols,
                values=y_values,
                title="نسبة كل مادة من مجموع درجاتك"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            # التوصيات الذكية
            st.subheader("🤖 توصيات ذكية لتحسين مستواك")
            recommendations = []

            weak_subjects = [sub for sub in subject_cols if data[sub] < 60]
            if weak_subjects:
                recommendations.append(f"📚 تحتاج تركز على المواد التالية: {', '.join(weak_subjects)}")
            
            if data['Attendance'] < 75:
                recommendations.append("📉 حاول ترفع نسبة حضورك")
            
            engagement = data.get('Engagement', 100)
            if engagement < 50:
                recommendations.append("🙋‍♂️ زيد مشاركتك داخل المحاضرات")
            
            if data['Success_Probability'] < 50:
                recommendations.append("⚠️ أنت في منطقة الخطر، تحتاج خطة مذاكرة مكثفة")
            
            if not recommendations:
                st.success("🔥 أداؤك ممتاز! استمر كذا")
            for rec in recommendations:
                st.write(rec)

            # خطة المذاكرة الذكية
            st.subheader("📅 خطة مذاكرة ذكية")
            plan = []
            if weak_subjects:
                for sub in weak_subjects:
                    plan.append(f"📌 ركّز على مادة {sub} لمدة ساعة يوميًا")
            if data['Attendance'] < 75:
                plan.append("📍 احرص على حضور جميع المحاضرات القادمة")
            if engagement < 50:
                plan.append("📍 شارك في الكلاس واسأل الأسئلة")
            if data['Success_Probability'] < 50:
                plan.append("🔥 خصص 3-4 ساعات يوميًا للمذاكرة المكثفة")
            else:
                plan.append("✅ استمر على نفس المستوى مع مراجعة يومية خفيفة")
            for p in plan:
                st.write(p)
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
