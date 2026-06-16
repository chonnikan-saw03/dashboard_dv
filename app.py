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
    iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

# ค้นหาตำแหน่งโฟลเดอร์ปัจจุบันของโปรเจกต์ ป้องกันปัญหา Path บน Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(current_dir, "Data exemple.xlsx")
html_path = os.path.join(current_dir, "dashboard_tenant_store_inspection (1).html")


# =================================================================
# 2. ฟังก์ชันอ่านไฟล์ Excel (ดึงมาทุกบรรทัดชัวร์ๆ)
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
# 3. ตรวจสอบว่าเปิดไฟล์สำเร็จหรือไม่ หากไม่สำเร็จให้แจ้งเตือนทันที
# =================================================================
if df_raw is None or df_raw.empty:
    st.error("❌ ระบบไม่สามารถอ่านข้อมูลจากไฟล์ Excel 'Data exemple.xlsx' ได้")
    st.info("💡 กรุณาตรวจสอบว่าได้อัปเดตไฟล์ Excel ขึ้นไปบน GitHub Repository ในโฟลเดอร์เดียวกับไฟล์ app.py แล้วหรือยัง")
    st.stop()  # สั่งหยุดการรันเพื่อไม่ให้เกิด Error บรรทัดถัดไป

if not os.path.exists(html_path):
    st.error("❌ ไม่พบไฟล์โครงแดชบอร์ดหน้ากาก HTML บนเซิร์ฟเวอร์")
    st.info(f"💡 กรุณาตรวจสอบว่ามีไฟล์ชื่อ 'dashboard_tenant_store_inspection (1).html' อยู่บน GitHub แล้วหรือยัง")
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

# สั่งกระตุ้นสคริปต์ให้รันซ้ำเมื่อขยับ Filter
render_trigger = """
<script>
    if (typeof init === 'function') { init(); }
    else if (typeof renderDashboard === 'function') { renderDashboard(); }
    else if (typeof updateCharts === 'function') { updateCharts(); }
</script>
"""
html_content += render_trigger


# =================================================================
# 7. แสดงผลแดชบอร์ด HTML (ใช้คำสั่งตรงของระบบเพื่อเลี่ยง TypeError ชัวร์ๆ)
# =================================================================
component_key = f"dash_{selected_branch}_{selected_building}_{selected_status}"

# เรียกใช้ผ่านคำสั่งเต็มขั้นเด็ดขาด การันตีไม่มีการชนกันของ Arguments
st.components.v1.html(html_content, height=1200, scrolling=True, key=component_key)
