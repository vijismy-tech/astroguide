import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. App Configuration (ONLY ONE CALL ALLOWED) ----------
st.set_page_config(page_title="AstroGuide Professional Panchangam", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

# ---------- 2. Combined CSS Styling ----------
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #ffffff 0%, #fcf9f0 100%); }
    h1, h2, h3, p, span, div, label, td, th { color: #1a1a1a; font-family: 'Arial', sans-serif; }
    
    .header-style { 
        background: linear-gradient(135deg, #4A0000 0%, #8B0000 50%, #4A0000 100%);
        color: #FFD700 !important; text-align: center; padding: 20px; border-radius: 15px; 
        font-size: 1.8em; font-weight: bold; box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        border: 2px solid #D4AF37; margin-bottom: 25px;
    }
    
    .main-box { max-width: 500px; margin: auto; padding: 15px; background: white; border-radius: 12px; border: 1px solid #8B0000; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
    
    .meroon-header { 
        background-color: #8B0000; color: white !important; text-align: center; 
        padding: 10px; border-radius: 5px; font-size: 1em; font-weight: bold; 
        margin-top: 20px; margin-bottom: 10px;
    }
    
    .panchang-table { width: 100%; border-collapse: collapse; background: white; border: 1px solid #8B0000; font-size: 0.85em; margin-bottom: 20px;}
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 10px; text-align: center; }
    .panchang-table td { padding: 8px; border: 1px solid #eee; font-weight: 500; }
    .asubha-row { background-color: #FFF5F5; }

    /* Rasi Chart Styles */
    .chart-container { display: flex; justify-content: center; align-items: center; padding: 20px; }
    .rasi-chart { width: 620px; border-collapse: collapse; border: 5px solid #8B0000; background: white; table-layout: fixed; box-shadow: 0 20px 50px rgba(0,0,0,0.2); }
    .rasi-chart td { border: 2px solid #D4AF37; height: 145px; vertical-align: top; padding: 12px; position: relative; }
    .planet-text { color: #1a1a1a; font-weight: 800; font-size: 0.9em; line-height: 1.3; }
    .vakra-text { color: #D32F2F; font-size: 0.8em; }
    .rasi-label { color: #8B0000; font-size: 0.7em; font-weight: bold; position: absolute; bottom: 5px; right: 8px; background: #fdf5e6; padding: 2px 5px; border-radius: 4px; }
    
    .center-info-box { text-align: center; background: #FFFBF2; border: 2.5px double #D4AF37; border-radius: 12px; padding: 12px; }
    .tamil-main { color: #8B0000; font-size: 1.1em; font-weight: bold; }
    .tamil-sub { color: #B22222; font-size: 1em; font-weight: bold; border-bottom: 1px solid #D4AF37; padding-bottom: 5px; margin-bottom: 5px;}

    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# ---------- 3. Login Logic ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<div class='header-style'>🔱 AstroGuide உள்நுழைவு</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-box'>", unsafe_allow_html=True)
    if st.button("உள்ளே செல்க"):
        st.session_state.logged_in = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------- 4. User Inputs ----------
st.markdown("<div class='header-style'>🔱 ஸ்ரீ திருக்கணித பஞ்சாங்கம் & ராசி கட்டம்</div>", unsafe_allow_html=True)

districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}

col_a, col_b = st.columns(2)
with col_a:
    s_dist = st.selectbox("ஊர் தேர்வு செய்க:", list(districts.keys()))
with col_b:
    s_date = st.date_input("தேதி தேர்வு செய்க:", datetime.now(IST))
    s_time = st.time_input("நேரம் (Live):", datetime.now(IST).time())

lat, lon = districts[s_dist]

# ---------- 5. Core Astro Calculations ----------
def get_astro_engine(date_obj, time_obj, lat, lon):
    # Setup Time and Location
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    tz = pytz.timezone(tz_name)
    dt = datetime.combine(date_obj, time_obj)
    
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=tz)
    mid_day = s["sunrise"] + (s["sunset"] - s["sunrise"]) / 2
    
    # Swiss Ephemeris Calculations
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(dt.year, dt.month, dt.day, (dt.hour + dt.minute/60.0 - 5.5))

    def get_raw_data(jd):
        m, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
        s_p, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)
        t = ((m[0]-s_p[0])%360)/12
        n = m[0]/(360/27)
        y = (m[0]+s_p[0])/(360/27)
        k = ((m[0]-s_p[0])%360)/6
        return m[0], s_p[0], int(t), int(n), int(y % 27), int(k)

    def find_end_time(jd_base, cur_idx, p_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid_v = (low + high) / 2
            res_val = get_raw_data(jd_base + mid_v)
            lookup = {"t":2, "n":3, "y":4, "k":5}[p_type]
            if res_val[lookup] == cur_idx: low = mid_v
            else: high = mid_v
        dt_end = datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)
        return f"{'இன்று' if dt_end.date() == date_obj else 'நாளை'} {dt_end.strftime('%I:%M %p')}"

    m_deg, s_deg, t_n, n_n, y_n, k_n = get_raw_data(jd_ut)
    
    # Tamil Metadata
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    months = ['சித்திரை', 'வைகாசி', 'ஆனி', 'ஆடி', 'ஆவணி', 'புரட்டாசி', 'ஐப்பசி', 'கார்த்திகை', 'மார்கழி', 'தை', 'மாசி', 'பங்குனி']
    years = ["பிரபவ", "விபவ", "சுக்ல", "பிரமோதூத", "பிரஜோத்பத்தி", "ஆங்கீரச", "ஸ்ரீமுக", "பவ", "யுவ", "தாது", "ஈஸ்வர", "வெகுதானிய", "பிரமாதி", "விக்ரம", "விஷு", "சித்ரபானு", "சுபானு", "தாரண", "பார்த்திப", "விய", "சர்வஜித்", "சர்வதாரி", "விரோதி", "விக்ருதி", "கர", "நந்தன", "விஜய", "ஜய", "மன்மத", "துன்முகி", "ஹேவிளம்பி", "விளம்பி", "விகாரி", "சார்வரி", "பிலவ", "சுபகிருது", "சோபகிருது", "குரோதி", "விசுவாசு", "பரபாவ", "பிளவங்க", "கீலக", "சௌமிய", "சாதாரண", "விரோதகிருது", "பரிதாபி", "பிரமாதீச", "ஆனந்த", "ராட்சச", "நள", "பிங்கள", "காளயுக்தி", "சித்தார்த்தி", "ரௌத்திரி", "துன்மதி", "துந்துபி", "ருத்ரோத்காரி", "ரக்தாட்சி", "குரோதன", "அட்சய"]

    # Year Calculation (Simplified)
    y_idx = (37 + (date_obj.year - 2024)) % 60

    # Planets for Rasi Chart
    p_map = {0: "சூரியன்", 1: "சந்திரன்", 2: "செவ்வாய்", 3: "புதன்", 4: "குரு", 5: "சுக்கிரன்", 6: "சனி", 10: "ராகு"}
    res_pos = {}
    for pid, name in p_map.items():
        pos, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        deg = pos[0]
        vakra = " <span class='vakra-text'>(வ)</span>" if pos[3] < 0 else ""
        idx = int(deg / 30)
        p_str = f"<div class='planet-text'>{name}{vakra} {int(deg%30)}°</div>"
        if idx not in res_pos: res_pos[idx] = []
        res_pos[idx].append(p_str)
        if pid == 10: # Kethu
            k_idx = (idx + 6) % 12
            if k_idx not in res_pos: res_pos[k_idx] = []
            res_pos[k_idx].append(f"<div class='planet-text'>கேது {int(deg%30)}°</div>")

    return {
        "tamil_month": months[int(s_deg/30)%12],
        "tamil_day": int(s_deg%30)+1,
        "tamil_year": years[y_idx],
        "wara": ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][date_obj.weekday()],
        "rise": s["sunrise"].strftime("%I:%M %p"), "set": s["sunset"].strftime("%I:%M %p"),
        "tithi": tithis[t_n % 30], "t_e": find_end_time(jd_ut, t_n, "t"),
        "nak": naks[n_n % 27], "n_idx": n_n % 27, "n_e": find_end_time(jd_ut, n_n, "n"),
        "rahu": ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][date_obj.weekday()],
        "yema": ["10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30", "13:30-15:00", "12:00-13:30"][date_obj.weekday()],
        "kuli": ["13:30-15:00", "12:00-13:30", "10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30"][date_obj.weekday()],
        "chart_data": res_pos,
        "f_date": dt.strftime("%d-%m-%Y"),
        "f_time": dt.strftime("%I:%M %p")
    }

# Run Engine
res = get_astro_engine(s_date, s_time, lat, lon)

# ---------- 6. Layout Display ----------

# Panchangam Table
st.markdown("<div class='meroon-header'>📅 இன்றைய பஞ்சாங்கம்</div>", unsafe_allow_html=True)
st.markdown(f"""
<table class="panchang-table">
    <tr><th colspan="2">{s_dist} - {res['wara']}</th></tr>
    <tr><td>📅 தமிழ் தேதி</td><td><b>{res['tamil_year']} வருடம், {res['tamil_month']} {res['tamil_day']}</b></td></tr>
    <tr><td>🌅 உதயம் / அஸ்தமனம்</td><td>{res['rise']} / {res['set']}</td></tr>
    <tr><td>🌙 திதி</td><td><b>{res['tithi']}</b> ({res['t_e']} வரை)</td></tr>
    <tr><td>⭐ நட்சத்திரம்</td><td><b>{res['nak']}</b> ({res['n_e']} வரை)</td></tr>
</table>
""", unsafe_allow_html=True)

# Auspicious Times
st.markdown("<div class='meroon-header'>⏳ சுப & அசுப நேரங்கள்</div>", unsafe_allow_html=True)
st.markdown(f"""
<table class="panchang-table">
    <tr class="asubha-row"><td>🌑 ராகு காலம்</td><td><b>{res['rahu']}</b></td></tr>
    <tr class="asubha-row"><td>🔥 எமகண்டம்</td><td><b>{res['yema']}</b></td></tr>
    <tr class="asubha-row"><td>🌀 குளிகை</td><td><b>{res['kuli']}</b></td></tr>
</table>
""", unsafe_allow_html=True)

# Rasi Chart
st.markdown("<div class='meroon-header'>🎡 திருக்கணித ராசி கட்டம்</div>", unsafe_allow_html=True)
def draw_box(i):
    planets = "".join(res['chart_data'].get(i, []))
    rasi_names = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]
    return f"{planets}<span class='rasi-label'>{rasi_names[i]}</span>"

st.markdown(f"""
<div class="chart-container">
    <table class="rasi-chart">
        <tr><td>{draw_box(11)}</td><td>{draw_box(0)}</td><td>{draw_box(1)}</td><td>{draw_box(2)}</td></tr>
        <tr>
            <td>{draw_box(10)}</td>
            <td colspan="2" rowspan="2" style="vertical-align:middle;">
                <div class="center-info-box">
                    <div class="tamil-main">{res['tamil_year']} வருடம்</div>
                    <div class="tamil-sub">{res['tamil_month']} {res['tamil_day']}</div>
                    <div class="eng-dt">{res['f_date']}</div>
                    <div class="eng-tm">{res['f_time']}</div>
                </div>
            </td>
            <td>{draw_box(3)}</td>
        </tr>
        <tr><td>{draw_box(9)}</td><td>{draw_box(4)}</td></tr>
        <tr><td>{draw_box(8)}</td><td>{draw_box(7)}</td><td>{draw_box(6)}</td><td>{draw_box(5)}</td></tr>
    </table>
</div>
""", unsafe_allow_html=True)

# Chandrashtama
st.markdown("<div class='meroon-header'>🌙 சந்திராஷ்டமம்</div>", unsafe_allow_html=True)
naks_list = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
c_idx = res['n_idx']
st.markdown(f"""
<div class="main-box" style="border-left: 5px solid red;">
    ⚠️ <b>சந்திராஷ்டமம்:</b> <b style="color:red;">{naks_list[(c_idx-16)%27]}</b> ({res['n_e']} வரை)<br>
    🕒 அடுத்து: <b>{naks_list[(c_idx-15)%27]}</b>
</div>
""", unsafe_allow_html=True)
