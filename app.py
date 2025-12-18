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

# --- Calculation Engine ---
def get_panchang_data(city_name, date_obj):
    try:
        geolocator = Nominatim(user_agent="astro_guide_pro")
        loc = geolocator.geocode(city_name)
        lat, lon = (loc.latitude, loc.longitude) if loc else (13.0827, 80.2707)
    except:
        lat, lon = 13.0827, 80.2707 # Default Chennai

    # Julian Day at 5:30 AM IST
    jd = swe.julday(date_obj.year, date_obj.month, date_obj.day, 5.5)
    swe.set_sid_mode(swe.SIDM_LAHIRI) # திருக்கணித முறை
    
    sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    moon_pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
    
    # நட்சத்திரம்
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    nak_idx = int(moon_pos / (360/27))
    nak = naks[nak_idx]
    
    # திதி
    diff = (moon_pos - sun_pos) % 360
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்தசி", "பௌர்ணமி/அமாவாசை"]
    tithi = tithis[int(diff / 12) % 15]

    # சந்திராஷ்டமம் (17th Star)
    chandrashtama_idx = (nak_idx + 16) % 27
    chandrashtama_star = naks[chandrashtama_idx]
    
    return tithi, nak, chandrashtama_star, lat, lon

# --- UI ---
st.sidebar.title("🌟 Astro Guide")
menu = ["முகப்பு", "🏹 ஜாமக்கோள்", "🎓 கற்றல் மையம்", "📞 ஆலோசனை"]
choice = st.sidebar.radio("பக்கங்கள்", menu)
if choice == "முகப்பு":
    st.title("🗓️ தினசரி பஞ்சாங்கம்")
    
    # ஒரு அழகான கார்டு போன்ற அமைப்பு
    with st.container():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 📅 தேதி தேர்வு")
            # தேதி மாற்றும் ஐகான் மற்றும் பெட்டி
            today = st.date_input("", datetime.now(), help="தேதியை மாற்ற இங்கே கிளிக் செய்யவும்")
            
            city = st.text_input("📍 ஊர் (City):", "Chennai")
            tithi, nak, c_star, lat, lon = get_panchang_data(city, today)
            
        with col2:
            st.markdown(f"""
            <div style="background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #FFD700; text-align: center;">
                <h2 style="color: #FF8C00; margin-bottom: 5px;">{city} - பஞ்சாங்கம்</h2>
                <p style="font-size: 1.1em; color: #555;">{today.strftime('%d %B, %Y')}</p>
                <hr style="border: 0.5px solid #eee;">
                <div style="display: flex; justify-content: space-around;">
                    <div>
                        <p style="margin:0; color: gray;">திதி</p>
                        <h4 style="color: #4B0082;">🌙 {tithi}</h4>
                    </div>
                    <div>
                        <p style="margin:0; color: gray;">நட்சத்திரம்</p>
                        <h4 style="color: #006400;">⭐ {nak}</h4>
                    </div>
                </div>
                <div style="margin-top: 20px; padding: 10px; background-color: #FFF0F0; border-radius: 10px;">
                    <p style="margin:0; color: #D32F2F; font-weight: bold;">⚠️ சந்திராஷ்டமம்</p>
                    <h4 style="color: #D32F2F;">{c_star}</h4>
                </div>
            </div>
            """, unsafe_allow_html=True)
