import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

# ஆப் கட்டமைப்பு
st.set_page_config(page_title="Astro Guide Pro", layout="wide")

# துல்லியமான நேரக் கணக்கீட்டு இயந்திரம்
def get_precise_panchang(city_name, date_obj):
    try:
        geolocator = Nominatim(user_agent="astro_pro_v4")
        loc = geolocator.geocode(city_name)
        lat, lon = (loc.latitude, loc.longitude) if loc else (13.0827, 80.2707)
    except:
        lat, lon = 13.0827, 80.2707

    # Julian Day (காலை 5.30 மணி நேரப்படி)
    jd_start = swe.julday(date_obj.year, date_obj.month, date_obj.day, 5.5)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    def get_moon_sun(jd):
        m = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
        s = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
        return m, s

    m_pos, s_pos = get_moon_sun(jd_start)
    
    # பெயர்கள்
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்தசி", "பௌர்ணமி", "பிரதமை (கிருஷ்ண பட்சம்)", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்தசி", "அமாவாசை"]

    # தற்போதைய நட்சத்திரம் & திதி
    curr_nak_idx = int(m_pos / (360/27))
    curr_tithi_idx = int(((m_pos - s_pos) % 360) / 12)

    # முடிவு நேரக் கணக்கீடு (Iterative Accuracy)
    def find_end_time(jd, type="nak"):
        step = 0.02 # 30 நிமிடங்கள் தோராயமாக
        target_jd = jd
        for _ in range(100): # துல்லியத்தை அதிகப்படுத்த
            m, s = get_moon_sun(target_jd)
            if type == "nak":
                idx = int(m / (360/27))
                if idx != curr_nak_idx: break
            else:
                idx = int(((m - s) % 360) / 12)
                if idx != curr_tithi_idx: break
            target_jd += step
        
        # நேரத்தை மாற்றவும்
        return datetime.combine(date_obj, datetime.min.time()) + timedelta(days=(target_jd - jd_start) + 0.229)

    nak_end_dt = find_end_time(jd_start, "nak")
    tithi_end_dt = find_end_time(jd_start, "tithi")

    return {
        "nak": naks[curr_nak_idx],
        "next_nak": naks[(curr_nak_idx + 1) % 27],
        "nak_end": nak_end_dt.strftime("%I:%M %p"),
        "tithi": tithis[curr_tithi_idx],
        "next_tithi": tithis[(curr_tithi_idx + 1) % 30],
        "tithi_end": tithi_end_dt.strftime("%I:%M %p")
    }

# --- UI ---
st.title("🌟 அஸ்ட்ரோ கைடு - துல்லிய பஞ்சாங்கம்")
city = st.sidebar.text_input("ஊர்:", "Chennai")
today = st.sidebar.date_input("தேதி:", datetime.now())

res = get_precise_panchang(city, today)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style="background-color:#E8F5E9; padding:20px; border-radius:15px; border-left:8px solid #2E7D32;">
        <h3 style="color:#2E7D32;">🌙 திதி விபரம்</h3>
        <p>இன்றைய திதி: <b>{res['tithi']}</b></p>
        <p style="color:#D84315;">⏳ <b>முடியும் நேரம்: இன்று {res['tithi_end']} வரை</b></p>
        <hr>
        <p>அடுத்த திதி: {res['next_tithi']}</p>
        <p>தொடங்கும் நேரம்: {res['tithi_end']}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background-color:#FFF3E0; padding:20px; border-radius:15px; border-left:8px solid #EF6C00;">
        <h3 style="color:#EF6C00;">⭐ நட்சத்திர விபரம்</h3>
        <p>இன்றைய நட்சத்திரம்: <b>{res['nak']}</b></p>
        <p style="color:#D84315;">⏳ <b>முடியும் நேரம்: இன்று {res['nak_end']} வரை</b></p>
        <hr>
        <p>அடுத்த நட்சத்திரம்: {res['next_nak']}</p>
        <p>தொடங்கும் நேரம்: {res['nak_end']}</p>
    </div>
    """, unsafe_allow_html=True)
