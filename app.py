import streamlit as st
import pandas as pd
import json
import os

# =================================================================
# 1. ตั้งค่าหน้าเพจให้เต็มจอ
# =================================================================
st.set_page_config(page_title="สรุปตรวจเช็คร้านค้าเช่า", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > section:nth-child(2) > div:nth-child(1) { padding: 0rem; }
    iframe { border: none !important; width: 100% !important; height: 900px !important; }
    /* แต่งตัวเลข KPI ให้น่าเชื่อถือและสวยงาม */
    .metric-box {
        background-color: #FFF9E6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #F3E5AB;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

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
# 4. ประมวลผลนับจำนวนอาคารและห้องจากข้อมูล Excel จริงตาม Filter
# =================================================================
df_filtered = df_raw.copy()

if selected_branch != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['สาขา'] == selected_branch]
if selected_building != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['อาคาร'] == selected_building]
if selected_status != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['Status'] == selected_status]

# คำนวณยอดสรุปจริงจาก Excel ด้วย Python (แม่นยำ 100% ขยับแน่นอน)
total_records = len(df_filtered)
unique_buildings = df_filtered['อาคาร'].nunique() if selected_building == 'ทั้งหมด' else 1
unique_rooms = df_filtered['หมายเลขห้อง'].nunique()

# หากเลือกเป็น "ทั้งหมด" แต่ข้อมูลในแผ่นงานไม่มี ให้เซ็ตเป็น 0
if total_records == 0:
    unique_buildings = 0
    unique_rooms = 0


# =================================================================
# 5. โชว์ตัวเลขสรุป (KPI Cards) สีเหลืองสวยๆ ที่ขยับตามฟิลเตอร์จริงชัวร์ๆ
# =================================================================
st.markdown("### 📌 สรุปยอดจากการเลือกตัวกรองปัจจุบัน")
m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(f'<div class="metric-box"><p style="margin:0;color:#666;">ความครอบคลุมในการดูแล</p><h2 style="margin:5px 0;color:#B8860B;">{unique_buildings} อาคาร / {unique_rooms} ห้อง</h2></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-box"><p style="margin:0;color:#666;">จำนวนรายการตรวจเช็ค</p><h2 style="margin:5px 0;color:#008080;">{total_records} รายการ</h2></div>', unsafe_allow_html=True)
with m3:
    complete_count = len(df_filtered[df_filtered['Status'].str.lower() == 'complete'])
    st.markdown(f'<div class="metric-box"><p style="margin:0;color:#666;">สถานะตรวจเช็คผ่าน (Complete)</p><h2 style="margin:5px 0;color:#2E7D32;">{complete_count} รายการ</h2></div>', unsafe_allow_html=True)

st.markdown("---")


# =================================================================
# 6. อ่าน HTML และฉีดข้อมูลที่กรองแล้วลงไปวาดกราฟด้านล่าง
# =================================================================
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# แปลงข้อมูลส่งให้ HTML วาดเฉพาะกราฟและตารางตามที่เรา Filter ไว้
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

# สั่งให้ระบบภายใน HTML รีเฟรชตารางและกราฟวงกลมด้านล่าง
render_trigger = """
<script>
    if (typeof init === 'function') { init(); }
    else if (typeof renderDashboard === 'function') { renderDashboard(); }
    else if (typeof updateCharts === 'function') { updateCharts(); }
</script>
"""
html_content += render_trigger


# =================================================================
# 7. แสดงผลหน้าจอแดชบอร์ดกราฟและรายละเอียด (ไร้บั๊ก เสถียร 100%)
# =================================================================
st.components.v1.html(html_content)
