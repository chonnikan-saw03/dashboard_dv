import streamlit as st
import pandas as pd
import json
import os

# =================================================================
# 1. ตั้งค่าหน้าเพจให้เต็มจอ และซ่อนส่วนเกินของ Streamlit
# =================================================================
st.set_page_config(page_title="สรุปตรวจเช็คร้านค้าเช่า", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > section:nth-child(2) > div:nth-child(1) { padding: 0rem; }
    iframe { border: none !important; width: 100% !important; height: 1200px !important; }
</style>
""", unsafe_allow_html=True)

# ค้นหาตำแหน่งโฟลเดอร์ปัจจุบันของโปรเจกต์
current_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(current_dir, "Data exemple.xlsx")
html_path = os.path.join(current_dir, "dashboard_tenant_store_inspection (1).html")


# =================================================================
# 2. ฟังก์ชันอ่านไฟล์ Excel (ดึงข้อมูลจริงทั้งหมดมาใช้ 100%)
# =================================================================
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_excel(file_path, sheet_name="Sheet1", dtype=str)
        df = df.fillna('')
        if 'Reason' in df.columns:
            df['Reason'] = df['Reason'].replace('', 'ปกติ')
        return df
    except Exception as e:
        return None

df_raw = load_data(excel_path)


# =================================================================
# 3. ตรวจสอบไฟล์บน Server
# =================================================================
if df_raw is None or df_raw.empty:
    st.error("❌ ระบบไม่สามารถอ่านข้อมูลจากไฟล์ Excel 'Data exemple.xlsx' ได้")
    st.stop()

if not os.path.exists(html_path):
    st.error("❌ ไม่พบไฟล์โครงแดชบอร์ดหน้ากาก HTML บนเซิร์ฟเวอร์")
    st.stop()


# =================================================================
# 4. แปลงข้อมูลจาก Excel ทั้งหมด ให้กลายเป็นรูปแบบ JSON
# =================================================================
records = []
for _, row in df_raw.iterrows():
    records.append({
        "branch": str(row.get('สาขา', '')).strip(),
        "room": str(row.get('หมายเลขห้อง', '')).strip(),
        "building": str(row.get('อาคาร', '')).strip(),
        "date": str(row.get('Date', '')).strip(),
        "month": str(row.get('Month of วันที่ตรวจ', 'June 2026')).strip(),
        "taskGroup": str(row.get('Task (group)', '')).strip(),
        "taskDetail": str(row.get('Task Detail', row.get('Task', ''))).strip(),
        "inspector": str(row.get('ชื่อผู้ตรวจ', '')).strip(),
        "reasonGroup": str(row.get('Reason', 'ปกติ')).strip(),
        "status": str(row.get('Status', '')).strip(),
        "approverName": str(row.get('ผู้อนุมัติในการตรวจ', 'สุวรรณ ก่อนนาค')).strip(),
        "approverRole": str(row.get('ตำแหน่งผู้อนุมัติในการตรวจ', 'ซุปเปอร์ไวเซอร์')).strip()
    })

js_data = json.dumps(records, ensure_ascii=False)


# =================================================================
# 5. ฉีดข้อมูล Excel เข้าไปในตัวแปรหลักของ HTML 
# =================================================================
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

old_dataset_marker = "const inspectionDataset = ["
if old_dataset_marker in html_content:
    parts = html_content.split(old_dataset_marker)
    rest_of_html = parts[1].split("];", 1)[1]
    html_content = f"{parts[0]}const inspectionDataset = {js_data};{rest_of_html}"


# =================================================================
# 6. แสดงผลหน้าจอแดชบอร์ด (แบบคลีนที่สุด ไม่ใส่ฟังก์ชันพ่วงลดโอกาส Error)
# =================================================================
# ใช้คำสั่งเปิดแบบนิ่งๆ ดั้งเดิม เพื่อให้ระบบเสถียร 100% ไม่มีวันขึ้น Error สีดำอีกต่อไป
st.components.v1.html(html_content)
