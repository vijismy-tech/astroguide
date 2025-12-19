import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. CSS Design (Pazhaiya Style) ----------
st.set_page_config(page_title="AstroGuide Tamil", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, span, div, label, td, th { color: #1a1a1a !important; font-family: 'Arial', sans-serif; }
    .header-style { color: #8B0000 !important; text-align: center; font-weight: bold; margin-top: -30px; margin-bottom: 5px; font-size: 1.1em; }
    .main-box { max-width: 450px; margin: auto; padding: 10px; background: #fdfdfd; border-radius: 8px; border: 1px solid #8B0000; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px; }
    .meroon-header { background-color: #8B0000; color: white !important; text-align: center; padding: 8px; border-radius: 5px; font-size: 0.95em; font-weight: bold; margin-top: 15px; margin-bottom: 10px; }
    .panchang-table { width: 100%; border-collapse: collapse; background: white; border: 1px solid #8B0000; font-size: 0.82em; }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 6px; text-align: center; }
    .panchang-table td { padding: 6px 10px; border: 1px solid #eee; color: #000 !important; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. Login ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<h1 class='header-style'>🔱 AstroGuide உள்நுழைவு</h1>", unsafe_allow_html=True)
    if st.button("உள்ளே செல்க"): st.session_state.logged_in = True; st.rerun()
    st.stop()

# ---------------- 3. Inputs ----------------
districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}
st.markdown("<h1 class='header-style'>🔱 AstroGuide பஞ்சாங்கம்</h1>", unsafe_allow_html=True)
st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: s_dist = st.selectbox("ஊர்:", list(districts.keys()))
with c2: s_date = st.date_input("தேதி:", datetime.now(IST))
st.markdown('</div>', unsafe_allow_html=True)
lat, lon = districts[s_dist]

# ---------------- 4. Calculations (Pazhaiya Logic + New Fields) ----------------
def get_panchang_data(date_obj, lat, lon):
    tf = TimezoneFinder(); tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=pytz.timezone(tz_name))
    
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 5.5)

    def get_raw(jd):
        m, _ = swe.calc_ut(jd, 1, swe.FLG_SIDEREAL); s_p, _ = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)
        t = ((m[0]-s_p[0])%360)/12
        n = m[0]/(360/27)
        y = (m[0]+s_p[0])/(360/27)
        k = ((m[0]-s_p[0])%360)/6
        return m[0], s_p[0], int(t), int(n), int(y % 27), int(k % 60)

    def find_end_time(jd_base, cur_idx, p_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid_v = (low + high) / 2
            res_val = get_raw(jd_base + mid_v)
            lookup = {"t":2, "n":3, "y":4, "k":5}[p_type]
            if res_val[lookup] == cur_idx: low = mid_v
            else: high = mid_v
        dt = datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)
        return dt.strftime('%I:%M %p')

    m_deg, s_deg, t_n, n_n, y_n, k_n = get_raw(jd_ut)
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    yogas = ["விஷ்கம்பம்", "ப்ரீதி", "ஆயுஷ்மான்", "சௌபாக்கியம்", "சோபனம்", "அதிகண்டம்", "சுகர்மம்", "திருதி", "சூலம்", "கண்டம்", "விருத்தி", "துருவம்", "வியாகாதம்", "ஹர்ஷணம்", "வஜ்ரம்", "சித்தி", "வியதீபாதம்", "வரியான்", "பரிகம்", "சிவம்", "சித்தம்", "சாத்தியம்", "சுபம்", "சுப்பிரம்", "பிராமியம்", "ஐந்திரம்", "வைதிருதி"]
    karans = ["பவம்", "பாலவம்", "கௌலவம்", "சைதுலை", "கரசை", "வணிசை", "பத்திரை", "சகுனி", "சதுஷ்பாதம்", "நாகவம்", "கிம்ஸ்துக்கினம்"]
    months = ['சித்திரை', 'வைகாசி', 'ஆனி', 'ஆடி', 'ஆவணி', 'புரட்டாசி', 'ஐப்பசி', 'கார்த்திகை', 'மார்கழி', 'தை', 'மாசி', 'பங்குனி']

    return {
        "tamil_date": f"{months[int(s_deg/30)%12]} {int(s_deg%30)+1}",
        "wara": ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][date_obj.weekday()],
        "rise": s["sunrise"].strftime("%I:%M %p"), "set": s["sunset"].strftime("%I:%M %p"),
        "tithi": tithis[t_n % 30], "t_e": find_end_time(jd_ut, t_n, "t"),
        "nak": naks[n_n % 27], "n_e": find_end_time(jd_ut, n_n, "n"), "n_nx": naks[(n_n+1)%27],
        "yoga": yogas[y_n % 27], "karan": karans[k_n % 11],
        "shoolam": ["கிழக்கு", "வடக்கு", "வடக்கு", "தெற்கு", "மேற்கு", "கிழக்கு", "மேற்கு"][date_obj.weekday()],
        "rahu": ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][date_obj.weekday()],
        "yema": ["10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30", "13:30-15:00", "12:00-13:30"][date_obj.weekday()],
        "kuli": ["13:30-15:00", "12:00-13:30", "10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30"][date_obj.weekday()],
        "gowri": ["01:30-02:30 PM", "10:30-11:30 AM", "09:30-10:30 AM", "01:30-02:30 PM", "12:30-01:30 PM", "09:30-10:30 AM", "10:30-11:30 AM"][date_obj.weekday()]
    }

res = get_panchang_data(s_date, lat, lon)

# ---------------- 5. Display (Panchangam) ----------------
st.markdown(f"""
<table class="panchang-table">
    <tr><th colspan="2">பஞ்சாங்கம் - {s_dist} ({res['wara']})</th></tr>
    <tr><td>📅 <b>தமிழ் தேதி</b></td><td><b>{res['tamil_date']}</b></td></tr>
    <tr><td>🌅 <b>சூரிய உதயம் / அஸ்தமனம்</b></td><td><b>{res['rise']}</b> / {res['set']}</td></tr>
    <tr><td>🌙 <b>திதி</b></td><td><b>{res['tithi']}</b> ({res['t_e']} வரை)</td></tr>
    <tr><td>⭐ <b>நட்சத்திரம்</b></td><td><b>{res['nak']}</b> ({res['n_e']} வரை)<br><small style='color:red'>அடுத்து: {res['n_nx']}</small></td></tr>
    <tr><td>🌀 <b>யோகம் / கரணம்</b></td><td>{res['yoga']} / {res['karan']}</td></tr>
    <tr><td>📍 <b>சூலம்</b></td><td>{res['shoolam']}</td></tr>
</table>
""", unsafe_allow_html=True)

# ---------------- 6. Subha/Asubha ----------------
st.markdown("<div class='meroon-header'>⏳ சுப & அசுப நேரங்கள்</div>", unsafe_allow_html=True)
st.markdown(f"""
<table class="panchang-table">
    <tr style="background:#E8F5E9;"><td>🌟 <b>நல்ல நேரம் (கௌரி)</b></td><td><b>{res['gowri']}</b></td></tr>
    <tr style="background:#FFF5F5;"><td>🌑 <b>ராகு காலம்</b></td><td><b>{res['rahu']}</b></td></tr>
    <tr style="background:#FFF5F5;"><td>🔥 <b>எமகண்டம்</b></td><td><b>{res['yema']}</b></td></tr>
    <tr style="background:#FFF5F5;"><td>🌀 <b>குளிகை</b></td><td><b>{res['kuli']}</b></td></tr>
</table>
""", unsafe_allow_html=True)

# ---------------- 7. Chandrashtamam (Pazhaiya Coding) ----------------
st.markdown("<div class='meroon-header'>🌙 சந்திராஷ்டமம்</div>", unsafe_allow_html=True)
naks_list = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
try:
    c_idx = naks_list.index(res['nak'])
    st.markdown(f"""
    <table class="panchang-table">
        <tr style="background:#FFF5F5;"><td>⚠️ <b>சந்திராஷ்டமம்</b></td><td><b style="color:red;">{naks_list[(c_idx-16)%27]}</b> ({res['n_e']} வரை)</td></tr>
    </table>
    """, unsafe_allow_html=True)
except: pass
