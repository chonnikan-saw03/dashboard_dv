import streamlit as st
import pandas as pd
import numpy as np

# 1. ตั้งค่าหน้าเพจให้เต็มจอ
st.set_page_config(page_title="สรุปตรวจเช็คร้านค้าเช่า", layout="wide", initial_sidebar_state="collapsed")

# ซ่อนพวกเมนูส่วนเกินของ Streamlit ออกไป
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div.block-container {padding-top: 2rem;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# 2. ฟังก์ชันอ่านไฟล์ Excel (ดึงมาทุกบรรทัดชัวร์ๆ)
@st.cache_data
def load_data():
    # บังคับให้อ่านเป็นตัวหนังสือ (String) ทุกช่อง ป้องกันข้อมูลเพี้ยนหรือตกหล่น
    df = pd.read_excel("Data exemple.xlsx", sheet_name="Sheet1", dtype=str)
    df = df.fillna('') # อุดรอยรั่วช่องว่าง
    if 'Reason' in df.columns:
        df['Reason'] = df['Reason'].replace('', 'ปกติ')
    return df

df_raw = load_data()


# ==========================================
# 3. ส่วนสร้าง FILTER ด้านบนของ Dashboard
# ==========================================
st.title("📊 แดชบอร์ดสรุปตรวจเช็คร้านค้าเช่า")

# สร้างกล่อง Filter เรียงกัน 3 กล่องในแถวเดียว (สาขา, อาคาร, สถานะ)
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    # ดึงรายชื่อสาขาทั้งหมดที่มีใน Excel ออกมาทำตัวเลือก (บวกคำว่า 'ทั้งหมด' เข้าไป)
    branch_options = ['ทั้งหมด'] + sorted(list(df_raw['สาขา'].unique()))
    selected_branch = st.selectbox("เลือกสาขา:", branch_options)

with col_f2:
    building_options = ['ทั้งหมด'] + sorted(list(df_raw['อาคาร'].unique()))
    selected_building = st.selectbox("เลือกอาคาร:", building_options)

with col_f3:
    status_options = ['ทั้งหมด'] + sorted(list(df_raw['Status'].unique()))
    selected_status = st.selectbox("เลือกสถานะ:", status_options)


# ==========================================
# 4. ส่วนเชื่อมโยงข้อมูล (สั่งให้ Filter ทำงาน)
# ==========================================
# เริ่มต้นจากข้อมูลดิบทั้งหมด
df_filtered = df_raw.copy()

# ถ้าคนใช้งานเลือกสาขา เจาะจง (ไม่ใช่ 'ทั้งหมด') -> ให้กรองเอาเฉพาะสาขานั้น
if selected_branch != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['สาขา'] == selected_branch]

# ถ้าคนใช้งานเลือกอาคาร เจาะจง -> ให้กรองต่อจากสาขาเมื่อกี้
if selected_building != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['อาคาร'] == selected_building]

# ถ้าคนใช้งานเลือกสถานะ เจาะจง -> ให้กรองต่อเป็นขั้นสุดท้าย
if selected_status != 'ทั้งหมด':
    df_filtered = df_filtered[df_filtered['Status'] == selected_status]


# ==========================================
# 5. ส่วนแสดงผลบน DASHBOARD (จะเปลี่ยนตาม Filter อัตโนมัติ)
# ==========================================
st.markdown("---")

# นับจำนวนข้อมูลที่กรองออกมาได้จริงเพื่อเอาไปโชว์เป็นตัวเลขสรุป
total_inspections = len(df_filtered)
success_count = len(df_filtered[df_filtered['Status'] == 'Complete']) # สมมติว่าใช้คำว่า Complete

# แสดงตัวเลขสรุป (Metrics)
m1, m2 = st.columns(2)
with m1:
    st.metric(label="จำนวนรายการที่ตรวจทั้งหมด (ตาม Filter)", value=f"{total_inspections} รายการ")
with m2:
    st.metric(label="ตรวจเสร็จสิ้นแล้ว", value=f"{success_count} รายการ")

st.markdown("### 📋 ตารางข้อมูลตรวจเช็คที่ผ่านการกรองแล้ว")
# แสดงตารางข้อมูลจริงที่แปรผันตามการกด Filter ของผู้ใช้งาน
st.dataframe(df_filtered, use_container_width=True)
