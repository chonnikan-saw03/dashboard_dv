import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเพจแบบ Wide Screen และใส่ CSS สไตล์เดียวกับ HTML ของคุณ
st.set_page_config(page_title="สรุปตรวจเช็คร้านค้าเช่า - Dashboard Overview", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* ใช้ฟอนต์ Sarabun แหล่งเดียวกับ HTML */
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Sarabun', sans-serif;
        background-color: #f1f5f9;
    }
    
    /* ตกแต่งแถบ Header ด้านบนสุดตามแบบ HTML */
    .top-header {
        background-color: #1e4666;
        color: white;
        padding: 8px 16px;
        font-size: 12px;
        border-bottom: 1px solid #1e3a5f;
        margin: -4rem -5rem 2rem -5rem; /* ดันให้เต็มขอบจอ Streamlit */
    }
    
    /* กล่องแบนเนอร์ชื่อดีไซน์คลาสสิก */
    .title-banner {
        background-color: rgba(245, 230, 211, 0.6);
        border: 1px solid #e6d0b5;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        margin-bottom: 20px;
    }
    .title-banner h1 {
        color: #5c4028;
        font-size: 20px;
        font-weight: 700;
        margin: 0;
    }

    /* ตกแต่งกล่องสรุปภาพรวม (Metrics) */
    .metric-card-top {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        overflow: hidden;
        margin-bottom: 15px;
    }
    .metric-header {
        color: white;
        font-size: 13px;
        font-weight: 500;
        text-align: center;
        padding: 8px;
    }
</style>
""", unsafe_allow_html=True)

# แปะแถบเมนูด้านบนให้ดูพรีเมียมเหมือนต้นฉบับ HTML
st.markdown("""
<div class="top-header">
    Explore / 1000 BTCL / Asset / <b>Report ตรวจเช็คร้านค้าเช่า</b> 
    <span style="background-color: rgba(30,144,255,0.4); color: #cffafe; padding: 2px 6px; border-radius: 4px; margin-left: 10px; font-weight: bold;">OVERVIEW</span>
</div>
""", unsafe_allow_html=True)

# 2. ฟังก์ชันโหลดข้อมูลจาก Excel
@st.cache_data
def load_data():
    df = pd.read_excel("Data exemple.xlsx", sheet_name="Sheet1")
    # เติมค่าว่างในคอลัมน์ Reason ให้เป็น 'ปกติ'
    if 'Reason' in df.columns:
        df['Reason'] = df['Reason'].fillna('ปกติ')
    return df

df = load_data()

# 3. ส่วนแถบตัวกรองด้านขวา (แปลงจาก Sidebar ใน HTML)
st.sidebar.markdown("<h3 style='color: #1e4666; font-size: 16px; font-weight: 700;'>🔍 ตัวกรองรายงาน (Filters)</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")

def create_filter(column_name, title):
    if column_name in df.columns:
        options = ["(All)"] + list(df[column_name].dropna().unique())
        return st.sidebar.selectbox(title, options)
    return "(All)"

selected_month = create_filter('Month of วันที่ตรวจ', 'Month of วันที่ตรวจ') # เพิ่มตามไอเดียใน HTML
selected_branch = create_filter('สาขา', 'สาขา')
selected_building = create_filter('อาคาร', 'อาคาร')
selected_room = create_filter('หมายเลขห้อง', 'หมายเลขห้อง')
selected_taskgroup = create_filter('Task (group)', 'Task (group)')
selected_status = create_filter('Status', 'Status (gr.)')
selected_inspector = create_filter('ชื่อผู้ตรวจ', 'ชื่อผู้ตรวจ*')

# จัดการกรองข้อมูลแบบ Dynamic ตามที่เลือก
filtered_df = df.copy()
if selected_branch != "(All)": filtered_df = filtered_df[filtered_df['สาขา'] == selected_branch]
if selected_building != "(All)": filtered_df = filtered_df[filtered_df['อาคาร'] == selected_building]
if selected_room != "(All)": filtered_df = filtered_df[filtered_df['หมายเลขห้อง'] == selected_room]
if selected_status != "(All)": filtered_df = filtered_df[filtered_df['Status'] == selected_status]
if selected_inspector != "(All)": filtered_df = filtered_df[filtered_df['ชื่อผู้ตรวจ'] == selected_inspector]

# 4. ป้ายชื่อแดชบอร์ดกลางหน้าจอ
st.markdown("""
<div class="title-banner">
    <h1>สรุปตรวจเช็คร้านค้าเช่า</h1>
