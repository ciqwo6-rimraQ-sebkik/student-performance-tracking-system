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
        background-color: #ffffff !important;
        padding: 15px !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        border-right: 5px solid #007b3e !important; 
    }
    h1 {
        color: #1a2a44;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True) # هنا كان الخطأ، تم التصحيح إلى html

# 3. الهيدر مع الشعار
col_logo, col_title = st.columns([1, 4])

with col_logo:
    # رابط شعار جامعة طيبة
    st.image("https://www.taibahu.edu.sa/Pages/AR/Image.aspx?ID=3", width=120)

with col_title:
    st.markdown("<h1 style='margin-top: 10px;'>وحدة المراقبة الأكاديمية</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.2rem; color: #555; text-align: right;'>جامعة طيبة - نظام التنبؤ بالأداء الأكاديمي</p>", unsafe_allow_html=True)

st.write("---")

# 4. الشريط الجانبي
st.sidebar.header("تحميل البيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف سجل الطلاب (Excel)", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # قراءة الملف
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        # التأكد من وجود عمود الدرجات (Grade)
        if 'Grade' in df.columns:
            # حساب الإحصائيات
            total_students = len(df)
            avg_grade = df['Grade'].mean()
            
            # منطق التنبؤ بسيط
            def predict(g):
                return "ناجح" if g >= 60 else "متعثر"
            df['Prediction'] = df['Grade'].apply(predict)
            
            fail_count = len(df[df['Prediction'] == 'متعثر'])
            fail_percent = (fail_count / total_students) * 100

            # عرض المؤشرات
            m1, m2, m3 = st.columns(3)
            m1.metric("إجمالي الطلاب", total_students)
            m2.metric("متوسط الدرجات", f"{avg_grade:.1f}")
            m3.metric("حالات التعثر المحتملة", f"{fail_percent:.1f}%", f"{fail_count} طالب")

            st.write("### 📋 تفاصيل السجل الأكاديمي")
            st.dataframe(df, use_container_width=True)

            # الرسم البياني
            st.write("### 📊 التحليل البياني")
            fig = px.pie(df, names='Prediction', color='Prediction',
                         color_discrete_map={'ناجح':'#007b3e', 'متعثر':'#dc3545'},
                         hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning("يرجى التأكد من أن ملف Excel يحتوي على عمود باسم 'Grade'")

    except Exception as e:
        st.error(f"حدث خطأ: {e}")
else:
    st.info("بانتظار رفع ملف البيانات للبدء...")
