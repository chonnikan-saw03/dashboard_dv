import streamlit as st
import pandas as pd
import json

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(page_title="สรุปตรวจเช็คร้านค้าเช่า", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > section:nth-child(2) > div:nth-child(1) { padding: 0rem; }
    iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

# 2. อ่านไฟล์ Excel (ดึงข้อมูลจริงทั้งหมดมาใช้)
@st.cache_data
def load_data():
    df = pd.read_excel("Data exemple.xlsx", sheet_name="Sheet1")
    df['Reason'] = df['Reason'].fillna('ปกติ')
    # ปรับชื่อคอลัมน์ให้ตรงกับที่ HTML เรียกใช้ (หากมี)
    return df

df = load_data()

# 3. แปลงข้อมูลจาก Excel ให้กลายเป็นรูปแบบ JSON เพื่อส่งให้ HTML
# (โค้ดส่วนนี้จะแปลงข้อมูลทุกแถวใน Excel ของคุณให้เป็นภาษาที่หน้าเว็บเข้าใจ)
records = []
for _, row in df.iterrows():
    records.append({
        "branch": str(row.get('สาขา', '')),
        "room": str(row.get('หมายเลขห้อง', '')),
        "building": str(row.get('อาคาร', '')),
        "date": str(row.get('Date', '')),
        "month": str(row.get('Month of วันที่ตรวจ', 'June 2026')),
        "taskGroup": str(row.get('Task (group)', '')),
        "taskDetail": str(row.get('Task Detail', row.get('Task', ''))),
        "inspector": str(row.get('ชื่อผู้ตรวจ', '')),
        "reasonGroup": str(row.get('Reason', 'ปกติ')),
        "status": str(row.get('Status', '')),
        "approverName": str(row.get('ผู้อนุมัติในการตรวจ', 'สุวรรณ ก่อนนาค')),
        "approverRole": str(row.get('ตำแหน่งผู้อนุมัติในการตรวจ', 'ซุปเปอร์ไวเซอร์'))
    })

js_data = json.dumps(records, ensure_ascii=False)

# 4. อ่านไฟล์ HTML ต้นฉบับมาโมดิฟายด์
with open("dashboard.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# นำข้อมูลจาก Excel (js_data) ไปเสียบแทนที่ตัวแปรเก่าใน HTML
# ค้นหาจุดที่เป็นตัวแปรชุดข้อมูลใน HTML แล้วสลับใส่ข้อมูลจริงเข้าไป
old_dataset_marker = "const inspectionDataset = ["
if old_dataset_marker in html_content:
    parts = html_content.split(old_dataset_marker)
    # ตัดส่วนที่เป็นข้อมูลเก่าออก แล้วต่อด้วยข้อมูลจริงจาก Excel
    rest_of_html = parts[1].split("];", 1)[1]
    html_content = f"{parts[0]}const inspectionDataset = {js_data};{rest_of_html}"

# 5. แสดงผลหน้าจอแบบข้อมูลสดใหม่จาก Excel
import streamlit.components.v1 as components
components.html(html_content, height=1200, scrolling=True)
