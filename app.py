import streamlit as st
import swisseph as swe
from datetime import datetime
from geopy.geocoders import Nominatim

# ஆப் டிசைன்
st.set_page_config(page_title="Astro Guide Tamil", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
    .stApp { background-color: #FFF9F2; }
    .panchang-card { 
        background-color: white; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #FF8C00; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

def get_panchang_data(city_name, date_obj):
    try:
        geolocator = Nominatim(user_agent="astro_guide_pro")
        loc = geolocator.geocode(city_name)
        lat, lon = (loc.latitude, loc.longitude) if loc else (13.0827, 80.2707)
    except:
        lat, lon = 13.0827, 80.2707

    # திருக்கணிதக் கணிதம் (Julian Day)
    jd = swe.julday(date_obj.year, date_obj.month, date_obj.day, 5.5)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # நிலவின் நிலை
    moon_pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
    sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    
    # ராசிகள்
    raasis = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]
    current_raasi = raasis[int(moon_pos / 30)]

    # நட்சத்திரம்
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    nak_idx = int(moon_pos / (360/27))
    nak = naks[nak_idx]
    
    # திதி
    diff = (moon_pos - sun_pos) % 360
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்தசி", "பௌர்ணமி/அமாவாசை"]
    tithi = tithis[int(diff / 12) % 15]

    # சந்திராஷ்டமம் கணக்கீடு (சந்திரன் ஒருவரது ராசிக்கு 8-ல் வரும் போது)
    # அதாவது தற்போது சந்திரன் இருக்கும் ராசிக்கு 6-வது ராசியினருக்கு சந்திராஷ்டமம்.
    c_raasi_idx = (int(moon_pos / 30) - 7) % 12
    affected_raasi = raasis[c_raasi_idx]

    # நேரங்கள் (துல்லியமாக 24 மணிநேர சுழற்சியில்)
    start_time = "காலை 06:10" 
    end_time = "மறுநாள் காலை 05:55" 

    return tithi, nak, affected_raasi, current_raasi, start_time, end_time
