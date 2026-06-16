import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os

# =================================================================
# 1. ตั้งค่าหน้าเพจให้เต็มจอ และซ่อนส่วนเกินของ Streamlit
# =================================================================
st.set_page_config(page_title="สรุปตรวจเช็คร้านค้าเช่า", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > section:nth-child(2) > div:nth-child(1) { padding: 0rem; }
    iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

# ค้นหาตำแหน่งโฟลเดอร์ปัจจุบันของโปรเจกต์ เพื่อไม่ให้มีปัญหาตำแหน่งไฟล์บน Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(current_dir, "Data exemple.xlsx")
html_path = os.path.join(current_dir, "dashboard_tenant_store_inspection (1).html")

# =================================================================
# 2. ฟังก์ชันอ่านไฟล์ Excel (ดึงมาทุกบรรทัดชัวร์ๆ)
# =================================================================
@st.cache_data
def load_data(file_path):
    # ป้องกันกรณีหาไฟล์ไม่เจอ จะได้แสดงข้อความเตือนชัดเจนบนหน้าเว็บ
    if not os.path.exists(file_path):
        st.error(f"❌ ไม่พบไฟล์ข้อมูลค้างบนระบบ: พยายามหาที่ {file_path} แต่ไม่เจอ กรุณาเช็คว่าอัปโหลดไฟล์ขึ้น GitHub หรือยัง")
        return pd.DataFrame()
        
    df = pd.read_excel(file_path, sheet_name="Sheet1", dtype=str)
    df = df.fillna('')
    if 'Reason' in df.columns:
        df['Reason'] = df['Reason'].replace('', 'ปกติ')
    return df

df_raw = load_data(excel_path)

# ตรวจสอบว่ามีข้อมูลจาก Excel โหลดเข้ามาได้จริงไหม
if not df_raw.empty:

    # =================================================================
    # 3. สร้าง Filter หน้าสาขาด้วย Streamlit
    # =================================================================
    st.title("📊 ระบบสรุปตรวจเช็คร้านค้าเช่า")

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
    # 4. กรองข้อมูลใน Excel ทันที 
    # =================================================================
    df_filtered = df_raw.copy()

    if selected_branch != 'ทั้งหมด':
        df_filtered = df_filtered[df_filtered['สาขา'] == selected_branch]
    
    # แก้ไขบั๊กคำว่า '健全' ออก ให้เป็นเช็คเงื่อนไข 'ทั้งหมด' อย่างถูกต้อง
    if selected_building != 'ทั้งหมด':
        df_filtered = df_filtered[df_filtered['อาคาร'] == selected_building]
        
    if selected_status != 'ทั้งหมด':
        df_filtered = df_filtered[df_filtered['Status'] == selected_status]

    # แปลงข้อมูลสาขาที่ถูกกรองแล้วให้เป็น JSON
    records = []
    for _, row in df_filtered.iterrows():
        records.append({
            "branch": str(row.get('สาขา', '')).strip(),
            "room": str(row.get('หมายเลขห้อง', '')).strip(),
            "building": str(row.get('อาคาร', '')).strip(),
            "date": str(row.get('Date', '')).strip(),
            "month": str(row.get('Month of วันที่ตรวจ', 'June 2026')).strip(),
            "taskGroup": str(row.get('Task (group)', '')).strip(),
            "taskDetail": str(row.get('Task Detail', row.get('Task', ''))).strip(),
            "inspector": str(row.get('ชื่อผู้ตรวจ', '')).strip(),
            "reasonGroup": str(row.get('Reason', 'ปกติ')).strip(),
            "status": str(row.get('Status', '')).strip(),
            "approverName": str(row.get('ผู้อนุมัติในการตรวจ', 'สุวรรณ ก่อนนาค')).strip(),
            "approverRole": str(row.get('ตำแหน่งผู้อนุมัติในการตรวจ', 'ซุปเปอร์ไวเซอร์')).strip()
        })

    js_data = json.dumps(records, ensure_ascii=False)

    # =================================================================
    # 5. ฉีดข้อมูลที่กรองแล้ว เข้าไปใน HTML 
    # =================================================================
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        old_dataset_marker = "const inspectionDataset = ["
        if old_dataset_marker in html_content:
            parts = html_content.split(old_dataset_marker)
            rest_of_html = parts[1].split("];", 1)[1]
            html_content = f"{parts[0]}const inspectionDataset = {js_data};{rest_of_html}"

        # สั่งรีรันตัวกระตุ้นสคริปต์
        render_trigger = """
        <script>
            if (typeof init === 'function') { init(); }
            else if (typeof renderDashboard === 'function') { renderDashboard(); }
            else if (typeof updateCharts === 'function') { updateCharts(); }
        </script>
        """
        html_content += render_trigger

        # =================================================================
        # 6. แสดงผลหน้าจอแดชบอร์ดสุดสวย (ใส่รหัส Key บังคับเปลี่ยนข้อมูล)
        # =================================================================
        # สร้างคีย์ไม่ซ้ำกันตามค่าฟิลเตอร์ เพื่อบังคับให้ HTML อัปเดตข้อมูลตาม Excel ทุกบรรทัดชัวร์ๆ
        component_key = f"dash_{selected_branch}_{selected_building}_{selected_status}"
        components.html(html_content, height=1200, scrolling=True, key=component_key)
    else:
        st.error(f"❌ ไม่พบไฟล์โครงหน้ากาก HTML: หาไม่เจอที่ {html_path}")
else:
    st.warning("⚠️ ไม่มีข้อมูลในไฟล์ Excel หรือโหลดข้อมูลไม่สำเร็จ")
