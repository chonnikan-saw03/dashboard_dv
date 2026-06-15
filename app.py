import streamlit as st
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าเพจให้กว้างเต็มจอและซ่อนขอบขาวของ Streamlit
st.set_page_config(
    page_title="สรุปตรวจเช็คร้านค้าเช่า - Dashboard Overview", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ใช้ CSS เพื่อซ่อนขอบ (Padding) และส่วนหัวของ Streamlit เพื่อให้ HTML แสดงผลได้เนียนตาที่สุด
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > section:nth-child(2) > div:nth-child(1) {
        padding: 0rem 0rem 0rem 0rem;
    }
    iframe {
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. ฟังก์ชันสำหรับอ่านไฟล์ HTML
def load_html_file(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return f.read()

# โหลดเนื้อหาจากไฟล์ HTML ที่อัปโหลดไว้บน GitHub
html_content = load_html_file("dashboard_tenant_store_inspection (1).html")

# 3. พ่นหน้าจอ HTML ออกมาแสดงผลแบบ Interactive (กำหนดความสูงให้พอดีหน้าจอประมาณ 1000 พิกเซล)
components.html(html_content, height=1100, scrolling=True)
