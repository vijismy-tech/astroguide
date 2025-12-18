import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder
import urllib.parse

# ---------- App Settings ----------
st.set_page_config(page_title="AstroGuide Mobile", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

ADMIN_WHATSAPP = "919876543210" 

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- CSS (Compact & Mobile Friendly) ----------
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
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
        font-size: 1.15em; 
    }
    .main-box { 
        max-width: 450px; margin: auto; padding: 10px; 
        background: #fdfdfd; border-radius: 8px; 
        border: 1px solid #8B0000; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .panchang-table {
        width: 100%; border-collapse: collapse; background: white;
        border-radius: 5px; overflow: hidden; border: 1px solid #8B0000;
        font-size: 0.8em; 
    }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 6px; text-align: center; font-size: 0.85em; }
    .panchang-table td { padding: 5px 8px; border: 1px solid #eee; color: #000 !important; font-weight: 500; }
    .special-note { 
        background-color: #FFF9C4; padding: 6px; border-radius: 5px; 
        border-left: 4px solid #FBC02D; margin-bottom: 8px; 
        color: #8B0000 !important; font-weight: bold; text-align: center; font-size: 0.8em;
    }
    .next-info { color: #8B0000 !important; font-size: 0.7em; font-style: italic; display: block; }
    .muhurtham-box { color: #2E7D32 !important; font-weight: bold; }
    .asubha-row { background-color: #FFF5F5; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- LOGIN / SIGNUP ----------------
if not st.session_state.logged_in:
    st.markdown("<h1 class='header-style'>🔱 AstroGuide Login</h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    mode = st.radio("Selection", ["Login", "Sign Up"], horizontal=True)
    if mode == "Login":
        u_name = st.text_input("Name")
        u_pass = st.text_input("Password", type="password")
        if st.button("Enter"):
            if u_name != "" and u_pass != "": st.session_state.logged_in = True; st.rerun()
            else: st.error("Fill details")
    else:
        s_name = st.text_input("Full Name")
        s_phone = st.text_input("WhatsApp No")
        if st.button("Request Access"):
            msg = urllib.parse.quote(f"AstroGuide Access: {s_name} - {s_phone}")
            st.markdown(f'<a href="https://wa.me/{ADMIN_WHATSAPP}?text={msg}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:8px; border-radius:5px; width:100%; cursor:pointer; font-weight:bold;">Send WhatsApp</button></a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- Districts ----------------
districts = {"Chennai": [13.08, 80.27], "Madurai": [9.93, 78.12], "Trichy": [10.79, 78.70], "Coimbatore": [11.02, 76.96], "Nellai": [8.71, 77.76], "Salem": [11.66, 78.15]}

st.markdown("<h1 class='header-style'>🔱 AstroGuide திருக்கணிதப் பஞ்சாங்கம்</h1>", unsafe_allow_html=True)

st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: s_dist = st.selectbox("Oor:", list(districts.keys()))
with c2: s_date = st.date_input("Date:", datetime.now(IST))
if st.button("Logout 🚪"): st.session_state.logged_in = False; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

lat, lon = districts[s_dist]

def get_full_panchang(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=pytz.timezone(tz_name))
    mid = s["sunrise"] + (s["sunset"] - s["sunrise"]) / 2
    
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 0.0)

    def get_raw(jd):
        m, _ = swe.calc_ut(jd, 1, swe.FLG_SIDEREAL); sun_p, _ = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)
        return m[0], sun_p[0], int(((m[0]-sun_p[0])%360)/12), int(m[0]/(360/27))

    def find_end(jd_base, cur_idx, c_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid_val = (low + high) / 2
            m, sun_p, t, n = get_raw(jd_base + mid_val)
            if (n if c_type == "nak" else t) == cur_idx: low = mid_val
            else: high = mid_val
        return (datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)).strftime("%I:%M %p")

    m_d, s_d, t_n, n_n = get_raw(jd_ut)
    tithis = ["Prathamai", "Dwitiyai", "Tritiyai", "Chaturthi", "Panchami", "Sashti", "Saptami", "Ashtami", "Navami", "Dasami", "Ekadasi", "Dwadasi", "Trayodasi", "Chaturdasi", "Pournami", "Prathamai", "Dwitiyai", "Tritiyai", "Chaturthi", "Panchami", "Sashti", "Saptami", "Ashtami", "Navami", "Dasami", "Ekadasi", "Dwadasi", "Trayodasi", "Chaturdasi", "Amavasai"]
    naks = ["Aswini", "Bharani", "Krithigai", "Rohini", "Mrigashirsham", "Thiruvathirai", "Punarpusam", "Poosam", "Ayilyam", "Magam", "Pooram", "Utthiram", "Hastam", "Chithirai", "Swathi", "Visakam", "Anusham", "Kettai", "Moolam", "Pooradam", "Utthiradam", "Thiruvonam", "Avittam", "Sadhayam", "Purattathi", "Utthirattathi", "Revathi"]
    
    d_idx = date_obj.weekday()
    wara = ["Thingal", "Chevvai", "Budhan", "Vyalan", "Velli", "Sani", "Gnayiru"][d_idx]
    
    special = "Normal Day"
    if t_n in [14, 29]: special = "🌟 Vishesham: Amavasai/Pournami"
    elif t_n in [12, 27]: special = "🔱 Vishesham: Pradosham"

    return {
        "tamil": f"{['Chithirai', 'Vaikasi', 'Aani', 'Aadi', 'Aavani', 'Purattasi', 'Aippasi', 'Karthigai', 'Margazhi', 'Thai', 'Maasi', 'Panguni'][int(s_d/30)%12]} {int(s_d%30)+1}",
        "rise": s["sunrise"].strftime("%I:%M %p"), "set": s["sunset"].strftime("%I:%M %p"),
        "abhijit": f"{(mid - timedelta(minutes=24)).strftime('%I:%M %p')} - {(mid + timedelta(minutes=24)).strftime('%I:%M %p')}",
        "tithi": tithis[t_n % 30], "t_end": find_end(jd_ut, t_n, "tithi"), "next_t": tithis[(t_n + 1) % 30],
        "nak": naks[n_n % 27], "n_end": find_end(jd_ut, n_n, "nak"), "next_n": naks[(n_n + 1) % 27],
        "rahu": ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][d_idx],
        "yema": ["10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30", "13:30-15:00", "12:00-13:30"][d_idx],
        "kuli": ["13:30-15:00", "12:00-13:30", "10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30"][d_idx],
        "gowri": ["01:30-02:30 PM", "10:30-11:30 AM", "09:30-10:30 AM", "01:30-02:30 PM", "12:30-01:30 PM", "09:30-10:30 AM", "10:30-11:30 AM"][d_idx],
        "shoolam": ["East", "North", "North", "South", "West", "East", "West"][d_idx],
        "wara": wara, "deg": round(m_d, 2), "special": special
    }

res = get_full_panchang(s_date, lat, lon)

st.markdown(f"<div class='special-note'>{res['special']}</div>", unsafe_allow_html=True)

st.markdown(f"""
<table class="panchang-table">
    <tr><th colspan="2">AstroGuide - {s_dist} ({res['wara']})</th></tr>
    <tr><td>📅 <b>Tamil Date</b></td><td>{res['tamil']}</td></tr>
    <tr><td>🌅 <b>Sunrise / Set</b></td><td>{res['rise']} / {res['set']}</td></tr>
    <tr><td>✨ <b>Abhijit</b></td><td><span class='muhurtham-box'>{res['abhijit']}</span></td></tr>
    <tr><td>🌙 <b>Tithi</b></td><td><b>{res['tithi']}</b> ({res['t_end']})<br><span class='next-info'>Next: {res['next_t']}</span></td></tr>
    <tr><td>⭐ <b>Nakshatram</b></td><td><b>{res['nak']}</b> ({res['n_end']})<br><span class='next-info'>Next: {res['next_n']}</span></td></tr>
    <tr><td>🌟 <b>Gowri Good Time</b></td><td>{res['gowri']}</td></tr>
    <tr class="asubha-row"><td>🚫 <b>Rahu / Yema</b></td><td>{res['rahu']} / {res['yema']}</td></tr>
    <tr class="asubha-row"><td>🚫 <b>Kuligai</b></td><td>{res['kuli']}</td></tr>
    <tr><td>📍 <b>Shoolam</b></td><td>{res['shoolam']} (Remedy: Milk/Curd)</td></tr>
    <tr><td>📊 <b>Moon Deg</b></td><td>{res['deg']}°</td></tr>
</table>
""", unsafe_allow_html=True)
