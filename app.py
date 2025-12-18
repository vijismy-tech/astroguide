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

# ---------- CSS வடிவமைப்பு (Mobile Friendly & Small Fonts) ----------
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    
    /* எழுத்து அளவு குறைப்பு மற்றும் ஸ்டைல் */
    h1, h2, h3, p, span, div, label, td, th { 
        color: #1a1a1a !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .header-style { 
        color: #8B0000 !important; 
        text-align: center; 
        font-weight: bold; 
        margin-bottom: 5px; 
        font-size: 1.4em; /* தலைப்பு சிறியதாக மாற்றப்பட்டது */
    }
    
    .main-box { 
        max-width: 500px; margin: auto; padding: 15px; 
        background: #fdfdfd; border-radius: 10px; 
        border: 1px solid #8B0000; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    
    /* அட்டவணை சிறிய எழுத்துக்களுடன் */
    .panchang-table {
        width: 100%; border-collapse: collapse; background: white;
        border-radius: 8px; overflow: hidden; border: 1px solid #8B0000;
        font-size: 0.85em; /* மொபைலுக்காக சிறிய எழுத்துக்கள் */
    }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 10px; text-align: left; }
    .panchang-table td { padding: 8px; border: 1px solid #eee; color: #000 !important; font-weight: 500; }
    
    .stButton>button { 
        background-color: #8B0000; color: white !important; 
        border-radius: 5px; font-weight: bold; width: 100%; font-size: 0.9em;
    }
    
    .special-note { 
        background-color: #FFF9C4; padding: 10px; border-radius: 5px; 
        border-left: 5px solid #FBC02D; margin-bottom: 15px; 
        color: #8B0000 !important; font-weight: bold; text-align: center; font-size: 0.95em;
    }
    
    .next-info { color: #8B0000 !important; font-size: 0.8em; font-style: italic; display: block; margin-top: 2px; }
    .muhurtham-box { color: #2E7D32 !important; font-weight: bold; }
    .sub-text { color: #666 !important; font-size: 0.8em; font-weight: normal; }
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
        if st.button("Sign Up Request"):
            msg = urllib.parse.quote(f"AstroGuide புதிய பதிவு:\nபெயர்: {s_name}\nஎண்: {s_phone}")
            st.markdown(f'<a href="https://wa.me/{ADMIN_WHATSAPP}?text={msg}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; width:100%; cursor:pointer; font-weight:bold;">வாட்ஸ்அப்பில் அனுப்பவும்</button></a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- மாவட்டங்கள் ----------------
districts = {
    "சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "கோயம்புத்தூர்": [11.02, 76.96],
    "திருச்சி": [10.79, 78.70], "திருநெல்வேலி": [8.71, 77.76], "சேலம்": [11.66, 78.15],
    "ஈரோடு": [11.34, 77.72], "வேலூர்": [12.92, 79.13], "தஞ்சாவூர்": [10.79, 79.14]
}

st.markdown("<h1 class='header-style'>🔱 AstroGuide திருக்கணிதப் பஞ்சாங்கம்</h1>", unsafe_allow_html=True)

st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: selected_dist = st.selectbox("மாவட்டம்:", list(districts.keys()))
with c2: selected_date = st.date_input("தேதி:", datetime.now(IST))
if st.button("Logout 🚪"): st.session_state.logged_in = False; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

lat, lon = districts[selected_dist]

# --- Sun & Astro Logic ---
def get_astro_data(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    city = LocationInfo(name="Loc", timezone=tz_name, latitude=lat, longitude=lon)
    s = sun(observer=city.observer, date=date_obj, tzinfo=pytz.timezone(tz_name))
    mid = s["sunrise"] + (s["sunset"] - s["sunrise"]) / 2
    
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 0.0) 
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    def get_raw(jd):
        m, _ = swe.calc_ut(jd, 1, swe.FLG_SIDEREAL); sun_p, _ = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)
        m_d, s_d = m[0], sun_p[0]; diff = (m_d - s_d) % 360
        return m_d, s_d, int(diff/12), int(m_d/(360/27)), int(((m_d+s_d)%360)/(360/27)), int(diff/6)%11

    def find_end(jd_base, current_idx, c_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid_val = (low + high) / 2
            _, _, t, n, _, _ = get_raw(jd_base + mid_val)
            if (n if c_type == "nak" else t) == current_idx: low = mid_val
            else: high = mid_val
        return datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)

    m_s, s_s, t_n, n_n, y_n, k_n = get_raw(jd_ut)
    
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    
    special = "சாதாரண நாள்"
    if t_n == 14: special = "🌟 விசேஷம்: அமாவாசை / பௌர்ணமி"
    elif t_n == 12: special = "🔱 விசேஷம்: பிரதோஷம்"
    elif t_n == 10: special = "🕉️ விசேஷம்: ஏகாதசி"

    return {
        "tamil": f"{['சித்திரை', 'வைகாசி', 'ஆனி', 'ஆடி', 'ஆவணி', 'புரட்டாசி', 'ஐப்பசி', 'கார்த்திகை', 'மார்கழி', 'தை', 'மாசி', 'பங்குனி'][int(s_s/30)%12]} {int(s_s%30)+1}",
        "wara": ["திங்கட்கிழமை", "செவ்வாய்க்கிழமை", "புதன்கிழமை", "வியாழக்கிழமை", "வெள்ளிக்கிழமை", "சனிக்கிழமை", "ஞாயிற்றுக்கிழமை"][date_obj.weekday()],
        "sunrise": s["sunrise"].strftime("%I:%M %p"), "sunset": s["sunset"].strftime("%I:%M %p"),
        "abhijit": f"{(mid - timedelta(minutes=24)).strftime('%I:%M %p')} - {(mid + timedelta(minutes=24)).strftime('%I:%M %p')}",
        "tithi": tithis[t_n % 30], "t_end": find_end(jd_ut, t_n, "tithi").strftime("%I:%M %p"), "next_t": tithis[(t_n + 1) % 30],
        "nak": naks[n_n % 27], "n_end": find_end(jd_ut, n_n, "nak").strftime("%I:%M %p"), "next_n": naks[(n_n + 1) % 27],
        "yog": ["விஷ்கம்பம்", "ப்ரீதி", "ஆயுஷ்மான்", "சௌபாக்கியம்", "சோபனம்", "அதிகண்டம்", "சுகர்மம்", "திருதி", "சூலம்", "கண்டம்", "விருத்தி", "துருவம்", "வியாகாதம்", "ஹர்ஷணம்", "வஜ்ரம்", "சித்தி", "வியதீபாதம்", "வரியான்", "பரிகம்", "சிவம்", "சித்தம்", "சாத்தியம்", "சுபம்", "சுப்பிரம்", "பிராமியம்", "ஐந்தரம்", "வைதிருதி"][y_n % 27],
        "kar": ["பவம்", "பாலவம்", "கௌலவம்", "சைதிலை", "கரசை", "வணிசை", "பத்திரை", "சகுனி", "சதுஷ்பாதம்", "நாகவம்", "கிம்ஸ்துக்னம்"][k_n % 11],
        "rahu": ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][date_obj.weekday()],
        "yema": ["10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30", "13:30-15:00", "12:00-13:30"][date_obj.weekday()],
        "kuli": ["13:30-15:00", "12:00-13:30", "10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30"][date_obj.weekday()],
        "shoolam": {"திங்கட்கிழமை": "கிழக்கு", "செவ்வாய்க்கிழமை": "வடக்கு", "புதன்கிழமை": "வடக்கு", "வியாழக்கிழமை": "தெற்கு", "வெள்ளிக்கிழமை": "மேற்கு", "சனிக்கிழமை": "கிழக்கு", "ஞாயிற்றுக்கிழமை": "மேற்கு"}.get(["திங்கட்கிழமை", "செவ்வாய்க்கிழமை", "புதன்கிழமை", "வியாழக்கிழமை", "வெள்ளிக்கிழமை", "சனிக்கிழமை", "ஞாயிற்றுக்கிழமை"][date_obj.weekday()]),
        "deg": round(m_s, 2), "special": special
    }

p = get_astro_data(selected_date, lat, lon)

st.markdown(f"<div class='special-note'>{p['special']}</div>", unsafe_allow_html=True)

st.markdown(f"""
<table class="panchang-table">
    <tr><th colspan="2">AstroGuide - {selected_dist} ({p['wara']})</th></tr>
    <tr><td>📅 <b>தமிழ் தேதி</b></td><td>{p['tamil']}</td></tr>
    <tr><td>🌅 <b>உதயம் / அஸ்தமனம்</b></td><td>{p['sunrise']} / {p['sunset']}</td></tr>
    <tr><td>✨ <b>அபிஜித் முகூர்த்தம்</b></td><td><span class='muhurtham-box'>{p['abhijit']}</span></td></tr>
    <tr><td>🌙 <b>திதி</b></td><td><b>{p['tithi']}</b> (முடிவு: {p['t_end']})<br><span class='next-info'>அடுத்து: {p['next_t']}</span></td></tr>
    <tr><td>⭐ <b>நட்சத்திரம்</b></td><td><b>{p['nak']}</b> (முடிவு: {p['n_end']})<br><span class='next-info'>அடுத்து: {p['next_n']}</span></td></tr>
    <tr><td>♈ <b>யோகம் / கரணம்</b></td><td>{p['yog']} / {p['kar']}</td></tr>
    <tr style="background-color: #FFF0F0;"><td>🚫 <b>ராகு / எம / குளிகை</b></td><td>{p['rahu']} / {p['yema']} / {p['kuli']}</td></tr>
    <tr><td>📍 <b>சூலம்</b></td><td>{p['shoolam']} (பரிகாரம்: பால்/தயிர்)</td></tr>
    <tr><td>📊 <b>நிலவின் பாகை</b></td><td>{p['deg']}°</td></tr>
</table>
""", unsafe_allow_html=True)
