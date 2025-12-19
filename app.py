import streamlit as st
import swisseph as swe
from datetime import datetime
import pytz

# ---------- 1. App Amaippu & CSS ----------
st.set_page_config(page_title="Accurate Transit Chart", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .stApp { background-color: #FDFEFE; }
    .header-style { background: #1A5276; color: white !important; text-align: center; padding: 12px; border-radius: 10px; font-size: 1.5em; font-weight: bold; margin-bottom: 20px; }
    .chart-container { display: flex; justify-content: center; align-items: center; margin-top: 20px; }
    .rasi-chart { width: 500px; border-collapse: collapse; border: 3px solid #1A5276; background: white; table-layout: fixed; }
    .rasi-chart td { border: 1.5px solid #1A5276; height: 120px; vertical-align: top; padding: 8px; position: relative; }
    .planet-text { color: #1B2631; font-weight: bold; font-size: 0.9em; line-height: 1.3; margin-bottom: 2px; }
    .rasi-name { color: #7F8C8D; font-size: 0.65em; font-weight: bold; position: absolute; bottom: 3px; right: 5px; opacity: 0.6; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='header-style'>🔱 Accurate India Transit (Kocharam) Chart</div>", unsafe_allow_html=True)

# ---------------- 2. Live Time Input ----------------
now_ist = datetime.now(IST)
c1, c2 = st.columns(2)
with c1: d_input = st.date_input("Thethi:", now_ist.date())
with c2: t_input = st.time_input("Neram (IST):", now_ist.time())

# ---------------- 3. Accurate Swiss Ephemeris ----------------
def get_accurate_transit(d, t):
    dt = datetime.combine(d, t)
    
    # Lahiri Ayanamsa - Thirukanitha Accurate Mode
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # UTC Convert (IST is +5.5)
    # Important: Julian Day based on Universal Time (UT)
    utc_hour = dt.hour + dt.minute/60.0 + dt.second/3600.0 - 5.5
    jd_ut = swe.julday(dt.year, dt.month, dt.day, utc_hour)

    # Planets and Labels (Tamil/English Mixed for clarity)
    planets = {
        swe.SUN: "Suri", swe.MOON: "Chan", swe.MARS: "Sev", 
        swe.MERCURY: "Budh", swe.JUPITER: "Guru", swe.VENUS: "Suk", 
        swe.SATURN: "Sani", swe.MEAN_NODE: "Rahu"
    }
    
    chart_pos = {}
    for pid, name in planets.items():
        # Using SIDEREAL flag for Indian Astrology
        res, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        deg = res[0]
        is_vakra = " (V)" if res[3] < 0 else "" 
        idx = int(deg / 30) # 0=Mesham...
        
        p_str = f"{name}{is_vakra} {int(deg%30)}°"
        if idx not in chart_pos: chart_pos[idx] = []
        chart_pos[idx].append(p_str)
        
        # Kethu Calculation (180 degrees from Rahu)
        if pid == swe.MEAN_NODE:
            k_deg = (deg + 180) % 360
            k_idx = int(k_deg / 30)
            if k_idx not in chart_pos: chart_pos[k_idx] = []
            chart_pos[k_idx].append(f"Kethu {int(k_deg%30)}°")
            
    return chart_pos, dt.strftime("%d-%m-%Y | %I:%M %p")

res_chart, display_time = get_accurate_transit(d_input, t_input)

# ---------------- 4. Display ----------------
def render_cell(i):
    planets_list = res_chart.get(i, [])
    p_html = "".join([f"<div class='planet-text'>{p}</div>" for p in planets_list])
    rasi_names = ["Mesham", "Rishabam", "Mithunam", "Kadagam", "Simmam", "Kanni", "Thulaam", "Viruchigam", "Thunusu", "Magaram", "Kumbam", "Meenam"]
    return f"{p_html}<span class='rasi-name'>{rasi_names[i]}</span>"

st.markdown(f"""
<div class="chart-container">
    <table class="rasi-chart">
        <tr><td>{render_cell(11)}</td><td>{render_cell(0)}</td><td>{render_cell(1)}</td><td>{render_cell(2)}</td></tr>
        <tr>
            <td>{render_cell(10)}</td>
            <td colspan="2" rowspan="2" style="text-align:center; vertical-align:middle; background:#F4F6F7;">
                <b style="color:#1A5276; font-size:1.1em;">RAASI CHART</b><br>
                <small>IST (India)</small><br>
                <small style="color:red;">{display_time}</small>
            </td>
            <td>{render_cell(3)}</td>
        </tr>
        <tr><td>{render_cell(9)}</td><td>{render_cell(4)}</td></tr>
        <tr><td>{render_cell(8)}</td><td>{render_cell(7)}</td><td>{render_cell(6)}</td><td>{render_cell(5)}</td></tr>
    </table>
</div>
""", unsafe_allow_html=True)
