import streamlit as st
import pandas as pd
import json

# 1. ตั้งค่าหน้าเพจให้กว้างเต็มจอ
st.set_page_config(page_title="สรุปตรวจเช็คร้านค้าเช่า", layout="wide", initial_sidebar_state="expanded")

# 2. โหลดข้อมูลจริงจาก Excelทั้งหมด
@st.cache_data
def load_data():
    df = pd.read_excel("Data exemple.xlsx", sheet_name="Sheet1")
    df['Reason'] = df['Reason'].fillna('ปกติ')
    # ตรวจสอบและสร้างคอลัมน์วันที่/เดือน เผื่อใน Excel ไม่มีให้ตรงกับระบบ
    if 'Date' in df.columns:
        df['Date_Str'] = pd.to_datetime(df['Date']).dt.strftime('%B %d, %Y')
        df['Month_Str'] = pd.to_datetime(df['Date']).dt.strftime('%B %Y')
    else:
        df['Date_Str'] = "June 6, 2026"
        df['Month_Str'] = "June 2026"
    return df

df = load_data()

# 3. สร้างระบบ Filter ด้วย Streamlit (แต่ออกแบบข้อความให้ตรงกับรายงานเดิม)
st.sidebar.markdown("<h3 style='color: #1e4666; font-size: 16px; font-weight: 700;'>🔍 ตัวกรองรายงาน (Filters)</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")

def create_sidebar_filter(column, label):
    options = ["All"] + list(df[column].dropna().unique())
    return st.sidebar.selectbox(label, options)

# สร้าง Dropdown ตัวกรองตามหน้าตาต้นฉบับ
sel_month = create_sidebar_filter('Month_Str', 'Month of วันที่ตรวจ')
sel_date = create_sidebar_filter('Date_Str', 'วันที่ตรวจ')
sel_branch = create_sidebar_filter('สาขา', 'สาขา')
sel_building = create_sidebar_filter('อาคาร', 'อาคาร')
sel_room = create_sidebar_filter('หมายเลขห้อง', 'หมายเลขห้อง')
sel_taskgroup = create_sidebar_filter('Task (group)', 'Task (group)')
sel_task = create_sidebar_filter('Task', 'Task') if 'Task' in df.columns else "All"
sel_status = create_sidebar_filter('Status', 'Status (gr.)')
sel_inspector = create_sidebar_filter('ชื่อผู้ตรวจ', 'ชื่อผู้ตรวจ*')

# ประมวลผลกรองข้อมูลในระบบ Python (แม่นยำ 100%)
f_df = df.copy()
if sel_month != "All": f_df = f_df[f_df['Month_Str'] == sel_month]
if sel_date != "All": f_df = f_df[f_df['Date_Str'] == sel_date]
if sel_branch != "All": f_df = f_df[f_df['สาขา'] == sel_branch]
if sel_building != "All": f_df = f_df[f_df['อาคาร'] == sel_building]
if sel_room != "All": f_df = f_df[f_df['หมายเลขห้อง'] == sel_room]
if sel_taskgroup != "All": f_df = f_df[f_df['Task (group)'] == sel_taskgroup]
if sel_task != "All" and 'Task' in df.columns: f_df = f_df[f_df['Task'] == sel_task]
if sel_status != "All": f_df = f_df[f_df['Status'] == sel_status]
if sel_inspector != "All": f_df = f_df[f_df['ชื่อผู้ตรวจ'] == sel_inspector]

# 4. คำนวณตัวเลขทางสถิติทั้งหมดส่งให้ HTML (คำนวณสดทุกครั้งที่เปลี่ยน Filter)
total_buildings = f_df['อาคาร'].nunique() if 'อาคาร' in f_df.columns else 0
total_rooms = f_df['หมายเลขห้อง'].nunique() if 'หมายเลขห้อง' in f_df.columns else 0
passed_cnt = len(f_df[f_df['Status'] == 'ตรวจเช็คผ่าน'])
failed_cnt = len(f_df[f_df['Status'] == 'ตรวจเปิดไม่ผ่าน'])
other_cnt = len(f_df) - (passed_cnt + failed_cnt)

# จัดแจงข้อมูลรายรายการสำหรับตาราง Detail ด้านล่าง
table_records = []
for _, row in f_df.iterrows():
    table_records.append(f"""
        <tr class="hover:bg-slate-50/80 transition-all border-b border-slate-100">
            <td class="p-3 font-semibold text-slate-600 text-xs">{row.get('สาขา','')}</td>
            <td class="p-3"><span class="bg-slate-100 px-1.5 py-0.5 rounded text-blue-600 font-mono font-bold">{row.get('หมายเลขห้อง','')}</span></td>
            <td class="p-3 text-slate-500 text-xs">{row.get('Date_Str','')}</td>
            <td class="p-3 text-slate-600 font-semibold text-xs">{row.get('Task (group)','')}</td>
            <td class="p-3 text-xs text-slate-600 font-medium max-w-xs truncate">{row.get('Task Detail', row.get('Task', ''))}</td>
            <td class="p-3 text-slate-600 font-medium text-xs">{row.get('ชื่อผู้ตรวจ','')}</td>
            <td class="p-3 text-slate-500 italic text-xs">{row.get('Reason','ปกติ')}</td>
            <td class="p-3 text-center">
                <div class="inline-flex items-center justify-center px-4 py-1.5 rounded-full text-[11px] font-semibold {'bg-emerald-50 text-emerald-700 border border-emerald-300' if row.get('Status') == 'ตรวจเช็คผ่าน' else 'bg-rose-50 text-rose-700 border border-rose-300'} shadow-sm min-w-[120px]">
                    {row.get('Status','')}
                </div>
            </td>
            <td class="p-3 text-center">
                <div class="bg-slate-50 border border-slate-200/60 text-slate-600 px-3 py-1.5 rounded-full text-center text-[10px] font-semibold shadow-sm inline-flex flex-col justify-center min-w-[150px]">
                    <span class="text-slate-700 leading-tight">{row.get('ผู้อนุมัติในการตรวจ', 'สุวรรณ ก่อนนาค')}</span>
                    <span class="text-[9px] text-slate-400 font-normal leading-none mt-0.5">{row.get('ตำแหน่งผู้อนุมัติในการตรวจ', 'ซุปเปอร์ไวเซอร์')}</span>
                </div>
            </td>
        </tr>
    """)
