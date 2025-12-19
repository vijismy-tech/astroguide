import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. ஆப் அமைப்புகள் ----------
st.set_page_config(page_title="துல்லிய ஜாமக்கோள் பிரசன்னம்", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .stApp { background-color: #FFFDF9; }
    .header-style { background: #8B0000; color: white !important; text-align: center; padding: 10px; border-radius: 8px; font-size: 1.3em; font-weight: bold; }
    .jamakkol-chart { width: 100%; border-collapse: collapse; border: 2.5px solid #8B0000; table-layout: fixed; background: white; }
    .jamakkol-chart td { border: 1.5px solid #8B0000; height: 115px; vertical-align: top; padding: 6px; font-size: 0.72em; }
    .rasi-label { color: #8B0000; font-weight: bold; display: block; border-bottom: 1px solid #f0f0f0; margin-bottom: 3px; font-size: 1em; }
    .jam-planet { color: #000; font-weight: 700; display: block; line-height: 1.2; margin-bottom: 1px; }
    .special-label { font-weight: bold; display: block; font-size: 0.85em; margin-top: 2px; padding: 2px; border-radius: 3px; border: 0.5px solid #eee; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. லாகின் & தேர்வுகள் ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<div class='header-style'>🔱 AstroGuide லாகின்</div>", unsafe_allow_html=True)
    if st.button("உள்ளே செல்க"): st.session_state.logged_in = True; st.rerun()
    st.stop()

districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}
st.markdown("<div class='header-style'>🔱 திருக்கணித ஜாமக்கோள் பிரசன்னம்</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1: s_dist = st.selectbox("ஊர் தேர்வு:", list(districts.keys()))
with c2: s_date = st.date_input("தேதி தேர்வு:", datetime.now(IST))
lat, lon = districts[s_dist]

# ---------------- 3. துல்லிய கணித லாஜிக் (Exact Prediction) ----------------
def get_exact_jamakkol(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    
    # 1. சூரிய உதயம் / அஸ்தமனம்
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=tz)
    sunrise, sunset = s["sunrise"], s["sunset"]
    
    # 2. ஜாமம் கண்டறிதல்
    is_day = sunrise <= now <= sunset
    if is_day:
        duration = (sunset - sunrise).total_seconds() / 8
        elapsed = (now - sunrise).total_seconds()
        j_type = "பகல்"
    else:
        next_sunrise = sun(observer=city.observer, date=date_obj + timedelta(days=1), tzinfo=tz)["sunrise"]
        if now < sunrise: # நள்ளிரவுக்குப் பின்
            prev_sunset = sun(observer=city.observer, date=date_obj - timedelta(days=1), tzinfo=tz)["sunset"]
            duration = (sunrise - prev_sunset).total_seconds() / 8
            elapsed = (now - prev_sunset).total_seconds()
        else:
            duration = (next_sunrise - sunset).total_seconds() / 8
            elapsed = (now - sunset).total_seconds()
        j_type = "இரவு"

    cur_jam = min(int(elapsed / duration) + 1, 8)

    # 3. துல்லிய கிரக நிலைகள் (Swiss Ephemeris - Lahiri)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    # UT Calculation: IST - 5:30
    jd_ut = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0 + now.second/3600.0 - 5.5)

    def fmt(deg): return f"{int(deg % 30)}°{int((deg % 1) * 60)}'"

    # கிரகங்கள்
    transit = {}
    # 0:சூரியன், 1:சந்திரன், 2:செவ்வாய், 3:புதன், 4:குரு, 5:சுக்கிரன், 6:சனி, 10:ராகு
    p_map = {0:"சூரி", 1:"சந்", 2:"செவ்", 3:"புத", 4:"குரு", 5:"சுக்", 6:"சனி", 10:"ராகு"}
    
    for pid, name in p_map.items():
        res, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        deg = res[0]
        vakra = " (வ)" if res[3] < 0 else ""
        idx = int(deg / 30)
        p_str = f"{name}{vakra}({fmt(deg)})"
        
        if idx not in transit: transit[idx] = []
        transit[idx].append(p_str)
        
        if pid == 10: # கேது ராகுவுக்கு 180°
            k_deg = (deg + 180) % 360
            k_idx = int(k_deg / 30)
            if k_idx not in transit: transit[k_idx] = []
            transit[k_idx].append(f"கேது({fmt(k_deg)})")

    # 4. உதய, ஆருட, கவிப்பு பாகை
    sun_pos = swe.calc_ut(jd_ut, 0, swe.FLG_SIDEREAL)[0][0]
    sun_sign = int(sun_pos / 30)
    jam_prog = (elapsed % duration) / duration
    
    u_deg = ((sun_sign + (cur_jam - 1)) * 30 + (jam_prog * 30)) % 360
    a_deg = ((sun_sign + cur_jam) * 30) % 360
    k_deg = (u_deg + (sun_pos % 30)) % 360

    return {
        "transit": transit, "jam_text": f"{j_type} {cur_jam}-ம் ஜாமம்",
        "u": [int(u_deg/30), fmt(u_deg)],
        "a": [int(a_deg/30), fmt(a_deg)],
        "k": [int(k_deg/30), fmt(k_deg)],
        "time": now.strftime("%I:%M:%S %p")
    }

res = get_exact_jamakkol(s_date, lat, lon)

# ---------------- 4. கட்டம் வெளியீடு ----------------
st.markdown(f"<div style='text-align:center; font-weight:bold; color:#8B0000; margin:5px;'>🕒 {res['jam_text']} | நேரம்: {res['time']}</div>", unsafe_allow_html=True)

def get_box(i):
    txt = "".join([f"<span class='jam-planet'>{p}</span>" for p in res['transit'].get(i, [])])
    if i == res['u'][0]: txt += f"<span class='special-label' style='background:#E8F5E9; color:green;'>உதய({res['u'][1]})</span>"
    if i == res['a'][0]: txt += f"<span class='special-label' style='background:#FDF2E9; color:#A04000;'>ஆருட({res['a'][1]})</span>"
    if i == res['k'][0]: txt += f"<span class='special-label' style='background:#FDEDEC; color:red;'>கவிப்பு({res['k'][1]})</span>"
    return txt

st.markdown(f"""
<table class="jamakkol-chart">
    <tr><td><span class='rasi-label'>மீனம்</span>{get_box(11)}</td><td><span class='rasi-label'>மேஷம்</span>{get_box(0)}</td><td><span class='rasi-label'>ரிஷபம்</span>{get_box(1)}</td><td><span class='rasi-label'>மிதுனம்</span>{get_box(2)}</td></tr>
    <tr><td><span class='rasi-label'>கும்பம்</span>{get_box(10)}</td><td colspan="2" rowspan="2" style="text-align:center; vertical-align:middle; color:#8B0000; font-weight:bold; font-size:1.1em; background:#f9f9f9;">ஜாமக்கோள்<br>திருக்கணிதம்</td><td><span class='rasi-label'>கடகம்</span>{get_box(3)}</td></tr>
    <tr><td><span class='rasi-label'>மகரம்</span>{get_box(9)}</td><td><span class='rasi-label'>சிம்மம்</span>{get_box(4)}</td></tr>
    <tr><td><span class='rasi-label'>தனுசு</span>{get_box(8)}</td><td><span class='rasi-label'>விருச்சி</span>{get_box(7)}</td><td><span class='rasi-label'>துலாம்</span>{get_box(6)}</td><td><span class='rasi-label'>கன்னி</span>{get_box(5)}</td></tr>
</table>
""", unsafe_allow_html=True)
