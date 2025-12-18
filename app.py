import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder
import urllib.parse

# ---------- ஆப் அமைப்புகள் ----------
st.set_page_config(page_title="AstroGuide Panchangam", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

ADMIN_WHATSAPP = "919876543210" 

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- CSS வடிவமைப்பு (Small & Neat Fonts) ----------
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    
    /* எழுத்து அளவுகளைக் குறைத்தல் */
    h1, h2, h3, p, span, div, label, td, th { 
        color: #1a1a1a !important; 
        font-family: 'Segoe UI', sans-serif;
    }
    
    .header-style { 
        color: #8B0000 !important; 
        text-align: center; 
        font-weight: bold; 
        margin-top: -30px;
        margin-bottom: 5px; 
        font-size: 1.2em; /* தலைப்பு சிறியதாக்கப்பட்டுள்ளது */
    }
    
    .main-box { 
        max-width: 480px; margin: auto; padding: 12px; 
        background: #fdfdfd; border-radius: 8px; 
        border: 1px solid #8B0000; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    
    /* அட்டவணை - மிகக் கச்சிதமான அளவு */
    .panchang-table {
        width: 100%; border-collapse: collapse; background: white;
        border-radius: 5px; overflow: hidden; border: 1px solid #8B0000;
        font-size: 0.82em; /* எழுத்துக்கள் சிறியதாக மாற்றப்பட்டது */
    }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 8px; text-align: center; font-size: 0.9em; }
    .panchang-table td { padding: 6px 10px; border: 1px solid #eee; color: #000 !important; }
    
    .stButton>button { 
        background-color: #8B0000; color: white !important; 
        font-size: 0.85em; padding: 5px; height: 35px;
    }
    
    .special-note { 
        background-color: #FFF9C4; padding: 8px; border-radius: 5px; 
        border-left: 4px solid #FBC02D; margin-bottom: 10px; 
        color: #8B0000 !important; font-weight: bold; text-align: center; font-size: 0.85em;
    }
    
    .next-info { color: #8B0000 !important; font-size: 0.75em; font-style: italic; }
    .muhurtham-box { color: #2E7D32 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIN / SIGNUP ----------------
if not st.session_state.logged_in:
    st.markdown("<h1 class='header-style'>🔱 AstroGuide Login</h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    mode = st.radio("தேர்வு செய்க", ["Login", "Sign Up"], horizontal=True)
    if mode == "Login":
        u_name = st.text_input("பெயர்")
        u_pass = st.text_input("கடவுச்சொல்", type="password")
        if st.button("Login"):
            if u_name != "" and u_pass != "": st.session_state.logged_in = True; st.rerun()
            else: st.error("விவரங்களை உள்ளிடவும்!")
    else:
        s_name = st.text_input("முழு பெயர்")
        s_phone = st.text_input("வாட்ஸ்அப் எண்")
        if st.button("Sign Up"):
            msg = urllib.parse.quote(f"AstroGuide Request: {s_name} - {s_phone}")
            st.markdown(f'<a href="https://wa.me/{ADMIN_WHATSAPP}?text={msg}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; width:100%; cursor:pointer; font-weight:bold;">வாட்ஸ்அப்பில் அனுப்பவும்</button></a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- தரவு ----------------
districts = {
    "சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70],
    "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]
}

st.markdown("<h1 class='header-style'>🔱 AstroGuide திருக்கணிதப் பஞ்சாங்கம்</h1>", unsafe_allow_html=True)

st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: selected_dist = st.selectbox("மாவட்டம்:", list(districts.keys()))
with c2: selected_date = st.date_input("தேதி:", datetime.now(IST))
if st.button("Logout 🚪"): st.session_state.logged_in = False; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

lat, lon = districts[selected_dist]

# --- கணக்கீடுகள் (உங்களின் 35-Iteration முறை) ---
def get_panchang_details(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=pytz.timezone(tz_name))
    mid = s["sunrise"] + (s["sunset"] - s["sunrise"]) / 2
    
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 0.0)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    def get_raw(jd):
        m, _ = swe.calc_ut(jd, 1, swe.FLG_SIDEREAL); sun_p, _ = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)
        diff = (m[0] - sun_p[0]) % 360
        return m[0], sun_p[0], int(diff/12), int(m[0]/(360/27))

    def find_end(jd_base, current_idx, c_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid_val = (low + high) / 2
            _, _, t, n = get_raw(jd_base + mid_val)
            if (n if c_type == "nak" else t) == current_idx: low = mid_val
            else: high = mid_val
        return (datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)).strftime("%I:%M %p")

    m_d, s_d, t_n, n_n = get_raw(jd_ut)
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    
    wara = ["திங்கட்கிழமை", "செவ்வாய்க்கிழமை", "புதன்கிழமை", "வியாழக்கிழமை", "வெள்ளிக்கிழமை", "சனிக்கிழமை", "ஞாயிற்றுக்கிழமை"][date_obj.weekday()]

    return {
        "tamil": f"{['சித்திரை', 'வைகாசி', 'ஆனி', 'ஆடி', 'ஆவணி', 'புரட்டாசி', 'ஐப்பசி', 'கார்த்திகை', 'மார்கழி', 'தை', 'மாசி', 'பங்குனி'][int(s_d/30)%12]} {int(s_d%30)+1}",
        "sunrise": s["sunrise"].strftime("%I:%M %p"), "sunset": s["sunset"].strftime("%I:%M %p"),
        "abhijit": f"{(mid - timedelta(minutes=24)).strftime('%I:%M %p')} - {(mid + timedelta(minutes=24)).strftime('%I:%M %p')}",
        "tithi": tithis[t_n % 30], "t_end": find_end(jd_ut, t_n, "tithi"), "next_t": tithis[(t_n + 1) % 30],
        "nak": naks[n_n % 27], "n_end": find_end(jd_ut, n_n, "nak"), "next_n": naks[(n_n + 1) % 27],
        "wara": wara, "deg": round(m_d, 2),
        "rahu": ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][date_obj.weekday()]
    }

p = get_panchang_details(selected_date, lat, lon)

st.markdown(f"""
<table class="panchang-table">
    <tr><th colspan="2">AstroGuide - {selected_dist} ({p['wara']})</th></tr>
    <tr><td>📅 <b>தமிழ் தேதி</b></td><td>{p['tamil']}</td></tr>
    <tr><td>🌅 <b>உதயம்/அஸ்தமனம்</b></td><td>{p['sunrise']} / {p['sunset']}</td></tr>
    <tr><td>✨ <b>அபிஜித்</b></td><td><span class='muhurtham-box'>{p['abhijit']}</span></td></tr>
    <tr><td>🌙 <b>திதி</b></td><td><b>{p['tithi']}</b> ({p['t_end']})<br><span class='next_info'>அடுத்து: {p['next_t']}</span></td></tr>
    <tr><td>⭐ <b>நட்சத்திரம்</b></td><td><b>{p['nak']}</b> ({p['n_end']})<br><span class='next_info'>அடுத்து: {p['next_n']}</span></td></tr>
    <tr><td>🚫 <b>ராகு காலம்</b></td><td>{p['rahu']}</td></tr>
    <tr><td>📊 <b>நிலவின் பாகை</b></td><td>{p['deg']}°</td></tr>
</table>
""", unsafe_allow_html=True)
