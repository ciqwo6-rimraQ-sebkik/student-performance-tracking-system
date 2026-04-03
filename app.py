import streamlit as st
import pandas as pd
import plotly.express as px

# 1. إعدادات الصفحة
st.set_page_config(page_title="وحدة المراقبة الأكاديمية - جامعة طيبة", layout="wide")

# 2. إضافة الشعار والهوية البصرية (Custom CSS)
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-right: 5px solid #007b3e; /* لون جامعة طيبة الأخضر */
    }
    h1 {
        color: #1a2a44; /* كحلي غامق */
    }
    </style>
    """, unsafe_allow_input=True)

# 3. الهيدر مع الشعار
col_logo, col_title = st.columns([1, 4])

with col_logo:
    # ملاحظة: استبدل الرابط أدناه برابط شعار جامعة طيبة الرسمي أو مسار ملف محلي
    st.image("https://www.taibahu.edu.sa/Pages/AR/Image.aspx?ID=3", width=150)

with col_title:
    st.markdown("<h1 style='margin-top: 20px;'>وحدة المراقبة الأكاديمية (أعضاء هيئة التدريس)</h1>", unsafe_allow_input=True)
    st.markdown("<p style='font-size: 1.2rem; color: #555;'>نظام التنبؤ بحالات التعثر - جامعة طيبة</p>", unsafe_allow_input=True)

st.write("---")

# 4. الشريط الجانبي
st.sidebar.header("لوحة التحكم")
uploaded_file = st.sidebar.file_uploader("ارفع سجل الطلاب (Excel)", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # قراءة البيانات
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        
        # التأكد من وجود الأعمدة المطلوبة (الدرجات، الحضور)
        # ملاحظة: عدلت أسماء الأعمدة لتناسب الكود السابق
        if 'Grade' in df.columns:
            
            # --- منطق التنبؤ (حالة التنبؤ) ---
            def predict_status(grade):
                return "ناجح" if grade >= 60 else "متعثر"
            
            df['AI_Status'] = df['Grade'].apply(predict_status)
            
            # حساب النسب
            total_students = len(df)
            fail_count = len(df[df['AI_Status'] == 'متعثر'])
            fail_percentage = (fail_count / total_students) * 100
            avg_grade = df['Grade'].mean()

            # --- عرض المؤشرات (مثل الصورة التي أرسلتها) ---
            m1, m2, m3 = st.columns(3)
            m1.metric("إجمالي الطلاب", f"{total_students}")
            m2.metric("متوسط الدرجات", f"{avg_grade:.1f}")
            m3.metric("حالات التعثر المحتملة", f"{fail_percentage:.1f}%", delta=f"{fail_count} طالب", delta_color="inverse")

            st.write("### 📊 تحليل النتائج")
            
            tab1, tab2 = st.tabs(["السجل الرقمي الموحد", "التحليل البياني"])
            
            with tab1:
                st.dataframe(df.style.highlight_max(axis=0, color='#d4edda'), use_container_width=True)
            
            with tab2:
                c1, c2 = st.columns(2)
                with c1:
                    # رسم بياني دائري (توزيع الحالات)
                    fig_pie = px.pie(df, names='AI_Status', title="نسبة النجاح والتعثر المتوقعة",
                                    color='AI_Status',
                                    color_discrete_map={'ناجح':'#007b3e', 'متعثر':'#dc3545'})
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with c2:
                    # رسم بياني للدرجات
                    fig_hist = px.histogram(df, x='Grade', title="توزيع درجات الطلاب",
                                           color_discrete_sequence=['#1a2a44'])
                    st.plotly_chart(fig_hist, use_container_width=True)

        else:
            st.error("خطأ: الملف لا يحتوي على عمود 'Grade'. يرجى التأكد من تسمية الأعمدة بشكل صحيح.")

    except Exception as e:
        st.error(f"حدث خطأ في معالجة الملف: {e}")
else:
    st.info("الرجاء رفع ملف Excel يحتوي على بيانات الطلاب لعرض التحليل.")
