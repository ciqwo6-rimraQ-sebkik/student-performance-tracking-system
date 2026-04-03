Import streamlit as st
import pandas as pd
import plotly.express as px

# إعدادات الصفحة
st.set_page_config(page_title="نظام متابعة أداء الطلاب", layout="wide")

# تصميم الهيدر وشعار بسيط
st.markdown("<h1 style='text-align: center; color: #2E4053;'>نظام التحليل الذكي لأداء الطلاب</h1>", unsafe_allow_input=True)
st.write("---")

# الجزء الخاص برفع الملف
st.sidebar.header("تحميل البيانات")
uploaded_file = st.sidebar.file_uploader("اختر ملف Excel أو CSV", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # قراءة الملف
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # --- منطق معالجة البيانات (بديل الـ AI المعقد) ---
        # لنفترض أن الملف يحتوي على أعمدة: Grade, Attendance
        if 'Grade' in df.columns and 'Attendance' in df.columns:
            def calculate_risk(row):
                if row['Grade'] < 60 or row['Attendance'] < 50:
                    return 'High'
                elif row['Grade'] < 75:
                    return 'Medium'
                else:
                    return 'Low'
            
            df['Risk Level'] = df.apply(calculate_risk, axis=1)
            
            # --- عرض الإحصائيات العلوية ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("إجمالي الطلاب", len(df))
            col2.metric("عالي الخطورة", len(df[df['Risk Level'] == 'High']))
            col3.metric("متوسط الخطورة", len(df[df['Risk Level'] == 'Medium']))
            col4.metric("منخفض الخطورة", len(df[df['Risk Level'] == 'Low']))

            st.write("### بيانات الطلاب المحللة")
            st.dataframe(df, use_container_width=True)

            # --- الرسوم البيانية ---
            st.write("---")
            c1, c2 = st.columns(2)
            
            with c1:
                st.write("#### توزيع مستويات الخطورة")
                fig_pie = px.pie(df, names='Risk Level', color='Risk Level',
                                 color_discrete_map={'High':'#FF4B4B', 'Medium':'#FFA500', 'Low':'#28A745'})
                st.plotly_chart(fig_pie)
                
            with c2:
                st.write("#### العلاقة بين الدرجات والحضور")
                fig_scatter = px.scatter(df, x='Attendance', y='Grade', color='Risk Level',
                                         hover_name='Name' if 'Name' in df.columns else None)
                st.plotly_chart(fig_scatter)

        else:
            st.error("تنبيه: تأكد أن الملف يحتوي على أعمدة باسم 'Grade' و 'Attendance'")

    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
else:
    st.info("الرجاء رفع ملف Excel للبدء في تحليل أداء الطلاب.")
    # عرض مثال لشكل الجدول المطلوب
    st.write("مثال لشكل البيانات المطلوبة:")
    example_df = pd.DataFrame({
        'Student_ID': [101, 102],
        'Name': ['أحمد', 'سارة'],
        'Grade': [85, 55],
        'Attendance': [90, 40]
    })
    st.table(example_df)
