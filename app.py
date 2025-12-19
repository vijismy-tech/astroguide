import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. ஆப் அமைப்புகள் & CSS ----------
st.set_page_config(page_title="AstroGuide ஜாமக்கோள்", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .stApp { background-color: #FFFDF9; }
    .header-style { background: #4A0000; color: white !important; text-align: center; padding: 12px; border-radius: 8px; font-size: 1.4em; font-weight: bold; }
    
    /* ஜாமக்கோள் கட்டம் -Exact Predictions ஸ்டைல் */
    .jam-chart { width: 100%; border-collapse: collapse; border: 2px solid #4A0000; table-layout: fixed; background: white; }
    .jam-chart td { border: 1px solid #4A0000; height: 110px; vertical-align: top; padding: 5px; position: relative; }
    
    .rasi-name { color: #4A0000; font-size: 0.7em; font-weight: bold; display: block; margin-bottom: 2px; }
    .inner-planets { color: #000; font-weight: bold; font-size: 0.8em; line-height: 1.1; }
    .outer-planets { color: #660066; font-weight: bold; font-size: 0.85em; display: block; margin-top: 5px; border-top: 0.5px dashed #ccc; padding-top: 2px; }
    .special-marker { color: #D32F2F; font-weight: bold; font-size: 0.85em; display: block; margin-top: 2px; }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. லாகின் & தேர்வுகள் ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<div class='header-style'>🔱 ஜாமக்கோள் பிரசன்னம் லாகின்</div>", unsafe_allow_html=True)
    if st.button("உள்ளே செல்க"): st.session_state.logged_in = True; st.rerun()
    st.stop()

districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}
st.markdown("<div class='header-style'>🔱 திருக்கணித ஜாமக்கோள் பிரசன்னம்</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1: s_dist = st.selectbox("ஊர்:", list(districts.keys()))
with c2: s_date = st.date_input("தேதி:", datetime.now(IST))
lat, lon = districts[s_dist]

# ---------------- 3. ஜாமக்கோள் கணித லாஜிக் ----------------
def get_jamakkol_pro(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=tz)
    sunrise, sunset = s["sunrise"], s["sunset"]
    
    # ஜாமம் கணக்கீடு
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

    # Swiss Ephemeris Lahiri
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0 + now.second/3600.0 - 5.5)

    # 1. உள்வட்ட கிரகங்கள் (கோச்சாரம்)
    inner_transit = {}
    p_map = {0:"சூரி", 1:"சந்", 2:"செவ்", 3:"புத", 4:"குரு", 5:"சுக்", 6:"சனி", 10:"ராகு"}
    for pid, name in p_map.items():
        res, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        deg = res[0]
        idx = int(deg / 30)
        p_str = f"{name} {int(deg%30)}"
        if idx not in inner_transit: inner_transit[idx] = []
        inner_transit[idx].append(p_str)
        if pid == 10:
            k_idx = (idx + 6) % 12
            if k_idx not in inner_transit: inner_transit[k_idx] = []
            inner_transit[k_idx].append(f"கேது {int(deg%30)}")

    # 2. வெளிவட்ட கிரகங்கள் (ஜாமக்கோள் கிரகங்கள்)
    # ஜாமக்கோள் கிரக வரிசை: வார கிரகம் தொடங்கி கடிகார சுற்றில்
    jam_order = ["சூரி", "சுக்", "புத", "சந்", "சனி", "குரு", "செவ்", "ராகு"] # ஜாமக்கோள் வரிசை
    # இன்றைய வாரத்தின் முதல் ஜாம கிரகம் (சூரிய உதயம் முதல்)
    weekday_map = {0:"சந்", 1:"செவ்", 2:"புத", 3:"குரு", 4:"சுக்", 5:"சனி", 6:"சூரி"}
    start_planet = weekday_map[date_obj.weekday()]
    
    outer_transit = {}
    start_idx = jam_order.index(start_planet)
    
    # நடப்பு ஜாம கிரகத்தைக் கண்டறிதல்
    current_jam_planet = jam_order[(start_idx + (cur_jam - 1)) % 8]
    
    # சூரியன் நின்ற ராசி (உதய ராசி ஆரம்பம்)
    sun_pos = swe.calc_ut(jd_ut, 0, swe.FLG_SIDEREAL)[0][0]
    sun_sign = int(sun_pos / 30)

    # ஜாமக்கோள் கிரகங்களை கட்டத்தில் அமர்த்துதல்
    for i in range(8):
        p_name = jam_order[(start_idx + i) % 8]
        # ஜாமக்கோள் கிரகங்கள் உதய ராசியிலிருந்து கடிகார சுற்றில் சுழலும்
        target_idx = (sun_sign + i) % 12
        if target_idx not in outer_transit: outer_transit[target_idx] = []
        outer_transit[target_idx].append(p_name)

    # 3. உதயம், ஆருடம், கவிப்பு
    jam_prog = (elapsed % duration) / duration
    u_deg = ((sun_sign + (cur_jam - 1)) * 30 + (jam_prog * 30)) % 360
    a_deg = ((sun_sign + cur_jam) * 30) % 360
    k_deg = (u_deg + (sun_pos % 30)) % 360

    return {
        "inner": inner_transit, "outer": outer_transit,
        "jam_info": f"{j_type} {cur_jam}-ம் ஜாமம் ({current_jam_planet})",
        "u": [int(u_deg/30), int(u_deg%30)],
        "a": [int(a_deg/30), int(a_deg%30)],
        "k": [int(k_deg/30), int(k_deg%30)],
        "details": f"{now.strftime('%d-%m-%Y %H:%M')} | {s_dist}"
    }

res = get_jamakkol_pro(s_date, lat, lon)

# ---------------- 4. கட்டம் வெளியீடு ----------------
st.markdown(f"<div style='text-align:center; font-weight:bold; color:#4A0000; margin-bottom:5px;'>{res['details']}</div>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center; font-size:0.9em; margin-bottom:10px;'>{res['jam_info']}</div>", unsafe_allow_html=True)


def get_cell(i):
    # உள்வட்ட கோச்சாரம்
    inner_html = "<div class='inner-planets'>" + " ".join(res['inner'].get(i, [])) + "</div>"
    # வெளிவட்ட ஜாமக்கோள்
    outer_html = "<div class='outer-planets'>" + " ".join(res['outer'].get(i, [])) + "</div>"
    # சிறப்புக் குறிகள்
    special = ""
    if i == res['u'][0]: special += f"<span class='special-marker' style='color:red;'>உத-{res['u'][1]}</span>"
    if i == res['a'][0]: special += f"<span class='special-marker' style='color:blue;'>ஆரு-{res['a'][1]}</span>"
    if i == res['k'][0]: special += f"<span class='special-marker' style='color:brown;'>கவி-{res['k'][1]}</span>"
    
    return f"{inner_html}{outer_html}{special}"

rasi_names = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சி", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]

st.markdown(f"""
<table class="jam-chart">
    <tr>
        <td><span class='rasi-name'>மீனம்</span>{get_cell(11)}</td>
        <td><span class='rasi-name'>மேஷம்</span>{get_cell(0)}</td>
        <td><span class='rasi-name'>ரிஷபம்</span>{get_cell(1)}</td>
        <td><span class='rasi-name'>மிதுனம்</span>{get_content(2)}</td>
    </tr>
    <tr>
        <td><span class='rasi-name'>கும்பம்</span>{get_cell(10)}</td>
        <td colspan="2" rowspan="2" style="text-align:center; vertical-align:middle; background:#f9f9f9;">
            <b style="font-size:1.2em; color:#4A0000;">ஜாமக்கோள்</b><br>
            <small>{res['details']}</small>
        </td>
        <td><span class='rasi-name'>கடகம்</span>{get_cell(3)}</td>
    </tr>
    <tr>
        <td><span class='rasi-name'>மகரம்</span>{get_cell(9)}</td>
        <td><span class='rasi-name'>சிம்மம்</span>{get_cell(4)}</td>
    </tr>
    <tr>
        <td><span class='rasi-label'>தனுசு</span>{get_cell(8)}</td>
        <td><span class='rasi-label'>விருச்சிகம்</span>{get_cell(7)}</td>
        <td><span class='rasi-label'>துலாம்</span>{get_cell(6)}</td>
        <td><span class='rasi-label'>கன்னி</span>{get_cell(5)}</td>
    </tr>
</table>
""", unsafe_allow_html=True)
