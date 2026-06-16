import streamlit as st
import time

# --- สมมติฐานต้นทางข้อมูล (แก้ไขให้ตรงกับระบบของคุณ) ---
# ตรงนี้คือจุดที่ html_content ถูกสร้างขึ้นมา (เช่น อ่านไฟล์ หรือรับค่าจากฟังก์ชันอื่น)
# html_content = ... 
# component_key = "my_dashboard_component"


st.title("Dashboard HTML Component")

# --- ส่วนดักจับและแก้ไขปัญหา (Error Handling) ---

# 1. ตรวจสอบว่ามีตัวแปร html_content อยู่จริงและไม่เป็นค่าว่าง
if 'html_content' not in locals() and 'html_content' not in globals():
    st.error("❌ ไม่พบตัวแปร `html_content` ในระบบ กรุณาตรวจสอบการประกาศตัวแปรต้นทาง")

elif html_content is None:
    st.error("❌ ตัวแปร `html_content` มีค่าเป็น `None` (ไม่มีข้อมูลส่งมา) กรุณาเช็กฟังก์ชันที่สร้าง HTML")

elif not isinstance(html_content, str):
    st.error(f"❌ ชนิดข้อมูลของ `html_content` ไม่ถูกต้อง! ต้องการ `str` แต่ตรวจพบเป็น `{type(html_content).__name__}`")

else:
    # 2. ป้องกันปัญหา Key ซ้ำ (Duplicate Key) 
    # ทำการสร้าง Unique Key โดยเอา component_key เดิมมาผสมกับค่าเวลาปัจจุบัน (Timestamp) 
    # หรือตรวจสอบว่าตัวแปร component_key มีอยู่หรือไม่ หากไม่มีให้กำหนดค่าเริ่มต้น
    if 'component_key' not in locals() and 'component_key' not in globals():
        component_key = "default_html_key"
        
    unique_component_key = f"{component_key}_{int(time.time())}"

    # 3. รัน Component อย่างปลอดภัย
    try:
        st.components.v1.html(
            html_content, 
            height=1200, 
            scrolling=True, 
            key=unique_component_key
        )
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดขณะโหลด HTML Component: {str(e)}")
        st.info("💡 แนะนำให้ตรวจสอบปุ่ม 'Manage app' ที่มุมขวาล่างของ Streamlit Cloud เพื่อดู Logs ตัวเต็ม")
