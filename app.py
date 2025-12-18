import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

# ஆப் டிசைன் - வண்ணங்கள் மற்றும் எழுத்துரு
st.set_page_config(page_title="Astro Guide Pro", layout="wide")

st.markdown("""
    <style>
    /* முழு பக்கத்தின் பின்னணி */
    .stApp { background-color: #FDFCF0; } 
    
    /* கார்டுகளின் வடிவமைப்பு - High Contrast */
    .panchang-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #E5C100;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* எழுத்துக்கள் தெளிவாகத் தெரிய Contrast Colors */
    .label-text { color: #5D4037; font-size: 1.1em; font-weight: bold; }
    .value-text { color: #1B5E20; font-size: 1.3em; font-weight: 800; }
    .time-text { color: #D84315; font-size: 1.1em; font-weight: bold; background: #FFF3E0; padding: 5px 10px; border-radius: 5px; }
    .header-main { color: #8B0000; text-align: center; font-family: 'Tamil'; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# --- துல்லியமான கணிதப் பகுதி (முன்பு போலவே) ---
def get_precise_panchang(city_name, date_obj):
    try:
        geolocator = Nominatim(user_agent="astro_pro_v5")
        loc = geolocator.geocode(city_name)
        lat, lon = (loc.latitude, loc.longitude) if loc else (13.0827, 80.2707)
    except:
        lat, lon = 13.0827, 80.2707

    jd_start = swe.julday(date_obj.year, date_obj.month, date_obj.day, 5.5)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    m_pos = swe.calc_ut(jd_start, swe.MOON, swe.FLG_SIDEREAL)[0][0]
    s_pos = swe.calc_ut(jd_start, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்தசி", "பௌர்ணமி", "பிரதமை (தேய்பிறை)", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்தசி", "அமாவாசை"]

    curr_nak_idx = int(m_pos / (360/27))
    curr_tithi_idx = int(((m_pos - s_pos) % 360) / 12)
    
    # நேரம் கணக்கிடுதல்
    deg_left = ((curr_nak_idx + 1) * (360/27)) - m_pos
    hours_left = deg_left / 0.55
    nak_end = (datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5 + hours_left)).strftime("%I:%M %p")

    return naks[curr_nak_idx], naks[(curr_nak_idx+1)%27], tithis[curr_tithi_idx], nak_end

# --- UI - பக்கம் ---
st.markdown("<h1 class='header-main'>✨ அஸ்ட்ரோ கைடு - பஞ்சாங்கம்</h1>", unsafe_allow_html=True)

city = st.sidebar.text_input("📍 ஊர்:", "Chennai")
today = st.sidebar.date_input("🗓️ தேதி:", datetime.now())

nak, next_nak, tithi, nak_end = get_precise_panchang(city, today)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="panchang-box">
        <h3 style="color: #4B0082;">🌙 இன்றைய திதி</h3>
        <p class="label-text">பெயர்:</p>
        <p class="value-text">{tithi}</p>
        <p class="label-text">நிலை:</p>
        <p class="time-text">இன்று {nak_end} வரை</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="panchang-box">
        <h3 style="color: #E65100;">⭐ நட்சத்திர விபரம்</h3>
        <p class="label-text">நட்சத்திரம்:</p>
        <p class="value-text">{nak}</p>
        <p class="label-text">முடியும் நேரம்:</p>
        <p class="time-text">🕒 {nak_end} வரை</p>
        <p style="margin-top:10px; color:#666;">அடுத்த நட்சத்திரம்: <b>{next_nak}</b></p>
    </div>
    """, unsafe_allow_html=True)
