import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. ஆப் அமைப்புகள் ----------
st.set_page_config(page_title="திருக்கணித ஜாமக்கோள்", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .stApp { background-color: #FFFDF9; }
    .header-style { background: linear-gradient(135deg, #8B0000 0%, #4A0000 100%); color: white !important; text-align: center; padding: 15px; border-radius: 10px; font-size: 1.4em; font-weight: bold; margin-bottom: 20px; }
    .jamakkol-chart { width: 100%; border-collapse: collapse; border: 3px solid #8B0000; table-layout: fixed; background: white; }
    .jamakkol-chart td { border: 1.5px solid #8B0000; height: 110px; vertical-align: top; padding: 8px; font-size: 0.75em; }
    .rasi-label { color: #8B0000; font-weight: bold; display: block; border-bottom: 1px solid #f0f0f0; margin-bottom: 5px; font-size: 1em; }
    .jam-planet { color: #000; font-weight: 700; display: block; line-height: 1.3; }
    .special-label { color: #d32f2f; font-weight: bold; display: block; font-size: 0.9em; margin-top: 4px; padding: 2px; border-radius: 3px; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. லாகின் ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<div class='header-style'>🔱 AstroGuide ஜாமக்கோள் லாகின்</div>", unsafe_allow_html=True)
    if st.button("உள்ளே செல்க"): st.session_state.logged_in = True; st.rerun()
    st.stop()

# ---------------- 3. தேர்வுகள் ----------------
districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}
st.markdown("<div class='header-style'>🔱 நவீன திருக்கணித ஜாமக்கோள் பிரசன்னம்</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1: s_dist = st.selectbox("ஊர்:", list(districts.keys()))
with col2: s_date = st.date_input("தேதி:", datetime.now(IST))
lat, lon = districts[s_dist]

# ---------------- 4. திருக்கணித ஜாமக்கோள் லாஜிக் ----------------
def get_jamakkol_final(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    tz = pytz.timezone(tz_name)
    now_time = datetime.now(tz)
    
    # சூரிய உதயம் & அஸ்தமனம் கணக்கீடு
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=tz)
    sunrise, sunset = s["sunrise"], s["sunset"]
    
    # பகல் அல்லது இரவு ஜாமம் கண்டறிதல்
    is_day = sunrise <= now_time <= sunset
    if is_day:
        duration = (sunset - sunrise).total_seconds() / 8
        elapsed = (now_time - sunrise).total_seconds()
        jam_type = "பகல்"
    else:
        # இரவு ஜாமம்: அடுத்த சூரிய உதயம் வரை
        next_day = date_obj + timedelta(days=1)
        s_next = sun(observer=city.observer, date=next_day, tzinfo=tz)
        if now_time < sunrise: # நள்ளிரவுக்குப் பின்
            prev_day = date_obj - timedelta(days=1)
            s_prev = sun(observer=city.observer, date=prev_day, tzinfo=tz)
            duration = (sunrise - s_prev["sunset"]).total_seconds() / 8
            elapsed = (now_time - s_prev["sunset"]).total_seconds()
        else: # சூரிய அஸ்தமனத்திற்குப் பின்
            duration = (s_next["sunrise"] - sunset).total_seconds() / 8
            elapsed = (now_time - sunset).total_seconds()
        jam_type = "இரவு"

    cur_jam = int(elapsed / duration) + 1
    if cur_jam > 8: cur_jam = 8

    # கிரக நிலைகள் (Swiss Ephemeris)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(now_time.year, now_time.month, now_time.day, now_time.hour + now_time.minute/60.0 - 5.5)

    def f_deg(deg): return f"{int(deg % 30)}°{int((deg % 1) * 60)}'"

    # 1. கிரகங்கள் பாகைகளுடன்
    transit = {}
    p_names = {0:"சூரி", 1:"சந்", 2:"செவ்", 3:"புத", 4:"குரு", 5:"சுக்", 6:"சனி", 10:"ராகு"}
    for pid, name in p_names.items():
        res, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        pos = res[0]
        vakra = "(வ)" if res[3] < 0 else ""
        idx = int(pos / 30)
        p_info = f"{name}{vakra}({f_deg(pos)})"
        if idx not in transit: transit[idx] = []
        transit[idx].append(p_info)
        if pid == 10: # கேது
            k_deg = (pos + 180) % 360
            k_idx = int(k_deg / 30)
            if k_idx not in transit: transit[k_idx] = []
            transit[k_idx].append(f"கேது({f_deg(k_deg)})")

    # 2. உதயம், ஆருடம், கவிப்பு பாகை
    sun_res, _ = swe.calc_ut(jd_ut, 0, swe.FLG_SIDEREAL)
    sun_pos = sun_res[0]
    sun_sign = int(sun_pos / 30)
    jam_prog = (elapsed % duration) / duration
    
    u_raw = ((sun_sign + (cur_jam - 1)) * 30 + (jam_prog * 30)) % 360
    a_raw = ((sun_sign + cur_jam) * 30) % 360
    k_raw = (u_raw + (sun_pos % 30)) % 360

    return {
        "transit": transit, "jam": f"{jam_type} ஜாமம் {cur_jam}",
        "udayam": [int(u_raw/30), f_deg(u_raw)],
        "arudam": [int(a_raw/30), f_deg(a_raw)],
        "kavippu": [int(k_raw/30), f_deg(k_raw)],
        "time": now_time.strftime("%I:%M:%S %p")
    }

res = get_jamakkol_final(s_date, lat, lon)

# ---------------- 5. கட்டம் வெளியீடு ----------------
st.markdown(f"<div style='text-align:center; font-weight:bold; color:#8B0000; margin-bottom:10px;'>🕒 {res['jam']} | நேரம்: {res['time']}</div>", unsafe_allow_html=True)

def get_c(i):
    txt = "".join([f"<span class='jam-planet'>{p}</span>" for p in res['transit'].get(i, [])])
    if i == res['udayam'][0]: txt += f"<span class='special-label' style='background:#E8F5E9; color:#2E7D32;'>[உதய {res['udayam'][1]}]</span>"
    if i == res['arudam'][0]: txt += f"<span class='special-label' style='background:#FDF2E9; color:#AF601A;'>[ஆருட {res['arudam'][1]}]</span>"
    if i == res['kavippu'][0]: txt += f"<span class='special-label' style='background:#FDEDEC; color:#CB4335;'>[கவிப்பு {res['kavippu'][1]}]</span>"
    return txt

st.markdown(f"""
<table class="jamakkol-chart">
    <tr><td><span class='rasi-label'>மீனம்</span>{get_c(11)}</td><td><span class='rasi-label'>மேஷம்</span>{get_c(0)}</td><td><span class='rasi-label'>ரிஷபம்</span>{get_c(1)}</td><td><span class='rasi-label'>மிதுனம்</span>{get_c(2)}</td></tr>
    <tr><td><span class='rasi-label'>கும்பம்</span>{get_c(10)}</td><td colspan="2" rowspan="2" style="text-align:center; vertical-align:middle; color:#8B0000; font-weight:bold; font-size:1.2em;">ஜாமக்கோள்<br>திருக்கணிதம்</td><td><span class='rasi-label'>கடகம்</span>{get_c(3)}</td></tr>
    <tr><td><span class='rasi-label'>மகரம்</span>{get_c(9)}</td><td><span class='rasi-label'>சிம்மம்</span>{get_c(4)}</td></tr>
    <tr><td><span class='rasi-label'>தனுசு</span>{get_c(8)}</td><td><span class='rasi-label'>விருச்சி</span>{get_c(7)}</td><td><span class='rasi-label'>துலாம்</span>{get_c(6)}</td><td><span class='rasi-label'>கன்னி</span>{get_c(5)}</td></tr>
</table>
""", unsafe_allow_html=True)
