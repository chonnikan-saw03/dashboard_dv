import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =================================================================
# 1. ตั้งค่าหน้าเพจให้เต็มจอ และจัดสไตล์กล่อง KPI สรุปตัวเลข
# =================================================================
st.set_page_config(page_title="สรุปตรวจเช็คร้านค้าเช่า", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* ปรับแต่งกล่องสรุปตัวเลขทอง-เหลือง ให้คล้ายดีไซน์เดิม */
    .kpi-card {
        background-color: #FFF9E6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #F3E5AB;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .kpi-title { margin: 0; color: #666666; font-size: 15px; font-weight: bold; }
    .kpi-value { margin: 8px 0 0 0; color: #B8860B; font-size: 26px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ดึงตำแหน่งไฟล์ Excel จากโฟลเดอร์โปรเจกต์
current_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(current_dir, "Data exemple.xlsx")


# =================================================================
# 2. ฟังก์ชันโหลดข้อมูล Excel (อ่านทุกบรรทัดตรงๆ เป็น String)
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
    st.error("❌ ไม่สามารถเปิดไฟล์ 'Data exemple.xlsx' ได้ กรุณาตรวจสอบการอัปโหลดไฟล์ขึ้น GitHub")
    st.stop()


# =================================================================
# 3. ส่วนสร้าง FILTERS ทั้ง 7 ตัวตามต้องการ (แบ่งเป็น 2 แถวเพื่อความสวยงาม)
# =================================================================
st.title("📊 ระบบสรุปตรวจเช็คร้านค้าเช่า")
st.write("---")

# แถวที่ 1: ตัวกรองหลัก 4 ตัว
col1, col2, col3, col4 = st.columns(4)
with col1:
    branch_options = ['ทั้งหมด'] + sorted(list(df_raw['สาขา'].unique())) if 'สาขา' in df_raw.columns else ['ทั้งหมด']
    selected_branch = st.selectbox("เลือกสาขา:", branch_options)

with col2:
    building_options = ['ทั้งหมด'] + sorted(list(df_raw['อาคาร'].unique())) if 'อาคาร' in df_raw.columns else ['ทั้งหมด']
    selected_building = st.selectbox("เลือกอาคาร:", building_options)

with col3:
    # ดึงค่าจากคอลลัมน์วันที่ตรวจ (อิงจากชื่อ Date หรือตามในโครงสร้าง)
    date_col = 'Date' if 'Date' in df_raw.columns else ('วันที่ตรวจ' if 'วันที่ตรวจ' in df_raw.columns else '')
    date_options = ['ทั้งหมด'] + sorted(list(df_raw[date_col].unique())) if date_col else ['ทั้งหมด']
    selected_date = st.selectbox("วันที่ตรวจ:", date_options)

with col4:
    inspector_options = ['ทั้งหมด'] + sorted(list(df_raw['ชื่อผู้ตรวจ'].unique())) if 'ชื่อผู้ตรวจ' in df_raw.columns else ['ทั้งหมด']
    selected_inspector = st.selectbox("ชื่อผู้ตรวจ:", inspector_options)

# แถวที่ 2: ตัวกรองหมวดหมู่และสถานะอีก 3 ตัว
col5, col6, col7, col_empty = st.columns(4)
with col5:
    task_group_options = ['ทั้งหมด'] + sorted(list(df_raw['Task (group)'].unique())) if 'Task (group)' in df_raw.columns else ['ทั้งหมด']
    selected_task_group = st.selectbox("Task (group):", task_group_options)

with col6:
    # อิงตามคอลัมน์ Task Detail หรือ Task
    task_col = 'Task Detail' if 'Task Detail' in df_raw.columns else ('Task' if 'Task' in df_raw.columns else '')
    task_options = ['ทั้งหมด'] + sorted(list(df_raw[task_col].unique())) if task_col else ['ทั้งหมด']
    selected_task = st.selectbox("Task:", task_options)

with col7:
    status_options = ['ทั้งหมด'] + sorted(list(df_raw['Status'].unique())) if 'Status' in df_raw.columns else ['ทั้งหมด']
    selected_status = st.selectbox("Status (สถานะ):", status_options)


# =================================================================
# 4. กลไกการ Filter ข้อมูลตาม Data จริง (ทำงานสัมพันธ์กันทุกตัว)
# =================================================================
df_filtered = df_raw.copy()

if selected_branch != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['สาขา'] == selected_branch]

if selected_building != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['อาคาร'] == selected_building]

if date_col and selected_date != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered[date_col] == selected_date]

