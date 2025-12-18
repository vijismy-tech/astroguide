import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder
import urllib.parse

# ---------- ஆப் அமைப்புகள் ----------
st.set_page_config(page_title="Tamil Precision Panchangam", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

ADMIN_WHATSAPP = "919876543210" 

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- CSS வடிவமைப்பு ----------
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
        margin-top: 10px;
    }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 15px; text-align: left; }
    .panchang-table td { padding: 12px; border: 1px solid #ddd; color: #000 !important; font-weight: 600; }
    .stButton>button { background-color: #8B0000; color: white !important; border-radius: 8px; font-weight: bold; width: 100%; }
    .special-note { 
        background-color: #FFF9C4; padding: 15px; border-radius: 10px; 
        border-left: 8px solid #FBC02D; margin-bottom: 20px; 
        color: #8B0000 !important; font-weight: bold; text-align: center; font-size: 1.3em;
    }
    .sub-text { color: #444 !important; font-size: 0.85em; font-weight: normal; display: block; }
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

# ---------------- மாவட்டங்கள் ----------------
districts = {
    "அரியலூர்": [11.1401, 79.0786], "சென்னை": [13.0827, 80.2707], "கோயம்புத்தூர்": [11.0168, 76.9558],
    "கடலூர்": [11.7480, 79.7714], "தர்மபுரி": [12.1271, 78.1582], "திண்டுக்கல்": [10.3673, 77.9803],
    "ஈரோடு": [11.3410, 77.7172], "காஞ்சிபுரம்": [12.8342, 79.7036], "மதுரை": [9.9252, 78.1198],
    "நாகப்பட்டினம்": [10.7672, 79.8444], "நாமக்கல்": [11.2189, 78.1674], "புதுக்கோட்டை": [10.3797, 78.8202],
    "இராமநாதபுரம்": [9.3639, 78.8395], "சேலம்": [11.6643, 78.1460], "தஞ்சாவூர்": [10.7870, 79.1378],
    "திருச்சிராப்பள்ளி": [10.7905, 78.7047], "திருநெல்வேலி": [8.7139, 77.7567], "வேலூர்": [12.9165, 79.1325]
}

st.markdown("<h1 class='header-style'>🔱 தமிழ்நாடு திருக்கணிதப் பஞ்சாங்கம்</h1>", unsafe_allow_html=True)
st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: selected_dist = st.selectbox("மாவட்டத்தைத் தேர்ந்தெடுக்கவும்:", list(districts.keys()))
with c2: selected_date = st.date_input("தேதியைத் தேர்ந்தெடுக்கவும்:", datetime.now(IST))
if st.button("Logout 🚪"): st.session_state.logged_in = False; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- கணக்கீடுகள் ----------------
lat, lon = districts[selected_dist]

def get_sunrise_sunset(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    city = LocationInfo(name="Loc", region="", timezone=tz_name, latitude=lat, longitude=lon)
    s = sun(observer=city.observer, date=date_obj, tzinfo=pytz.timezone(tz_name))
    return s["sunrise"].strftime("%I:%M %p"), s["sunset"].strftime("%I:%M %p")

def get_precise_panchang(date_obj, lat, lon):
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 0.0) 
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_topo(lon, lat, 0)
    
    def get_raw_astro(jd):
        m, _ = swe.calc_ut(jd, 1, swe.FLG_SIDEREAL)
        s, _ = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)
        m_deg, s_deg = m[0], s[0]
        diff = (m_deg - s_deg) % 360
        t_idx = int(diff/12)
        n_idx = int(m_deg/(360/27))
        y_idx = int(((m_deg+s_deg)%360)/(360/27))
        k_idx = int(diff/6)%11
        return m_deg, s_deg, t_idx, n_idx, y_idx, k_idx

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
    t_boundary = find_boundary(jd_ut, t_n, "tithi")
    n_boundary = find_boundary(jd_ut, n_n, "nak")
    
    special_msg = "இன்று சாதாரண நாள்"
    if t_n == 14: special_msg = "🌟 இன்று பௌர்ணமி / அமாவாசை - வழிபாடு சிறப்பு!"
    elif t_n == 12: special_msg = "🔱 இன்று பிரதோஷம் - சிவ வழிபாடு நலம் தரும்!"
    elif t_n == 10: special_msg = "🕉️ இன்று ஏகாதசி - பெருமாள் வழிபாடு சிறப்பு!"
    elif t_n == 3: special_msg = "🐘 இன்று சங்கடஹர சதுர்த்தி - விநாயகர் வழிபாடு சிறப்பு!"
    elif t_n == 5: special_msg = "🔥 இன்று சஷ்டி விரதம் - முருகப் பெருமான் வழிபாடு சிறப்பு!"
    elif n_n == 3: special_msg = "🕉️ இன்று ரோகிணி நட்சத்திரம் - கிருஷ்ணர் வழிபாடு சிறப்பு!"
    elif n_n == 5: special_msg = "🔱 இன்று திருவாதிரை நட்சத்திரம் - நடராஜர் வழிபாடு சிறப்பு!"

    return {
        "m_deg": round(m_s, 2), 
        "tamil": f"{['சித்திரை', 'வைகாசி', 'ஆனி', 'ஆடி', 'ஆவணி', 'புரட்டாசி', 'ஐப்பசி', 'கார்த்திகை', 'மார்கழி', 'தை', 'மாசி', 'பங்குனி'][int(s_s/30)%12]} {int(s_s%30)+1}",
        "wara": ["திங்கட்கிழமை", "செவ்வாய்க்கிழமை", "புதன்கிழமை", "வியாழக்கிழமை", "வெள்ளிக்கிழமை", "சனிக்கிழமை", "ஞாயிற்றுக்கிழமை"][date_obj.weekday()], 
        "paksha": "வளர்பிறை" if t_n < 15 else "தேய்பிறை",
        "tithi": ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"][t_n % 30],
        "t_end": t_boundary.strftime("%I:%M %p"),
        "nak": ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"][n_n % 27],
        "n_end": n_boundary.strftime("%I:%M %p"),
        "yog": ["விஷ்கம்பம்", "ப்ரீதி", "ஆயுஷ்மான்", "சௌபாக்கியம்", "சோபனம்", "அதிகண்டம்", "சுகர்மம்", "திருதி", "சூலம்", "கண்டம்", "விருத்தி", "துருவம்", "வியாகாதம்", "ஹர்ஷணம்", "வஜ்ரம்", "சித்தி", "வியதீபாதம்", "வரியான்", "பரிகம்", "சிவம்", "சித்தம்", "சாத்தியம்", "சுபம்", "சுப்பிரம்", "பிராமியம்", "ஐந்தரம்", "வைதிருதி"][y_n % 27],
        "kar": ["பவம்", "பாலவம்", "கௌலவம்", "சைதிலை", "கரசை", "வணிசை", "பத்திரை", "சகுனி", "சதுஷ்பாதம்", "நாகவம்", "கிம்ஸ்துக்னம்"][k_n % 11],
        "special": special_msg
    }

p = get_precise_panchang(selected_date, lat, lon)
sunrise, sunset = get_sunrise_sunset(selected_date, lat, lon)

st.markdown(f"<div class='special-note'>{p['special']}</div>", unsafe_allow_html=True)

st.markdown(f"""
<table class="panchang-table">
    <tr><th>அங்கம்</th><th>விவரம் ({selected_dist})</th></tr>
    <tr><td>📅 <b>தமிழ் தேதி</b></td><td><b>{p['tamil']}</b> | {p['wara']} ({p['paksha']})</td></tr>
    <tr><td>🌙 <b>திதி</b></td><td><b>{p['tithi']}</b><br><span class='sub-text'>முடிவு: {p['t_end']}</span></td></tr>
    <tr><td>⭐ <b>நட்சத்திரம்</b></td><td><b>{p['nak']}</b><br><span class='sub-text'>முடிவு: {p['n_end']}</span></td></tr>
    <tr><td>🌅 <b>உதயம்/அஸ்தமனம்</b></td><td>உதயம்: {sunrise} | அஸ்தமனம்: {sunset}</td></tr>
    <tr><td>♈ <b>யோகம் / கரணம்</b></td><td>{p['yog']} / {p['kar']}</td></tr>
    <tr><td>📊 <b>நிலவின் பாகை</b></td><td>{p['m_deg']}°</td></tr>
</table>
""", unsafe_allow_html=True)
