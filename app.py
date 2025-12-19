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
    .stApp { background-color: #FFF8F0; }
    .header-style { background-color: #8B0000; color: white !important; text-align: center; padding: 10px; border-radius: 10px; font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
    .main-box { max-width: 450px; margin: auto; padding: 10px; background: white; border-radius: 8px; border: 1px solid #8B0000; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .meroon-header { color: #8B0000 !important; font-size: 1.1em; font-weight: bold; border-bottom: 2px solid #8B0000; margin: 15px 0; padding-bottom: 5px; }
    
    /* ஜாமக்கோள் கட்டம் வடிவமைப்பு */
    .jamakkol-chart { width: 100%; border-collapse: collapse; border: 2px solid #8B0000; table-layout: fixed; background: white; }
    .jamakkol-chart td { border: 1px solid #8B0000; height: 100px; vertical-align: top; padding: 5px; font-size: 0.75em; }
    .rasi-label { color: #8B0000; font-weight: bold; display: block; border-bottom: 1px solid #eee; margin-bottom: 2px; }
    .jam-planet { color: #000; font-weight: 600; display: block; line-height: 1.2; }
    .special-label { color: #d32f2f; font-weight: bold; display: block; font-size: 0.9em; }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. லாகின் & தேர்வுகள் ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<div class='header-style'>🔱 AstroGuide ஜாமக்கோள் லாகின்</div>", unsafe_allow_html=True)
    if st.button("உள்ளே செல்க"): st.session_state.logged_in = True; st.rerun()
    st.stop()

districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}
st.markdown("<div class='header-style'>🔱 AstroGuide ஜாமக்கோள் பிரசன்னம்</div>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: s_dist = st.selectbox("ஊர்:", list(districts.keys()))
with c2: s_date = st.date_input("தேதி:", datetime.now(IST))
lat, lon = districts[s_dist]

# ---------------- 3. ஜாமக்கோள் லாஜிக் & கணக்கீடுகள் ----------------
def get_jamakkol_data(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=pytz.timezone(tz_name))
    
    sunrise = s["sunrise"]
    sunset = s["sunset"]
    current_time = datetime.now(pytz.timezone(tz_name))
    
    # 1. ஜாமம் கணக்கீடு (8 ஜாமங்கள்)
    day_duration = (sunset - sunrise).total_seconds() / 8
    elapsed = (current_time - sunrise).total_seconds()
    current_jam = int(elapsed / day_duration) + 1 if elapsed > 0 else 1
    if current_jam > 8: current_jam = 8

    # 2. உதய ராசி கணக்கீடு (Sunrise based)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, current_time.hour + current_time.minute/60.0 - 5.5)
    sun_pos, _ = swe.calc_ut(jd_ut, 0, swe.FLG_SIDEREAL)
    sunrise_rasi = int(sun_pos[0] / 30) # சூரியன் நின்ற ராசி

    # ஜாமக்கோள் கிரக வரிசை: செவ், புத, குரு, சுக், சனி, சந், ராகு, கேது (சூரியன் கணக்கில் வராது)
    jam_planets_order = ["செவ்", "புத", "குரு", "சுக்", "சனி", "சந்", "ராகு", "கேது"]
    
    # வாரத்தின் முதல் கிரகம்
    weekday_start = {0:0, 1:4, 2:2, 3:1, 4:5, 5:3, 6:0}[date_obj.weekday()] # திங்கள்-சந் (இங்கு ஜாம வரிசைப்படி)
    
    jamakkol_pos = {}
    
    # 3. கவிப்பு கணக்கீடு
    # உதயத்திலிருந்து சூரியன் நின்ற பாகை வரை உள்ள தூரம்
    kavippu_idx = (sunrise_rasi + (current_jam - 1)) % 12
    
    # 4. ஆருடம் கணக்கீடு (தற்போதைய ஜாமம் அடிப்படையில்)
    arudam_idx = (sunrise_rasi + current_jam) % 12

    # 5. கோச்சார கிரகங்களை எடுத்தல்
    transit = {}
    p_ids = {0:"சூரி", 1:"சந்", 2:"செவ்", 3:"புத", 4:"குரு", 5:"சுக்", 6:"சனி", 10:"ராகு"}
    for pid, name in p_ids.items():
        pos, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        idx = int(pos[0]/30)
        if idx not in transit: transit[idx] = []
        transit[idx].append(name)
        if pid == 10:
            k_idx = (idx + 6) % 12
            if k_idx not in transit: transit[k_idx] = []
            transit[k_idx].append("கேது")

    return {
        "transit": transit,
        "jam": current_jam,
        "kavippu": kavippu_idx,
        "arudam": arudam_idx,
        "udayam": (sunrise_rasi + current_jam - 1) % 12,
        "time": current_time.strftime("%I:%M %p")
    }

res = get_jamakkol_data(s_date, lat, lon)

# ---------------- 4. ஜாமக்கோள் அட்டவணை & கட்டம் ----------------

st.markdown(f"<div class='meroon-header'>🕒 தற்போதைய ஜாமம்: {res['jam']} | நேரம்: {res['time']}</div>", unsafe_allow_html=True)



def get_box_content(i):
    content = ""
    # கோச்சார கிரகங்கள்
    for p in res['transit'].get(i, []):
        content += f"<span class='jam-planet'>{p}</span>"
    # ஜாமக்கோள் சிறப்பம்சங்கள்
    if i == res['udayam']: content += "<span class='special-label'>[உதயம்]</span>"
    if i == res['arudam']: content += "<span class='special-label'>[ஆருடம்]</span>"
    if i == res['kavippu']: content += "<span class='special-label' style='color:blue;'>[கவிப்பு]</span>"
    return content

st.markdown(f"""
<table class="jamakkol-chart">
    <tr>
        <td><span class='rasi-label'>மீனம்</span>{get_box_content(11)}</td>
        <td><span class='rasi-label'>மேஷம்</span>{get_box_content(0)}</td>
        <td><span class='rasi-label'>ரிஷபம்</span>{get_box_content(1)}</td>
        <td><span class='rasi-label'>மிதுனம்</span>{get_box_content(2)}</td>
    </tr>
    <tr>
        <td><span class='rasi-label'>கும்பம்</span>{get_box_content(10)}</td>
        <td colspan="2" rowspan="2" style="background:#fdfdfd; text-align:center; vertical-align:middle; color:#8B0000; font-weight:bold; font-size:1.2em;">
            ஜாமக்கோள்<br>பிரசன்னம்
        </td>
        <td><span class='rasi-label'>கடகம்</span>{get_box_content(3)}</td>
    </tr>
    <tr>
        <td><span class='rasi-label'>மகரம்</span>{get_box_content(9)}</td>
        <td><span class='rasi-label'>சிம்மம்</span>{get_box_content(4)}</td>
    </tr>
    <tr>
        <td><span class='rasi-label'>தனுசு</span>{get_box_content(8)}</td>
        <td><span class='rasi-label'>விருச்சிகம்</span>{get_box_content(7)}</td>
        <td><span class='rasi-label'>துலாம்</span>{get_box_content(6)}</td>
        <td><span class='rasi-label'>கன்னி</span>{get_box_content(5)}</td>
    </tr>
</table>
<p style='font-size:0.8em; color:gray; text-align:center; margin-top:5px;'>* உதயம், ஆருடம், கவிப்பு ஆகியவை தற்போதைய ஜாம நேரத்தின் அடிப்படையில் கணக்கிடப்பட்டுள்ளது.</p>
""", unsafe_allow_html=True)

# ---------------- 5. ஜாமக்கோள் பலன் குறிப்பு ----------------
st.markdown("<div class='meroon-header'>💡 ஜாமக்கோள் பலன் காணும் முறை</div>", unsafe_allow_html=True)
st.info("""
1. **உதயம்:** கேள்வி கேட்பவரை குறிக்கும்.
2. **ஆருடம்:** காரியத்தின் வெற்றியை குறிக்கும்.
3. **கவிப்பு:** தடையை குறிக்கும் (கவிப்பு நின்ற ராசி அல்லது கிரகம் கவிழ்ந்துள்ளது என்று பொருள்).
4. கவிப்பு உதயத்திலோ அல்லது ஆருடத்திலோ இருந்தால் காரியம் தடைபடும்.
""")
