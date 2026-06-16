import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =================================================================
# 1. ตั้งค่าหน้าเพจให้เต็มจอ (Wide Layout) และตกแต่ง CSS
# =================================================================
st.set_page_config(page_title="สรุปตรวจเช็คร้านค้าเช่า", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* ปรับแต่งกล่อง KPI สรุปตัวเลขให้คล้ายของเดิม */
    .kpi-card {
        background-color: #FFF9E6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #F3E5AB;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .kpi-title { margin: 0; color: #666666; font-size: 16px; }
    .kpi-value { margin: 5px 0 0 0; color: #B8860B; font-size: 28px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ค้นหาตำแหน่งไฟล์ Excel ในโฟลเดอร์โปรเจกต์
current_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(current_dir, "Data exemple.xlsx")


# =================================================================
# 2. ฟังก์ชันอ่านข้อมูลจาก Excel
# =================================================================
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        # อ่านข้อมูลและจัดการค่าว่าง
        df = pd.read_excel(file_path, sheet_name="Sheet1", dtype=str)
        df = df.fillna('')
        if 'Reason' in df.columns:
            df['Reason'] = df['Reason'].replace('', 'ปกติ')
        return df
    except Exception as e:
        return None

df_raw = load_data(excel_path)

# ตรวจสอบว่าไฟล์พร้อมใช้งานไหม
if df_raw is None or df_raw.empty:
    st.error("❌ ไม่สามารถเปิดไฟล์ 'Data exemple.xlsx' ได้ กรุณาตรวจสอบการอัปโหลดไฟล์")
    st.stop()


# =================================================================
# 3. ส่วนของตัวกรองข้อมูล (FILTERS ด้านบน)
# =================================================================
st.title("📊 ระบบสรุปตรวจเช็คร้านค้าเช่า (แดชบอร์ดจริง)")

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
# 4. ประมวลผลกรองข้อมูลตามเงื่อนไขจริง
# =================================================================
df_filtered = df_raw.copy()

if selected_branch != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['สาขา'] == selected_branch]

if selected_building != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['อาคาร'] == selected_building]

if selected_status != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['Status'] == selected_status]


# =================================================================
# 5. แสดงผลยอดสรุป (KPI Cards แบบในรูปตัวอย่าง)
# =================================================================
total_inspections = len(df_filtered)
unique_buildings = df_filtered['อาคาร'].nunique() if total_inspections > 0 else 0
unique_rooms = df_filtered['หมายเลขห้อง'].nunique() if total_inspections > 0 else 0

st.write("") # เว้นช่องไฟ
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
        <p class="kpi-title">📝 จำนวนรายการตรวจเช็คทั้งหมด</p>
        <p class="kpi-value" style="color: #008080;">{total_inspections} รายการ</p>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    # นับจำนวนสถานะตรวจเสร็จ (Complete) ปรับตามตัวเล็ก/ใหญ่
    complete_count = len(df_filtered[df_filtered['Status'].str.lower() == 'complete'])
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-title">✅ สถานะตรวจเช็คผ่าน (Complete)</p>
        <p class="kpi-value" style="color: #2E7D32;">{complete_count} รายการ</p>
    </div>
    """, unsafe_allow_html=True)


# =================================================================
# 6. สร้างส่วนแสดงกราฟวงกลม (Pie Chart) ถอดแบบมาจากตัวอย่าง HTML
# =================================================================
st.write("")
st.write("")

if total_inspections > 0:
    st.subheader("🎯 สัดส่วนสถานะการตรวจเช็ค (Status)")
    
    # คำนวณนับกลุ่ม Status
    status_counts = df_filtered['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'จำนวน']
    
    # สร้างกราฟวงกลมด้วย Plotly Express (สวยงาม ขยับแบบอินเตอร์แอกทีฟได้)
    fig = px.pie(
        status_counts, 
        values='จำนวน', 
        names='Status',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4 # ทำเป็น Donut Chart เหมือนในตัวอย่าง HTML
    )
    
    fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=400)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("💡 ไม่มีข้อมูลตามเงื่อนไขที่เลือก")


# =================================================================
# 7. แสดงตารางข้อมูลรายละเอียด (Data Table ด้านล่างสุด)
# =================================================================
st.write("")
st.subheader("📋 ตารางบันทึกข้อมูลการตรวจเช็คตามจริง")

# จัดระเบียบชื่อคอลัมน์ให้แสดงผลอ่านง่ายภาษาไทย
df_display = df_filtered.copy()
rename_cols = {
    'สาขา': 'สาขา', 'อาคาร': 'อาคาร', 'หมายเลขห้อง': 'หมายเลขห้อง',
    'Date': 'วันที่', 'Task (group)': 'หมวดหมู่งาน', 'ชื่อผู้ตรวจ': 'ผู้ตรวจ',
    'Reason': 'เหตุผล/ความผิดปกติ', 'Status': 'สถานะ'
}

# แสดงเฉพาะคอลัมน์สำคัญที่ต้องการโชว์ในตาราง
available_cols = [c for c in rename_cols.keys() if c in df_display.columns]
df_display = df_display[available_cols].rename(columns=rename_cols)

# เรนเดอร์ตารางบนหน้าเว็บ ให้ผู้ใช้สามารถกดค้นหาหรือกดกรองเพิ่มในตารางได้เอง
st.dataframe(df_display, use_container_width=True, hide_index=True)
