import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. ஆப் அமைப்புகள் & CSS ----------
st.set_page_config(page_title="AstroGuide Tamil", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, span, div, label, td, th { color: #1a1a1a !important; font-family: 'Arial', sans-serif; }
    .header-style { color: #8B0000 !important; text-align: center; font-weight: bold; margin-top: -30px; margin-bottom: 5px; font-size: 1.1em; }
    .main-box { max-width: 450px; margin: auto; padding: 10px; background: #fdfdfd; border-radius: 8px; border: 1px solid #8B0000; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px; }
    .meroon-header { background-color: #8B0000; color: white !important; text-align: center; padding: 10px; border-radius: 5px; font-size: 1em; font-weight: bold; margin-top: 15px; margin-bottom: 10px; }
    .panchang-table { width: 100%; border-collapse: collapse; background: white; border: 1px solid #8B0000; font-size: 0.78em; }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 6px; text-align: center; }
    .panchang-table td { padding: 5px 8px; border: 1px solid #eee; color: #000 !important; font-weight: 500; }
    .vrat-table { width:100%; border:1px solid #8B0000; border-radius:10px; background-color:#FFFAF0; margin-bottom:10px; border-collapse: separate; }
    
    /* ராசி கட்ட வடிவமைப்பு */
    .rasi-chart { width: 100%; border-collapse: collapse; border: 2px solid #8B0000; table-layout: fixed; }
    .rasi-chart td { border: 1px solid #8B0000; height: 80px; width: 25%; vertical-align: top; padding: 5px; font-size: 0.7em; background: #fff; }
    .rasi-label { color: #8B0000; font-weight: bold; display: block; margin-bottom: 2px; border-bottom: 1px solid #eee; }
    .planet-text { color: #000; font-weight: 500; display: block; line-height: 1.2; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. லாகின் ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<h1 class='header-style'>🔱 AstroGuide உள்நுழைவு</h1>", unsafe_allow_html=True)
    if st.button("உள்ளே செல்க"): st.session_state.logged_in = True; st.rerun()
    st.stop()

# ---------------- 3. தேர்வுகள் ----------------
districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}
st.markdown("<h1 class='header-style'>🔱 AstroGuide திருக்கணிதப் பஞ்சாங்கம்</h1>", unsafe_allow_html=True)
st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: s_dist = st.selectbox("ஊர்:", list(districts.keys()))
with c2: s_date = st.date_input("தேதி:", datetime.now(IST))
st.markdown('</div>', unsafe_allow_html=True)
lat, lon = districts[s_dist]

# ---------------- 4. பஞ்சாங்கம் & கோச்சார லாஜிக் ----------------
def get_full_data(date_obj, lat, lon):
    tf = TimezoneFinder(); tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=pytz.timezone(tz_name))
    
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 5.5) # IST 11:00 AM approximate for transit

    def get_raw(jd):
        m, _ = swe.calc_ut(jd, 1, swe.FLG_SIDEREAL); s_p, _ = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)
        return m[0], s_p[0], int(((m[0]-s_p[0])%360)/12), int(m[0]/(360/27))

    def find_end_time(jd_base, cur_idx, p_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid_v = (low + high) / 2
            res_val = get_raw(jd_base + mid_v)
            lookup = {"t":2, "n":3}[p_type]
            if res_val[lookup] == cur_idx: low = mid_v
            else: high = mid_v
        dt = datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)
        return f"{'இன்று' if dt.date() == date_obj else 'நாளை'} {dt.strftime('%I:%M %p')}"

    m_deg, s_deg, t_n, n_n = get_raw(jd_ut)
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அනුஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    months = ['சித்திரை', 'வைகாசி', 'ஆனி', 'ஆடி', 'ஆவணி', 'புரட்டாசி', 'ஐப்பசி', 'கார்த்திகை', 'மார்கழி', 'தை', 'மாசி', 'பங்குனி']
    
    # கிரக நிலைகள் (Transit)
    planets = {0: "சூரியன்", 1: "சந்திரன்", 2: "செவ்வாய்", 3: "புதன்", 4: "குரு", 5: "சுக்கிரன்", 6: "சனி", 10: "ராகு", 11: "கேது"}
    transit_data = {}
    for p_id, p_name in planets.items():
        if p_id == 11: # கேது (ராகுவுக்கு 180 பாகை தள்ளி)
            pos, _ = swe.calc_ut(jd_ut, 10, swe.FLG_SIDEREAL)
            deg = (pos[0] + 180) % 360
        else:
            pos, _ = swe.calc_ut(jd_ut, p_id, swe.FLG_SIDEREAL)
            deg = pos[0]
        rasi_idx = int(deg / 30)
        p_deg = round(deg % 30, 2)
        if rasi_idx not in transit_data: transit_data[rasi_idx] = []
        transit_data[rasi_idx].append(f"{p_name} {p_deg}°")

    return {
        "tamil_date": f"{months[int(s_deg/30)%12]} {int(s_deg%30)+1}",
        "wara": ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][date_obj.weekday()],
        "rise": s["sunrise"].strftime("%I:%M %p"), "set": s["sunset"].strftime("%I:%M %p"),
        "tithi": tithis[t_n % 30], "t_e": find_end_time(jd_ut, t_n, "t"),
        "nak": naks[n_n % 27], "n_e": find_end_time(jd_ut, n_n, "n"),
        "month_name": months[int(s_deg/30)%12], "transit": transit_data
    }

res = get_full_data(s_date, lat, lon)

# --- 5. காட்சிப்படுத்துதல் (Panchangam) ---
st.markdown(f"""
<table class="panchang-table">
    <tr><th colspan="2">பஞ்சாங்கம் - {s_dist} ({res['wara']})</th></tr>
    <tr><td>📅 <b>தமிழ் தேதி</b></td><td>{res['tamil_date']}</td></tr>
    <tr><td>🌅 <b>உதயம்/அஸ்தமனம்</b></td><td>{res['rise']} / {res['set']}</td></tr>
    <tr><td>🌙 <b>திதி</b></td><td>{res['tithi']} ({res['t_e']})</td></tr>
    <tr><td>⭐ <b>நட்சத்திரம்</b></td><td>{res['nak']} ({res['n_e']})</td></tr>
</table>
""", unsafe_allow_html=True)

# --- 6. கோச்சார ராசி கட்டம் ---
st.markdown("<div class='meroon-header'>🎡 இன்றைய கோச்சார ராசி கட்டம்</div>", unsafe_allow_html=True)

def get_p(idx):
    return "".join([f"<span class='planet-text'>{p}</span>" for p in res['transit'].get(idx, [])])

st.markdown(f"""
<table class="rasi-chart">
    <tr><td><span class='rasi-label'>மீனம்</span>{get_p(11)}</td><td><span class='rasi-label'>மேஷம்</span>{get_p(0)}</td><td><span class='rasi-label'>ரிஷபம்</span>{get_p(1)}</td><td><span class='rasi-label'>மிதுனம்</span>{get_p(2)}</td></tr>
    <tr><td><span class='rasi-label'>கும்பம்</span>{get_p(10)}</td><td colspan="2" rowspan="2" style="background:#fdfdfd; text-align:center; vertical-align:middle; font-weight:bold; color:#8B0000; font-size:1.2em;">AstroGuide<br>ராசி கட்டம்</td><td><span class='rasi-label'>கடகம்</span>{get_p(3)}</td></tr>
    <tr><td><span class='rasi-label'>மகரம்</span>{get_p(9)}</td><td><span class='rasi-label'>சிம்மம்</span>{get_p(4)}</td></tr>
    <tr><td><span class='rasi-label'>தனுசு</span>{get_p(8)}</td><td><span class='rasi-label'>விருச்சிகம்</span>{get_p(7)}</td><td><span class='rasi-label'>துலாம்</span>{get_p(6)}</td><td><span class='rasi-label'>கன்னி</span>{get_p(5)}</td></tr>
</table>
""", unsafe_allow_html=True)

# --- 7. சந்திராஷ்டமம் & விசேஷங்கள் (பழைய லாஜிக்) ---
st.markdown("<div class='meroon-header'>🌙 சந்திராஷ்டமம் & விசேஷங்கள்</div>", unsafe_allow_html=True)
st.markdown('<div class="main-box">', unsafe_allow_html=True)
# (இங்கு உங்கள் பழைய சந்திராஷ்டமம் மற்றும் விரத லாஜிக்கை அப்படியே இணைத்துக் கொள்ளலாம்)
st.write(f"இன்று நட்சத்திரம்: **{res['nak']}**. இதற்குரிய சந்திராஷ்டம நட்சத்திரங்களை மேலேயுள்ள விதிமுறைப்படி கவனிக்கவும்.")

vrat_db = {("அமாவாசை", None, "மார்கழி"): ["ஸ்ரீ ஹனுமன் ஜெயந்தி", "அஞ்சனை மைந்தனின் பூரண அருள் கிட்டும்.", "https://img.freepik.com/premium-photo/god-lord-hanuman-statue_1156453-157.jpg"]}
for (t, n, m), d in vrat_db.items():
    if t == res['tithi'] and (m is None or m == res['month_name']):
        st.markdown(f"""<table class="vrat-table"><tr><td style="width:30%"><img src="{d[2]}" width="80" style="border-radius:50%"></td><td><b>✨ {d[0]}</b><br><small>{d[1]}</small></td></tr></table>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