</div>
""", unsafe_allow_html=True)

# 5. การจัดสรรกล่องข้อมูลและกราฟ (แบ่งเป็น 3 คอลัมน์หลักเหมือนตัวอย่าง)
col_left, col_mid, col_right = st.columns(3)

# --- คอลัมน์ที่ 1: จำนวนอาคาร / จำนวนห้อง ---
with col_left:
    st.markdown('<div class="metric-card-top"><div class="metric-header" style="background-color: #3b82f6;">จำนวนอาคาร / จำนวนห้อง</div></div>', unsafe_allow_html=True)
    total_buildings = filtered_df['อาคาร'].nunique() if 'อาคาร' in filtered_df.columns else 0
    total_rooms = filtered_df['หมายเลขห้อง'].nunique() if 'หมายเลขห้อง' in filtered_df.columns else 0
    
    st.metric(label="ความครอบคลุมในการดูแล", value=f"{total_buildings} อาคาร / {total_rooms} ห้อง")
    
    # กราฟแท่งแสดงจำนวนห้องและอาคารแยกตามสาขา
    st.markdown("<p style='font-size:11px; font-weight:bold; color:#64748b; text-align:center;'>จำนวนอาคาร / จำนวนห้อง by สาขา</p>", unsafe_allow_html=True)
    if not filtered_df.empty and 'สาขา' in filtered_df.columns:
        branch_data = filtered_df.groupby('สาขา')['หมายเลขห้อง'].nunique().reset_index()
        fig_branch = px.bar(branch_data, x='หมายเลขห้อง', y='สาขา', orientation='h', color_discrete_sequence=['#93c5fd'])
        fig_branch.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), margin=dict(l=10, r=10, t=10, b=10), height=180)
        st.plotly_chart(fig_branch, use_container_width=True, config={'displayModeBar': False})

# --- คอลัมน์ที่ 2: Status Overview (คำนวณจากไฟล์ข้อมูลจริง) ---
with col_mid:
    st.markdown('<div class="metric-card-top"><div class="metric-header" style="background-color: #f3a659;">Status Overview</div></div>', unsafe_allow_html=True)
    
    # คำนวณยอด Task ตามแต่ละสถานะ
    passed_tasks = len(filtered_df[filtered_df['Status'] == 'ตรวจเช็คผ่าน'])
    failed_tasks = len(filtered_df[filtered_df['Status'] == 'ตรวจเปิดไม่ผ่าน'])
    other_tasks = len(filtered_df) - (passed_tasks + failed_tasks)
    
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("ผ่าน", f"{passed_tasks}")
    m_col2.metric("ไม่ผ่าน", f"{failed_tasks}")
    m_col3.metric("อื่นๆ", f"{other_tasks}")
    
    # กราฟวงกลม % Status
    st.markdown("<p style='font-size:11px; font-weight:bold; color:#64748b; text-align:center;'>% Status</p>", unsafe_allow_html=True)
    if not filtered_df.empty:
        status_counts = filtered_df['Status'].value_counts().reset_index()
        fig_pie = px.pie(status_counts, values='count', names='Status', hole=0.5,
                         color='Status', color_discrete_map={'ตรวจเช็คผ่าน': '#2ecc71', 'ตรวจเปิดไม่ผ่าน': '#e74c3c', 'ปกติ': '#cbd5e1'})
        fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=5, r=5, t=5, b=5), height=180, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

# --- คอลัมน์ที่ 3: Status by สาขา ---
with col_right:
    st.markdown('<div class="metric-card-top"><div class="metric-header" style="background-color: #64748b;">Status by สาขา</div></div>', unsafe_allow_html=True)
    
    # ตาราง Matrix สรุปสั้นๆ แยกสาขา
    if not filtered_df.empty and 'สาขา' in filtered_df.columns:
        matrix_df = pd.crosstab(filtered_df['สาขา'], filtered_df['Status']).reset_index()
        st.dataframe(matrix_df, use_container_width=True, hide_index=True, height=110)
    
    # กราฟแท่งสะสม % Status by สาขา
    st.markdown("<p style='font-size:11px; font-weight:bold; color:#64748b; text-align:center;'>% Status by สาขา</p>", unsafe_allow_html=True)
    if not filtered_df.empty and 'สาขา' in filtered_df.columns:
        fig_stack = px.bar(filtered_df, y='สาขา', color='Status', orientation='h',
                           color_discrete_map={'ตรวจเช็คผ่าน': '#2ecc71', 'ตรวจเปิดไม่ผ่าน': '#e74c3c'},
                           barnorm='percent')
        fig_stack.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, title=''), yaxis=dict(showgrid=False, title=''), showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=140)
        st.plotly_chart(fig_stack, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# 6. ส่วนตารางรายละเอียดด้านล่าง (Detail)
st.markdown(f"<h3 style='color: #1e4666; font-size: 16px; font-weight: 700;'>📋 Detail ข้อมูลการตรวจเช็ครายรายการ (พบ {len(filtered_df)} รายการ)</h3>", unsafe_allow_html=True)

# ดึงคอลัมน์ให้ตรงตามหัวตารางของ HTML ที่คุณออกแบบไว้
columns_to_show = ['สาขา', 'หมายเลขห้อง', 'Date', 'Task (group)', 'Task Detail', 'ชื่อผู้ตรวจ', 'Reason (group)', 'Status', 'ผู้อนุมัติ/ผู้ยืนยัน']
# ตรวจสอบว่าคอลัมน์ไหนมีอยู่ใน Excel จริง ค่อยเอามาโชว์
available_columns = [col for col in columns_to_show if col in filtered_df.columns]

if not filtered_df.empty:
    st.dataframe(filtered_df[available_columns], use_container_width=True, hide_index=True)
else:
    st.info("ไม่พบข้อมูลตามตัวเลือกตัวกรอง")
