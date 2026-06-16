import streamlit as st
import pandas as pd
import json

# =================================================================
# 1. ตั้งค่าหน้าเพจให้เต็มจอ และซ่อนส่วนเกินของ Streamlit
# =================================================================
st.set_page_config(page_title="สรุปตรวจเช็คร้านค้าเช่า", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > section:nth-child(2) > div:nth-child(1) { padding: 0rem; }
    iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)


# =================================================================
# 2. ฟังก์ชันอ่านไฟล์ Excel (กวาดข้อมูลมาทุกบรรทัดชัวร์ๆ)
# =================================================================
@st.cache_data
def load_data():
    # บังคับอ่านเป็นตัวหนังสือเพื่อป้องกัน Format เพี้ยน
    df = pd.read_excel("Data exemple.xlsx", sheet_name="Sheet1", dtype=str)
    df = df.fillna('')
    if 'Reason' in df.columns:
        df['Reason'] = df['Reason'].replace('', 'ปกติ')
    return df

df_raw = load_data()


# =================================================================
# 3. สร้าง Filter ด้านบนด้วย Streamlit
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
# 4. ประมวลผล Filter บนข้อมูล Excel จริง (เช่น เลือกรัชดา เหลือแค่รัชดา)
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
# 5. อ่านไฟล์ HTML ตัวอย่าง แล้วฉีดข้อมูล JSON ใส่เข้าไปแทนที่ข้อมูลเก่า
# =================================================================
with open("dashboard_tenant_store_inspection (1).html", "r", encoding="utf-8") as f:
    html_content = f.read()

old_dataset_marker = "const inspectionDataset = ["
if old_dataset_marker in html_content:
    parts = html_content.split(old_dataset_marker)
    rest_of_html = parts[1].split("];", 1)[1]
    html_content = f"{parts[0]}const inspectionDataset = {js_data};{rest_of_html}"


# =================================================================
# 6. แสดงผลแดชบอร์ด HTML (บังคับโหลดใหม่ชัวร์ๆ ด้วย component_key)
# =================================================================
import streamlit.components.v1 as components

# บังคับสร้างรหัสตามการเลือกฟิลเตอร์เพื่อสั่งให้หน้าจอ HTML รีเฟรชตัวเองตามข้อมูลล่าสุด
component_key = f"dash_{selected_branch}_{selected_building}_{selected_status}"

# แสดงผลหน้าจอแดชบอร์ดสุดสวยตาม HTML ตัวอย่าง
components.html(html_content, height=1200, scrolling=True, key=component_key)