table_rows_html = "".join(table_records)

# สรุปข้อมูลสำหรับทำ Matrix 'Status by สาขา'
matrix_rows = []
if 'สาขา' in f_df.columns:
    for branch in f_df['สาขา'].unique():
        b_df = f_df[f_df['สาขา'] == branch]
        p_b = len(b_df[b_df['Status'] == 'ตรวจเช็คผ่าน'])
        f_b = len(b_df[b_df['Status'] == 'ตรวจเปิดไม่ผ่าน'])
        o_b = len(b_df) - (p_b + f_b)
        matrix_rows.append(f"""
            <tr>
                <td class="py-1 font-semibold text-slate-700">{branch}</td>
                <td class="py-1 text-right text-emerald-600">{p_b:,}</td>
                <td class="py-1 text-right text-rose-500">{f_b:,}</td>
                <td class="py-1 text-right text-slate-400">{o_b:,}</td>
            </tr>
        """)
matrix_html = "".join(matrix_rows) if matrix_rows else "<tr><td colspan='4' class='text-center py-2'>ไม่มีข้อมูล</td></tr>"

# เตรียมข้อมูลกราฟส่งไปให้ Chart.js ใน HTML วาดใหม่
branches_list = list(f_df['สาขา'].unique()) if 'สาขา' in f_df.columns else []
rooms_by_branch = [int(f_df[f_df['สาขา'] == b]['หมายเลขห้อง'].nunique()) for b in branches_list]
buildings_by_branch = [int(f_df[f_df['สาขา'] == b]['อาคาร'].nunique()) for b in branches_list]

# 5. อ่านไฟล์ HTML แล้วใช้เทคนิคแทนที่ค่า (Injection) ด้วยข้อมูลที่ผ่านการกรองแล้ว
with open("dashboard_tenant_store_inspection (1).html", "r", encoding="utf-8") as f:
    html_content = f.read()

# เขียนสคริปต์ทับไปใน HTML เพื่อบังคับให้ตัวเลขและกราฟวาดค่าใหม่ตาม Python ทันที
injection_script = f"""
<script>
    // อัปเดตตัวเลขการ์ดสรุปด้านบน
    document.getElementById('metric-buildings').innerText = "{total_buildings}";
    document.getElementById('metric-rooms').innerText = "{total_rooms}";
    document.getElementById('metric-passed').innerText = "{passed_cnt:,}";
    document.getElementById('metric-failed').innerText = "{failed_cnt:,}";
    document.getElementById('metric-other').innerText = "{other_cnt:,}";
    document.getElementById('filtered-count-label').innerText = "พบ {len(f_df):,} รายการ";
    
    // อัปเดตเนื้อหาในตาราง
    document.getElementById('detail-table-body').innerHTML = `{table_rows_html}`;
    document.getElementById('branch-status-matrix').innerHTML = `{matrix_html}`;
    
    // บังคับให้กราฟ Chart.js วาดข้อมูลใหม่ตามการ Filter
    setTimeout(function() {{
        if(window.chartBranchRoomsInstance) {{
            window.chartBranchRoomsInstance.data.labels = {json.dumps(branches_list, ensure_ascii=False)};
            window.chartBranchRoomsInstance.data.datasets[0].data = {json.dumps(buildings_by_branch)};
            window.chartBranchRoomsInstance.data.datasets[1].data = {json.dumps(rooms_by_branch)};
            window.chartBranchRoomsInstance.update();
        }}
        if(window.chartPieStatusInstance) {{
            window.chartPieStatusInstance.data.datasets[0].data = [{passed_cnt}, {failed_cnt}, {other_cnt}];
            window.chartPieStatusInstance.update();
        }}
    }}, 500);
</script>
"""

# ค้นหาจุดปิดแท็ก body เพื่อฉีดโค้ดตัวกรองใหม่เข้าไปทำงาน
html_content = html_content.replace("</body>", f"{injection_script}</body>")

# 6. แสดงผลลัพธ์พรีเมียมแบบกว้างเต็มจอและมีสัญญานตอบสนองตัวกรอง
import streamlit.components.v1 as components
st.markdown("<style>iframe {border: none !important;} [data-testid='stSidebar'] {background-color: #ffffff;}</style>", unsafe_allow_html=True)
components.html(html_content, height=1300, scrolling=True)
