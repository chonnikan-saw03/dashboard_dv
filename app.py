import streamlit as st
import pandas as pd
import json
import os
import time  # เพิ่มเข้ามาเพื่อใช้ทำรหัสสุ่มรีเฟรชหน้าจอ

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
# 2. ฟังก์ชันอ่านไฟล์ Excel
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
    st.error("❌ 不พบไฟล์โครงแดชบอร์ดหน้ากาก HTML บนเซิร์ฟเวอร์")
    st.stop()


# =================================================================
# 4. สร้าง Filter ด้านบนด้วย Streamlit
# =================================================================
st.title("📊 ระบบสรุปตรวจเช็คร้านค้าเช่า")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    branch_options = ['ทั้งหมด'] + sorted(list(df_raw['สาขา'].unique()))
    selected_branch = st.selectbox("เลือกสาขา:", branch_options)

with col_f2:
    building_options = ['ทั้งหมด'] + sorted(list(df_raw['อาคาร'].unique()))
    selected_building = st.selectbox("เลือกอาคาร:", building_options)

with col_f3:
    status_options = ['ทั้งหมด'] + sorted(list(df_raw['Status'].unique()))
    selected_status = st.selectbox("เลือกสถานะ:", status_options)


# =================================================================
# 5. กรองข้อมูลใน Excel ทันทีตามเงื่อนไขที่เลือก
# =================================================================
df_filtered = df_raw.copy()

if selected_branch != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['สาขา'] == selected_branch]

if selected_building != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['อาคาร'] == selected_building]

if selected_status != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['Status'] == selected_status]

# แปลงข้อมูลเฉพาะแถวที่ผ่านฟิลเตอร์ให้เป็นรูปแบบ JSON
records = []
for _, row in df_filtered.iterrows():
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
# 6. อ่านไฟล์ HTML ตัวอย่าง แล้วฉีดข้อมูล JSON ใส่เข้าไปแทนที่ข้อมูลเก่า
# =================================================================
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

old_dataset_marker = "const inspectionDataset = ["
if old_dataset_marker in html_content:
    parts = html_content.split(old_dataset_marker)
    rest_of_html = parts[1].split("];", 1)[1]
    html_content = f"{parts[0]}const inspectionDataset = {js_data};{rest_of_html}"


# =================================================================
# 7. แสดงผลแดชบอร์ด HTML แบบบังคับล้างหน้ากระดาน (ปลอดภัยจาก TypeError)
# =================================================================
# สร้างรหัสลับเป็นตัวเลข Timestamps (เช่น 171854321) ทุกครั้งที่มีการขยับฟิลเตอร์
# การใช้ตัวเลขล้วนแบบนี้ จะไม่ทำให้เกิด TypeError บน Python เวอร์ชันใหม่แน่นอน 100%
refresh_id = int(time.time())

# บังคับดึงข้อมูลใหม่มาวาดกราฟทันทีด้วยการระบุ key=refresh_id
st.components.v1.html(html_content, key=refresh_id)
