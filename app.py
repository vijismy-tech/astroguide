import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. ஆப் அமைப்புகள் (ஒருமுறை மட்டுமே) ----------
st.set_page_config(page_title="AstroGuide Professional Panchangam", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

# ---------- 2. ஒருங்கிணைந்த CSS வடிவமைப்பு ----------
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
    
    .main-box { max-width: 450px; margin: auto; padding: 10px; background: #fdfdfd; border-radius: 8px; border: 1px solid #8B0000; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px; }
    
    .meroon-header { 
        background-color: #8B0000; color: white !important; text-align: center; 
        padding: 10px; border-radius: 5px; font-size: 1em; font-weight: bold; 
        margin-top: 15px; margin-bottom: 10px;
    }
    
    .panchang-table { width: 100%; border-collapse: collapse; background: white; border: 1px solid #8B0000; font-size: 0.85em; }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 6px; text-align: center; }
    .panchang-table td { padding: 5px 8px; border: 1px solid #eee; color: #000 !important; font-weight: 500; }
    .asubha-row { background-color: #FFF5F5; }

    /* ராசி கட்டம் வடிவமைப்புகள் */
    .chart-container { display: flex; justify-content: center; align-items: center; padding: 10px; }
    .rasi-chart { width: 620px; border-collapse: collapse; border: 5px solid #8B0000; background: white; table-layout: fixed; box-shadow: 0 20px 50px rgba(0,0,0,0.2); }
    .rasi-chart td { border: 2px solid #D4AF37; height: 145px; vertical-align: top; padding: 12px; position: relative; }
    .planet-text { color: #1a1a1a; font-weight: 800; font-size: 1.05em; line-height: 1.4; }
    .vakra-text { color: #D32F2F; font-size: 0.85em; }
    .rasi-label { color: #8B0000; font-size: 0.7em; font-weight: bold; position: absolute; bottom: 5px; right: 8px; background: #fdf5e6; padding: 2px 5px; border-radius: 4px; }
    
    .center-info-box { text-align: center; background: #FFFBF2; border: 2.5px double #D4AF37; border-radius: 12px; padding: 12px; }
    .tamil-main { color: #8B0000; font-size: 1.2em; font-weight: bold; margin-bottom: 2px; }
    .tamil-sub { color: #B22222; font-size: 1.1em; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #D4AF37; padding-bottom: 5px; }

    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# ---------- 3. லாகின் ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 class='header-style'>🔱 AstroGuide உள்நுழைவு</h1>", unsafe_allow_html=True)
    if st.button("உள்ளே செல்க"):
        st.session_state.logged_in = True
        st.rerun()
    st.stop()

# ---------- 4. தேர்வுகள் ----------
st.markdown("<div class='header-style'>🔱 ஸ்ரீ திருக்கணித பஞ்சாங்கம் & ராசி கட்டம்</div>", unsafe_allow_html=True)

districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}

col_x, col_y = st.columns(2)
with col_x:
    s_dist = st.selectbox("ஊர்:", list(districts.keys()))
with col_y:
    current_now = datetime.now(IST)
    s_date = st.date_input("தேதி:", current_now.date())
    s_time = st.time_input("நேரம் (Live):", current_now.time())

lat, lon = districts[s_dist]

# ---------- 5. ஜோதிடக் கணக்கீட்டு இயந்திரம் ----------
def get_astro_data(date_obj, time_obj, lat, lon):
    dt = datetime.combine(date_obj, time_obj)
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    tz = pytz.timezone(tz_name)
    
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=tz)
    mid = s["sunrise"] + (s["sunset"] - s["sunrise"]) / 2
    
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(dt.year, dt.month, dt.day, (dt.hour + dt.minute/60.0 - 5.5))

    def get_raw(jd):
        m, _ = swe.calc_ut(jd, 1, swe.FLG_SIDEREAL)
        s_p, _ = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)
        t = ((m[0]-s_p[0])%360)/12
        n = m[0]/(360/27)
        y = (m[0]+s_p[0])/(360/27)
        k = ((m[0]-s_p[0])%360)/6
        return m[0], s_p[0], int(t), int(n), int(y % 27), int(k)

    def find_end_time(jd_base, cur_idx, p_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid_v = (low + high) / 2
            res_val = get_raw(jd_base + mid_v)
            lookup = {"t":2, "n":3, "y":4, "k":5}[p_type]
            if res_val[lookup] == cur_idx: low = mid_v
            else: high = mid_v
        dt_end = datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)
        return f"{'இன்று' if dt_end.date() == date_obj else 'நாளை'} {dt_end.strftime('%I:%M %p')}"

    m_deg, s_deg, t_n, n_n, y_n, k_n = get_raw(jd_ut)
    
    months = ["சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி", "ஐப்பசி", "கார்த்திகை", "மார்கழி", "தை", "மாசி", "பங்குனி"]
    years = ["குரோதி", "விசுவாசு", "பரபாவ", "பிலவங்க", "கீலக", "சௌமிய"] # எளிமைக்காக
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]

    # ராசி கட்ட கிரகங்கள்
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
        if pid == 10:
            k_idx = (idx + 6) % 12
            if k_idx not in res_pos: res_pos[k_idx] = []
            res_pos[k_idx].append(f"<div class='planet-text'>கேது {int(deg%30)}°</div>")

    return {
        "tamil_year": "குரோதி வருடம்",
        "tamil_month_date": f"{months[int(s_deg/30)%12]} {int(s_deg%30)+1}",
        "wara": ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][date_obj.weekday()],
        "rise": s["sunrise"].strftime("%I:%M %p"), "set": s["sunset"].strftime("%I:%M %p"),
        "tithi": tithis[t_n % 30], "t_e": find_end_time(jd_ut, t_n, "t"),
        "nak": naks[n_n % 27], "n_idx": n_n % 27, "n_e": find_end_time(jd_ut, n_n, "n"),
        "abhijit": f"{(mid - timedelta(minutes=24)).strftime('%I:%M %p')} - {(mid + timedelta(minutes=24)).strftime('%I:%M %p')}",
        "rahu": ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][date_obj.weekday()],
        "yema": ["10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30", "13:30-15:00", "12:00-13:30"][date_obj.weekday()],
        "kuli": ["13:30-15:00", "12:00-13:30", "10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30"][date_obj.weekday()],
        "gowri": ["01:30-02:30 PM", "10:30-11:30 AM", "09:30-10:30 AM", "01:30-02:30 PM", "12:30-01:30 PM", "09:30-10:30 AM", "10:30-11:30 AM"][date_obj.weekday()],
        "res_pos": res_pos, "f_date": dt.strftime("%d-%m-%Y"), "f_time": dt.strftime("%I:%M %p")
    }

# கணக்கீட்டை இயக்கு
res = get_astro_data(s_date, s_time, lat, lon)

# ---------- 6. பஞ்சாங்க காட்சி ----------
st.markdown(f"""
<table class="panchang-table">
    <tr><th colspan="2">பஞ்சாங்கம் - {s_dist} ({res['wara']})</th></tr>
    <tr><td>📅 <b>தமிழ் தேதி</b></td><td><b>{res['tamil_year']}, {res['tamil_month_date']}</b></td></tr>
    <tr><td>🌅 <b>உதயம் / அஸ்தமனம்</b></td><td><b>{res['rise']}</b> / {res['set']}</td></tr>
    <tr><td>🌙 <b>திதி</b></td><td><b>{res['tithi']}</b> ({res['t_e']} வரை)</td></tr>
    <tr><td>⭐ <b>நட்சத்திரம்</b></td><td><b>{res['nak']}</b> ({res['n_e']} வரை)</td></tr>
</table>
""", unsafe_allow_html=True)

# ---------- 7. சுப & அசுப நேரங்கள் ----------
st.markdown("<div class='meroon-header'>⏳ இன்றைய சுப & அசுப நேரங்கள்</div>", unsafe_allow_html=True)
st.markdown(f"""
<table class="panchang-table">
    <tr><th colspan="2" style="background-color: #2E7D32;">✨ சுப நேரங்கள்</th></tr>
    <tr><td>🌟 <b>கௌரி நல்ல நேரம்</b></td><td><b>{res['gowri']}</b></td></tr>
    <tr><td>☀️ <b>அபிஜித் முகூர்த்தம்</b></td><td><b>{res['abhijit']}</b></td></tr>
    <tr><th colspan="2" style="background-color: #d32f2f;">🚫 அசுப நேரங்கள்</th></tr>
    <tr class="asubha-row"><td>🌑 <b>ராகு காலம்</b></td><td><b>{res['rahu']}</b></td></tr>
    <tr class="asubha-row"><td>🔥 <b>எமகண்டம்</b></td><td><b>{res['yema']}</b></td></tr>
    <tr class="asubha-row"><td>🌀 <b>குளிகை</b></td><td><b>{res['kuli']}</b></td></tr>
</table>
""", unsafe_allow_html=True)

# ---------- 8. ராசி கட்டம் ----------
st.markdown("<div class='meroon-header'>🎡 ஸ்ரீ திருக்கணித நேரடி ராசி கட்டம்</div>", unsafe_allow_html=True)
def draw_box(i):
    planets = "".join(res['res_pos'].get(i, []))
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
                    <div class="tamil-main">{res['tamil_year']}</div>
                    <div class="tamil-sub">{res['tamil_month_date']}</div>
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

# ---------- 9. சந்திராஷ்டமம் ----------
st.markdown("<div class='meroon-header'>🌙 இன்றைய சந்திராஷ்டமம்</div>", unsafe_allow_html=True)
naks_list = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
c_idx = res['n_idx']
st.markdown(f"""
<table class="panchang-table">
    <tr style="background:#FFF5F5;"><td>⚠️ <b>சந்திராஷ்டமம்</b></td><td><b style="color:red;">{naks_list[(c_idx-16)%27]}</b> ({res['n_e']} வரை)</td></tr>
    <tr><td>🕒 <b>அடுத்து</b></td><td><b>{naks_list[(c_idx-15)%27]}</b></td></tr>
</table>
""", unsafe_allow_html=True)
