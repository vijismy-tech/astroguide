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
    .header-style { background: #4A0000; color: white !important; text-align: center; padding: 12px; border-radius: 8px; font-size: 1.4em; font-weight: bold; margin-bottom: 20px; }
    
    /* ஜாமக்கோள் கட்டம் வடிவமைப்பு */
    .chart-container { display: flex; flex-direction: column; align-items: center; justify-content: center; margin: auto; max-width: 600px; }
    .jam-chart { width: 100%; border-collapse: collapse; border: 2px solid #4A0000; table-layout: fixed; background: white; }
    .jam-chart td { border: 1.5px solid #4A0000; height: 100px; vertical-align: top; padding: 5px; position: relative; }
    
    /* ஜாம கிரகங்கள் - கட்டத்திற்கு வெளியே */
    .outer-top, .outer-bottom { display: flex; justify-content: space-around; width: 100%; padding: 5px 0; color: #660066; font-weight: bold; font-size: 0.85em; }
    .outer-side-container { display: flex; align-items: center; width: 100%; }
    .outer-left, .outer-right { display: flex; flex-direction: column; justify-content: space-around; height: 400px; padding: 0 15px; color: #660066; font-weight: bold; font-size: 0.85em; }

    .inner-planets { color: #000; font-weight: bold; font-size: 0.8em; line-height: 1.2; }
    .special-marker { color: #D32F2F; font-weight: bold; font-size: 0.85em; display: block; margin-top: 3px; }
    .rasi-label { color: #8B0000; font-size: 0.65em; font-weight: bold; position: absolute; bottom: 2px; right: 2px; opacity: 0.5; }

    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. லாகின் & தேர்வுகள் ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<div class='header-style'>🔱 ஜாமக்கோள் பிரசன்னம்</div>", unsafe_allow_html=True)
    if st.button("கணிக்க உள்ளே செல்க"): st.session_state.logged_in = True; st.rerun()
    st.stop()

districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}
st.markdown("<div class='header-style'>🔱 திருக்கணித ஜாமக்கோள் பிரசன்னம்</div>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: s_dist = st.selectbox("ஊர்:", list(districts.keys()))
with c2: s_date = st.date_input("தேதி:", datetime.now(IST))
lat, lon = districts[s_dist]

# ---------------- 3. கணித லாஜிக் ----------------
def get_jamakkol_final(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    tz = pytz.timezone(tz_name); now = datetime.now(tz)
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=tz)
    sunrise, sunset = s["sunrise"], s["sunset"]
    
    is_day = sunrise <= now <= sunset
    if is_day:
        duration = (sunset - sunrise).total_seconds() / 8
        elapsed = (now - sunrise).total_seconds(); j_type = "பகல்"
    else:
        next_s = sun(observer=city.observer, date=date_obj+timedelta(days=1), tzinfo=tz)["sunrise"]
        if now < sunrise:
            prev_s = sun(observer=city.observer, date=date_obj-timedelta(days=1), tzinfo=tz)["sunset"]
            duration = (sunrise - prev_s).total_seconds() / 8; elapsed = (now - prev_s).total_seconds()
        else:
            duration = (next_s - sunset).total_seconds() / 8; elapsed = (now - sunset).total_seconds()
        j_type = "இரவு"

    cur_jam = min(int(elapsed / duration) + 1, 8)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0 + now.second/3600.0 - 5.5)

    # கோச்சாரம்
    inner = {}
    p_map = {0:"சூரி", 1:"சந்", 2:"செவ்", 3:"புத", 4:"குரு", 5:"சுக்", 6:"சனி", 10:"ராகு"}
    for pid, name in p_map.items():
        res, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        idx = int(res[0]/30)
        p_str = f"{name} {int(res[0]%30)}"
        if idx not in inner: inner[idx] = []
        inner[idx].append(p_str)
        if pid == 10:
            k_idx = (idx + 6) % 12
            if k_idx not in inner: inner[k_idx] = []
            inner[k_idx].append(f"கேது {int(res[0]%30)}")

    # ஜாமக்கோள் கிரகங்கள் (வெளியே இருப்பவை)
    jam_order = ["சூரி", "சுக்", "புத", "சந்", "சனி", "குரு", "செவ்", "ராகு"]
    wk_map = {0:"சந்", 1:"செவ்", 2:"புத", 3:"குரு", 4:"சுக்", 5:"சனி", 6:"சூரி"}
    start_p = wk_map[date_obj.weekday()]
    start_idx = jam_order.index(start_p)
    sun_pos = swe.calc_ut(jd_ut, 0, swe.FLG_SIDEREAL)[0][0]
    sun_sign = int(sun_pos / 30)

    outer_planets_list = []
    for i in range(8):
        p_name = jam_order[(start_idx + i) % 8]
        outer_planets_list.append(p_name)

    # உதயம், ஆருடம், கவிப்பு
    j_prog = (elapsed % duration) / duration
    u_deg = ((sun_sign + (cur_jam - 1)) * 30 + (j_prog * 30)) % 360
    a_deg = ((sun_sign + cur_jam) * 30) % 360
    k_deg = (u_deg + (sun_pos % 30)) % 360

    return {
        "inner": inner, "outer": outer_planets_list,
        "jam_txt": f"{j_type} {cur_jam}-ம் ஜாமம்",
        "u": [int(u_deg/30), int(u_deg%30)], "a": [int(a_deg/30), int(a_deg%30)], "k": [int(k_deg/30), int(k_deg%30)],
        "details": now.strftime("%d-%m-%Y | %H:%M")
    }

res = get_jamakkol_final(s_date, lat, lon)

# ---------------- 4. கட்டம் வெளியீடு ----------------
def get_in(i):
    txt = "<div class='inner-planets'>" + " ".join(res['inner'].get(i, [])) + "</div>"
    if i == res['u'][0]: txt += f"<span class='special-marker' style='color:red;'>உத-{res['u'][1]}</span>"
    if i == res['a'][0]: txt += f"<span class='special-marker' style='color:blue;'>ஆரு-{res['a'][1]}</span>"
    if i == res['k'][0]: txt += f"<span class='special-marker' style='color:brown;'>கவி-{res['k'][1]}</span>"
    return txt

st.markdown(f"""
<div class="chart-container">
    <div class="outer-top">
        <span>{res['outer'][7]}</span><span>{res['outer'][0]}</span><span>{res['outer'][1]}</span><span>{res['outer'][2]}</span>
    </div>
    <div class="outer-side-container">
        <div class="outer-left"><span>{res['outer'][6]}</span><span>{res['outer'][5]}</span></div>
        <table class="jam-chart">
            <tr><td>{get_in(11)}</td><td>{get_in(0)}</td><td>{get_in(1)}</td><td>{get_in(2)}</td></tr>
            <tr><td>{get_in(10)}</td><td colspan="2" rowspan="2" style="text-align:center; background:#FFF9F0;"><b>ஜாமக்கோள்</b><br><small>{res['jam_txt']}</small></td><td>{get_in(3)}</td></tr>
            <tr><td>{get_in(9)}</td><td>{get_in(4)}</td></tr>
            <tr><td>{get_in(8)}</td><td>{get_in(7)}</td><td>{get_in(6)}</td><td>{get_in(5)}</td></tr>
        </table>
        <div class="outer-right"><span>{res['outer'][3]}</span><span>{res['outer'][4]}</span></div>
    </div>
    <div class="outer-bottom">
        <span></span><span></span><span></span><span></span>
    </div>
</div>
""", unsafe_allow_html=True)
