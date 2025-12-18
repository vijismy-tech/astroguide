import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta, date
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder
import urllib.parse

# ---------- ஆப் அமைப்புகள் ----------
st.set_page_config(page_title="AstroGuide Tamil", layout="wide")
IST = pytz.timezone('Asia/Kolkata')
ADMIN_WHATSAPP = "919876543210" 

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- CSS வடிவமைப்பு (சிறிய எழுத்துக்கள் & மொபைல் வியூ) ----------
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, span, div, label, td, th { color: #1a1a1a !important; font-family: 'Arial', sans-serif; }
    .header-style { color: #8B0000 !important; text-align: center; font-weight: bold; margin-top: -30px; margin-bottom: 5px; font-size: 1.1em; }
    .main-box { max-width: 450px; margin: auto; padding: 10px; background: #fdfdfd; border-radius: 8px; border: 1px solid #8B0000; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px; }
    .panchang-table { width: 100%; border-collapse: collapse; background: white; border-radius: 5px; border: 1px solid #8B0000; font-size: 0.78em; }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 6px; text-align: center; }
    .panchang-table td { padding: 5px 8px; border: 1px solid #eee; color: #000 !important; font-weight: 500; }
    .special-note { background-color: #FFF9C4; padding: 8px; border-radius: 5px; border-left: 5px solid #FBC02D; margin-bottom: 8px; color: #8B0000 !important; font-weight: bold; text-align: center; font-size: 0.8em; }
    .next-info { color: #8B0000 !important; font-size: 0.7em; font-style: italic; display: block; }
    .muhurtham-box { color: #2E7D32 !important; font-weight: bold; }
    .asubha-row { background-color: #FFF5F5; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- லாகின் லாஜிக் ----------------
if not st.session_state.logged_in:
    st.markdown("<h1 class='header-style'>🔱 AstroGuide உள்நுழைவு</h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    mode = st.radio("தேர்வு செய்க", ["உள்நுழைவு", "பதிவு செய்க"], horizontal=True)
    if mode == "உள்நுழைவு":
        if st.button("நேரடியாக உள்ளே செல்ல (Demo)"): st.session_state.logged_in = True; st.rerun()
    else:
        st.info("அனுமதிக்க நிர்வாகியை வாட்ஸ்அப்பில் தொடர்பு கொள்ளவும்")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------- மாவட்டங்கள் ----------------
districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15], "தஞ்சாவூர்": [10.79, 79.14]}

st.markdown("<h1 class='header-style'>🔱 AstroGuide திருக்கணிதப் பஞ்சாங்கம்</h1>", unsafe_allow_html=True)
st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: s_dist = st.selectbox("ஊர்:", list(districts.keys()))
with c2: s_date = st.date_input("தேதி:", datetime.now(IST))
st.markdown('</div>', unsafe_allow_html=True)

lat, lon = districts[s_dist]

def get_full_details_tamil(date_obj, lat, lon):
    tf = TimezoneFinder(); tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
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
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    
    # திதி பலன்கள் (Thithi Specific Significance)
    tithi_sig = {
        0: "சுப காரியங்களுக்கு ஏற்ற நாள்", 1: "மங்கல நிகழ்வுகள் செய்யலாம்", 2: "பயணம் மேற்கொள்ள உகந்தது",
        3: "விநாயகர் வழிபாடு மிகுந்த பலன் தரும்", 4: "தான தர்மங்கள் செய்ய நல்ல நாள்", 5: "முருகப் பெருமான் வழிபாடு வெற்றி தரும்",
        10: "ஏகாதசி - பெருமாள் வழிபாடு சிறப்பு", 12: "பிரதோஷம் - சிவ வழிபாடு சிறப்பு",
        14: "குலதெய்வ வழிபாடு மற்றும் சக்தி வழிபாடு சிறப்பு"
    }
    palangal = tithi_sig.get(t_n % 15, "தெய்வீக வழிபாட்டிற்கு உகந்த நாள்")

    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    d_idx = date_obj.weekday()
    wara = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][d_idx]

    return {
        "tamil": f"{['சித்திரை', 'வைகாசி', 'ஆனி', 'ஆடி', 'ஆவணி', 'புரட்டாசி', 'ஐப்பசி', 'கார்த்திகை', 'மார்கழி', 'தை', 'மாசி', 'பங்குனி'][int(s_d/30)%12]} {int(s_d%30)+1}",
        "rise": s["sunrise"].strftime("%I:%M %p"), "set": s["sunset"].strftime("%I:%M %p"),
        "abhijit": f"{(mid - timedelta(minutes=24)).strftime('%I:%M %p')} - {(mid + timedelta(minutes=24)).strftime('%I:%M %p')}",
        "tithi": tithis[t_n % 30], "t_end": find_end(jd_ut, t_n, "tithi"), "next_t": tithis[(t_n + 1) % 30],
        "nak": naks[n_n % 27], "n_end": find_end(jd_ut, n_n, "nak"), "next_n": naks[(n_n + 1) % 27],
        "rahu": ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][d_idx],
        "yema": ["10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30", "13:30-15:00", "12:00-13:30"][d_idx],
        "kuli": ["13:30-15:00", "12:00-13:30", "10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30"][d_idx],
        "gowri": ["01:30-02:30 PM", "10:30-11:30 AM", "09:30-10:30 AM", "01:30-02:30 PM", "12:30-01:30 PM", "09:30-10:30 AM", "10:30-11:30 AM"][d_idx],
        "shoolam": ["கிழக்கு", "வடக்கு", "வடக்கு", "தெற்கு", "மேற்கு", "கிழக்கு", "மேற்கு"][d_idx],
        "wara": wara, "deg": round(m_d, 2), "palangal": palangal
    }

res = get_full_details_tamil(s_date, lat, lon)

st.markdown(f"<div class='special-note'>🌟 இன்றைய சிறப்பு: {res['palangal']}</div>", unsafe_allow_html=True)

st.markdown(f"""
<table class="panchang-table">
    <tr><th colspan="2">AstroGuide - {s_dist} ({res['wara']})</th></tr>
    <tr><td>📅 <b>தமிழ் தேதி</b></td><td>{res['tamil']}</td></tr>
    <tr><td>🌅 <b>உதயம் / அஸ்தமனம்</b></td><td>{res['rise']} / {res['set']}</td></tr>
    <tr><td>✨ <b>அபிஜித் முகூர்த்தம்</b></td><td><span class='muhurtham-box'>{res['abhijit']}</span></td></tr>
    <tr><td>🌙 <b>திதி</b></td><td><b>{res['tithi']}</b> ({res['t_end']})<br><span class='next-info'>அடுத்து: {res['next_t']}</span></td></tr>
    <tr><td>⭐ <b>நட்சத்திரம்</b></td><td><b>{res['nak']}</b> ({res['n_end']})<br><span class='next-info'>அடுத்து: {res['next_n']}</span></td></tr>
    <tr><td>🌟 <b>கௌரி நல்ல நேரம்</b></td><td>{res['gowri']}</td></tr>
    <tr class="asubha-row"><td>🚫 <b>ராகு / எமகண்டம்</b></td><td>{res['rahu']} / {res['yema']}</td></tr>
    <tr class="asubha-row"><td>🚫 <b>குளிகை</b></td><td>{res['kuli']}</td></tr>
    <tr><td>📍 <b>சூலம்</b></td><td>{res['shoolam']} (பரிகாரம்: பால்/தயிர்)</td></tr>
    <tr><td>📊 <b>சந்திர பாகை</b></td><td>{res['deg']}°</td></tr>
</table>
""", unsafe_allow_html=True)
