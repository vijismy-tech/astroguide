import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

# ஆப் டிசைன்
st.set_page_config(page_title="Astro Guide Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; } 
    .panchang-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #E5C100;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .label-text { color: #5D4037; font-size: 1.1em; font-weight: bold; }
    .value-text { color: #1B5E20; font-size: 1.4em; font-weight: 800; }
    .time-text { color: #D84315; font-size: 1.1em; font-weight: bold; background: #FFF3E0; padding: 5px 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

def get_precise_data(city_name, date_obj):
    try:
        geolocator = Nominatim(user_agent="astro_pro_final_v1")
        loc = geolocator.geocode(city_name)
        lat, lon = (loc.latitude, loc.longitude) if loc else (13.0827, 80.2707)
    except:
        lat, lon = 13.0827, 80.2707

    jd_start = swe.julday(date_obj.year, date_obj.month, date_obj.day, 5.5)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    def get_moon_sun(jd):
        m = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
        s = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
        return m, s

    m_pos, s_pos = get_moon_sun(jd_start)
    
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்தசி", "பௌர்ணமி", "பிரதமை (தேய்பிறை)", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்தசி", "அமாவாசை"]

    curr_nak_idx = int(m_pos / (360/27))
    curr_tithi_idx = int(((m_pos - s_pos) % 360) / 12)
    
    # நேரம் கணக்கிடுதல் (முடிவு நேரம்)
    step = 0.01 
    t_jd = jd_start
    while int(((swe.calc_ut(t_jd, swe.MOON, swe.FLG_SIDEREAL)[0][0] - swe.calc_ut(t_jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]) % 360) / 12) == curr_tithi_idx:
        t_jd += step
        if t_jd > jd_start + 1: break
    
    end_dt = datetime.combine(date_obj, datetime.min.time()) + timedelta(days=(t_jd - jd_start) + 0.229)
    
    return {
        "tithi": tithis[curr_tithi_idx],
        "next_tithi": tithis[(curr_tithi_idx + 1) % 30],
        "nak": naks[curr_nak_idx],
        "end_time": end_dt.strftime("%I:%M %p")
    }

# --- UI ---
st.title("✨ அஸ்ட்ரோ கைடு - துல்லிய பஞ்சாங்கம்")

city = st.sidebar.text_input("📍 ஊர்:", "Chennai")
today = st.sidebar.date_input("🗓️ தேதி:", datetime.now())

# தரவுகளைப் பெறுதல்
result = get_precise_data(city, today)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="panchang-box">
        <h3 style="color: #4B0082;">🌙 திதி விபரம்</h3>
        <p class="label-text">இன்றைய திதி:</p>
        <p class="value-text">{result['tithi']}</p>
        <p class="time-text">🕒 முடிவு நேரம்: இன்று {result['end_time']} வரை</p>
        <div style="margin-top:15px; padding-top:10px; border-top:1px dashed #ccc;">
            <p style="color:#666;">இதற்குப் பின் தொடங்கும் திதி: <b>{result['next_tithi']}</b></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="panchang-box">
        <h3 style="color: #E65100;">⭐ நட்சத்திர விபரம்</h3>
        <p class="label-text">நட்சத்திரம்:</p>
        <p class="value-text">{result['nak']}</p>
        <p class="time-text">🕒 முடிவு நேரம்: இன்று {result['end_time']} வரை</p>
        <p style="margin-top:15px; color:#666; font-size:0.9em;">(நேரம் ஊருக்குத் தக்கபடி மாறுபடும்)</p>
    </div>
    """, unsafe_allow_html=True)
