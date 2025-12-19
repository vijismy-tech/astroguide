import streamlit as st
import swisseph as swe
from datetime import datetime
import pytz

# ---------- 1. ஆப் அமைப்புகள் & Premium CSS ----------
st.set_page_config(page_title="Professional Rasi Chart", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    /* முழு பக்கத்திற்கான பின்னணி */
    .stApp { 
        background: radial-gradient(circle, #ffffff 0%, #f7f3e9 100%);
    }
    
    /* தலைப்பு ஸ்டைல் */
    .header-style { 
        background: linear-gradient(135deg, #4A0000 0%, #8B0000 50%, #4A0000 100%);
        color: #FFD700 !important; 
        text-align: center; 
        padding: 20px; 
        border-radius: 15px; 
        font-size: 1.8em; 
        font-weight: bold; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        border: 2px solid #D4AF37;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* ராசி கட்ட பெட்டி (Container) */
    .chart-container { 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        padding: 20px;
    }
    
    /* ராசி கட்டம் - Professional Table */
    .rasi-chart { 
        width: 600px; 
        border-collapse: collapse; 
        border: 5px solid #8B0000; 
        background: #ffffff; 
        table-layout: fixed; 
        box-shadow: 0 20px 50px rgba(0,0,0,0.25);
        border-radius: 10px;
        overflow: hidden;
    }
    
    .rasi-chart td { 
        border: 2px solid #D4AF37; 
        height: 140px; 
        vertical-align: top; 
        padding: 12px; 
        position: relative; 
        background: linear-gradient(to bottom right, #ffffff, #fffdfa);
    }
    
    /* கிரகங்கள் ஸ்டைல் */
    .planet-text { 
        color: #1a1a1a; 
        font-weight: 800; 
        font-size: 1.1em; 
        line-height: 1.5;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    
    .vakra-text { color: #D32F2F; font-size: 0.9em; } /* வக்ரம் சிவப்பு நிறத்தில் */

    /* ராசி பெயர்கள் */
    .rasi-label { 
        color: #8B0000; 
        font-size: 0.75em; 
        font-weight: bold; 
        position: absolute; 
        bottom: 5px; 
        right: 8px; 
        background: rgba(212, 175, 55, 0.1);
        padding: 2px 5px;
        border-radius: 4px;
    }
    
    /* மையத் தகவல் பெட்டி */
    .center-info-box {
        text-align: center;
        background: #FFF9F0;
        border: 2px inset #D4AF37;
        border-radius: 12px;
        padding: 15px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.05);
    }
    .center-date { color: #4A0000; font-size: 1.1em; font-weight: bold; }
    .center-time { color: #B22222; font-size: 1.3em; font-weight: bold; margin: 8px 0; border-bottom: 1px solid #D4AF37; display: inline-block; }
    
    /* Streamlit கூறுகளை மறைத்தல் */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='header-style'>🔱 ஸ்ரீ திருக்கணித நித்ய கோச்சார ராசி கட்டம் 🔱</div>", unsafe_allow_html=True)

# ---------------- 2. நேரடி நேர அமைப்பு ----------------
current_now = datetime.now(IST)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("<div style='background: white; padding:15px; border-radius:10px; border: 1px solid #D4AF37;'>", unsafe_allow_html=True)
    d_input = st.date_input("கணிப்புத் தேதி (Prediction Date):", current_now.date())
    t_input = st.time_input("கணிப்பு நேரம் (Prediction Time):", current_now.time())
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- 3. துல்லியமான கணிதம் (Exact Math) ----------------
def get_premium_rasi_data(d, t):
    dt = datetime.combine(d, t)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # IST to UTC Adjustment
    utc_h = dt.hour + dt.minute/60.0 + dt.second/3600.0 - 5.5
    jd_ut = swe.julday(dt.year, dt.month, dt.day, utc_h)

    # கிரகங்களின் பட்டியல்
    p_map = {
        swe.SUN: "சூரியன்", swe.MOON: "சந்திரன்", swe.MARS: "செவ்வாய்", 
        swe.MERCURY: "புதன்", swe.JUPITER: "குரு", swe.VENUS: "சுக்கிரன்", 
        swe.SATURN: "சனி", swe.MEAN_NODE: "ராகு"
    }
    
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
            
    return res_chart, dt.strftime("%d-%m-%Y"), dt.strftime("%I:%M:%S %p")

chart_data, final_d, final_t = get_premium_rasi_data(d_input, t_input)

# ---------------- 4. ராசி கட்டம் அவுட்புட் ----------------
def draw_box(i):
    planets = "".join(chart_data.get(i, []))
    rasi_names = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]
    return f"{planets}<span class='rasi-label'>{rasi_names[i]}</span>"



st.markdown(f"""
<div class="chart-container">
    <table class="rasi-chart">
        <tr>
            <td>{draw_box(11)}</td><td>{draw_box(0)}</td><td>{draw_box(1)}</td><td>{draw_box(2)}</td>
        </tr>
        <tr>
            <td>{draw_box(10)}</td>
            <td colspan="2" rowspan="2" style="vertical-align:middle; background: #fffaf0;">
                <div class="center-info-box">
                    <div style="font-weight:bold; color:#8B0000; letter-spacing: 2px; margin-bottom:5px;">கோச்சார நிலவரம்</div>
                    <div class="center-date">{final_d}</div>
                    <div class="center-time">{final_t}</div>
                    <div style="font-size:0.7em; color:#555; font-style: italic;">திருக்கணித பஞ்சாங்கம் (IST)</div>
                </div>
            </td>
            <td>{draw_box(3)}</td>
        </tr>
        <tr>
            <td>{draw_box(9)}</td><td>{draw_box(4)}</td>
        </tr>
        <tr>
            <td>{draw_box(8)}</td><td>{draw_box(7)}</td><td>{draw_box(6)}</td><td>{draw_box(5)}</td>
        </tr>
    </table>
</div>
""", unsafe_allow_html=True)

st.info("குறிப்பு: (வ) என்பது வக்ர நிலையைக் குறிக்கும். கிரகங்களின் பெயருக்கு அருகில் உள்ள பாகை அந்த ராசியில் அதன் நிலையைக் குறிக்கும்.")
