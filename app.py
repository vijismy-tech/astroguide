import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder
import urllib.parse

# ---------- App Settings ----------
st.set_page_config(page_title="Tamil Precision Panchangam", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

ADMIN_WHATSAPP = "919876543210" 

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- CSS Design ----------
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, span, div, label { color: #1a1a1a !important; font-family: 'Arial', sans-serif; }
    .header-style { color: #8B0000 !important; text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 2.2em; }
    .main-box { 
        max-width: 800px; margin: auto; padding: 25px; 
        background: #fdfdfd; border-radius: 15px; 
        border: 2px solid #8B0000; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .panchang-table {
        width: 100%; border-collapse: collapse; background: white;
        border-radius: 12px; overflow: hidden; border: 2px solid #8B0000;
    }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 15px; text-align: left; }
    .panchang-table td { padding: 12px; border: 1px solid #ddd; color: #000 !important; font-weight: 600; }
    .special-note { 
        background-color: #FFF9C4; padding: 15px; border-radius: 10px; 
        border-left: 8px solid #FBC02D; margin-bottom: 20px; 
        color: #8B0000 !important; font-weight: bold; text-align: center; font-size: 1.3em;
    }
    .next-info { color: #5D4037 !important; font-size: 0.85em; font-weight: normal; font-style: italic; }
    .muhurtham-box { background-color: #E8F5E9; color: #2E7D32 !important; font-weight: bold; padding: 5px; border-radius: 5px; border: 1px solid #2E7D32; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIN / SIGNUP ----------------
if not st.session_state.logged_in:
    st.markdown("<h1 class='header-style'>🔱 Astro Guide Login</h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    mode = st.radio("தேர்வு செய்க", ["Login", "Sign Up"], horizontal=True)
    if mode == "Login":
        u_name = st.text_input("பெயர் (Name)")
        u_pass = st.text_input("கடவுச்சொல் (Password)", type="password")
        if st.button("Login"):
            if u_name != "" and u_pass != "": st.session_state.logged_in = True; st.rerun()
            else: st.error("விவரங்களை உள்ளிடவும்!")
    else:
        s_name = st.text_input("முழு பெயர்")
        s_phone = st.text_input("வாட்ஸ்அப் எண்")
        if st.button("Sign Up Request"):
            msg = urllib.parse.quote(f"புதிய பதிவு:\nபெயர்: {s_name}\nஎண்: {s_phone}")
            st.markdown(f'<a href="https://wa.me/{ADMIN_WHATSAPP}?text={msg}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; width:100%; cursor:pointer; font-weight:bold;">வாட்ஸ்அப்பில் அனுப்பவும்</button></a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- தரவு ----------------
districts = {
    "அரியலூர்": [11.14, 79.08], "சென்னை": [13.08, 80.27], "கோயம்புத்தூர்": [11.02, 76.96],
    "மதுரை": [9.93, 78.12], "திருச்சிராப்பள்ளி": [10.79, 78.70], "திருநெல்வேலி": [8.71, 77.76],
    "சேலம்": [11.66, 78.15], "தஞ்சாவூர்": [10.79, 79.14], "வேலூர்": [12.92, 79.13]
}

st.markdown("<h1 class='header-style'>🔱 தமிழ்நாடு திருக்கணிதப் பஞ்சாங்கம்</h1>", unsafe_allow_html=True)
st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: selected_dist = st.selectbox("மாவட்டத்தைத் தேர்ந்தெடுக்கவும்:", list(districts.keys()))
with c2: selected_date = st.date_input("தேதியைத் தேர்ந்தெடுக்கவும்:", datetime.now(IST))
if st.button("Logout 🚪"): st.session_state.logged_in = False; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

lat, lon = districts[selected_dist]

# --- Sunrise, Sunset & Abhijit ---
def get_sun_data(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    city = LocationInfo(name="Loc", region="", timezone=tz_name, latitude=lat, longitude=lon)
    s = sun(observer=city.observer, date=date_obj, tzinfo=pytz.timezone(tz_name))
    sunrise, sunset = s["sunrise"], s["sunset"]
    
    midday = sunrise + (sunset - sunrise) / 2
    # அபிஜித் முகூர்த்தம் - நண்பகலுக்கு முன் பின் 24 நிமிடங்கள்
    abhijit_start = midday - timedelta(minutes=24)
    abhijit_end = midday + timedelta(minutes=24)
    
    return {
        "sunrise": sunrise.strftime("%I:%M %p"),
        "sunset": sunset.strftime("%I:%M %p"),
        "abhijit": f"{abhijit_start.strftime('%I:%M %p')} - {abhijit_end.strftime('%I:%M %p')}"
    }

def get_precise_panchang(date_obj, lat, lon):
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 0.0) 
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_topo(lon, lat, 0)
    
    def get_raw_astro(jd):
        m, _ = swe.calc_ut(jd, 1, swe.FLG_SIDEREAL)
        s, _ = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)
        m_deg, s_deg = m[0], s[0]
        diff = (m_deg - s_deg) % 360
        return m_deg, s_deg, int(diff/12), int(m_deg/(360/27)), int(((m_deg+s_deg)%360)/(360/27)), int(diff/6)%11

    def find_boundary(jd_base, current_idx, c_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid = (low + high) / 2
            _, _, t, n, _, _ = get_raw_astro(jd_base + mid)
            val = n if c_type == "nak" else t
            if val == current_idx: low = mid
            else: high = mid
        return datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)

    m_s, s_s, t_n, n_n, y_n, k_n = get_raw_astro(jd_ut)
    t_end = find_boundary(jd_ut, t_n, "tithi")
    n_end = find_boundary(jd_ut, n_n, "nak")
    
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    
    special_msg = "இன்று விசேஷங்கள் இல்லை"
    if t_n == 14: special_msg = "🌟 இன்று அமாவாசை / பௌர்ணமி"
    elif t_n == 12: special_msg = "🔱 இன்று பிரதோஷம்"

    return {
        "m_deg": round(m_s, 2), 
        "tamil": f"{['சித்திரை', 'வைகாசி', 'ஆனி', 'ஆடி', 'ஆவணி', 'புரட்டாசி', 'ஐப்பசி', 'கார்த்திகை', 'மார்கழி', 'தை', 'மாசி', 'பங்குனி'][int(s_s/30)%12]} {int(s_s%30)+1}",
        "wara": ["திங்கட்கிழமை", "செவ்வாய்க்கிழமை", "புதன்கிழமை", "வியாழக்கிழமை", "வெள்ளிக்கிழமை", "சனிக்கிழமை", "ஞாயிற்றுக்கிழமை"][date_obj.weekday()],
        "tithi": tithis[t_n % 30], "t_end": t_end.strftime("%I:%M %p"), "next_t": tithis[(t_n + 1) % 30],
        "nak": naks[n_n % 27], "n_end": n_end.strftime("%I:%M %p"), "next_n": naks[(n_n + 1) % 27],
        "yog": ["விஷ்கம்பம்", "ப்ரீதி", "ஆயுஷ்மான்", "சௌபாக்கியம்", "சோபனம்", "அதிகண்டம்", "சுகர்மம்", "திருதி", "சூலம்", "கண்டம்", "விருத்தி", "துருவம்", "வியாகாதம்", "ஹர்ஷணம்", "வஜ்ரம்", "சித்தி", "வியதீபாதம்", "வரியான்", "பரிகம்", "சிவம்", "சித்தம்", "சாத்தியம்", "சுபம்", "சுப்பிரம்", "பிராமியம்", "ஐந்தரம்", "வைதிருதி"][y_n % 27],
        "kar": ["பவம்", "பாலவம்", "கௌலவம்", "சைதிலை", "கரசை", "வணிசை", "பத்திரை", "சகுனி", "சதுஷ்பாதம்", "நாகவம்", "கிம்ஸ்துக்னம்"][k_n % 11],
        "rahu": ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][date_obj.weekday()],
        "special": special_msg
    }

p = get_precise_panchang(selected_date, lat, lon)
sd = get_sun_data(selected_date, lat, lon)

st.markdown(f"<div class='special-note'>{p['special']}</div>", unsafe_allow_html=True)

st.markdown(f"""
<table class="panchang-table">
    <tr><th>அங்கம்</th><th>விவரம் ({selected_dist})</th></tr>
    <tr><td>📅 <b>தமிழ் தேதி</b></td><td><b>{p['tamil']}</b> | {p['wara']}</td></tr>
    <tr><td>✨ <b>அபிஜித் முகூர்த்தம்</b></td><td><span class='muhurtham-box'>{sd['abhijit']}</span></td></tr>
    <tr><td>🌙 <b>திதி</b></td><td><b>{p['tithi']}</b> (முடிவு: {p['t_end']})<br><span class='next-info'>அடுத்த திதி: {p['next_t']}</span></td></tr>
    <tr><td>⭐ <b>நட்சத்திரம்</b></td><td><b>{p['nak']}</b> (முடிவு: {p['n_end']})<br><span class='next-info'>அடுத்த நட்சத்திரம்: {p['next_n']}</span></td></tr>
    <tr><td>🌅 <b>சூரிய உதயம் / அஸ்தமனம்</b></td><td>உதயம்: {sd['sunrise']} | அஸ்தமனம்: {sd['sunset']}</td></tr>
    <tr><td>🚫 <b>ராகு காலம்</b></td><td>{p['rahu']}</td></tr>
    <tr><td>♈ <b>யோகம் / கரணம்</b></td><td>{p['yog']} | {p['kar']}</td></tr>
    <tr><td>📊 <b>நிலவின் பாகை</b></td><td>{p['m_deg']}°</td></tr>
</table>
""", unsafe_allow_html=True)
