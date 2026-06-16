import streamlit as st
import pandas as pd
import json
import os

# =================================================================
# 1. ตั้งค่าหน้าเพจให้เต็มจอ และล็อกขนาดกล่องแสดงผลด้วย CSS
# =================================================================
st.set_page_config(page_title="สรุปตรวจเช็คร้านค้าเช่า", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] > section:nth-child(2) > div:nth-child(1) { padding: 0rem; }
    iframe { border: none !important; width: 100% !important; height: 1200px !important; }
</style>
""", unsafe_allow_html=True)

# ค้นหาตำแหน่งโฟลเดอร์ปัจจุบันของโปรเจกต์
current_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(current_dir, "Data exemple.xlsx")
html_path = os.path.join(current_dir, "dashboard_tenant_store_inspection (1).html")


# =================================================================
# 2. ฟังก์ชันอ่านไฟล์ Excel (ดึงมาตรงๆ 100% ไม่มีการตัดแถวทิ้ง)
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
    st.error("❌ ระบบไม่สามารถอ่านข้อมูลจากไฟล์ Excel ได้")
    st.stop()


# =================================================================
# 3. ส่วนสร้าง FILTER ด้านบนสุดด้วย Streamlit
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
# 4. แปลงข้อมูล Excel ทั้งหมดให้เป็น JSON (ส่งชุดเต็มไปให้ HTML)
# =================================================================
records = []
for _, row in df_raw.iterrows():
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
# 5. อ่าน HTML และฝังกลไกสั่งควบคุม Filter จากภายในโครงสร้างเว็บ
# =================================================================
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# เสียบข้อมูลดิบชุดเต็มเข้าตัวแปรดั้งเดิม
old_dataset_marker = "const inspectionDataset = ["
if old_dataset_marker in html_content:
    parts = html_content.split(old_dataset_marker)
    rest_of_html = parts[1].split("];", 1)[1]
    html_content = f"{parts[0]}const inspectionDataset = {js_data};{rest_of_html}"

# 🔥 สคริปต์ขั้นเด็ดขาด: วิ่งไปสั่งเปลี่ยนค่า Filter ในแถบขวาของ HTML โดยตรง
# เปลี่ยนคำว่า 'ทั้งหมด' เป็นค่าว่างเพื่อให้แมตช์กับเงื่อนไขดั้งเดิมในโครงสร้าง HTML ของพี่
js_branch = "" if selected_branch == "ทั้งหมด" else selected_branch
js_building = "" if selected_building == "ทั้งหมด" else selected_building
js_status = "" if selected_status == "ทั้งหมด" else selected_status

html_filter_bridge = f"""
<script>
    // ทำงานทันทีเมื่อโครงสร้างหน้าจอโหลดเสร็จ
    window.addEventListener('DOMContentLoaded', () => {{
        setTimeout(() => {{
            // 1. ฟังก์ชันค้นหาและกรองข้อมูลเลียนแบบพฤติกรรมการคลิกเลือกของมนุษย์
            function triggerHTMLFilter(val) {{
                if (!val) return;
                const selectors = document.querySelectorAll('select, input');
                selectors.forEach(el => {{
                    if (el.value === val || el.innerText.includes(val)) {{
                        el.value = val;
                        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }});
            }}

            // 2. สั่งเปิดสวิตช์ฟิลเตอร์ตามที่พี่กดใน Streamlit ทันที
            triggerHTMLFilter("{js_branch}");
            triggerHTMLFilter("{js_building}");
            triggerHTMLFilter("{js_status}");

            // 3. สั่งให้ฟังก์ชันหลักใน HTML ทำการรีเฟรชยอดอาคาร/ห้อง และวาดกราฟวงกลมใหม่
            if (typeof init === 'function') {{ init(); }}
            if (typeof renderDashboard === 'function') {{ renderDashboard(); }}
            if (typeof updateCharts === 'function') {{ updateCharts(); }}
        }}, 400); // ดีเลย์สั้นๆ เพื่อรอให้ตาราง HTML พร้อมทำงาน
    }});
</script>
"""
html_content += html_filter_bridge


# =================================================================
# 6. แสดงผลหน้าจอแดชบอร์ด (เอาคำว่า key= ออกถาวร บดขยี้ปัญหากวนใจ)
# =================================================================
# เรียกแบบคลีนที่สุด ไม่พ่วงอาร์กิวเมนต์ใดๆ ที่จะจุดชนวนให้เกิด TypeError อีกแน่นอน 100%
st.components.v1.html(html_content)
