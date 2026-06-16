import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

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
    /* สีหัวตาราง (ปรับเป็นสีโทนเดียวกับแดชบอร์ด HTML ของพี่ได้เลย) */
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
    /* ไฮไลท์สีสลับแถว */
    .custom-dashboard-table tr:nth-child(even) {
        background-color: #fdfdfd;
    }
    .custom-dashboard-table tr:hover {
        background-color: #f1f3f5;
    }
    /* ตกแต่งปุ่มหรือ Badge สถานะ */
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
# 4. กลไกการ Filter ข้อมูลตาม Data จริง
# =================================================================
df_filtered = df_raw.copy()

if selected_branch != 'ทั้งหมด': df_filtered = df_filtered[df_filtered['สาขา'] == selected_branch]
if selected_building != 'ทั้งหมด': df_filtered = df_filtered[df_filtered['อาคาร'] == selected_building]
if date_col and selected_date != '
