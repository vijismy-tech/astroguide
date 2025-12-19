import streamlit as st
import swisseph as swe
from datetime import datetime
import pytz

# ---------- 1. Settings & Style ----------
st.set_page_config(page_title="Professional Tamil Transit", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #ffffff 0%, #f7f3e9 100%); }
    .header-style { 
        background: linear-gradient(135deg, #4A0000 0%, #8B0000 50%, #4A0000 100%);
        color: #FFD700 !important; text-align: center; padding: 20px; border-radius: 15px; 
        font-size: 1.8em; font-weight: bold; box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        border: 2px solid #D4AF37; margin-bottom: 25px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .chart-container { display: flex; justify-content: center; align-items: center; padding: 10px; }
    .rasi-chart { 
        width: 600px; border-collapse: collapse; border: 5px solid #8B0000; 
        background: #ffffff; table-layout: fixed; box-shadow: 0 20px 50px rgba(0,0,0,0.25);
    }
    .rasi-chart td { 
        border: 2px solid #D4AF37; height: 140px; vertical-align: top; padding: 12px; 
        position: relative; background: linear-gradient(to bottom right, #ffffff, #fffdfa);
    }
    .planet-text { color: #1a1a1a; font-weight: 800; font-size: 1.05em; line-height: 1.4; }
    .vakra-text { color: #D32F2F; font-size: 0.85em; font-weight: bold; }
    .rasi-label { 
        color: #8B0000; font-size: 0.7em; font-weight: bold; position: absolute; 
        bottom: 5px; right: 8px; background: rgba(212, 175, 55, 0.15); padding: 2px 5px; border-radius: 4px;
    }
    .center-info-box {
        text-align: center; background: #FFF9F0; border: 2.5px double #D4AF37;
        border-radius: 12px; padding: 10px; box-shadow: inset 0 0 15px rgba(0,0,0,0.05);
    }
    .tamil-info { color: #8B0000; font-size: 1.1em; font-weight: bold; margin-bottom: 3px; border-bottom: 1px dashed #D4AF37; padding-bottom: 3px; }
    .center-date { color: #333; font-size: 0.9em; font-weight: bold; }
    .center-time { color: #B22222; font-size: 1.15em; font-weight: bold; margin-top: 5px; }
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='header-style'>🔱 ஸ்ரீ திருக்கணித நித்ய கோச்சார ராசி கட்டம் 🔱</div>", unsafe_allow_html=True)

# ---------------- 2. Date/Time Input ----------------
current_now = datetime.now(IST)
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("<div style='background: white; padding:10px; border-radius:10px; border: 1px solid #D4AF37; text-align:center;'>", unsafe_allow_html=True)
    d_input = st.date_input("தேதி:", current_now.date())
    t_input = st.time_input("நேரம் (Live):", current_now.time())
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- 3. Calculation Logic ----------------
def get_tamil_details(jd_ut):
    # Tamizh Maathangal & Varudangal
    months = ["சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி", "ஐப்பசி", "கார்த்திகை", "மார்கழி", "தை", "மாசி", "பங்குனி"]
    years = ["பிரபவ", "விபவ", "சுக்ல", "பிரமோதூத", "பிரஜோத்பத்தி", "ஆங்கீரச", "ஸ்ரீமுக", "பவ", "யுவ", "தாது", "ஈஸ்வர", "வெகுதானிய", "பிரமாதி", "விக்ரம", "விஷு", "சித்ரபானு", "சுபானு", "தாரண", "பார்த்திப", "விய", "சர்வஜித்", "சர்வதாரி", "விரோதி", "விக்ருதி", "கர", "நந்தன", "விஜய", "ஜய", "மன்மத", "துன்முகி", "ஹேவிளம்பி", "விளம்பி", "விகாரி", "சார்வரி", "பிலவ", "சுபகிருது", "சோபகிருது", "குரோதி", "விசுவாசு", "பரபாவ", "பிளவங்க", "கீலக", "சௌமிய", "சாதாரண", "விரோதகிருது", "பரிதாபி", "பிரமாதீச", "ஆனந்த", "ராட்சச", "நள", "பிங்கள", "காளயுக்தி", "சித்தார்த்தி", "ரௌத்திரி", "துன்மதி", "துந்துபி", "ருத்ரோத்காரி", "ரக்தாட்சி", "குரோதன", "அட்சய"]
    
    # Sun position for month
    res, _ = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_SIDEREAL)
    sun_deg = res[0]
    month_idx = int(sun_deg / 30)
    tamil_month = months[month_idx]
    
    # Year Calculation (Approximation for Display)
    # 2024-25 is Krodhi (37th in cycle)
    base_year = 2024 
    base_idx = 37 # Krodhi
    current_year = datetime.now().year
    year_idx = (base_idx + (current_year - base_year)) % 60
    tamil_year = years[year_idx]
    
    return f"{tamil_year} வருடம் - {tamil_month} மாதம்"

def get_complete_data(d, t):
    dt = datetime.combine(d, t)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    utc_h = dt.hour + dt.minute/60.0 + dt.second/3600.0 - 5.5
    jd_ut = swe.julday(dt.year, dt.month, dt.day, utc_h)

    tamil_header = get_tamil_details(jd_ut)
    p_map = {swe.SUN: "சூரியன்", swe.MOON: "சந்திரன்", swe.MARS: "செவ்வாய்", swe.MERCURY: "புதன்", swe.JUPITER: "குரு", swe.VENUS: "சுக்கிரன்", swe.SATURN: "சனி", swe.MEAN_NODE: "ராகு"}
    
    res_chart = {}
    for pid, name in p_map.items():
        res, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        deg = res[0]
        vakra = " <span class='vakra-text'>(வ)</span>" if res[3] < 0 else ""
        idx = int(deg / 30)
        p_str = f"<div class='planet-text'>{name}{vakra} {int(deg%30)}°</div>"
        if idx not in res_chart: res_chart[idx] = []
        res_chart[idx].append(p_str)
        if pid == swe.MEAN_NODE:
            k_idx = (idx + 6) % 12
            if k_idx not in res_chart: res_chart[k_idx] = []
            res_chart[k_idx].append(f"<div class='planet-text'>கேது {int(deg%30)}°</div>")
            
    return res_chart, dt.strftime("%d-%m-%Y"), dt.strftime("%I:%M:%S %p"), tamil_header

chart_data, f_date, f_time, tamil_info = get_complete_data(d_input, t_input)

# ---------------- 4. Render ----------------
def draw_box(i):
    planets = "".join(chart_data.get(i, []))
    rasi_names = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]
    return f"{planets}<span class='rasi-label'>{rasi_names[i]}</span>"

st.markdown(f"""
<div class="chart-container">
    <table class="rasi-chart">
        <tr><td>{draw_box(11)}</td><td>{draw_box(0)}</td><td>{draw_box(1)}</td><td>{draw_box(2)}</td></tr>
        <tr>
            <td>{draw_box(10)}</td>
            <td colspan="2" rowspan="2" style="vertical-align:middle;">
                <div class="center-info-box">
                    <div class="tamil-info">{tamil_info}</div>
                    <div class="center-date">{f_date}</div>
                    <div class="center-time">{f_time}</div>
                    <div style="font-size:0.65em; color:#666; margin-top:5px;">திருக்கணித முறை (IST)</div>
                </div>
            </td>
            <td>{draw_box(3)}</td>
        </tr>
        <tr><td>{draw_box(9)}</td><td>{draw_box(4)}</td></tr>
        <tr><td>{draw_box(8)}</td><td>{draw_box(7)}</td><td>{draw_box(6)}</td><td>{draw_box(5)}</td></tr>
    </table>
</div>
""", unsafe_allow_html=True)
