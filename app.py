import streamlit as st
import swisseph as swe
from datetime import datetime
import pytz

# ---------- 1. ஆப் அமைப்புகள் & நவீன ஸ்டைல் (CSS) ----------
st.set_page_config(page_title="தமிழ் திருக்கணித ராசி கட்டம்", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    /* பின்னணி மற்றும் எழுத்து வடிவம் */
    .stApp { background: linear-gradient(135deg, #FFF8F0 0%, #F5E6D3 100%); }
    
    .header-style { 
        background: linear-gradient(90deg, #4A0000, #922B21); 
        color: white !important; 
        text-align: center; 
        padding: 15px; 
        border-radius: 12px; 
        font-size: 1.6em; 
        font-weight: bold; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 25px;
    }
    
    /* ராசி கட்ட அமைப்பு */
    .chart-container { 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        margin-top: 10px;
    }
    
    .rasi-chart { 
        width: 580px; 
        border-collapse: collapse; 
        border: 4px solid #4A0000; 
        background: #ffffff; 
        table-layout: fixed; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    
    .rasi-chart td { 
        border: 2px solid #4A0000; 
        height: 130px; 
        vertical-align: top; 
        padding: 10px; 
        position: relative; 
    }
    
    /* கிரகங்கள் மற்றும் ராசி பெயர்கள் */
    .planet-text { 
        color: #1a1a1a; 
        font-weight: bold; 
        font-size: 1.05em; 
        line-height: 1.4; 
    }
    
    .rasi-name { 
        color: #8B0000; 
        font-size: 0.7em; 
        font-weight: bold; 
        position: absolute; 
        bottom: 5px; 
        right: 8px; 
        opacity: 0.4;
    }
    
    /* மையப் பெட்டி தகவல் */
    .center-box {
        text-align: center;
        background: #FFFBF0;
        border-radius: 8px;
        padding: 12px;
    }
    .center-date { color: #333; font-size: 1em; font-weight: bold; }
    .center-time { color: #D32F2F; font-size: 1.1em; font-weight: bold; margin: 5px 0; }
    
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='header-style'>🔱 நவீன திருக்கணித நேரடி ராசி கட்டம்</div>", unsafe_allow_html=True)

# ---------------- 2. ஆட்டோமேட்டிக் லைவ் டைம் (Automatic Time) ----------------
# ஆப்பைத் திறக்கும்போது தற்போதைய நேரத்தை தானாகவே எடுக்கும்
current_now = datetime.now(IST)

col1, col2 = st.columns(2)
with col1:
    d_input = st.date_input("தேதி:", current_now.date())
with col2:
    t_input = st.time_input("நேரம் (Live):", current_now.time())

# ---------------- 3. துல்லியமான திருக்கணிதக் கணக்கீடு ----------------
def get_dynamic_rasi_chart(d, t):
    dt_combined = datetime.combine(d, t)
    swe.set_sid_mode(swe.SIDM_LAHIRI) # லாகிரி அயனாம்சம்
    
    # இந்திய நேரத்தை (IST) உலக நேரத்திற்கு (UTC) மாற்றுதல் (-5.5 மணிநேரம்)
    utc_hour = dt_combined.hour + dt_combined.minute/60.0 + dt_combined.second/3600.0 - 5.5
    jd_ut = swe.julday(dt_combined.year, dt_combined.month, dt_combined.day, utc_hour)

    # தமிழ் கிரகப் பெயர்கள்
    planets_map = {
        swe.SUN: "சூரியன்", swe.MOON: "சந்திரன்", swe.MARS: "செவ்வாய்", 
        swe.MERCURY: "புதன்", swe.JUPITER: "குரு", swe.VENUS: "சுக்கிரன்", 
        swe.SATURN: "சனி", swe.MEAN_NODE: "ராகு"
    }
    
    rasi_data = {}
    for pid, name in planets_map.items():
        res, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        deg = res[0]
        vakra = " (வ)" if res[3] < 0 else "" # வக்ர நிலை
        idx = int(deg / 30) # ராசி இன்டெக்ஸ் (0=மேஷம்)
        
        # பாகையுடன் கிரகம் (எ.கா: சூரியன் 4°)
        p_info = f"{name}{vakra} {int(deg%30)}°"
        if idx not in rasi_data: rasi_data[idx] = []
        rasi_data[idx].append(p_info)
        
        # கேது கணக்கீடு (ராகுவிற்கு நேர் 180° எதிரில்)
        if pid == swe.MEAN_NODE:
            k_idx = (idx + 6) % 12
            if k_idx not in rasi_data: rasi_data[k_idx] = []
            rasi_data[k_idx].append(f"கேது {int(deg%30)}°")
            
    return rasi_data, dt_combined.strftime("%d-%m-%Y"), dt_combined.strftime("%I:%M:%S %p")

chart_res, final_date, final_time = get_dynamic_rasi_chart(d_input, t_input)

# ---------------- 4. ராசி கட்டம் வரைதல் ----------------
def render_rasi_box(i):
    planets_list = chart_res.get(i, [])
    p_html = "".join([f"<div class='planet-text'>{p}</div>" for p in planets_list])
    rasi_names = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]
    return f"{p_html}<span class='rasi-name'>{rasi_names[i]}</span>"

st.markdown(f"""
<div class="chart-container">
    <table class="rasi-chart">
        <tr>
            <td>{render_rasi_box(11)}</td><td>{render_rasi_box(0)}</td><td>{render_rasi_box(1)}</td><td>{render_rasi_box(2)}</td>
        </tr>
        <tr>
            <td>{render_rasi_box(10)}</td>
            <td colspan="2" rowspan="2" style="vertical-align:middle;">
                <div class="center-box">
                    <div style="color:#4A0000; font-weight:bold; margin-bottom:5px;">ராசி கட்டம்</div>
                    <div class="center-date">{final_date}</div>
                    <div class="center-time">{final_time}</div>
                    <div style="font-size:0.65em; color:#666; margin-top:5px;">திருக்கணித முறை (IST)</div>
                </div>
            </td>
            <td>{render_rasi_box(3)}</td>
        </tr>
        <tr>
            <td>{render_rasi_box(9)}</td><td>{render_rasi_box(4)}</td>
        </tr>
        <tr>
            <td>{render_rasi_box(8)}</td><td>{render_rasi_box(7)}</td><td>{render_rasi_box(6)}</td><td>{render_rasi_box(5)}</td>
        </tr>
    </table>
</div>
""", unsafe_allow_html=True)
