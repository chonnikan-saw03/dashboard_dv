import streamlit as st
import pandas as pd
import json
import os

# =================================================================
# 1. ตั้งค่าหน้าเพจให้เต็มจอ และล็อกขนาดกล่องแสดงผลด้วย CSS
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
# 2. ฟังก์ชันอ่านไฟล์ Excel (ดึงมาครบทุกบรรทัดชัวร์ๆ)
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

if df_raw is None or df_raw.empty:
    st.error("❌ ระบบไม่สามารถอ่านข้อมูลจากไฟล์ Excel ได้")
    st.stop()


# =================================================================
# 3. ส่วนสร้าง FILTER ด้านบนสุด (Streamlit)
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
# 4. ประมวลผลตัดข้อมูลใน Excel จริงตาม Filter ที่เลือก
# =================================================================
df_filtered = df_raw.copy()

if selected_branch != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['สาขา'] == selected_branch]
if selected_building != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['อาคาร'] == selected_building]
if selected_status != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['Status'] == selected_status]

total_records = len(df_filtered)


# =================================================================
# 5. อ่าน HTML และฉีดข้อมูลที่ผ่านฟิลเตอร์แล้วเข้าไปแทนที่ข้อมูลชุดเก่า
# =================================================================
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# แปลงข้อมูลแถวที่กรอกเสร็จแล้วส่งให้ HTML ตัวอย่างวาดกราฟ
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

old_dataset_marker = "const inspectionDataset = ["
if old_dataset_marker in html_content:
    parts = html_content.split(old_dataset_marker)
    rest_of_html = parts[1].split("];", 1)[1]
    html_content = f"{parts[0]}const inspectionDataset = {js_data};{rest_of_html}"


# =================================================================
# 6. แสดงผลหน้าจอแดชบอร์ดกราฟและรายละเอียด (ขยับตามชัวร์ ปลอดภัยไร้ Error)
# =================================================================
# ใช้จำนวนแถวข้อมูลมาตั้งรหัสลับ (ตัวเลขล้วน 100% ไม่มีวันเกิด TypeError)
# เพื่อส่งสัญญาณบอกให้ระบบรื้อกราฟอันเก่าออก แล้ววาดกราฟวงกลมของสาขาที่เลือกใหม่ทันที
component_key = f"dashboard_view_{total_records}"

st.components.v1.html(html_content, key=component_key)
