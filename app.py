import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =================================================================
# 1. ตั้งค่าหน้าเพจให้เต็มจอ และจัดสไตล์ CSS (ถอดแบบสีสันจาก HTML ตัวอย่าง)
# =================================================================
st.set_page_config(page_title="สรุปตรวจเช็คร้านค้าเช่า", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* ปรับแต่งกล่องสรุปตัวเลข */
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

    /* 🎨 แต่งหน้าตาตารางให้ถอดแบบมาจาก HTML ตัวอย่าง */
    .custom-table-container {
        width: 100%;
        overflow-x: auto;
        margin-top: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .custom-dashboard-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Prompt', 'Helvetica Neue', sans-serif;
        font-size: 14px;
        background-color: #ffffff;
    }
    .custom-dashboard-table th {
        background-color: #f8f9fa;
        color: #333333;
        font-weight: 600;
        text-align: left;
        padding: 12px 16px;
        border-bottom: 2px solid #dee2e6;
    }
    .custom-dashboard-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #eee;
        color: #495057;
        vertical-align: middle;
    }
    .custom-dashboard-table tr:nth-child(even) {
        background-color: #fdfdfd;
    }
    .custom-dashboard-table tr:hover {
        background-color: #f1f3f5;
    }
    .status-badge {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        text-transform: uppercase;
    }
    .status-complete { background-color: #d4edda; color: #155724; }
    .status-pending { background-color: #fff3cd; color: #856404; }
    .status-error { background-color: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

current_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(current_dir, "Data exemple.xlsx")


# =================================================================
# 2. ฟังก์ชันโหลดข้อมูล Excel
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
    st.error("❌ ไม่สามารถเปิดไฟล์ 'Data exemple.xlsx' ได้")
    st.stop()


# =================================================================
# 3. ส่วนสร้าง FILTERS ทั้ง 7 ตัวตามจริง
# =================================================================
st.title("📊 ระบบสรุปตรวจเช็คร้านค้าเช่า")
st.write("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    branch_options = ['ทั้งหมด'] + sorted(list(df_raw['สาขา'].unique())) if 'สาขา' in df_raw.columns else ['ทั้งหมด']
    selected_branch = st.selectbox("เลือกสาขา:", branch_options)
with col2:
    building_options = ['ทั้งหมด'] + sorted(list(df_raw['อาคาร'].unique())) if 'อาคาร' in df_raw.columns else ['ทั้งหมด']
    selected_building = st.selectbox("เลือกอาคาร:", building_options)
with col3:
    date_col = 'Date' if 'Date' in df_raw.columns else ('วันที่ตรวจ' if 'วันที่ตรวจ' in df_raw.columns else '')
    date_options = ['ทั้งหมด'] + sorted(list(df_raw[date_col].unique())) if date_col else ['ทั้งหมด']
    selected_date = st.selectbox("วันที่ตรวจ:", date_options)
with col4:
    inspector_options = ['ทั้งหมด'] + sorted(list(df_raw['ชื่อผู้ตรวจ'].unique())) if 'ชื่อผู้ตรวจ' in df_raw.columns else ['ทั้งหมด']
    selected_inspector = st.selectbox("ชื่อผู้ตรวจ:", inspector_options)

col5, col6, col7, col_empty = st.columns(4)
with col5:
    task_group_options = ['ทั้งหมด'] + sorted(list(df_raw['Task (group)'].unique())) if 'Task (group)' in df_raw.columns else ['ทั้งหมด']
    selected_task_group = st.selectbox("Task (group):", task_group_options)
with col6:
    task_col = 'Task Detail' if 'Task Detail' in df_raw.columns else ('Task' if 'Task' in df_raw.columns else '')
    task_options = ['ทั้งหมด'] + sorted(list(df_raw[task_col].unique())) if task_col else ['ทั้งหมด']
    selected_task = st.selectbox("Task:", task_options)
with col7:
    status_options = ['ทั้งหมด'] + sorted(list(df_raw['Status'].unique())) if 'Status' in df_raw.columns else ['ทั้งหมด']
    selected_status = st.selectbox("Status (สถานะ):", status_options)


# =================================================================
# 4. กลไกการ Filter ข้อมูลตาม Data จริง (แก้ไขจุดบั๊กตัวแปรเรียบร้อย)
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
    df_filtered = df_filtered[df_filtered[task_col] == selected_task]  # แก้งานตรงนี้ให้ดึงจากคอลัมน์จริงแล้ว
if selected_status != 'ทั้งหมด': 
    df_filtered = df_filtered[df_filtered['Status'] == selected_status]

total_records = len(df_filtered)


# =================================================================
# 5. ส่วนแสดงผลยอดสรุป (KPI Cards)
# =================================================================
st.write("")
unique_buildings = df_filtered['อาคาร'].nunique() if total_records > 0 else 0
unique_rooms = df_filtered['หมายเลขห้อง'].nunique() if total_records > 0 else 0

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.markdown(f'<div class="kpi-card"><p class="kpi-title">🏢 ความครอบคลุมในการดูแล</p><p class="kpi-value">{unique_buildings} อาคาร / {unique_rooms} ห้อง</p></div>', unsafe_allow_html=True)
with col_m2:
    st.markdown(f'<div class="kpi-card"><p class="kpi-title">📝 จำนวนรายการตรวจเช็คตามตัวกรอง</p><p class="kpi-value" style="color: #008080;">{total_records} รายการ</p></div>', unsafe_allow_html=True)
with col_m3:
    complete_count = len(df_filtered[df_filtered['Status'].str.lower() == 'complete'])
    st.markdown(f'<div class="kpi-card"><p class="kpi-title">✅ Status ผ่าน (Complete)</p><p class="kpi-value" style="color: #2E7D32;">{complete_count} รายการ</p></div>', unsafe_allow_html=True)


# =================================================================
# 6. ส่วนเรนเดอร์กราฟวงกลมสรุปสัดส่วน (Donut Chart)
# =================================================================
st.write("")
if total_records > 0:
    st.subheader("🎯 สัดส่วนสถานะการตรวจเช็ค (Status)")
    status_counts = df_filtered['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'จำนวน']
    fig = px.pie(status_counts, values='จำนวน', names='Status', hole=0.4,
                 color_discrete_sequence=['#2E7D32', '#C62828', '#1565C0', '#EF6C00'])
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
    st.plotly_chart(fig, use_container_width=True)


# =================================================================
# 7. สร้างตาราง HTML หน้าตาเหมือนตัวอย่าง (ดึงข้อมูล Dynamic จาก Python)
# =================================================================
st.write("")
st.subheader("📋 รายละเอียดบันทึกข้อมูลการตรวจเช็ค (หน้าตาตามสไตล์ HTML)")

if total_records > 0:
    html_table = """
    <div class="custom-table-container">
        <table class="custom-dashboard-table">
            <thead>
                <tr>
                    <th>สาขา</th>
                    <th>อาคาร</th>
                    <th>หมายเลขห้อง</th>
                    <th>วันที่ตรวจ</th>
                    <th>หมวดหมู่งาน</th>
                    <th>Task Detail</th>
                    <th>ชื่อผู้ตรวจ</th>
                    <th>Reason / ความผิดปกติ</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for _, row in df_filtered.iterrows():
        status_raw = str(row.get('Status', '')).strip()
        status_lower = status_raw.lower()
        
        if 'complete' in status_lower:
            status_html = f'<span class="status-badge status-complete">{status_raw}</span>'
        elif 'pending' in status_lower or 'wait' in status_lower:
            status_html = f'<span class="status-badge status-pending">{status_raw}</span>'
        else:
            status_html = f'<span class="status-badge status-error">{status_raw}</span>'
            
        html_table += f"""
                <tr>
                    <td>{row.get('สาขา', '-')}</td>
                    <td>{row.get('อาคาร', '-')}</td>
                    <td>{row.get('หมายเลขห้อง', '-')}</td>
                    <td>{row.get('Date', '-')}</td>
                    <td>{row.get('Task (group)', '-')}</td>
                    <td>{row.get('Task Detail', row.get('Task', '-'))}</td>
                    <td>{row.get('ชื่อผู้ตรวจ', '-')}</td>
                    <td>{row.get('Reason', 'ปกติ')}</td>
                    <td>{status_html}</td>
                </tr>
        """
        
    html_table += """
            </tbody>
        </table>
    </div>
    """
    st.markdown(html_table, unsafe_allow_html=True)
else:
    st.info("💡 ไม่มีข้อมูลแสดงผลตามเงื่อนไขตัวกรอง")
