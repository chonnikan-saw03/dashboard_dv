import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเพจและธีมดีไซน์สุดหรู (Advanced CSS)
st.set_page_config(page_title="KPI Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* พื้นหลังแบบ Soft Gray ผ่อนคลายสายตา */
    .stApp {
        background-color: #f4f6f9;
    }
    
    /* กล่อง KPI ดีไซน์หรูหรา มีขอบเงาจางๆ และแทบสีด้านซ้าย */
    .kpi-card {
        background-color: #ffffff;
        border-left: 5px solid #1E3A8A; /* เส้นสีน้ำเงินกรมท่าด้านข้าง */
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02), 0 1px 3px rgba(0, 0, 0, 0.08);
        margin-bottom: 15px;
    }
    .kpi-title {
        font-size: 14px;
        font-weight: 600;
        color: #6B7280;
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 700;
        color: #111827;
    }
    
    /* ตกแต่งตารางให้ดูสะอาดตา */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
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

# 3. ส่วนตัวกรองข้อมูล (Sidebar ดีไซน์เรียบหรู)
st.sidebar.markdown("<h2 style='color: #1E3A8A; font-size: 22px;'>🔍 ค้นหา & ตัวกรอง</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

def create_filter(column_name, title):
    options = ["ทั้งหมด (All)"] + list(df[column_name].dropna().unique())
    return st.sidebar.selectbox(title, options)

selected_branch = create_filter('สาขา', '🏢 เลือกสาขา')
selected_building = create_filter('อาคาร', '🏬 เลือกอาคาร')
selected_room = create_filter('หมายเลขห้อง', '🔑 หมายเลขห้อง')
selected_status = create_filter('Status', '📊 สถานะการตรวจ')

# กรองข้อมูล
filtered_df = df.copy()
if selected_branch != "ทั้งหมด (All)":
    filtered_df = filtered_df[filtered_df['สาขา'] == selected_branch]
if selected_building != "ทั้งหมด (All)":
    filtered_df = filtered_df[filtered_df['อาคาร'] == selected_building]
if selected_room != "ทั้งหมด (All)":
    filtered_df = filtered_df[filtered_df['หมายเลขห้อง'] == selected_room]
if selected_status != "ทั้งหมด (All)":
    filtered_df = filtered_df[filtered_df['Status'] == selected_status]

# 4. ส่วนหัวข้อเว็บบอร์ด (Header)
st.markdown("<h1 style='text-align: left; color: #1E3A8A; font-weight: 800; margin-bottom: 5px;'>📊 Executive KPI Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #6B7280; font-size: 14px; margin-bottom: 30px;'>ระบบรายงานและสรุปผลการตรวจเช็คร้านค้าเช่าเรียลไทม์</p>", unsafe_allow_html=True)

# 5. จัด Layout แบบอัปเกรด: แบ่งฝั่งซ้าย (KPI) และฝั่งขวา (Graphs)
main_col1, main_col2 = st.columns([1, 3]) # ฝั่งขวากว้างกว่าเพื่อโชว์กราฟเต็มๆ

with main_col1:
    st.markdown("<h4 style='color: #1E3A8A; font-size: 16px; font-weight:700;'>Overview</h4>", unsafe_allow_html=True)
    
    # คำนวณตัวเลข
    total_buildings = filtered_df['อาคาร'].nunique()
    total_rooms = filtered_df['หมายเลขห้อง'].nunique()
    passed = len(filtered_df[filtered_df['Status'] == 'ตรวจเช็คผ่าน'])
    failed = len(filtered_df[filtered_df['Status'] == 'ตรวจเช็คไม่ผ่าน'])
    total_tasks = len(filtered_df)
    
    # พ่นกล่อง KPI สไตล์ Custom HTML
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🏢 อาคาร / ห้องทั้งหมด</div>
        <div class="kpi-value">{total_buildings} / {total_rooms}</div>
    </div>
    <div class="kpi-card" style="border-left-color: #10B981;">
        <div class="kpi-title">✅ ตรวจเช็คผ่าน</div>
        <div class="kpi-value" style="color: #10B981;">{passed} <span style="font-size:14px; font-weight:normal; color:#6B7280;">Tasks</span></div>
    </div>
    <div class="kpi-card" style="border-left-color: #EF4444;">
        <div class="kpi-title">❌ ตรวจเช็คไม่ผ่าน</div>
        <div class="kpi-value" style="color: #EF4444;">{failed} <span style="font-size:14px; font-weight:normal; color:#6B7280;">Tasks</span></div>
    </div>
    <div class="kpi-card" style="border-left-color: #6B7280;">
        <div class="kpi-title">📋 Task ทั้งหมด</div>
        <div class="kpi-value">{total_tasks}</div>
    </div>
    """, unsafe_allow_html=True)

with main_col2:
    # แบ่งพื้นที่กราฟเป็น 2 คอลุมน์ย่อยด้านขวา
    sub_chart_col1, sub_chart_col2 = st.columns(2)
    
    with sub_chart_col1:
        st.markdown("<h4 style='color: #1E3A8A; font-size: 16px; font-weight:700;'>สัดส่วนสถานะการตรวจเช็ค</h4>", unsafe_allow_html=True)
        if not filtered_df.empty:
            status_counts = filtered_df['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            fig_pie = px.pie(status_counts, values='Count', names='Status', hole=0.6,
                             color='Status', 
                             color_discrete_map={'ตรวจเช็คผ่าน': '#10B981', 'ตรวจเช็คไม่ผ่าน': '#EF4444', 'ไม่ระบุ': '#9CA3AF'})
            
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("ไม่มีข้อมูล")

    with sub_chart_col2:
        st.markdown("<h4 style='color: #1E3A8A; font-size: 16px; font-weight:700;'>จำนวนห้องที่ตรวจแยกตามสาขา</h4>", unsafe_allow_html=True)
        if not filtered_df.empty:
            branch_counts = filtered_df.groupby('สาขา')['หมายเลขห้อง'].nunique().reset_index()
            branch_counts.columns = ['สาขา', 'จำนวนห้อง']
            
            # ใช้สีโทน Corporate Soft Blue
            fig_bar = px.bar(branch_counts, x='จำนวนห้อง', y='สาขา', orientation='h', 
                             text='จำนวนห้อง', color_discrete_sequence=['#3B82F6'])
            
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, visible=False), 
                yaxis=dict(showgrid=False, title=""),      
                margin=dict(l=10, r=10, t=10, b=10)
            )
            fig_bar.update_traces(textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("ไม่มีข้อมูล")

st.markdown("---")

# 6. ส่วนตารางรายละเอียดด้านล่างสุด (Full Width)
st.markdown("<h4 style='color: #1E3A8A; font-size: 18px; font-weight:700; margin-bottom:15px;'>📄 รายละเอียดการบันทึกข้อมูลทั้งหมด</h4>", unsafe_allow_html=True)

columns_to_show = ['สาขา', 'หมายเลขห้อง', 'Date', 'Task', 'ชื่อผู้ตรวจ', 'Reason', 'Status']

if not filtered_df.empty:
    display_df = filtered_df[columns_to_show].copy()
    if 'Date' in display_df.columns:
        display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%d-%m-%Y')
        
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไข")
