import streamlit as st
import swisseph as swe
from datetime import datetime
import pytz

# ---------- 1. App Settings & Premium Style ----------
st.set_page_config(page_title="Tamil Panchangam Chart", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #ffffff 0%, #fcf9f0 100%); }
    .header-style { 
        background: linear-gradient(135deg, #4A0000 0%, #8B0000 50%, #4A0000 100%);
        color: #FFD700 !important; text-align: center; padding: 20px; border-radius: 15px; 
        font-size: 1.8em; font-weight: bold; box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        border: 2px solid #D4AF37; margin-bottom: 25px;
    }
    .chart-container { display: flex; justify-content: center; align-items: center; padding: 10px; }
    .rasi-chart { 
        width: 620px; border-collapse: collapse; border: 5px solid #8B0000; 
        background: #ffffff; table-layout: fixed; box-shadow: 0 20px 50px rgba(0,0,0,0.2);
    }
    .rasi-chart td { 
        border: 2px solid #D4AF37; height: 145px; vertical-align: top; padding: 12px; 
        position: relative; background: #fff;
    }
    .planet-text { color: #1a1a1a; font-weight: 800; font-size: 1.05em; line-height: 1.4; }
    .vakra-text { color: #D32F2F; font-size: 0.85em; }
    .rasi-label { 
        color: #8B0000; font-size: 0.7em; font-weight: bold; position: absolute; 
        bottom: 5px; right: 8px; background: #fdf5e6; padding: 2px 5px; border-radius: 4px;
    }
    .center-info-box {
        text-align: center; background: #FFFBF2; border: 2.5px double #D4AF37;
        border-radius: 12px; padding: 12px;
    }
    .tamil-main { color: #8B0000; font-size: 1.2em; font-weight: bold; margin-bottom: 2px; }
    .tamil-sub { color: #B22222; font-size: 1.1em; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #D4AF37; padding-bottom: 5px; }
    .eng-dt { color: #333; font-size: 0.85em; font-weight: bold; }
    .eng-tm { color: #D32F2F; font-size: 1em; font-weight: bold; margin-top: 3px; }
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='header-style'>🔱 ஸ்ரீ திருக்கணித நேரடி ராசி கட்டம் 🔱</div>", unsafe_allow_html=True)

# ---------------- 2. Input ----------------
current_now = datetime.now(IST)
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("<div style='background: white; padding:10px; border-radius:10px; border: 1px solid #D4AF37; text-align:center;'>", unsafe_allow_html=True)
    d_input = st.date_input("தேதி:", current_now.date())
    t_input = st.time_input("நேரம் (Live):", current_now.time())
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- 3. Logic ----------------
def get_panchangam_details(jd_ut):
    months = ["சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி", "ஐப்பசி", "கார்த்திகை", "மார்கழி", "தை", "மாசி", "பங்குனி"]
    years = ["பிரபவ", "விபவ", "சுக்ல", "பிரமோதூத", "பிரஜோத்பத்தி", "ஆங்கீரச", "ஸ்ரீமுக", "பவ", "யுவ", "தாது", "ஈஸ்வர", "வெகுதானிய", "பிரமாதி", "விக்ரம", "விஷு", "சித்ரபானu", "சுபானு", "தாரண", "பார்த்திப", "விய", "சர்வஜித்", "சர்வதாரி", "விரோதி", "விக்ருதி", "கர", "நந்தன", "விஜய", "ஜய", "மன்மத", "துன்முகி", "ஹேவிளம்பி", "விளம்பி", "விகாரி", "சார்வரி", "பிலவ", "சுபகிருது", "சோபகிருது", "குரோதி", "விசுவாசு", "பரபாவ", "பிளவங்க", "கீலக", "சௌமிய", "சாதாரண", "விரோதகிருது", "பரிதாபி", "பிரமாதீச", "ஆனந்த", "ராட்சச", "நள", "பிங்கள", "காளயுக்தி", "சித்தார்த்தி", "ரௌத்திரி", "துன்மதி", "துந்துபி", "ருத்ரோத்காரி", "ரக்தாட்சி", "குரோதன", "அட்சய"]
    
    # Sun pos
    res, _ = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_SIDEREAL)
    sun_deg = res[0]
    month_idx = int(sun_deg / 30)
    
    # Tamil Date Calculation (Degrees in current rasi + 1)
    tamil_date = int(sun_deg % 30) + 1
    
    # Year Logic
    base_idx = 37 # Krodhi for 2024-25
    y_idx = (base_idx + (datetime.now().year - 2024)) % 60
    
    return f"{years[y_idx]} வருடம்", f"{months[month_idx]} {tamil_date}"

def get_full_chart(d, t):
    dt = datetime.combine(d, t)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    utc_h = dt.hour + dt.minute/60.0 + dt.second/3600.0 - 5.5
    jd_ut = swe.julday(dt.year, dt.month, dt.day, utc_h)

    y_txt, m_txt = get_panchangam_details(jd_ut)
    p_map = {swe.SUN: "சூரியன்", swe.MOON: "சந்திரன்", swe.MARS: "செவ்வாய்", swe.MERCURY: "புதன்", swe.JUPITER: "குரு", swe.VENUS: "சுக்கிரன்", swe.SATURN: "சனி", swe.MEAN_NODE: "ராகு"}
    
    res_pos = {}
    for pid, name in p_map.items():
        res, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        deg = res[0]
        vakra = " <span class='vakra-text'>(வ)</span>" if res[3] < 0 else ""
        idx = int(deg / 30)
        p_str = f"<div class='planet-text'>{name}{vakra} {int(deg%30)}°</div>"
        if idx not in res_pos: res_pos[idx] = []
        res_pos[idx].append(p_str)
        if pid == swe.MEAN_NODE:
            k_idx = (idx + 6) % 12
            if k_idx not in res_pos: res_pos[k_idx] = []
            res_pos[k_idx].append(f"<div class='planet-text'>கேது {int(deg%30)}°</div>")
            
    return res_pos, dt.strftime("%d-%m-%Y"), dt.strftime("%I:%M %p"), y_txt, m_txt

chart_data, f_date, f_time, y_info, m_info = get_full_chart(d_input, t_input)

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
                    <div class="tamil-main">{y_info}</div>
                    <div class="tamil-sub">{m_info}</div>
                    <div class="eng-dt">{f_date}</div>
                    <div class="eng-tm">{f_time}</div>
                    <div style="font-size:0.6em; color:#777; margin-top:5px;">திருக்கணித முறை (IST)</div>
                </div>
            </td>
            <td>{draw_box(3)}</td>
        </tr>
        <tr><td>{draw_box(9)}</td><td>{draw_box(4)}</td></tr>
        <tr><td>{draw_box(8)}</td><td>{draw_box(7)}</td><td>{draw_box(6)}</td><td>{draw_box(5)}</td></tr>
    </table>
</div>
""", unsafe_allow_html=True)
