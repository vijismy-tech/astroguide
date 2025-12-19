import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. ஆப் அமைப்புகள் & CSS வடிவமைப்பு ----------
st.set_page_config(page_title="AstroGuide Tamil Pro Full", layout="wide")
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
        padding: 10px; border-radius: 5px; font-size: 1.1em; font-weight: bold; 
        margin-top: 15px; margin-bottom: 10px;
    }
    
    .panchang-table { width: 100%; border-collapse: collapse; background: white; border: 1.5px solid #8B0000; font-size: 0.9em; }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 10px; text-align: center; }
    .panchang-table td { padding: 10px 12px; border: 1px solid #eee; font-weight: 500; }
    .asubha-row { background-color: #FFF5F5; }
    .subha-row { background-color: #F5FFF5; }
    .next-info { color: #8B0000; font-size: 0.85em; font-style: italic; display: block; margin-top: 2px; }

    .rasi-chart { width: 620px; border-collapse: collapse; border: 5px solid #8B0000; background: white; table-layout: fixed; margin: auto; box-shadow: 0 20px 50px rgba(0,0,0,0.2); }
    .rasi-chart td { border: 2px solid #D4AF37; height: 145px; vertical-align: top; padding: 12px; position: relative; }
    .planet-text { color: #1a1a1a; font-weight: 800; font-size: 1.05em; line-height: 1.4; }
    .vakra-text { color: #D32F2F; font-size: 0.85em; }
    .rasi-label { color: #8B0000; font-size: 0.7em; font-weight: bold; position: absolute; bottom: 5px; right: 8px; background: #fdf5e6; padding: 2px 5px; border-radius: 4px; }
    
    .center-info-box { text-align: center; background: #FFFBF2; border: 2.5px double #D4AF37; border-radius: 12px; padding: 12px; }
    .tamil-main { color: #8B0000; font-size: 1.2em; font-weight: bold; }
    .tamil-sub { color: #B22222; font-size: 1.1em; font-weight: bold; border-bottom: 1px solid #D4AF37; padding-bottom: 5px; margin-bottom: 5px;}

    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True)

# ---------- 2. லாகின் ----------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<div class='header-style'>🔱 AstroGuide Pro உள்நுழைவு</div>", unsafe_allow_html=True)
    if st.button("உள்ளே செல்க"): st.session_state.logged_in = True; st.rerun()
    st.stop()

# ---------- 3. தேர்வுகள் ----------
st.markdown("<div class='header-style'>🔱 ஸ்ரீ திருக்கணித பஞ்சாங்கம் & ராசி கட்டம்</div>", unsafe_allow_html=True)
districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}

col_a, col_b = st.columns(2)
with col_a: s_dist = st.selectbox("ஊர் தேர்வு செய்க:", list(districts.keys()))
with col_b:
    current_now = datetime.now(IST)
    s_date = st.date_input("தேதி தேர்வு செய்க:", current_now.date())
    s_time = st.time_input("நேரம் தேர்வு செய்க (Live):", current_now.time())

lat, lon = districts[s_dist]

# ---------- 4. ஜோதிடக் கணக்கீட்டு இயந்திரம் ----------
def get_panchangam_engine(date_obj, time_obj, lat, lon):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    dt_combined = datetime.combine(date_obj, time_obj)
    tf = TimezoneFinder(); tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    tz = pytz.timezone(tz_name)
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s_info = sun(observer=city.observer, date=date_obj, tzinfo=tz)
    sunrise, sunset = s_info["sunrise"], s_info["sunset"]
    mid_day = sunrise + (sunset - sunrise) / 2
    
    jd_sunrise = swe.julday(sunrise.year, sunrise.month, sunrise.day, sunrise.hour + sunrise.minute/60.0 - 5.5)
    jd_current = swe.julday(dt_combined.year, dt_combined.month, dt_combined.day, (dt_combined.hour + dt_combined.minute/60.0 - 5.5))

    def get_raw(jd):
        m, _ = swe.calc_ut(jd, 1, swe.FLG_SIDEREAL)
        s, _ = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)
        thithi = ((m[0]-s[0])%360)/12
        nak = m[0]/(360/27)
        yoga = ((m[0]+s[0])%360)/(360/27)
        karanam = ((m[0]-s[0])%360)/6
        return int(thithi), int(nak), int(yoga), int(karanam), m[0], s[0]

    t_idx, n_idx, y_idx, k_idx, m_deg, s_deg = get_raw(jd_sunrise)

    def find_end_time(jd_base, cur_idx, p_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid_v = (low + high) / 2
            res_v = get_raw(jd_base + mid_v)
            lookup = {"t":0, "n":1}[p_type]
            if res_v[lookup] == cur_idx: low = mid_v
            else: high = mid_v
        dt_end = datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)
        return f"{'இன்று' if dt_end.date() == date_obj else 'நாளை'} {dt_end.strftime('%I:%M %p')}"

    # தரவுகள்
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    yogas = ["விஷ்கம்பம்", "ப்ரீதி", "ஆயுஷ்மான்", "சௌபாக்கியம்", "சோபனம்", "அதிகண்டம்", "சுகர்மம்", "திருதி", "சூலம்", "கண்டம்", "விருத்தி", "துருவம்", "வியாகாதம்", "ஹர்ஷணம்", "வஜ்ரம்", "சித்தி", "வியதீபாதம்", "வரியான்", "பரிகம்", "சிவம்", "சித்தம்", "சாத்தியம்", "சுபம்", "சுப்பிரம்", "பிராமியம்", "ஐந்திரம்", "வைதிருதி"]
    karans = ["பவம்", "பாலவம்", "கௌலவம்", "சைதுலை", "கரசை", "வணிசை", "பத்திரை", "சகுனி", "சதுஷ்பாதம்", "நாகவம்", "கிம்ஸ்துக்கினம்"]
    months = ["சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி", "ஐப்பசி", "கார்த்திகை", "மார்கழி", "தை", "மாசி", "பங்குனி"]
    
    # பட்சம் விவரம்
    paksham = "வளர்பிறை (சுக்ல பட்சம்)" if t_idx < 15 else "தேய்பிறை (கிருஷ்ண பட்சம்)"
    
    # தானியங்கி வருடம்
    y_name = "விசுவாசு" if (date_obj.year > 2025 or (date_obj.year == 2025 and date_obj.month >= 4 and date_obj.day >= 14)) else "குரோதி"

    # சுப மற்றும் கௌரி நல்ல நேரங்கள்
    weekday = date_obj.weekday()
    subha_hours = {0: "06:00-07:30 AM", 1: "07:30-09:00 AM", 2: "09:00-10:30 AM", 3: "10:30-12:00 PM", 4: "12:00-01:30 PM", 5: "07:30-09:00 AM", 6: "06:00-07:30 AM"}
    gowri_hours = {
        0: "10:30-11:30 AM, 01:30-02:30 PM", 1: "10:30-11:30 AM, 04:30-05:30 PM",
        2: "09:30-10:30 AM, 01:30-02:30 PM", 3: "12:30-01:30 PM, 04:30-05:30 PM",
        4: "09:30-10:30 AM, 01:30-02:30 PM", 5: "10:30-11:30 AM, 04:30-05:30 PM",
        6: "10:30-11:30 AM, 01:30-02:30 PM"
    }

    # ராசி கட்டம் கணக்கீடு
    p_map = {0: "சூரியன்", 1: "சந்திரன்", 2: "செவ்வாய்", 3: "புதன்", 4: "குரு", 5: "சுக்கிரன்", 6: "சனி", 10: "ராகு"}
    res_pos = {}
    for pid, name in p_map.items():
        pos, _ = swe.calc_ut(jd_current, pid, swe.FLG_SIDEREAL)
        idx = int(pos[0]/30); v = " <span class='vakra-text'>(வ)</span>" if pos[3] < 0 else ""
        if idx not in res_pos: res_pos[idx] = []
        res_pos[idx].append(f"<div class='planet-text'>{name}{v} {int(pos[0]%30)}°</div>")
        if pid == 10:
            ki = (idx + 6) % 12
            if ki not in res_pos: res_pos[ki] = []
            res_pos[ki].append(f"<div class='planet-text'>கேது {int(pos[0]%30)}°</div>")

    return {
        "y": y_name, "m": months[int(s_deg/30)%12], "d": int(s_deg%30)+1,
        "paksham": paksham, "wara": ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][weekday],
        "rise": sunrise.strftime("%I:%M %p"), "set": sunset.strftime("%I:%M %p"),
        "tithi": tithis[t_idx % 30], "t_e": find_end_time(jd_sunrise, t_idx, "t"), "t_next": tithis[(t_idx+1)%30],
        "nak": naks[n_idx % 27], "n_idx": n_idx, "n_e": find_end_time(jd_sunrise, n_idx, "n"), "n_next": naks[(n_idx+1)%27],
        "yoga": yogas[y_idx % 27], "karan": karans[k_idx % 11],
        "subha": subha_hours[weekday], "gowri": gowri_hours[weekday],
        "abhijit": f"{(mid_day - timedelta(minutes=24)).strftime('%I:%M %p')} - {(mid_day + timedelta(minutes=24)).strftime('%I:%M %p')}",
        "rahu": ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][weekday],
        "yema": ["10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30", "13:30-15:00", "12:00-13:30"][weekday],
        "kuli": ["13:30-15:00", "12:00-13:30", "10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30"][weekday],
        "chart": res_pos, "f_date": dt_combined.strftime("%d-%m-%Y"), "f_time": dt_combined.strftime("%I:%M %p")
    }

res = get_panchangam_engine(s_date, s_time, lat, lon)

# ---------- 5. காட்சி அமைப்பு ----------

# பஞ்சாங்கம்
st.markdown("<div class='meroon-header'>📅 இன்றைய பஞ்சாங்கம் (உதய கால அடிப்படை)</div>", unsafe_allow_html=True)
st.markdown(f"""
<table class="panchang-table">
    <tr><th colspan="2">{s_dist} - {res['wara']}</th></tr>
    <tr><td>📅 தமிழ் தேதி</td><td><b>{res['y']} வருடம், {res['m']} {res['d']}</b></td></tr>
    <tr><td>🌗 பட்சம்</td><td><b>{res['paksham']}</b></td></tr>
    <tr>
        <td>🌙 உதய திதி</td>
        <td><b>{res['tithi']}</b> ({res['t_e']} வரை)<br>
            <span class='next-info'>அடுத்து: <b>{res['t_next']}</b></span>
        </td>
    </tr>
    <tr>
        <td>⭐ நட்சத்திரம்</td>
        <td><b>{res['nak']}</b> ({res['n_e']} வரை)<br>
            <span class='next-info'>அடுத்து: <b>{res['n_next']}</b></span>
        </td>
    </tr>
    <tr><td>🌀 யோகம் / கரணம்</td><td><b>{res['yoga']} / {res['karan']}</b></td></tr>
    <tr><td>☀️ உதயம் / அஸ்தமனம்</td><td>{res['rise']} / {res['set']}</td></tr>
</table>
""", unsafe_allow_html=True)

# சுப/அசுப நேரங்கள்
st.markdown("<div class='meroon-header'>⏳ சுப & அசுப நேரங்கள்</div>", unsafe_allow_html=True)
st.markdown(f"""
<table class="panchang-table">
    <tr class="subha-row"><td>✨ நல்ல நேரம்</td><td><b>{res['subha']}</b></td></tr>
    <tr class="subha-row"><td>🌟 கௌரி நல்ல நேரம்</td><td><b>{res['gowri']}</b></td></tr>
    <tr class="subha-row"><td>☀️ அபிஜித் முகூர்த்தம்</td><td><b>{res['abhijit']}</b></td></tr>
    <tr class="asubha-row"><td>🌑 ராகு காலம்</td><td><b>{res['rahu']}</b></td></tr>
    <tr class="asubha-row"><td>🔥 எமகண்டம்</td><td><b>{res['yema']}</b></td></tr>
    <tr class="asubha-row"><td>🌀 குளிகை</td><td><b>{res['kuli']}</b></td></tr>
</table>
""", unsafe_allow_html=True)

# ராசி கட்டம்
st.markdown("<div class='meroon-header'>🎡 ஸ்ரீ திருக்கணித நேரடி ராசி கட்டம்</div>", unsafe_allow_html=True)
def draw_box(i):
    planets = "".join(res['chart'].get(i, []))
    names = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]
    return f"{planets}<span class='rasi-label'>{names[i]}</span>"

st.markdown(f"""
<div class="chart-container">
    <table class="rasi-chart">
        <tr><td>{draw_box(11)}</td><td>{draw_box(0)}</td><td>{draw_box(1)}</td><td>{draw_box(2)}</td></tr>
        <tr><td>{draw_box(10)}</td>
            <td colspan="2" rowspan="2" style="vertical-align:middle;">
                <div class="center-info-box">
                    <div class="tamil-main">{res['y']} வருடம்</div>
                    <div class="tamil-sub">{res['m']} {res['d']}</div>
                    <div style="font-size:0.85em; color:#333; font-weight:bold; margin-top:5px;">{res['f_date']}</div>
                    <div style="font-size:0.85em; color:#B22222; font-weight:bold;">{res['f_time']}</div>
                </div>
            </td>
            <td>{draw_box(3)}</td></tr>
        <tr><td>{draw_box(9)}</td><td>{draw_box(4)}</td></tr>
        <tr><td>{draw_box(8)}</td><td>{draw_box(7)}</td><td>{draw_box(6)}</td><td>{draw_box(5)}</td></tr>
    </table>
</div>
""", unsafe_allow_html=True)

# சந்திராஷ்டமம்
st.markdown("<div class='meroon-header'>🌙 சந்திராஷ்டமம்</div>", unsafe_allow_html=True)
naks_list = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
c_idx = res['n_idx']
st.markdown(f"""
<div class="main-box" style="border-left: 5px solid red; max-width: 620px;">
    ⚠️ <b>இன்று சந்திராஷ்டமம்:</b> <b style="color:red;">{naks_list[(c_idx-16)%27]}</b> நட்சத்திரம் பிறந்தவர்களுக்கு ({res['n_e']} வரை)<br>
    🕒 <b>அடுத்து சந்திராஷ்டமம்:</b> <b>{naks_list[(c_idx-15)%27]}</b> நட்சத்திரம் பிறந்தவர்களுக்கு.
</div>
""", unsafe_allow_html=True)
