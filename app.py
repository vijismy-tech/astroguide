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
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, span, div, label, td, th { color: #1a1a1a !important; font-family: 'Arial', sans-serif; }
    .header-style { color: #8B0000 !important; text-align: center; font-weight: bold; margin-top: -30px; margin-bottom: 5px; font-size: 1.1em; }
    .main-box { max-width: 450px; margin: auto; padding: 10px; background: #fdfdfd; border-radius: 8px; border: 1px solid #8B0000; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px; }
    
    /* மெரூன் தலைப்பு மற்றும் வெள்ளை எழுத்துக்கள் */
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .panchang-table { width: 100%; border-collapse: collapse; background: white; border-radius: 5px; border: 1px solid #8B0000; font-size: 0.78em; }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 6px; text-align: center; }
    .panchang-table td { padding: 5px 8px; border: 1px solid #eee; color: #000 !important; font-weight: 500; }
    .next-info { color: #8B0000 !important; font-size: 0.7em; font-style: italic; display: block; margin-top: 1px; }
    .asubha-row { background-color: #FFF5F5; }
    .vrat-table { width:100%; border:1px solid #8B0000; border-radius:10px; background-color:#FFFAF0; margin-bottom:10px; border-collapse: separate; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. லாகின் பகுதி ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<h1 class='header-style'>🔱 AstroGuide உள்நுழைவு</h1>", unsafe_allow_html=True)
    if st.button("உள்ளே செல்க"): st.session_state.logged_in = True; st.rerun()
    st.stop()

# ---------------- 3. மாவட்டங்கள் & தேர்வுகள் ----------------
districts = {"சென்னை": [13.08, 80.27], "மதுரை": [9.93, 78.12], "திருச்சி": [10.79, 78.70], "கோவை": [11.02, 76.96], "நெல்லை": [8.71, 77.76], "சேலம்": [11.66, 78.15]}

st.markdown("<h1 class='header-style'>🔱 AstroGuide திருக்கணிதப் பஞ்சாங்கம்</h1>", unsafe_allow_html=True)
st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: s_dist = st.selectbox("ஊர்:", list(districts.keys()))
with c2: s_date = st.date_input("தேதி:", datetime.now(IST))
st.markdown('</div>', unsafe_allow_html=True)

lat, lon = districts[s_dist]

# ---------------- 4. பஞ்சாங்க லாஜிக் ----------------
def get_full_panchang_tamil(date_obj, lat, lon):
    tf = TimezoneFinder(); tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=pytz.timezone(tz_name))
    mid = s["sunrise"] + (s["sunset"] - s["sunrise"]) / 2
    
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 0.0)

    def get_raw(jd):
        m, _ = swe.calc_ut(jd, 1, swe.FLG_SIDEREAL); s_p, _ = swe.calc_ut(jd, 0, swe.FLG_SIDEREAL)
        t = ((m[0]-s_p[0])%360)/12
        n = m[0]/(360/27)
        return m[0], s_p[0], int(t), int(n)

    def find_end_time(jd_base, cur_idx, p_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid_v = (low + high) / 2
            res_val = get_raw(jd_base + mid_v)
            lookup = {"t":2, "n":3}[p_type]
            if res_val[lookup] == cur_idx: low = mid_v
            else: high = mid_v
        dt = datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)
        day_str = "இன்று" if dt.date() == date_obj else "நாளை"
        return f"{day_str} {dt.strftime('%I:%M %p')}"

    m_deg, s_deg, t_n, n_n = get_raw(jd_ut)
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    
    d_idx = date_obj.weekday()
    wara = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][d_idx]
    months = ['சித்திரை', 'வைகாசி', 'ஆனி', 'ஆடி', 'ஆவணி', 'புரட்டாசி', 'ஐப்பசி', 'கார்த்திகை', 'மார்கழி', 'தை', 'மாசி', 'பங்குனி']

    return {
        "tamil_date": f"{months[int(s_deg/30)%12]} {int(s_deg%30)+1}",
        "wara": wara, "rise": s["sunrise"].strftime("%I:%M %p"), "set": s["sunset"].strftime("%I:%M %p"),
        "tithi": tithis[t_n % 30], "t_e": find_end_time(jd_ut, t_n, "t"),
        "nak": naks[n_n % 27], "n_e": find_end_time(jd_ut, n_n, "n"), "n_nx": naks[(n_n+1)%27],
        "rahu": ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][d_idx],
        "yema": ["10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30", "13:30-15:00", "12:00-13:30"][d_idx],
        "gowri": ["01:30-02:30 PM", "10:30-11:30 AM", "09:30-10:30 AM", "01:30-02:30 PM", "12:30-01:30 PM", "09:30-10:30 AM", "10:30-11:30 AM"][d_idx],
        "month_name": months[int(s_deg/30)%12]
    }

res = get_full_panchang_tamil(s_date, lat, lon)

# --- பஞ்சாங்க அட்டவணை காட்சி ---
st.markdown(f"""
<table class="panchang-table">
    <tr><th colspan="2">AstroGuide - {s_dist} ({res['wara']})</th></tr>
    <tr><td>📅 <b>தமிழ் தேதி</b></td><td>{res['tamil_date']}</td></tr>
    <tr><td>🌅 <b>உதயம் / அஸ்தமனம்</b></td><td>{res['rise']} / {res['set']}</td></tr>
    <tr><td>🌙 <b>திதி</b></td><td><b>{res['tithi']}</b> வரை ({res['t_e']})</td></tr>
    <tr><td>⭐ <b>நட்சத்திரம்</b></td><td><b>{res['nak']}</b> வரை ({res['n_e']})</td></tr>
    <tr><td>🌟 <b>கௌரி நல்ல நேரம்</b></td><td>{res['gowri']}</td></tr>
    <tr class="asubha-row"><td>🚫 <b>ராகு காலம்</b></td><td>{res['rahu']}</td></tr>
    <tr class="asubha-row"><td>🚫 <b>எமகண்டம்</b></td><td>{res['yema']}</td></tr>
</table>
""", unsafe_allow_html=True)

# ---------------- 5. சந்திராஷ்டம அட்டவணை (மெரூன் தலைப்புடன்) ----------------
st.markdown("<div class='meroon-header'>🌙 இன்றைய சந்திராஷ்டமம்</div>", unsafe_allow_html=True)
naks_list = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]

try:
    c_idx = naks_list.index(res['nak'])
    cur_aff = (c_idx - 16) % 27
    nxt_aff = (c_idx - 15) % 27
    st.markdown(f"""
    <table class="panchang-table">
        <tr><td>🚩 <b>தற்போதைய நிலை ({res['nak']})</b></td><td><b style="color:red;">{naks_list[cur_aff]}</b> நட்சத்திரத்திற்கு ({res['n_e']} வரை)</td></tr>
        <tr class="asubha-row"><td>🕒 <b>அடுத்த நிலை ({res['n_nx']})</b></td><td><b>{naks_list[nxt_aff]}</b> நட்சத்திரத்திற்கு ({res['n_e']} முதல்)</td></tr>
    </table>
    """, unsafe_allow_html=True)
except: pass

# ---------------- 6. விரதங்கள் & விசேஷங்கள் (மெரூன் தலைப்பு & டைனமிக் லாஜிக்) ----------------
st.markdown("<div class='meroon-header'>🪷 இன்றைய விரதங்கள் & விசேஷங்கள்</div>", unsafe_allow_html=True)

vrat_db = {
    # (திதி, நட்சத்திரம், மாதம்): [பெயர், பலன், படம்]
    ("அமாவாசை", None, "மார்கழி"): ["ஸ்ரீ ஹனுமன் ஜெயந்தி", "அஞ்சனை மைந்தனின் பூரண அருள் கிட்டும், பயம் நீங்கும்.", "https://img.freepik.com/premium-photo/god-lord-hanuman-statue_1156453-157.jpg"],
    ("அமாவாசை", None, None): ["அமாவாசை தர்ப்பணம்", "முன்னோர்களின் ஆசி கிட்டும், குடும்பத்தில் சுபிட்சம் உண்டாகும்.", "https://img.freepik.com/premium-photo/hindu-ritual-called-tharpanam-ancestor-worship_1029679-65039.jpg"],
    ("பௌர்ணமி", None, None): ["பௌர்ணமி விரதம்", "மன அமைதி மற்றும் செல்வச் செழிப்பு உண்டாகும்.", "https://img.freepik.com/free-photo/view-bright-full-moon-night-sky_23-2151000305.jpg"],
    ("சதுர்த்தி", None, None): ["சங்கடஹர சதுர்த்தி", "காரியத் தடைகள் விலகும், எடுத்த காரியங்கள் சித்திக்கும்.", "https://img.freepik.com/premium-photo/ganesha-god-success_662214-41154.jpg"],
    ("சஷ்டி", None, None): ["சஷ்டி விரதம்", "முருகப் பெருமானின் அருளும் குழந்தை பாக்கியமும் கிட்டும்.", "https://img.freepik.com/premium-photo/lord-murugan-statue-temple_950133-1463.jpg"],
    ("ஏகாதசி", None, None): ["ஏகாதசி விரதம்", "மகாவிஷ்ணுவின் அருள் கிடைக்கும், மோட்சம் கிட்டும்.", "https://img.freepik.com/premium-photo/god-vishnu-shiva-statue_950133-1188.jpg"]
}

found_vrat = False
st.markdown('<div class="main-box">', unsafe_allow_html=True)

for (t, n, m), d in vrat_db.items():
    t_match = (t == res['tithi'])
    n_match = (n is None or n == res['nak'])
    m_match = (m is None or m == res['month_name'])

    if t_match and n_match and m_match:
        found_vrat = True
        st.markdown(f"""
        <table class="vrat-table">
            <tr>
                <td style="width:35%; text-align:center; padding:10px;">
                    <img src="{d[2]}" style="width:110px; height:110px; border-radius:50%; border:3px solid #8B0000; object-fit: cover;">
                </td>
                <td style="padding:10px; vertical-align:middle;">
                    <b style="color:#8B0000; font-size:1.1em;">✨ {d[0]}</b><br>
                    <p style="font-size:0.85em; margin-top:5px; line-height:1.4;"><b>பலன்:</b> {d[1]}</p>
                </td>
            </tr>
        </table>
        """, unsafe_allow_html=True)

if not found_vrat:
    st.info("இன்று குறிப்பிட்ட விசேஷங்கள் அல்லது விரதங்கள் ஏதுமில்லை.")

st.markdown('</div>', unsafe_allow_html=True)
