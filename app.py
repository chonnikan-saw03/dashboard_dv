import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเพจและตกแต่งความสวยงาม (CSS)
st.set_page_config(page_title="Dashboard สรุปตรวจเช็คร้านค้า", layout="wide", initial_sidebar_state="expanded")

# แทรกโค้ด CSS เพื่อเนรมิตกล่อง KPI และพื้นหลังให้สวยงาม
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 4px 12px rgba(0,0,0,0.05);
        text-align: center;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-weight: bold;
        color: #495057;
        justify-content: center;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        color: #212529;
    }
</style>
""", unsafe_allow_html=True)

# 2. ฟังก์ชันโหลดข้อมูล
@st.cache_data
def load_data():
    df = pd.read_excel("Data exemple.xlsx", sheet_name="Sheet1")
    df['Reason'] = df['Reason'].fillna('ปกติ')
    return df

df = load_data()

# 3. ส่วนตัวกรองข้อมูล (Sidebar)
st.sidebar.markdown("### 🔍 ตัวกรองข้อมูล (Filters)")

def create_filter(column_name, title):
    options = ["(All)"] + list(df[column_name].dropna().unique())
    return st.sidebar.selectbox(title, options)

selected_branch = create_filter('สาขา', 'สาขา')
selected_building = create_filter('อาคาร', 'อาคาร')
selected_room = create_filter('หมายเลขห้อง', 'หมายเลขห้อง')
selected_status = create_filter('Status', 'Status (ผ่าน/ไม่ผ่าน)')

filtered_df = df.copy()
if selected_branch != "(All)":
    filtered_df = filtered_df[filtered_df['สาขา'] == selected_branch]
if selected_building != "(All)":
    filtered_df = filtered_df[filtered_df['อาคาร'] == selected_building]
if selected_room != "(All)":
    filtered_df = filtered_df[filtered_df['หมายเลขห้อง'] == selected_room]
if selected_status != "(All)":
    filtered_df = filtered_df[filtered_df['Status'] == selected_status]

# 4. ส่วนหัวและกล่องสรุปตัวเลข (KPI Cards)
st.markdown("<h2 style='text-align: center; color: #343a40; margin-bottom: 30px;'>📊 สรุปตรวจเช็คร้านค้าเช่า</h2>", unsafe_allow_html=True)

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

st.markdown("<br>", unsafe_allow_html=True)

# 5. ส่วนกราฟแสดงผล (Charts) แบบ Clean Design
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("<h4 style='color: #495057;'>% Status การตรวจเช็ค</h4>", unsafe_allow_html=True)
    if not filtered_df.empty:
        status_counts = filtered_df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        fig_pie = px.pie(status_counts, values='Count', names='Status', hole=0.6,
                         color='Status', 
                         color_discrete_map={'ตรวจเช็คผ่าน': '#28a745', 'ตรวจเช็คไม่ผ่าน': '#dc3545', 'ไม่ระบุ': '#6c757d'})
        
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("ไม่มีข้อมูลสำหรับแสดงกราฟ")

with chart_col2:
    st.markdown("<h4 style='color: #495057;'>จำนวนห้องที่ตรวจแยกตามสาขา</h4>", unsafe_allow_html=True)
    if not filtered_df.empty:
        branch_counts = filtered_df.groupby('สาขา')['หมายเลขห้อง'].nunique().reset_index()
        branch_counts.columns = ['สาขา', 'จำนวนห้อง']
        
        fig_bar = px.bar(branch_counts, x='จำนวนห้อง', y='สาขา', orientation='h', 
                         text='จำนวนห้อง', color_discrete_sequence=['#5D8AA8'])
        
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, visible=False), 
            yaxis=dict(showgrid=False, title=""),      
            margin=dict(l=0, r=0, t=10, b=0)
        )
        fig_bar.update_traces(textposition='outside')
        
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("ไม่มีข้อมูลสำหรับแสดงกราฟ")

st.markdown("<br>", unsafe_allow_html=True)

# 6. ส่วนตารางรายละเอียด (Data Table)
st.markdown("<h4 style='color: #495057;'>📄 รายละเอียดการตรวจเช็ค (Detail)</h4>", unsafe_allow_html=True)

columns_to_show = ['สาขา', 'หมายเลขห้อง', 'Date', 'Task', 'ชื่อผู้ตรวจ', 'Reason', 'Status']

if not filtered_df.empty:
    display_df = filtered_df[columns_to_show].copy()
    if 'Date' in display_df.columns:
        display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%d-%m-%Y')
        
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไขตัวกรอง")
