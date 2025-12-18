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
ADMIN_WHATSAPP = "919876543210"  # 🔁 உங்கள் வாட்ஸ்அப் எண்ணை மாற்றவும்

# ---------- SESSION STATE ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- புதிய CSS வடிவமைப்பு (Clear Visibility) ----------
st.markdown("""
    <style>
    /* முழு பின்னணி நிறம் */
    .stApp { background-color: #FFFFFF; }
    
    /* தலைப்பு மற்றும் எழுத்துக்கள் */
    h1, h2, h3, p, span, div { color: #1a1a1a !important; font-family: 'Arial', sans-serif; }
    
    .header-style { color: #8B0000 !important; text-align: center; font-weight: bold; margin-bottom: 20px; font-size: 2.5em; }
    
    /* லாகின் பாக்ஸ் வடிவமைப்பு */
    .auth-container { 
        max-width: 450px; margin: auto; padding: 30px; 
        background: #f9f9f9; border-radius: 20px; 
        border: 2px solid #8B0000; box-shadow: 0 10px 25px rgba(0,0,0,0.1); 
    }
    
    /* அட்டவணை வடிவமைப்பு */
    .panchang-table {
        width: 100%; border-collapse: collapse; background: white;
        border-radius: 12px; overflow: hidden; border: 2px solid #8B0000;
        margin-top: 20px;
    }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 18px; text-align: left; font-size: 1.2em; }
    .panchang-table td { padding: 15px; border: 1px solid #ddd; color: #000 !important; font-weight: 600; font-size: 1.1em; }
    
    /* பட்டன் ஸ்டைல் */
    .stButton>button {
        background-color: #8B0000; color: white !important; 
        border-radius: 8px; font-weight: bold; width: 100%; height: 45px;
    }
    
    .sub-text { color: #444 !important; font-size: 0.9em; font-weight: normal; display: block; margin-top: 4px; }
    .special-note { background-color: #FFF9C4; padding: 20px; border-radius: 10px; border-left: 8px solid #FBC02D; margin-bottom: 25px; color: #000 !important; font-size: 1.2em; }
    
    /* இன்புட் பீல்டு நிறம் */
    input { color: #000 !important; background-color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIN / SIGNUP ----------------
if not st.session_state.logged_in:
    st.markdown("<h1 class='header-style'>🔱 Astro Guide Login</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        mode = st.radio("தேர்வு செய்க (Select)", ["Login", "Sign Up"], horizontal=True)
        
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
                message = f"புதிய பதிவு:\nபெயர்: {s_name}\nஎண்: {s_phone}\nஊர்: {s_city}"
                wa_url = f"https://wa.me/{ADMIN_WHATSAPP}?text={urllib.parse.quote(message)}"
                st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; width:100%; cursor:pointer; font-weight:bold;">வாட்ஸ்அப்பில் அனுப்பவும்</button></a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- மெயின் பஞ்சாங்கம் (LOGIN ஆன பிறகு) ----------------

# Logout Button
if st.sidebar.button("Logout 🚪"):
    st.session_state.logged_in = False
    st.rerun()

districts = {
    "அரியலூர்": [11.1401, 79.0786], "சென்னை": [13.0827, 80.2707], "கோயம்புத்தூர்": [11.0168, 76.9558],
    "கடலூர்": [11.7480, 79.7714], "தர்மபுரி": [12.1271, 78.1582], "திண்டுக்கல்": [10.3673, 77.9803],
    "ஈரோடு": [11.3410, 77.7172], "காஞ்சிபுரம்": [12.8342, 79.7036], "மதுரை": [9.9252, 78.1198],
    "நாகப்பட்டினம்": [10.7672, 79.8444], "நாமக்கல்": [11.2189, 78.1674], "புதுக்கோட்டை": [10.3797, 78.8202],
    "இராமநாதபுரம்": [9.3639, 78.8395], "சேலம்": [11.6643, 78.1460], "தஞ்சாவூர்": [10.7870, 79.1378],
    "திருச்சிராப்பள்ளி": [10.7905, 78.7047], "திருநெல்வேலி": [8.7139, 77.7567], "வேலூர்": [12.9165, 79.1325]
}

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
        return m_deg, s_deg, int(diff / 12), int(m_deg / (360/27)), int(((m_deg + s_deg) % 360) / (360/27)), int(diff / 6) % 11

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
    wara = ["திங்கட்கிழமை", "செவ்வாய்க்கிழமை", "புதன்கிழமை", "வியாழக்கிழமை", "வெள்ளிக்கிழமை", "சனிக்கிழமை", "ஞாயிற்றுக்கிழமை"][date_obj.weekday()]

    return {
        "m_deg": round(m_start, 2), "wara": wara, "tamil_month": t_month, "tamil_date": t_date,
        "tithi": ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"][t_now % 30],
        "tithi_end": t_end_dt.strftime("%I:%M %p"),
        "nak": ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"][n_now % 27],
        "nak_end": n_end_dt.strftime("%I:%M %p"),
        "yog": ["விஷ்கம்பம்", "ப்ரீதி", "ஆயுஷ்மான்", "சௌபாக்கியம்", "சோபனம்", "அதிகண்டம்", "சுகர்மம்", "திருதி", "சூலம்", "கண்டம்", "விருத்தி", "துருவம்", "வியாகாதம்", "ஹர்ஷணம்", "வஜ்ரம்", "சித்தி", "வியதீபாதம்", "வரியான்", "பரிகம்", "சிவம்", "சித்தம்", "சாத்தியம்", "சுபம்", "சுப்பிரம்", "பிராமியம்", "ஐந்தரம்", "வைதிருதி"][y_now % 27],
        "kar": ["பவம்", "பாலவம்", "கௌலவம்", "சைதிலை", "கரசை", "வணிசை", "பத்திரை", "சகுனி", "சதுஷ்பாதம்", "நாகவம்", "கிம்ஸ்துக்னம்"][k_now % 11],
        "paksha": "வளர்பிறை" if t_now < 15 else "தேய்பிறை"
    }

# Main UI
st.markdown("<h1 class='header-style'>🔱 தமிழ்நாடு திருக்கணிதப் பஞ்சாங்கம்</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings")
    selected_dist = st.selectbox("மாவட்டத்தைத் தேர்ந்தெடுக்கவும்:", list(districts.keys()))
    selected_date = st.date_input("தேதியைத் தேர்ந்தெடுக்கவும்:", datetime.now(IST))

lat, lon = districts[selected_dist]
p = get_precise_panchang(selected_date, lat, lon)
sunrise, sunset = get_sunrise_sunset(selected_date, lat, lon)

st.markdown(f"<div class='special-note'>📅 தமிழ் தேதி: {p['tamil_month']} {p['tamil_date']} | {p['wara']}</div>", unsafe_allow_html=True)

st.markdown(f"""
<table class="panchang-table">
    <tr><th>அங்கம் (Panchangam)</th><th>விவரம் (Details - {selected_dist})</th></tr>
    <tr><td>📅 <b>தமிழ் மாதம் & தேதி</b></td><td><b>{p['tamil_month']} {p['tamil_date']}</b> | {p['wara']}</td></tr>
    <tr><td>🌙 <b>திதி சஞ்சாரம்</b></td><td><b>{p['tithi']}</b> ({p['paksha']})<br><span class='sub-text'>முடிவு: {p['tithi_end']}</span></td></tr>
    <tr><td>⭐ <b>நட்சத்திரம்</b></td><td><b>{p['nak']}</b><br><span class='sub-text'>முடிவு: {p['nak_end']}</span></td></tr>
    <tr><td>♈ <b>யோகம் / கரணம்</b></td><td>யோகம்: {p['yog']} | கரணம்: {p['kar']}</td></tr>
    <tr><td>🌅 <b>சூரிய உதயம் / அஸ்தமனம்</b></td><td>உதயம்: <b>{sunrise}</b> | அஸ்தமனம்: <b>{sunset}</b></td></tr>
    <tr><td>📊 <b>நிலவின் பாகை</b></td><td>{p['m_deg']}° (திருக்கணிதம்)</td></tr>
</table>
""", unsafe_allow_html=True)
