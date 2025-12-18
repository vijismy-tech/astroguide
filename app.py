import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

# ஆப் அமைப்பு
st.set_page_config(page_title="Astro Guide Pro", layout="wide")

# துல்லியமான கணக்கீட்டு இயந்திரம்
def get_detailed_panchang(city_name, date_obj):
    try:
        geolocator = Nominatim(user_agent="astro_pro_detail")
        loc = geolocator.geocode(city_name)
        lat, lon = (loc.latitude, loc.longitude) if loc else (13.0827, 80.2707)
    except:
        lat, lon = 13.0827, 80.2707

    # ஜூலியன் நாள் கணக்கீடு
    jd = swe.julday(date_obj.year, date_obj.month, date_obj.day, 5.5)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # நிலவின் தற்போதைய நிலை
    moon_pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
    
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    raasis = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]
    
    # தற்போதைய நட்சத்திரம் மற்றும் ராசி
    curr_nak_idx = int(moon_pos / (360/27))
    curr_nak = naks[curr_nak_idx]
    curr_raasi = raasis[int(moon_pos / 30)]
    
    # சந்திராஷ்டம ராசி கணக்கீடு (சந்திரன் ஒருவரது ராசிக்கு 8-ல் வரும் நேரம்)
    c_raasi_idx = (int(moon_pos / 30) - 7) % 12
    c_raasi = raasis[c_raasi_idx]

    # நேரம் கணக்கிடுதல் (தோராயமாக நிலவின் வேகத்தை வைத்து)
    deg_left = ((curr_nak_idx + 1) * (360/27)) - moon_pos
    hours_left = deg_left / 0.55  # நிலவின் வேகம் ஒரு மணி நேரத்திற்கு 0.55 டிகிரி
    
    # முடியும் நேரம்
    end_dt = datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5 + hours_left)
    end_time_str = end_dt.strftime("%I:%M %p") # மணி:நிமிடம் வடிவம்
    
    next_nak = naks[(curr_nak_idx + 1) % 27]

    return {
        "nak": curr_nak,
        "raasi": curr_raasi,
        "c_raasi": c_raasi,
        "end_time": end_time_str,
        "next_nak": next_nak
    }

# --- பயனர் இடைமுகம் (UI) ---
st.sidebar.title("🌟 Astro Guide")
city = st.sidebar.text_input("ஊர் பெயரை உள்ளிடவும்:", "Chennai")
today = st.sidebar.date_input("தேதியைத் தேர்ந்தெடுக்கவும்:", datetime.now())

data = get_detailed_panchang(city, today)

st.markdown(f"<h1 style='text-align: center; color: #8B4513;'>📊 துல்லியமான பஞ்சாங்க விபரங்கள்</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border-top: 5px solid #4B0082; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
        <h3 style="color: #4B0082;">✨ நட்சத்திர விபரம்</h3>
        <p style="font-size: 1.2em;"><b>இன்றைய நட்சத்திரம்:</b> <span style="color: #006400;">{data['nak']}</span></p>
        <p style="font-size: 1.1em; background-color: #F0F8FF; padding: 10px; border-radius: 5px;">
            🕒 <b>முடியும் நேரம்:</b> <span style="color: blue;">இன்று {data['end_time']} வரை</span>
        </p>
        <hr>
        <p><b>அடுத்த நட்சத்திரம்:</b> {data['next_nak']}</p>
        <p><b>தொடங்கும் நேரம்:</b> {data['end_time']}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border-top: 5px solid #D32F2F; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
        <h3 style="color: #D32F2F;">⚠️ சந்திராஷ்டம எச்சரிக்கை</h3>
        <p style="font-size: 1.2em;"><b>சந்திராஷ்டம ராசி:</b> <span style="font-size: 1.5em; color: red; font-weight: bold;">{data['c_raasi']}</span></p>
        <p><b>நட்சத்திரம்:</b> {data['nak']}</p>
        <p style="background-color: #FFEBEE; padding: 10px; border-radius: 5px;">
            ⏰ <b>நேரம்:</b> {data['end_time']} வரை இந்த ராசியினருக்கு எச்சரிக்கை தேவை.
        </p>
        <p style="font-size: 0.9em; color: #555; margin-top: 10px;">
            <i>*குறிப்பு: இந்த ராசியினர் புதிய முயற்சிகள் மற்றும் பயணங்களைத் தவிர்ப்பது நலம்.</i>
        </p>
    </div>
    """, unsafe_allow_html=True)