if selected_inspector != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['ชื่อผู้ตรวจ'] == selected_inspector]

if selected_task_group != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['Task (group)'] == selected_task_group]

if task_col and selected_task != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered[task_col] == selected_task]

if selected_status != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['Status'] == selected_status]


# =================================================================
# 5. ส่วนแสดงผลคำนวณตัวเลขสรุปจริงจากข้อมูลที่ผ่านการกรอง (KPI Cards)
# =================================================================
st.write("")
total_records = len(df_filtered)
unique_buildings = df_filtered['อาคาร'].nunique() if total_records > 0 else 0
unique_rooms = df_filtered['หมายเลขห้อง'].nunique() if total_records > 0 else 0

col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-title">🏢 ความครอบคลุมในการดูแล</p>
        <p class="kpi-value">{unique_buildings} อาคาร / {unique_rooms} ห้อง</p>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-title">📝 จำนวนรายการตรวจเช็คตามตัวกรอง</p>
        <p class="kpi-value" style="color: #008080;">{total_records} รายการ</p>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    # นับจำนวนสถานะเสร็จสิ้น
    complete_count = len(df_filtered[df_filtered['Status'].str.lower() == 'complete'])
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-title">✅ สถานะตรวจเช็คผ่าน (Complete)</p>
        <p class="kpi-value" style="color: #2E7D32;">{complete_count} รายการ</p>
    </div>
    """, unsafe_allow_html=True)


# =================================================================
# 6. ส่วนเรนเดอร์กราฟวงกลมสรุปสัดส่วนตาม Data จริง
# =================================================================
st.write("")
st.write("")

if total_records > 0:
    st.subheader("🎯 สัดส่วนสถานะการตรวจเช็ค (Status)")
    
    # ดึงข้อมูลมานับกลุ่มเพื่อทำชาร์ต
    status_counts = df_filtered['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'จำนวน']
    
    fig = px.pie(
        status_counts, 
        values='จำนวน', 
        names='Status',
        color_discrete_sequence=['#2E7D32', '#C62828', '#1565C0', '#EF6C00'], # เขียว แดง น้ำเงิน ส้ม ตามลำดับความสำคัญ
        hole=0.4 # ทำทรงโดนัทเหมือนในตัวอย่าง HTML
    )
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=380)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("💡 ไม่มีข้อมูลที่ตรงกับเงื่อนไขตัวกรองที่คุณเลือก")


# =================================================================
# 7. ตารางสรุปรายละเอียดบันทึกจริงด้านล่างสุด
# =================================================================
st.write("")
st.subheader("📋 ตารางบันทึกข้อมูลการตรวจเช็ครายเส้น (Detail)")

# กรองคอลลัมน์ให้แสดงผลสวยงามและเป็นภาษาไทย
df_display = df_filtered.copy()
rename_map = {
    'สาขา': 'สาขา', 'อาคาร': 'อาคาร', 'หมายเลขห้อง': 'หมายเลขห้อง',
    'Date': 'วันที่ตรวจ', 'Task (group)': 'Task (group)', 'Task Detail': 'Task Detail',
    'Task': 'Task', 'ชื่อผู้ตรวจ': 'ชื่อผู้ตรวจ', 'Reason': 'Reason/ความผิดปกติ', 'Status': 'Status'
}

available_to_show = [c for c in rename_map.keys() if c in df_display.columns]
df_display = df_display[available_to_show].rename(columns=rename_map)

# แสดงตารางข้อมูลจริงที่ขยับและค้นหาเพิ่มเติม
