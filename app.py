import streamlit as st
import pandas as pd
import json

# 1. ตั้งค่าหน้าเพจให้เต็มจอ
st.set_page_config(page_title="สรุปตรวจเช็คร้านค้าเช่า", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > section:nth-child(2) > div:nth-child(1) { padding: 0rem; }
    iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

# 2. อ่านไฟล์ Excel (ปรับให้อ่านทุกคอลัมน์เป็น String เพื่อไม่ให้ข้อมูลบรรทัดไหนตกหล่น)
@st.cache_data
def load_data():
    # บังคับดึงข้อมูลทุกช่องออกมาเป็นข้อความ (dtype=str) จะได้ไม่มีปัญหาเรื่อง Format วันที่หรือตัวเลขเพี้ยน
    df = pd.read_excel("Data exemple.xlsx", sheet_name="Sheet1", dtype=str)
    
    # จัดการเคลียร์ค่าว่าง (NaN) ในทุกๆ คอลัมน์ให้กลายเป็นช่องว่างธรรมดา หรือคำว่า 'ปกติ'
    df = df.fillna('')
    if 'Reason' in df.columns:
        # แทนที่ช่องว่างใน Reason ด้วยคำว่า 'ปกติ' ตามเงื่อนไขเดิมของคุณ
        df['Reason'] = df['Reason'].replace('', 'ปกติ')
    return df

df = load_data()

# 3. แปลงข้อมูลจาก Excel ทุกบรรทัดให้กลายเป็นรูปแบบ JSON เพื่อส่งให้ HTML
records = []
for _, row in df.iterrows():
    # อ่านข้อมูลทุกบรรทัดชัวร์ๆ โดยแปลงเป็นข้อความและตัดช่องว่างส่วนเกิน (strip)
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

# 4. อ่านไฟล์ HTML ตามชื่อที่คุณระบุเป๊ะๆ
with open("dashboard_tenant_store_inspection (1).html", "r", encoding="utf-8") as f:
    html_content = f.read()

# นำข้อมูลจริงจาก Excel (js_data) ไปเสียบแทนที่ตัวแปรเก่าใน HTML
old_dataset_marker = "const inspectionDataset = ["
if old_dataset_marker in html_content:
    parts = html_content.split(old_dataset_marker)
    rest_of_html = parts[1].split("];", 1)[1]
    html_content = f"{parts[0]}const inspectionDataset = {js_data};{rest_of_html}"

# 5. แสดงผลหน้าจอ
import streamlit.components.v1 as components
components.html(html_content, height=1200, scrolling=True)
