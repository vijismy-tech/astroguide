import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. நவீன மற்றும் கச்சிதமான CSS வடிவமைப்பு ----------
st.set_page_config(page_title="AstroGuide திருக்கணிதப் பஞ்சாங்கம்", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    /* பொதுவான பின்னணி */
    .stApp { background-color: #FFF8F0; font-family: 'Segoe UI', Arial, sans-serif; }
    
    /* கச்சிதமான மெரூன் தலைப்பு */
    .header-style { 
        color: #FFFFFF !important; 
        background-color: #8B0000;
        text-align: center; 
        padding: 10px; 
        border-radius: 8px;
        font-size: 1.3em; 
        font-weight: bold;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* கார்டுகள் அமைப்பு */
    .compact-box { 
        background: #FFFFFF; 
        border-radius: 10px; 
        border-top: 4px solid #8B0000;
        padding: 12px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }

    .meroon-header { 
        color: #8B0000 !important; 
        font-size: 1em; 
        font-weight: bold; 
        border-bottom: 1px solid #eee;
        margin-bottom: 10px;
        padding-bottom: 5px;
        display: flex;
        align-items: center;
    }

    /* கச்சிதமான அட்டவணை */
    .panchang-table { width: 100%; border-collapse: collapse; font-size: 0.85em; }
    .panchang-table td { padding: 6px 4px; border-bottom: 1px solid #f9f9f9; color: #333 !important; }
    .label-cell { color: #8B0000 !important; font-weight: bold; width: 40%; }
    .value-cell { font-weight: 500; }

    /* ராசி கட்டம் - கச்சிதமானது */
    .rasi-grid { 
        display: grid; 
        grid-template-columns: repeat(4, 1fr); 
        gap: 2px; 
        background: #8B0000; 
        border: 2px solid #8B0000;
        max-width: 320px;
        margin: auto;
    }
    .rasi-cell { 
        background: #FFFFFF; 
        height: 70px; 
        padding: 3px; 
        font-size: 0.7em; 
        position: relative;
    }
    .rasi-name { color: #8B0000; font-weight: bold; font-size: 0.8em; display: block; border-bottom: 1px solid #f0f0f0; }
    .planet-text { color: #000; font-weight: bold; display: block; line-height: 1.1; }

    /* விசேஷங்கள் சிறிய அட்டவணை */
    .vrat-item { 
        display: flex; 
        align-items: center; 
        background: #FFF5F5; 
        padding: 8px; 
        border-radius: 6px; 
        margin-bottom: 5px;
        border: 1px solid #FFE0E0;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. லாகின் ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<div class='header-style'>🔱 AstroGuide உள்நுழைவு</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    if st.button("பஞ்சாங்கத்தைக் காண கிளிக் செய்க"): st.session_state.logged_in = True; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------- 3. தலைப்பு & தேர்வுகள் ----------------
st.markdown("<div class='header-style'>🔱 AstroGuide திருக்கணிதப் பஞ்சாங்கம்</div>", unsafe_allow_html=True)

col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}
    s_dist = st.selectbox("ஊர்:", list(districts.keys()))
with col_sel2:
    s_date = st.date_input("தேதி:", datetime.now(IST))

lat, lon = districts[s_dist]

# ---------------- 4. கணக்கீடுகள் (உங்கள் ஒரிஜினல் லாஜிக்) ----------------
def get_all_astro_data(date_obj, lat, lon):
    tf = TimezoneFinder(); tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=pytz.timezone(tz_name))
    mid = s["sunrise"] + (s["sunset"] - s["sunrise"]) / 2
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 5.5)

    def get_raw(jd):
        m, _ = swe.calc_ut(jd, 1, swe.FLG_SIDEREAL); s_p, _ = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)
        t = ((m[0]-s_p[0])%360)/12; n = m[0]/(360/27); y = (m[0]+s_p[0])/(360/27); k = ((m[0]-s_p[0])%360)/6
        return m[0], s_p[0], int(t), int(n), int(y % 27), int(k)

    def find_end_time(jd_base, cur_idx, p_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid_v = (low + high) / 2
            res_val = get_raw(jd_base + mid_v)
            lookup = {"t":2, "n":3, "y":4, "k":5}[p_type]
            if res_val[lookup] == cur_idx: low = mid_v
            else: high = mid_v
        dt = datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)
        return dt.strftime('%I:%M %p')

    m_deg, s_deg, t_n, n_n, y_n, k_n = get_raw(jd_ut)
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    months = ['சித்திரை', 'வைகாசி', 'ஆனி', 'ஆடி', 'ஆவணி', 'புரட்டாசி', 'ஐப்பசி', 'கார்த்திகை', 'மார்கழி', 'தை', 'மாசி', 'பங்குனி']
    planet_ids = {0: "சூரி", 1: "சந்", 2: "செவ்", 3: "புத", 4: "குரு", 5: "சுக்", 6: "சனி", 10: "ராகு"}
    transit = {}
    for pid, name in planet_ids.items():
        pos, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        idx = int(pos[0] / 30)
        if idx not in transit: transit[idx] = []
        transit[idx].append(name)
        if pid == 10: 
            k_idx = int(((pos[0] + 180) % 360) / 30)
            if k_idx not in transit: transit[k_idx] = []
            transit[k_idx].append("கேது")

    return {
        "tamil_date": f"{months[int(s_deg/30)%12]} {int(s_deg%30)+1}",
        "wara": ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][date_obj.weekday()],
        "rise": s["sunrise"].strftime("%I:%M %p"), "set": s["sunset"].strftime("%I:%M %p"),
        "tithi": tithis[t_n % 30], "t_e": find_end_time(jd_ut, t_n, "t"),
        "nak": naks[n_n % 27], "n_e": find_end_time(jd_ut, n_n, "n"),
        "rahu": ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][date_obj.weekday()],
        "yema": ["10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30", "13:30-15:00", "12:00-13:30"][date_obj.weekday()],
        "gowri": ["01:30-02:30 PM", "10:30-11:30 AM", "09:30-10:30 AM", "01:30-02:30 PM", "12:30-01:30 PM", "09:30-10:30 AM", "10:30-11:30 AM"][date_obj.weekday()],
        "moon_deg": round(m_deg % 30, 2), "transit": transit, "n_idx": n_n % 27, "month_name": months[int(s_deg/30)%12]
    }

res = get_all_astro_data(s_date, lat, lon)

# ---------------- 5. காட்சி அமைப்பு (Columns) ----------------


col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<div class='compact-box'>", unsafe_allow_html=True)
    st.markdown("<div class='meroon-header'>📅 இன்றைய நாள்</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <table class='panchang-table'>
        <tr><td class='label-cell'>தமிழ் தேதி</td><td class='value-cell'>{res['tamil_date']} ({res['wara']})</td></tr>
        <tr><td class='label-cell'>திதி</td><td class='value-cell'>{res['tithi']} ({res['t_e']})</td></tr>
        <tr><td class='label-cell'>நட்சத்திரம்</td><td class='value-cell'>{res['nak']} ({res['n_e']})</td></tr>
        <tr><td class='label-cell'>உதயம்/அஸ்தமனம்</td><td class='value-cell'>{res['rise']} / {res['set']}</td></tr>
        <tr><td class='label-cell'>சந்திர பாகை</td><td class='value-cell'>{res['moon_deg']}°</td></tr>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='compact-box'>", unsafe_allow_html=True)
    st.markdown("<div class='meroon-header'>⏳ நேரங்கள்</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <table class='panchang-table'>
        <tr style='background:#E8F5E9;'><td class='label-cell'>கௌரி நல்ல நேரம்</td><td class='value-cell'>{res['gowri']}</td></tr>
        <tr><td class='label-cell'>ராகு காலம்</td><td class='value-cell'>{res['rahu']}</td></tr>
        <tr><td class='label-cell'>எமகண்டம்</td><td class='value-cell'>{res['yema']}</td></tr>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='compact-box'>", unsafe_allow_html=True)
    st.markdown("<div class='meroon-header'>🎡 கோச்சார ராசி கட்டம்</div>", unsafe_allow_html=True)
    def gp(i): return "".join([f"<span class='planet-text'>{x}</span>" for x in res['transit'].get(i, [])])
    st.markdown(f"""
    <div class='rasi-grid'>
        <div class='rasi-cell'><span class='rasi-name'>மீனம்</span>{gp(11)}</div>
        <div class='rasi-cell'><span class='rasi-name'>மேஷம்</span>{gp(0)}</div>
        <div class='rasi-cell'><span class='rasi-name'>ரிஷபம்</span>{gp(1)}</td>
        <div class='rasi-cell'><span class='rasi-name'>மிதுனம்</span>{gp(2)}</div>
        <div class='rasi-cell'><span class='rasi-label'>கும்பம்</span>{gp(10)}</div>
        <div class='rasi-cell' style='grid-column: span 2; grid-row: span 2; background:#f9f9f9; display:flex; align-items:center; justify-content:center; color:#8B0000; font-weight:bold;'>ராசி</div>
        <div class='rasi-cell'><span class='rasi-name'>கடகம்</span>{gp(3)}</div>
        <div class='rasi-cell'><span class='rasi-label'>மகரம்</span>{gp(9)}</div>
        <div class='rasi-cell'><span class='rasi-label'>சிம்மம்</span>{gp(4)}</div>
        <div class='rasi-cell'><span class='rasi-name'>தனுசு</span>{gp(8)}</div>
        <div class='rasi-cell'><span class='rasi-name'>விருச்சி</span>{gp(7)}</div>
        <div class='rasi-cell'><span class='rasi-name'>துலாம்</span>{gp(6)}</div>
        <div class='rasi-cell'><span class='rasi-name'>கன்னி</span>{gp(5)}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # சந்திராஷ்டமம்
    naks_list = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    st.markdown("<div class='compact-box' style='border-left: 4px solid red;'>", unsafe_allow_html=True)
    st.markdown("<div class='meroon-header' style='color:red !important;'>🌙 சந்திராஷ்டமம்</div>", unsafe_allow_html=True)
    st.write(f"⚠️ **{naks_list[(res['n_idx']-16)%27]}** நட்சத்திரத்திற்கு இன்று சந்திராஷ்டமம்.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- 6. விசேஷங்கள் ----------------
st.markdown("<div class='compact-box'>", unsafe_allow_html=True)
st.markdown("<div class='meroon-header'>🪷 இன்றைய விசேஷங்கள்</div>", unsafe_allow_html=True)
vrat_db = {
    ("அமாவாசை", None, "மார்கழி"): ["🐒", "ஸ்ரீ ஹனுமன் ஜெயந்தி", "அஞ்சனை மைந்தன் அருள் கிட்டும்."],
    ("அமாவாசை", None, None): ["🌑", "அமாவாசை தர்ப்பணம்", "முன்னோர்களின் ஆசி கிட்டும்."],
    ("பௌர்ணமி", None, None): ["🌕", "பௌர்ணமி விரதம்", "செல்வச் செழிப்பு கிட்டும்."],
    ("சதுர்த்தி", None, None): ["🐘", "சங்கடஹர சதுர்த்தி", "காரியத் தடைகள் நீங்கும்."],
    ("திரயோதசி", None, None): ["🐂", "பிரதோஷம்", "சிவனருள் கிட்டும்."]
}
found = False
for (t, n, m), d in vrat_db.items():
    if t == res['tithi'] and (m is None or m == res['month_name']):
        found = True
        st.markdown(f"""
        <div class='vrat-item'>
            <span style='font-size:1.5em; margin-right:10px;'>{d[0]}</span>
            <div><b>{d[1]}</b><br><small>{d[2]}</small></div>
        </div>
        """, unsafe_allow_html=True)
if not found: st.write("இன்று விசேஷங்கள் ஏதுமில்லை.")
st.markdown("</div>", unsafe_allow_html=True)
