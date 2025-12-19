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
    .stApp { background-color: #FFF9F2; }
    .header-style { background-color: #8B0000; color: white !important; text-align: center; padding: 12px; border-radius: 10px; font-size: 1.3em; font-weight: bold; margin-bottom: 15px; }
    .main-box { max-width: 500px; margin: auto; padding: 15px; background: white; border-radius: 10px; border: 1px solid #8B0000; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .meroon-header { color: #8B0000 !important; font-size: 1.1em; font-weight: bold; border-bottom: 2px solid #8B0000; margin: 15px 0; padding-bottom: 5px; text-align: center; }
    
    /* ஜாமக்கோள் கட்டம் வடிவமைப்பு */
    .jamakkol-chart { width: 100%; border-collapse: collapse; border: 2.5px solid #8B0000; table-layout: fixed; background: white; }
    .jamakkol-chart td { border: 1.5px solid #8B0000; height: 110px; vertical-align: top; padding: 6px; font-size: 0.72em; }
    .rasi-label { color: #8B0000; font-weight: bold; display: block; border-bottom: 1px solid #f0f0f0; margin-bottom: 4px; font-size: 1.1em; }
    .jam-planet { color: #000; font-weight: 700; display: block; line-height: 1.3; margin-bottom: 2px; }
    .special-label { color: #d32f2f; font-weight: bold; display: block; font-size: 0.95em; margin-top: 3px; background: #fff5f5; border-radius: 3px; padding: 1px; }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. லாகின் ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<div class='header-style'>🔱 AstroGuide ஜாமக்கோள் பிரசன்னம்</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-box' style='text-align:center;'>", unsafe_allow_html=True)
    if st.button("ஜாமக்கோள் கணிக்க உள்ளே செல்க"): st.session_state.logged_in = True; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------- 3. தேர்வுகள் ----------------
districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}
st.markdown("<div class='header-style'>🔱 AstroGuide ஜாமக்கோள் பிரசன்னம்</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1: s_dist = st.selectbox("ஊர்:", list(districts.keys()))
with c2: s_date = st.date_input("தேதி:", datetime.now(IST))
lat, lon = districts[s_dist]

# ---------------- 4. ஜாமக்கோள் கணித லாஜிக் ----------------
def get_jamakkol_details(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    tz = pytz.timezone(tz_name)
    current_time = datetime.now(tz)
    
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=tz)
    sunrise, sunset = s["sunrise"], s["sunset"]
    
    # ஜாமம் கணக்கீடு
    day_dur = (sunset - sunrise).total_seconds() / 8
    elapsed = (current_time - sunrise).total_seconds()
    cur_jam = int(elapsed / day_dur) + 1 if elapsed > 0 else 1
    if cur_jam > 8: cur_jam = 8

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(current_time.year, current_time.month, current_time.day, 
                       current_time.hour + current_time.minute/60.0 - 5.5)

    def f_deg(deg):
        return f"{int(deg % 30)}°{int((deg % 1) * 60)}'"

    # கிரகங்களின் பாகை
    transit = {}
    p_names = {0:"சூரி", 1:"சந்", 2:"செவ்", 3:"புத", 4:"குரு", 5:"சுக்", 6:"சனி", 10:"ராகு"}
    for pid, name in p_names.items():
        pos, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        idx = int(pos[0]/30)
        p_info = f"{name}({f_deg(pos[0])})"
        if idx not in transit: transit[idx] = []
        transit[idx].append(p_info)
        if pid == 10:
            k_deg = (pos[0] + 180) % 360
            k_info = f"கேது({f_deg(k_deg)})"
            k_idx = int(k_deg/30)
            if k_idx not in transit: transit[k_idx] = []
            transit[k_idx].append(k_info)

    # உதய ஆருட கவிப்பு பாகை கணக்கீடு
    sun_pos, _ = swe.calc_ut(jd_ut, 0, swe.FLG_SIDEREAL)
    sun_sign = int(sun_pos[0]/30)
    jam_prog = (elapsed % day_dur) / day_dur
    
    u_raw = ((sun_sign + (cur_jam - 1)) * 30) + (jam_prog * 30)
    a_raw = ((sun_sign + cur_jam) * 30)
    k_raw = (u_raw + (sun_pos[0] % 30)) % 360

    return {
        "transit": transit, "jam": cur_jam,
        "udayam": [int((u_raw/30)%12), f_deg(u_raw)],
        "arudam": [int((a_raw/30)%12), f_deg(a_raw)],
        "kavippu": [int((k_raw/30)%12), f_deg(k_raw)],
        "time": current_time.strftime("%I:%M %p")
    }

res = get_jamakkol_details(s_date, lat, lon)

# ---------------- 5. ஜாமக்கோள் கட்டம் வெளியீடு ----------------
st.markdown(f"<div class='meroon-header'>🕒 ஜாமம்: {res['jam']} | நேரம்: {res['time']}</div>", unsafe_allow_html=True)



def get_content(idx):
    html = ""
    for p in res['transit'].get(idx, []):
        html += f"<span class='jam-planet'>{p}</span>"
    if idx == res['udayam'][0]: html += f"<span class='special-label' style='color:green;'>[உதய {res['udayam'][1]}]</span>"
    if idx == res['arudam'][0]: html += f"<span class='special-label' style='color:brown;'>[ஆருட {res['arudam'][1]}]</span>"
    if idx == res['kavippu'][0]: html += f"<span class='special-label' style='color:red;'>[கவிப்பு {res['kavippu'][1]}]</span>"
    return html

st.markdown(f"""
<table class="jamakkol-chart">
    <tr>
        <td><span class='rasi-label'>மீனம்</span>{get_content(11)}</td>
        <td><span class='rasi-label'>மேஷம்</span>{get_content(0)}</td>
        <td><span class='rasi-label'>ரிஷபம்</span>{get_content(1)}</td>
        <td><span class='rasi-label'>மிதுனம்</span>{get_content(2)}</td>
    </tr>
    <tr>
        <td><span class='rasi-label'>கும்பம்</span>{get_content(10)}</td>
        <td colspan="2" rowspan="2" style="background:#fdfdfd; text-align:center; vertical-align:middle; color:#8B0000; font-weight:bold; font-size:1.3em;">
            ஜாமக்கோள்<br>பாகை பிரசன்னம்
        </td>
        <td><span class='rasi-label'>கடகம்</span>{get_content(3)}</td>
    </tr>
    <tr>
        <td><span class='rasi-label'>மகரம்</span>{get_content(9)}</td>
        <td><span class='rasi-label'>சிம்மம்</span>{get_content(4)}</td>
    </tr>
    <tr>
        <td><span class='rasi-label'>தனுசு</span>{get_content(8)}</td>
        <td><span class='rasi-label'>விருச்சி</span>{get_content(7)}</td>
        <td><span class='rasi-label'>துலாம்</span>{get_content(6)}</td>
        <td><span class='rasi-label'>கன்னி</span>{get_content(5)}</td>
    </tr>
</table>
""", unsafe_allow_html=True)

st.success("குறிப்பு: கிரகங்களின் பெயருக்கு அருகில் உள்ள அடைப்புக்குறிக்குள் இருப்பது அந்த ராசியில் அதன் தொடு பாகை ஆகும்.")
