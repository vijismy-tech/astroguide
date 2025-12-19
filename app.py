import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. ஆப் அமைப்புகள் & CSS வடிவமைப்பு ----------
st.set_page_config(page_title="AstroGuide Pro - Panchangam & Horai", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #ffffff 0%, #fcf9f0 100%); }
    h1, h2, h3, p, span, div, label, td, th { color: #1a1a1a !important; font-family: 'Arial', sans-serif; }
    
    .header-style { 
        background: linear-gradient(135deg, #4A0000 0%, #8B0000 50%, #4A0000 100%);
        color: #FFD700 !important; text-align: center; padding: 20px; border-radius: 15px; 
        font-size: 1.8em; font-weight: bold; box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        border: 2px solid #D4AF37; margin-bottom: 25px;
    }
    
    .meroon-header { 
        background-color: #8B0000; color: white !important; text-align: center; 
        padding: 8px; border-radius: 5px; font-size: 1.1em; font-weight: bold; 
        margin-top: 15px; margin-bottom: 10px;
    }
    
    .panchang-table { width: 100%; border-collapse: collapse; background: white; border: 1.5px solid #8B0000; font-size: 0.9em; }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 10px; text-align: center; }
    .panchang-table td { padding: 8px 12px; border: 1px solid #eee; font-weight: 500; }
    
    .horai-box { background-color: #f0f7ff; border-left: 5px solid #1A5276; padding: 10px; margin-top: 5px; font-weight: bold; }
    .subha-box { background-color: #F5FFFA; border-left: 5px solid #2E7D32; padding: 10px; margin-top: 5px; font-weight: bold; color: #1B5E20; }

    .rasi-chart { width: 620px; border-collapse: collapse; border: 5px solid #8B0000; background: white; table-layout: fixed; margin: auto; }
    .rasi-chart td { border: 2px solid #D4AF37; height: 140px; vertical-align: top; padding: 10px; position: relative; }
    .planet-text { color: #1a1a1a; font-weight: 800; font-size: 1em; line-height: 1.3; }
    .vakra-text { color: #D32F2F; font-size: 0.85em; }
    .rasi-label { color: #8B0000; font-size: 0.7em; font-weight: bold; position: absolute; bottom: 5px; right: 8px; background: #fdf5e6; padding: 2px 5px; border-radius: 4px; }
    
    .center-info-box { text-align: center; background: #FFFBF2; border: 2.5px double #D4AF37; border-radius: 12px; padding: 12px; }
    </style>
    """, unsafe_allow_html=True)

# ---------- 2. லாகின் ----------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<div class='header-style'>🔱 AstroGuide Pro உள்நுழைவு</div>", unsafe_allow_html=True)
    if st.button("உள்ளே செல்க"): st.session_state.logged_in = True; st.rerun()
    st.stop()

# ---------- 3. தேர்வுகள் ----------
st.markdown("<div class='header-style'>🔱 ஸ்ரீ திருக்கணித பஞ்சாங்கம் & ஹோரை</div>", unsafe_allow_html=True)
districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}

col_x, col_y = st.columns(2)
with col_x: s_dist = st.selectbox("ஊர் தேர்வு செய்க:", list(districts.keys()))
with col_y: 
    s_date = st.date_input("தேதி:", datetime.now(IST))
    s_time = st.time_input("நேரம் (Live):", datetime.now(IST).time())
lat, lon = districts[s_dist]

# ---------- 4. ஜோதிடக் கணக்கீடுகள் ----------
def get_pro_astro_data(date_obj, time_obj, lat, lon):
    dt_combined = datetime.combine(date_obj, time_obj)
    tf = TimezoneFinder(); tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    tz = pytz.timezone(tz_name)
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s_info = sun(observer=city.observer, date=date_obj, tzinfo=tz)
    sunrise = s_info["sunrise"]
    
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_sunrise = swe.julday(sunrise.year, sunrise.month, sunrise.day, sunrise.hour + sunrise.minute/60.0 - 5.5)
    jd_current = swe.julday(dt_combined.year, dt_combined.month, dt_combined.day, (dt_combined.hour + dt_combined.minute/60.0 - 5.5))

    def get_raw(jd):
        m, _ = swe.calc_ut(jd, 1, swe.FLG_SIDEREAL)
        s_p, _ = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)
        t = ((m[0]-s_p[0])%360)/12
        n = m[0]/(360/27)
        return m[0], int(t), int(n), s_p[0]

    m_deg_rise, t_n, n_n, s_deg_rise = get_raw(jd_sunrise)
    
    # தமிழ் பஞ்சாங்க விவரங்கள்
    months = ["சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி", "ஐப்பசி", "கார்த்திகை", "மார்கழி", "தை", "மாசி", "பங்குனி"]
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    
    # 60 வருடங்கள் (தானியங்கி விசுவாசு அப்டேட்)
    years_60 = ["பிரபவ", "விபவ", "சுக்ல", "பிரமோதூத", "பிரஜோத்பத்தி", "ஆங்கீரச", "ஸ்ரீமுக", "பவ", "யுவ", "தாது", "ஈஸ்வர", "வெகுதானிய", "பிரமாதி", "விக்ரம", "விஷு", "சித்ரபானு", "சுபானு", "தாரண", "பார்த்திப", "விய", "சர்வஜித்", "சர்வதாரி", "விரோதி", "விக்ருதி", "கர", "நந்தன", "விஜய", "ஜய", "மன்மத", "துன்முகி", "ஹேவிளம்பி", "விளம்பி", "விகாரி", "சார்வரி", "பிலவ", "சுபகிருது", "சோபகிருது", "குரோதி", "விசுவாசு", "பராபவ", "பிளவங்க", "கீலக", "சௌமிய", "சாதாரண", "விரோதகிருது", "பரிதாபி", "பிரமாதீச", "ஆனந்த", "ராட்சச", "நள", "பிங்கள", "காளயுக்தி", "சித்தார்த்தி", "ரௌத்திரி", "துன்மதி", "துந்துபி", "ருத்ரோத்காரி", "ரக்தாட்சி", "குரோதன", "அட்சய"]
    y_cycle = (date_obj.year - 1987) % 60
    if (date_obj.month < 4) or (date_obj.month == 4 and date_obj.day < 14): y_cycle -= 1
    
    # ஹோரை கணக்கீடு (Horai Calculation)
    # ஞாயிறு: சூரி, சுக், புத, சந், சனி, குரு, செவ்...
    horai_order = ["சூரியன்", "சுக்கிரன்", "புதன்", "சந்திரன்", "சனி", "குரு", "செவ்வாய்"]
    wk_day_to_horai_start = {6:0, 0:3, 1:6, 2:2, 3:5, 4:1, 5:4} # Sunday=Sun, Monday=Moon...
    start_horai_idx = wk_day_to_horai_start[date_obj.weekday()]
    
    diff_hours = (dt_combined.replace(tzinfo=tz) - sunrise).total_seconds() / 3600
    current_horai = horai_order[(start_horai_idx + int(diff_hours)) % 7]

    # சுப முகூர்த்த நாள் கணக்கீடு (எளிமைப்படுத்தப்பட்ட விதி)
    bad_tithis = ["சதுர்த்தி", "அஷ்டமி", "நவமி", "சதுர்த்தசி", "அமாவாசை"]
    is_subha = "சுப முகூர்த்த நாள் அல்ல" if tithis[t_n % 30] in bad_tithis else "சுப முகூர்த்த நாள் (விசேஷமான நாள்)"

    # ராசி கட்டம்
    p_map = {0: "சூரியன்", 1: "சந்திரன்", 2: "செவ்வாய்", 3: "புதன்", 4: "குரு", 5: "சுக்கிரன்", 6: "சனி", 10: "ராகு"}
    res_pos = {}
    for pid, name in p_map.items():
        pos, _ = swe.calc_ut(jd_current, pid, swe.FLG_SIDEREAL)
        deg = pos[0]; idx = int(deg / 30)
        v = " <span class='vakra-text'>(வ)</span>" if pos[3] < 0 else ""
        if idx not in res_pos: res_pos[idx] = []
        res_pos[idx].append(f"<div class='planet-text'>{name}{v} {int(deg%30)}°</div>")
        if pid == 10:
            ki = (idx + 6) % 12
            if ki not in res_pos: res_pos[ki] = []
            res_pos[ki].append(f"<div class='planet-text'>கேது {int(deg%30)}°</div>")

    return {
        "y": years_60[y_cycle % 60], "m": months[int(s_deg_rise/30)%12], "d": int(s_deg_rise%30)+1,
        "tithi": tithis[t_n % 30], "nak": naks[n_n % 27], "n_idx": n_n % 27,
        "rise": sunrise.strftime("%I:%M %p"), "horai": current_horai, "subha": is_subha,
        "wara": ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][date_obj.weekday()],
        "chart": res_pos, "f_dt": dt_combined.strftime("%d-%m-%Y %I:%M %p")
    }

res = get_pro_astro_data(s_date, s_time, lat, lon)

# ---------- 5. காட்சி அமைப்பு ----------
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.markdown("<div class='meroon-header'>📅 இன்றைய பஞ்சாங்கம்</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <table class="panchang-table">
        <tr><td>📅 தமிழ் தேதி</td><td><b>{res['y']} வருடம், {res['m']} {res['d']}</b></td></tr>
        <tr><td>🌅 உதய திதி</td><td><b>{res['tithi']}</b></td></tr>
        <tr><td>⭐ நட்சத்திரம்</td><td><b>{res['nak']}</b></td></tr>
        <tr><td>☀️ சூரிய உதயம்</td><td>{res['rise']}</td></tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div class='horai-box'>🕒 இப்பொழுது நடக்கும் ஹோரை: {res['horai']} ஹோரை</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subha-box'>✨ முகூர்த்த நிலை: {res['subha']}</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='meroon-header'>🎡 திருக்கணித ராசி கட்டம்</div>", unsafe_allow_html=True)
    def draw_box(i):
        planets = "".join(res['chart'].get(i, []))
        rasi_names = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]
        return f"{planets}<span class='rasi-label'>{rasi_names[i]}</span>"

    st.markdown(f"""
    <div class="chart-container">
        <table class="rasi-chart">
            <tr><td>{draw_box(11)}</td><td>{draw_box(0)}</td><td>{draw_box(1)}</td><td>{draw_box(2)}</td></tr>
            <tr><td>{draw_box(10)}</td>
                <td colspan="2" rowspan="2" style="vertical-align:middle;">
                    <div class="center-info-box">
                        <div style="font-weight:bold; color:#8B0000;">{res['y']} வருடம்</div>
                        <div style="color:#B22222;">{res['m']} {res['d']}</div>
                        <div style="font-size:0.8em; margin-top:5px;">{res['f_dt']}</div>
                    </div>
                </td>
                <td>{draw_box(3)}</td></tr>
            <tr><td>{draw_box(9)}</td><td>{draw_box(4)}</td></tr>
            <tr><td>{draw_box(8)}</td><td>{draw_box(7)}</td><td>{draw_box(6)}</td><td>{draw_box(5)}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# சந்திராஷ்டமம்
naks_list = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
st.markdown(f"<div class='meroon-header'>🌙 சந்திராஷ்டமம்: <b style='color:yellow;'>{naks_list[(res['n_idx']-16)%27]}</b> நட்சத்திரம்</div>", unsafe_allow_html=True)
