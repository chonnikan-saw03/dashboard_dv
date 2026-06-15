import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 1. ตั้งค่าหน้าเพจและตกแต่งความสวยงาม (CSS)
# ---------------------------------------------------------
st.set_page_config(page_title="Dashboard สรุปตรวจเช็คร้านค้า", layout="wide", initial_sidebar_state="expanded")

# แทรกโค้ด CSS เพื่อเนรมิตกล่อง KPI และพื้นหลังให้สวยงาม
st.markdown("""
<style>
    /* เปลี่ยนสีพื้นหลังของเว็บให้เป็นสีเทาอ่อนๆ เพื่อให้กล่องข้อมูลดูโดดเด่น */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* ตกแต่งกล่องตัวเลข KPI (Metric) ให้เป็น Card สีขาว มีเงา และขอบโค้งมน */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 4px 12px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    /* ปรับแต่งตัวหนังสือของ Label ในกล่อง KPI */
    div[data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-weight: bold;
        color: #495057;
        justify-content: center;
    }
    
    /* ปรับแต่งตัวเลขในกล่อง KPI */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        color: #212529;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. ฟังก์ชันโหลดข้อมูล
# ---------------------------------------------------------
@st.cache_data
def load_data():
    # โหลดไฟล์ Excel (ถ้าใช้ Google Sheets สามารถเปลี่ยนเป็น pd.read_csv("ลิงก์") ได้เลย)
    df = pd.read_excel("Data exemple.xlsx", sheet_name="Sheet1")
    # เติมค่าว่างในคอลัมน์ Reason ให้เป็น 'ปกติ'
    df['Reason'] = df['Reason'].fillna('ปกติ')
    return df

df = load_data()

# ---------------------------------------------------------
# 3. ส่วนตัวกรองข้อมูล (Sidebar)
# ---------------------------------------------------------
st.sidebar.markdown("### 🔍 ตัวกรองข้อมูล (Filters)")

def create_filter(column_name, title):
    # ดึงค่าที่ไม่ซ้ำกันมาทำเป็นตัวเลือก และเพิ่ม "(All)" ไว้บนสุด
    options = ["(All)"] + list(df[column_name].dropna().unique())
    return st.sidebar.selectbox(title, options)

selected_branch = create_filter('สาขา', 'สาขา')
selected_building = create_filter('อาคาร', 'อาคาร')
selected_room = create_filter('หมายเลขห้อง', 'หมายเลขห้อง')
selected_status = create_filter('Status', 'Status (ผ่าน/ไม่ผ่าน)')

# กรองข้อมูลตามที่ผู้ใช้เลือก
filtered_df = df.copy()
if selected_branch != "(All)":
    filtered_df = filtered_df[filtered_df['สาขา'] == selected_branch]
if selected_building != "(All)":
    filtered_df = filtered_df[filtered_df['อาคาร'] == selected_building]
if selected_room != "(All)":
    filtered_df = filtered_df[filtered_df['หมายเลขห้อง'] == selected_room]
if selected_status != "(All)":
    filtered_df = filtered_df[filtered_df['Status'] == selected_status]

# ---------------------------------------------------------
# 4. ส่วนหัวและกล่องสรุปตัวเลข (KPI Cards)
# ---------------------------------------------------------
st.markdown("<h2 style='text-align: center; color: #343a40; margin-bottom: 30px;'>📊 สรุปตรวจเช็คร้านค้าเช่า</h2>", unsafe_allow_html=True)

# แบ่งหน้าจอเป็น 4 คอลัมน์สำหรับกล่อง KPI
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_buildings = filtered_df['อาคาร'].nunique()
    total_rooms = filtered_df['หมายเลขห้อง'].nunique()
    st.metric(label="จำนวนอาคาร / จำนวนห้อง", value=f"{total_buildings} อาคาร / {total_rooms} ห้อง")

with col2:
    passed = len(filtered_df[filtered_df['Status'] == 'ตรวจเช็คผ่าน'])
    st.metric(label="✅ ตรวจเช็คผ่าน", value=f"{passed} Task")

with col3:
    failed = len(filtered_df[filtered_df['Status'] == 'ตรวจเช็คไม่ผ่าน'])
    st.metric(label="❌ ตรวจเช็คไม่ผ่าน", value=f"{failed} Task")

with col4:
    total_tasks = len(filtered_df)
    st.metric(label="📋 จำนวน Task ทั้งหมด", value=f"{total_tasks} Task")

st.markdown("<br>", unsafe_allow_html=True) # เว้นบรรทัด

# ---------------------------------------------------------
# 5. ส่วนกราฟแสดงผล (Charts) แบบ Clean Design
# ---------------------------------------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("<h4 style='color: #495057;'>% Status การตรวจเช็ค</h4>", unsafe_allow_html=True)
    if not filtered_df.empty:
        status_counts = filtered_df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        # กราฟโดนัท
        fig_pie = px.pie(status_counts, values='Count', names='Status', hole=0.6,
                         color='Status', 
                         color_discrete_map={'ตรวจเช็คผ่าน': '#28a745', 'ตรวจเช็คไม่ผ่าน': '#dc3545', 'ไม่ระบุ': '#6c757d'})
        
        # ปรับพื้นหลังกราฟให้โปร่งใสและนำเส้นขอบออก
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l