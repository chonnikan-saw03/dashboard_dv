import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้าเพจให้เป็นแบบกว้าง (Wide Layout) เหมือนต้นฉบับ
st.set_page_config(page_title="Dashboard สรุปตรวจเช็คร้านค้า", layout="wide")

# ---------------------------------------------------------
# 1. ฟังก์ชันโหลดข้อมูล (ใช้ @st.cache_data เพื่อให้โหลดเร็วขึ้น)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    # เปลี่ยนชื่อไฟล์ให้ตรงกับของคุณหากจำเป็น
    df = pd.read_excel("Data exemple.xlsx", sheet_name="Sheet1")
    # เติมค่าว่างในคอลัมน์ Reason ให้เป็น 'ปกติ' เพื่อให้แสดงผลสวยงาม
    df['Reason'] = df['Reason'].fillna('ปกติ')
    return df

df = load_data()

# ---------------------------------------------------------
# 2. ส่วนตัวกรองข้อมูล (Sidebar) ด้านขวามือ
# ---------------------------------------------------------
st.sidebar.header("ตัวกรองข้อมูล (Filters)")

# สร้าง Dropdown สำหรับกรอง (เพิ่มตัวเลือก "(All)" เข้าไป)
def create_filter(column_name, title):
    options = ["(All)"] + list(df[column_name].dropna().unique())
    return st.sidebar.selectbox(title, options)

selected_branch = create_filter('สาขา', 'สาขา')
selected_building = create_filter('อาคาร', 'อาคาร')
selected_room = create_filter('หมายเลขห้อง', 'หมายเลขห้อง')
selected_status = create_filter('Status', 'Status')

# นำเงื่อนไขมากรองข้อมูลใน DataFrame
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
# 3. ส่วนหัวและ KPI (ด้านบน)
# ---------------------------------------------------------
st.markdown("<h2 style='text-align: center;'>สรุปตรวจเช็คร้านค้าเช่า</h2>", unsafe_allow_html=True)
st.markdown("---")

# แบ่งหน้าจอเป็น 3 คอลัมน์สำหรับ KPI
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

with kpi_col1:
    total_buildings = filtered_df['อาคาร'].nunique()
    total_rooms = filtered_df['หมายเลขห้อง'].nunique()
    st.info(f"**จำนวนอาคาร / จำนวนห้อง**\n\n### {total_buildings} อาคาร / {total_rooms} ห้อง")

with kpi_col2:
    # นับจำนวนสถานะ
    passed = len(filtered_df[filtered_df['Status'] == 'ตรวจเช็คผ่าน'])
    failed = len(filtered_df[filtered_df['Status'] == 'ตรวจเช็คไม่ผ่าน'])
    other = len(filtered_df) - (passed + failed)
    st.warning(f"**Status (จำนวน Task)**\n\n✅ ผ่าน: **{passed}** | ❌ ไม่ผ่าน: **{failed}** | ⚪ Other: **{other}**")

with kpi_col3:
    st.success(f"**จำนวน Task ทั้งหมดที่ตรวจเช็ค**\n\n### {len(filtered_df)} Task")

st.markdown("---")

# ---------------------------------------------------------
# 4. ส่วนกราฟ (Charts)
# ---------------------------------------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### % Status")
    # สร้างกราฟโดนัทด้วย Plotly
    if not filtered_df.empty:
        status_counts = filtered_df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig_pie = px.pie(status_counts, values='Count', names='Status', hole=0.5, 
                         color='Status', color_discrete_map={'ตรวจเช็คผ่าน': 'green', 'ตรวจเช็คไม่ผ่าน': 'red', 'ไม่ระบุ': 'gray'})
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.write("ไม่มีข้อมูลสำหรับแสดงกราฟ")

with chart_col2:
    st.markdown("#### จำนวนห้องที่ตรวจแยกตามสาขา")
    # สร้างกราฟแท่ง
    if not filtered_df.empty:
        branch_counts = filtered_df.groupby('สาขา')['หมายเลขห้อง'].nunique().reset_index()
        branch_counts.columns = ['สาขา', 'จำนวนห้อง']
        fig_bar = px.bar(branch_counts, x='จำนวนห้อง', y='สาขา', orientation='h', 
                         text='จำนวนห้อง', color_discrete_sequence=['#5D8AA8'])
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.write("ไม่มีข้อมูลสำหรับแสดงกราฟ")

st.markdown("---")

# ---------------------------------------------------------
# 5. ส่วนตารางรายละเอียด (Data Table)
# ---------------------------------------------------------
st.markdown("### Detail")

# เลือกเฉพาะคอลัมน์ที่ต้องการแสดงในตารางให้ดูสะอาดตา
columns_to_show = ['สาขา', 'หมายเลขห้อง', 'Date', 'Task', 'ชื่อผู้ตรวจ', 'Reason', 'Status']
display_df = filtered_df[columns_to_show]

# แสดงผลตาราง (สามารถปรับขนาดความกว้างได้เต็มจอ)
st.dataframe(display_df, use_container_width=True, hide_index=True)