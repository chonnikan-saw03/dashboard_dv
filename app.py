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

# 2. อ่านไฟล์ Excel (ดึงมาทุกบรรทัดชัวร์ๆ)
@st.cache_data
def load_data():
    df = pd.read_excel("Data exemple.xlsx", sheet_name="Sheet1", dtype=str)
    df = df.fillna('')
    if 'Reason' in df.columns:
        df['Reason'] = df['Reason'].replace('', 'ปกติ')
    return df

df_raw = load_data()

# =================================================================
# 3. สร้าง Filter หน้าสาขาด้วย Streamlit (เช่น เลือก สาขารัชดา)
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
# 4. กรองข้อมูลใน Excel ทันที (สมมติเลือก รัชดา -> df_filtered จะเหลือแค่รัชดา)
# =================================================================
df_filtered = df_raw.copy()

if selected_branch != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['สาขา'] == selected_branch]
if selected_building != '健全': # ปรับตามเงื่อนไข 'ทั้งหมด'
    if selected_building != 'ทั้งหมด':
        df_filtered = df_filtered[df_filtered['อาคาร'] == selected_building]
if selected_status != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['Status'] == selected_status]

# แปลงข้อมูลสาขาที่ถูกกรองแล้วให้เป็น JSON
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
# 5. ฉีดข้อมูลที่กรองแล้ว เข้าไปใน HTML และสั่งให้หน้าจอวาดใหม่ (Re-render)
# =================================================================
with open("dashboard_tenant_store_inspection (1).html", "r", encoding="utf-8") as f:
    html_content = f.read()

# แทนที่ตัวแปรเก็บข้อมูลใน HTML ด้วยข้อมูลที่ผ่านฟิลเตอร์แล้ว
old_dataset_marker = "const inspectionDataset = ["
if old_dataset_marker in html_content:
    parts = html_content.split(old_dataset_marker)
    rest_of_html = parts[1].split("];", 1)[1]
    html_content = f"{parts[0]}const inspectionDataset = {js_data};{rest_of_html}"

# 🔥 โค้ดพิเศษ: สั่งให้ JavaScript ใน HTML ทำงานใหม่ทันทีเมื่อข้อมูลเปลี่ยน
# โดยปกติใน HTML ตัวอย่างมักจะมีฟังก์ชันชื่อ init() หรือ render() หรือบรรทัดที่ใช้วาดกราฟตอนเปิดเว็บ
# เราจะบังคับให้มันรันซ้ำอีกรอบตอนท้ายไฟล์เพื่ออัปเดตหน้าจอให้เปลี่ยนตามฟิลเตอร์
render_trigger = """
<script>
    // สั่งให้ระบบใน HTML วาดตารางและกราฟใหม่ด้วยข้อมูลล่าสุดที่คัดกรองแล้ว
    if (typeof init === 'function') { init(); }
    else if (typeof renderDashboard === 'function') { renderDashboard(); }
    else if (typeof updateCharts === 'function') { updateCharts(); }
</script>
"""
html_content += render_trigger


# =================================================================
# 6. แสดงผลหน้าจอแดชบอร์ดสุดสวย
# =================================================================
import streamlit.components.v1 as components
components.html(html_content, height=1200, scrolling=True)
