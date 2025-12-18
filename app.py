import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder
import urllib.parse

# ---------- ஆப் அமைப்புகள் ----------
st.set_page_config(page_title="Ultra Precise Tamil Panchangam", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

# ---------- நிர்வாகி வாட்ஸ்அப் எண் ----------
ADMIN_WHATSAPP = "919876543210" 

# ---------- SESSION STATE ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- CSS வடிவமைப்பு (Full Visibility) ----------
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, span, div, label { color: #1a1a1a !important; font-family: 'Arial', sans-serif; }
    .header-style { color: #8B0000 !important; text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 2.2em; }
    
    /* லாகின் மற்றும் செட்டிங்ஸ் பாக்ஸ் */
    .main-box { 
        max-width: 600px; margin: auto; padding: 25px; 
        background: #fdfdfd; border-radius: 15px; 
        border: 2px solid #8B0000; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* அட்டவணை வடிவமைப்பு */
    .panchang-table {
        width: 100%; border-collapse: collapse; background: white;
        border-radius: 12px; overflow: hidden; border: 2px solid #8B0000;
        margin-top: 10px;
    }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 15px; text-align: left; }
    .panchang-table td { padding: 12px; border: 1px solid #ddd; color: #000 !important; font-weight: 600; }
    
    .stButton>button {
        background-color: #8B0000; color: white !important; 
        border-radius: 8px; font-weight: bold; width: 100%;
    }
    .special-note { 
        background-color: #FFF9C4; padding: 15px; border-radius: 10px; 
        border-left: 8px solid #FBC02D; margin-bottom: 20px; 
        color: #000 !important; font-weight: bold; text-align: center;
    }
    /* Input Visibility */
    .stSelectbox, .stDateInput { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIN / SIGNUP (Main Page) ----------------
if not st.session_state.logged_in:
    st.markdown("<h1 class='header-style'>🔱 Astro Guide Login</h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    
    mode = st.radio("தேர்வு செய்க", ["Login", "Sign Up"], horizontal=True)
    
    if mode == "Login":
        u_name = st.text_input("பயனர் பெயர் (Name)")
        u_pass = st.text_input("கடவுச்சொல் (Password)", type="password")
        if st.button("Login"):
            if u_name != "" and u_pass != "":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("விவரங்களை உள்ளிடவும்!")
    else:
        s_name = st.text_input("முழு பெயர்")
        s_phone = st.text_input("வாட்ஸ்அப் எண்")
        s_city = st.text_input("ஊர்")
        if st.button("Sign Up Request"):
            msg = urllib.parse.quote(f"புதிய பதிவு:\nபெயர்: {s_name}\nஎண்: {s_phone}\nஊர்: {s_city}")
            st.markdown(f'<a href="https://wa.me/{ADMIN_WHATSAPP}?text={msg}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; width:100%; cursor:pointer; font-weight:bold;">வாட்ஸ்அப்பில் விவரங்களை அனுப்பவும்</button></a>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- மெயின் பஞ்சாங்கம் ----------------

districts = {
    "அரியலூர்": [11.1401, 79.0786], "சென்னை": [13.0827, 80.2707], "கோயம்புத்தூர்": [11.0168, 76.9558],
    "கடலூர்": [11.7480, 79.7714], "தர்மபுரி": [12.1271, 78.1582], "திண்டுக்கல்": [10.3673, 77.9803],
    "ஈரோடு": [11.3410, 77.7172], "காஞ்சிபுரம்": [12.8342, 79.7036], "மதுரை": [9.9252, 78.1198],
    "நாகப்பட்டினம்": [10.7672, 79.8444], "நாமக்கல்": [11.2189, 78.1674], "புதுக்கோட்டை": [10.3797, 78.8202],
    "இராமநாதபுரம்": [9.3639, 78.8395], "சேலம்": [11.6643, 78.1460], "தஞ்சாவூர்": [10.7870, 79.1378],
    "திருச்சிராப்பள்ளி": [10.7905, 78.7047], "திருநெல்வேலி": [8.7139, 77.7567], "வேலூர்": [12.9165, 79.1325]
}

# --- SETTINGS ON MAIN PAGE ---
st.markdown("<h1 class='header-style'>🔱 தமிழ்நாடு திருக்கணிதப் பஞ்சாங்கம்</h1>", unsafe_allow_html=True)

st.markdown('<div class="main-box">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    selected_dist = st.selectbox("மாவட்டத்தைத் தேர்ந்தெடுக்கவும்:", list(districts.keys()))
with col2:
    selected_date = st.date_input("தேதியைத் தேர்ந்தெடுக்கவும்:", datetime.now(IST))

if st.button("Logout 🚪"):
    st.session_state.logged_in = False
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- கணக்கீடுகள் ---
lat, lon = districts[selected_dist]

def get_sunrise_sunset(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    city = LocationInfo(name="Selected", region="", timezone=tz_name, latitude=lat, longitude=lon)
    s = sun(observer=city.observer, date=date_obj, tzinfo=pytz.timezone(tz_name))
    return s["sunrise"].strftime("%I:%M %p"), s["sunset"].strftime("%I:%M %p")

def get_precise_panchang(date_obj, lat, lon):
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 0.0) 
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_topo(lon, lat, 0)
    def get_raw_astronomy(jd):
        m, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
        s, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)
        m_deg, s_deg = m[0], s[0]
        diff = (m_deg - s_deg) % 360
        return m_deg, s_deg, int(diff/12), int(m_deg/(360/27)), int(((m_deg+s_deg)%360)/(360/27)), int(diff/6)%11

    def find_boundary(jd_base, current_idx, calc_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid = (low + high) / 2
            _, _, t, n, _, _ = get_raw_astronomy(jd_base + mid)
            val = n if calc_type == "nak" else t
            if val == current_idx: low = mid
            else: high = mid
        return datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)

    m_start, s_start, t_now, n_now, y_now, k_now = get_raw_astronomy(jd_ut)
    t_end_dt = find_boundary(jd_ut, t_now, "tithi")
    n_end_dt = find_boundary(jd_ut, n_now, "nak")
    
    t_month = ["சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி", "ஐப்பசி", "கார்த்திகை", "மார்கழி", "தை", "மாசி", "பங்குனி"][int(s_start / 30) % 12]
    t_date = int(s_start % 30) + 1
    return {
        "m_deg": round(m_start, 2), "tamil": f"{t_month} {t_
