import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

st.set_page_config(page_title="Astro Guide Pro", layout="wide")

def get_super_detailed_panchang(city_name, date_obj):
    try:
        geolocator = Nominatim(user_agent="astro_pro_v3")
        loc = geolocator.geocode(city_name)
        lat, lon = (loc.latitude, loc.longitude) if loc else (13.0827, 80.2707)
    except:
        lat, lon = 13.0827, 80.2707

    jd = swe.julday(date_obj.year, date_obj.month, date_obj.day, 5.5)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # Moon calculation
    moon_pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
    
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    raasis = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]
    
    # Current Status
    curr_nak_idx = int(moon_pos / (360/27))
    curr_nak = naks[curr_nak_idx]
    curr_raasi_idx = int(moon_pos / 30)
    curr_raasi = raasis[curr_raasi_idx]
    
    # Timing - Current Nakshatra ends
    deg_left = ((curr_nak_idx + 1) * (360/27)) - moon_pos
    hours_to_end = deg_left / 0.55 
    end_time_dt = datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5 + hours_to_end)
    end_time_str = end_time_dt.strftime("%I:%M %p")

    # Next Nakshatra
    next_nak = naks[(curr_nak_idx + 1) % 27]

    # --- Chandrashtama Logic ---
    # Chandra in Vrichigam (7) means Chandrashtama for Mithunam (2)
    aff_raasi_idx = (curr_raasi_idx - 5) % 12
    aff_raasi = raasis[aff_raasi_idx]
    
    # Chandrashtama Nakshatram:
    # Chandra current star is Chandrashtama for the star that is 17 places behind.
    aff_nak_idx = (curr_nak_idx - 16) % 27
    aff_nak = naks[aff_nak_idx]

    return curr_nak, end_time_str, next_nak, aff_raasi, aff_nak

# --- UI Interface ---
st.title("🌟 அஸ்ட்ரோ கைடு - துல்லிய விபரங்கள்")
city = st.sidebar.text_input("ஊர்:", "Chennai")
today = st.sidebar.date_input("தேதி:", datetime.now())

c_nak, c_end, n_nak, a_raasi, a_nak = get_super_detailed_panchang(city, today)

# Display Cards
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 15px; border-top: 5px solid green;">
        <h3 style="color: green;">⭐ நட்சத்திர விபரம்</h3>
        <p>இன்றைய நட்சத்திரம்: <b>{c_nak}</b></p>
        <p style="color: blue;">🕒 <b>முடியும் நேரம்: {c_end}</b> வரை</p>
        <hr>
        <p>அடுத்த நட்சத்திரம்: <b>{n_nak}</b></p>
        <p>🕒 <b>தொடங்கும் நேரம்: {c_end}</b></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background-color: #fff5f5; padding: 20px; border-radius: 15px; border-top: 5px solid red;">
        <h3 style="color: red;">⚠️ சந்திராஷ்டம விபரம்</h3>
        <p>பாதிக்கப்படும் ராசி: <b>{a_raasi}</b></p>
        <p>பாதிக்கப்படும் நட்சத்திரம்: <b>{a_nak}</b></p>
        <p style="color: darkred;">🕒 <b>எச்சரிக்கை நேரம்: {c_end} வரை</b></p>
        <p style="font-size: 0.8em; color: gray;">(குறிப்பு: இன்று சந்திரன் {c_nak} நட்சத்திரத்தில் சஞ்சரிப்பதால், {a_nak} நட்சத்திரத்தில் பிறந்தவர்களுக்கு சந்திராஷ்டமம் நடக்கிறது.)</p>
    </div>
    """, unsafe_allow_html=True)
