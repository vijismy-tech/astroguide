import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. ஆப் அமைப்புகள் & CSS வடிவமைப்பு ----------
st.set_page_config(page_title="AstroGuide Tamil", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
# ---------- 1. ஆப் அமைப்புகள் & CSS வடிவமைப்பு ----------
st.set_page_config(page_title="AstroGuide Tamil", layout="wide")

st.markdown("""
    <style>
    /* ஏற்கனவே இருக்கும் உங்கள் கோடிங் இங்கே இருக்கும்... */
    .stApp { background-color: #FFFFFF; }
    
    /* இதோ இங்கே தான் அந்தப் புதிய வரிகளைச் சேர்க்க வேண்டும்: */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    </style>
    """, unsafe_allow_html=True)
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, span, div, label, td, th { color: #1a1a1a !important; font-family: 'Arial', sans-serif; }
    .header-style { color: #8B0000 !important; text-align: center; font-weight: bold; margin-top: -30px; margin-bottom: 5px; font-size: 1.1em; }
    .main-box { max-width: 450px; margin: auto; padding: 10px; background: #fdfdfd; border-radius: 8px; border: 1px solid #8B0000; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px; }
    
    .meroon-header { 
        background-color: #8B0000; 
        color: white !important; 
        text-align: center; 
        padding: 10px; 
        border-radius: 5px; 
        font-size: 1em; 
        font-weight: bold; 
        margin-top: 15px; 
        margin-bottom: 10px;
    }
    
    .panchang-table { width: 100%; border-collapse: collapse; background: white; border: 1px solid #8B0000; font-size: 0.78em; }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 6px; text-align: center; }
    .panchang-table td { padding: 5px 8px; border: 1px solid #eee; color: #000 !important; font-weight: 500; }
    .next-info { color: #8B0000 !important; font-size: 0.85em; font-style: italic; display: block; margin-top: 2px; }

    .rasi-chart { width: 100%; border-collapse: collapse; border: 2px solid #8B0000; table-layout: fixed; }
    .rasi-chart td { border: 1px solid #8B0000; height: 95px; vertical-align: top; padding: 4px; font-size: 0.65em; background: #fff; }
    .rasi-label { color: #8B0000; font-weight: bold; display: block; border-bottom: 1px solid #eee; margin-bottom: 2px; }
    .planet-text { color: #000; font-weight: 600; display: block; line-height: 1.2; }
    
    .vrat-table { width:100%; border:1px solid #8B0000; border-radius:10px; background-color:#FFFAF0; margin-bottom:10px; border-collapse: separate; }
    .asubha-row { background-color: #FFF5F5; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. லாகின் ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<h1 class='header-style'>🔱 AstroGuide உள்நுழைவு</h1>", unsafe_allow_html=True)
    if st.button("உள்ளே செல்க"): st.session_state.logged_in = True; st.rerun()
    st.stop()

# ---------------- 3. தேர்வுகள் ----------------
districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}
st.markdown("<h2 class='header-style'>🔱 AstroGuide திருக்கணித பஞ்சாங்கம்</h2>", unsafe_allow_html=True)
st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: s_dist = st.selectbox("ஊர்:", list(districts.keys()))
with c2: s_date = st.date_input("தேதி:", datetime.now(IST))
st.markdown('</div>', unsafe_allow_html=True)
lat, lon = districts[s_dist]

# ---------------- 4. ஜோதிடக் கணக்கீடுகள் ----------------
def get_all_astro_data(date_obj, lat, lon):
    tf = TimezoneFinder(); tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=pytz.timezone(tz_name))
    mid = s["sunrise"] + (s["sunset"] - s["sunrise"]) / 2
    
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 5.5)

    def get_raw(jd):
        m, _ = swe.calc_ut(jd, 1, swe.FLG_SIDEREAL); s_p, _ = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)
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
        dt = datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)
        return f"{'இன்று' if dt.date() == date_obj else 'நாளை'} {dt.strftime('%I:%M %p')}"

    m_deg, s_deg, t_n, n_n, y_n, k_n = get_raw(jd_ut)
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    yogas = ["விஷ்கம்பம்", "ப்ரீதி", "ஆயுஷ்மான்", "சௌபாக்கியம்", "சோபனம்", "அதிகண்டம்", "சுகர்மம்", "திருதி", "சூலம்", "கண்டம்", "விருத்தி", "துருவம்", "வியாகாதம்", "ஹர்ஷணம்", "வஜ்ரம்", "சித்தி", "வியதீபாதம்", "வரியான்", "பரிகம்", "சிவம்", "சித்தம்", "சாத்தியம்", "சுபம்", "சுப்பிரம்", "பிராமியம்", "ஐந்திரம்", "வைதிருதி"]
    karans = ["பவம்", "பாலவம்", "கௌலவம்", "சைதுலை", "கரசை", "வணிசை", "பத்திரை", "சகுனி", "சதுஷ்பாதம்", "நாகவம்", "கிம்ஸ்துக்கினம்"]
    months = ['சித்திரை', 'வைகாசி', 'ஆனி', 'ஆடி', 'ஆவணி', 'புரட்டாசி', 'ஐப்பசி', 'கார்த்திகை', 'மார்கழி', 'தை', 'மாசி', 'பங்குனி']
    
    # கோச்சார கிரகங்கள்
    planet_ids = {0: "சூரியன்", 1: "சந்திரன்", 2: "செவ்வாய்", 3: "புதன்", 4: "குரு", 5: "சுக்கிரன்", 6: "சனி", 10: "ராகு"}
    transit = {}
    for pid, name in planet_ids.items():
        pos, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        deg = pos[0]; idx = int(deg / 30)
        p_val = f"{name} {round(deg % 30, 2)}°"
        if idx not in transit: transit[idx] = []
        transit[idx].append(p_val)
        if pid == 10: # கேது
            k_deg = (deg + 180) % 360; k_idx = int(k_deg / 30)
            if k_idx not in transit: transit[k_idx] = []
            transit[k_idx].append(f"கேது {round(k_deg % 30, 2)}°")

    return {
        "tamil_date": f"{months[int(s_deg/30)%12]} {int(s_deg%30)+1}",
        "wara": ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][date_obj.weekday()],
        "rise": s["sunrise"].strftime("%I:%M %p"), "set": s["sunset"].strftime("%I:%M %p"),
        "tithi": tithis[t_n % 30], "t_e": find_end_time(jd_ut, t_n, "t"), "t_nx": tithis[(t_n+1)%30],
        "nak": naks[n_n % 27], "n_e": find_end_time(jd_ut, n_n, "n"), "n_nx": naks[(n_n+1)%27],
        "yoga": yogas[y_n % 27], "karan": karans[k_n % 11],
        "abhijit": f"{(mid - timedelta(minutes=24)).strftime('%I:%M %p')} - {(mid + timedelta(minutes=24)).strftime('%I:%M %p')}",
        "rahu": ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][date_obj.weekday()],
        "yema": ["10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30", "13:30-15:00", "12:00-13:30"][date_obj.weekday()],
        "kuli": ["13:30-15:00", "12:00-13:30", "10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30"][date_obj.weekday()],
        "gowri": ["01:30-02:30 PM", "10:30-11:30 AM", "09:30-10:30 AM", "01:30-02:30 PM", "12:30-01:30 PM", "09:30-10:30 AM", "10:30-11:30 AM"][date_obj.weekday()],
        "shoolam": ["கிழக்கு", "வடக்கு", "வடக்கு", "தெற்கு", "மேற்கு", "கிழக்கு", "மேற்கு"][date_obj.weekday()],
        "moon_deg": round(m_deg % 30, 2), "transit": transit, "month_name": months[int(s_deg/30)%12]
    }

res = get_all_astro_data(s_date, lat, lon)

# ---------------- 5. பஞ்சாங்க அட்டவணை ----------------
st.markdown(f"""
<table class="panchang-table">
    <tr><th colspan="2">பஞ்சாங்கம் - {s_dist} ({res['wara']})</th></tr>
    <tr><td>📅 <b>தமிழ் தேதி</b></td><td><b>{res['tamil_date']}</b></td></tr>
    <tr><td>🌅 <b>சூரிய உதயம் / அஸ்தமனம்</b></td><td><b>{res['rise']}</b> / {res['set']}</td></tr>
    <tr><td>🌙 <b>திதி</b></td><td><b>{res['tithi']}</b> வரை ({res['t_e']})</td></tr>
    <tr>
        <td>⭐ <b>நட்சத்திரம்</b></td>
        <td>
            <b>{res['nak']}</b> ({res['n_e']} வரை)<br>
            <span class='next-info'>அடுத்து: <b>{res['n_nx']}</b></span>
        </td>
    </tr>
    <tr><td>🌀 <b>யோகம் / கரணம்</b></td><td>{res['yoga']} / {res['karan']}</td></tr>
    <tr><td>📍 <b>சூலம்</b></td><td>{res['shoolam']}</td></tr>
    <tr style="background:#f0f7ff;"><td>📊 <b>சந்திர பாகை</b></td><td><b>{res['moon_deg']}°</b></td></tr>
</table>
""", unsafe_allow_html=True)

# ---------------- 6. சுப & அசுப நேரங்கள் ----------------
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

# ---------------- 7. கோச்சார ராசி கட்டம் ----------------

st.markdown("<div class='meroon-header'>🎡 இன்றைய கோச்சார ராசி கட்டம்</div>", unsafe_allow_html=True)
def get_p(i): return "".join([f"<span class='planet-text'>{x}</span>" for x in res['transit'].get(i, [])])

st.markdown(f"""
<table class="rasi-chart">
    <tr><td><span class='rasi-label'>மீனம்</span>{get_p(11)}</td><td><span class='rasi-label'>மேஷம்</span>{get_p(0)}</td><td><span class='rasi-label'>ரிஷபம்</span>{get_p(1)}</td><td><span class='rasi-label'>மிதுனம்</span>{get_p(2)}</td></tr>
    <tr><td><span class='rasi-label'>கும்பம்</span>{get_p(10)}</td><td colspan="2" rowspan="2" style="background:#fdfdfd; text-align:center; vertical-align:middle; color:#8B0000; font-weight:bold;">AstroGuide<br>கோச்சாரம்</td><td><span class='rasi-label'>கடகம்</span>{get_p(3)}</td></tr>
    <tr><td><span class='rasi-label'>மகரம்</span>{get_p(9)}</td><td><span class='rasi-label'>சிம்மம்</span>{get_p(4)}</td></tr>
    <tr><td><span class='rasi-label'>தனுசு</span>{get_p(8)}</td><td><span class='rasi-label'>விருச்சிகம்</span>{get_p(7)}</td><td><span class='rasi-label'>துலாம்</span>{get_p(6)}</td><td><span class='rasi-label'>கன்னி</span>{get_p(5)}</td></tr>
</table>
""", unsafe_allow_html=True)

# ---------------- 8. சந்திராஷ்டமம் ----------------
st.markdown("<div class='meroon-header'>🌙 இன்றைய சந்திராஷ்டமம்</div>", unsafe_allow_html=True)
naks_list = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
try:
    c_idx = naks_list.index(res['nak'])
    st.markdown(f"""
    <table class="panchang-table">
        <tr style="background:#FFF5F5;"><td>⚠️ <b>சந்திராஷ்டமம்</b></td><td><b style="color:red;">{naks_list[(c_idx-16)%27]}</b> ({res['n_e']} வரை)</td></tr>
        <tr><td>🕒 <b>அடுத்து</b></td><td><b>{naks_list[(c_idx-15)%27]}</b> ({res['n_e']} முதல்)</td></tr>
    </table>
    """, unsafe_allow_html=True)
except: pass
# ---------------- 9. விசேஷங்கள் (நேரடி அட்டவணை முறை) ----------------
st.markdown("<div class='meroon-header'>🪷 இன்றைய விரதங்கள் & விசேஷங்கள்</div>", unsafe_allow_html=True)

# விசேஷ தரவுத்தளம்
vrat_db = {
    ("அமாவாசை", None, "மார்கழி"): ["🐒", "ஸ்ரீ ஹனுமன் ஜெயந்தி", "அஞ்சனை மைந்தனின் பூரண அருள் கிட்டும்."],
    ("அமாவாசை", None, None): ["🌑", "அமாவாசை தர்ப்பணம்", "முன்னோர்களின் ஆசி கிட்டும்."],
    ("பௌர்ணமி", None, None): ["🌕", "பௌர்ணமி விரதம்", "செல்வச் செழிப்பு மற்றும் மன அமைதி தரும்."],
    ("சதுர்த்தி", None, None): ["🐘", "சங்கடஹர சதுர்த்தி", "காரியத் தடைகள் நீங்கும்."],
    ("சஷ்டி", None, None): ["🔱", "சஷ்டி விரதம்", "முருகன் அருள் கிட்டும்."],
    ("திரயோதசி", None, None): ["🐂", "பிரதோஷம்", "சிவனருள் கிட்டும், கஷ்டங்கள் நீங்கும்."],
    ("ஏகாதசி", None, None): ["📿", "ஏகாதசி விரதம்", "மகாவிஷ்ணுவின் அருள் கிட்டும்."],
    (None, "கார்த்திகை", None): ["🔥", "கிருத்திகை விரதம்", "முருகப்பெருமானின் விசேஷ வழிபாடு."]
}

found_v = False
# விசேஷங்கள் இருக்கிறதா என்று முதலில் சரிபார்க்கிறோம்
for (t, n, m), d in vrat_db.items():
    if (t == res['tithi']) and (n is None or n == res['nak']) and (m is None or m == res['month_name']):
        found_v = True
        # ஒவ்வொரு விசேஷத்தையும் தனித்தனி அட்டவணை வரிசையாக வெளியிடுகிறோம்
        st.markdown(f"""
        <div class="main-box" style="padding: 0; margin-bottom: 5px;">
            <table style="width:100%; border-collapse: collapse; background-color:#FFFAF0;">
                <tr>
                    <td style="font-size: 1.5em; width: 50px; text-align: center; padding: 10px;">{d[0]}</td>
                    <td style="padding: 10px;">
                        <b style="color: #8B0000; font-size: 0.9em;">{d[1]}</b><br>
                        <small style="color: #555; font-size: 0.8em;">{d[2]}</small>
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

if not found_v:
    st.info("இன்று குறிப்பிட்ட விசேஷங்கள் ஏதுமில்லை.")
