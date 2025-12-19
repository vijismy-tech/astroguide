import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. App Settings & CSS ----------
st.set_page_config(page_title="AstroGuide Tamil", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, span, div, label, td, th { color: #1a1a1a !important; font-family: 'Arial', sans-serif; }
    .header-style { color: #8B0000 !important; text-align: center; font-weight: bold; margin-top: -30px; margin-bottom: 5px; font-size: 1.1em; }
    .main-box { max-width: 450px; margin: auto; padding: 10px; background: #fdfdfd; border-radius: 8px; border: 1px solid #8B0000; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px; }
    .meroon-header { background-color: #8B0000; color: white !important; text-align: center; padding: 8px; border-radius: 5px; font-size: 0.95em; font-weight: bold; margin-top: 15px; margin-bottom: 10px; }
    .panchang-table { width: 100%; border-collapse: collapse; background: white; border: 1px solid #8B0000; font-size: 0.82em; }
    .panchang-table th { background-color: #8B0000; color: white !important; padding: 6px; text-align: center; }
    .panchang-table td { padding: 6px 10px; border: 1px solid #eee; color: #000 !important; font-weight: 500; }
    .vrat-table { width:100%; border-collapse: collapse; border:1px solid #8B0000; background-color:#FFFAF0; }
    .vrat-table td { padding: 10px; border: 1px solid #ddd; vertical-align: middle; }
    .symbol-style { font-size: 1.4em; text-align: center; width: 45px; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. Logic ----------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<h1 class='header-style'>🔱 AstroGuide Login</h1>", unsafe_allow_html=True)
    if st.button("Ulle Selga"): st.session_state.logged_in = True; st.rerun()
    st.stop()

# ---------------- 3. Inputs ----------------
districts = {"Chennai": [13.08, 80.27], "Madurai": [9.93, 78.12], "Trichy": [10.79, 78.70], "Coimbatore": [11.02, 76.96], "Nellai": [8.71, 77.76], "Salem": [11.66, 78.15]}
st.markdown("<h1 class='header-style'>🔱 AstroGuide Panchangam</h1>", unsafe_allow_html=True)
st.markdown('<div class="main-box">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: s_dist = st.selectbox("Oor:", list(districts.keys()))
with c2: s_date = st.date_input("Thethi:", datetime.now(IST))
st.markdown('</div>', unsafe_allow_html=True)
lat, lon = districts[s_dist]

# ---------------- 4. Calculations ----------------
def get_panchang_data(date_obj, lat, lon):
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
        return m[0], s_p[0], int(t), int(n), int(y % 27), int(k % 60)

    def find_end_time(jd_base, cur_idx, p_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid_v = (low + high) / 2
            res_val = get_raw(jd_base + mid_v)
            lookup = {"t":2, "n":3, "y":4, "k":5}[p_type]
            if res_val[lookup] == cur_idx: low = mid_v
            else: high = mid_v
        dt = datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)
        return f"{'Indru' if dt.date() == date_obj else 'Naalai'} {dt.strftime('%I:%M %p')}"

    m_deg, s_deg, t_n, n_n, y_n, k_n = get_raw(jd_ut)
    tithis = ["Prathamai", "Thuvithiyai", "Thrithiyai", "Chathurthi", "Panchami", "Sashti", "Sapthami", "Ashtami", "Navami", "Dasami", "Ekadasi", "Thuvadasi", "Thirayodasi", "Chathurdasi", "Pournami", "Prathamai", "Thuvithiyai", "Thrithiyai", "Chathurthi", "Panchami", "Sashti", "Sapthami", "Ashtami", "Navami", "Dasami", "Ekadasi", "Thuvadasi", "Thirayodasi", "Chathurdasi", "Amavasai"]
    naks = ["Aswini", "Barani", "Karthigai", "Rohini", "Mirugasiridam", "Thiruvathirai", "Punarpusam", "Pusam", "Ayilyam", "Magam", "Puram", "Uthiram", "Astham", "Chithirai", "Swathi", "Visagam", "Anusham", "Kettai", "Moolam", "Pooradam", "Uthiradam", "Thiruvonam", "Avittam", "Sathayam", "Poorattathi", "Uthirattathi", "Revathi"]
    yogas = ["Vishkambam", "Preethi", "Ayushman", "Saubhagyam", "Sobanam", "Athigandam", "Sukarmam", "Thrithi", "Soolam", "Gandam", "Vriddhi", "Druvam", "Vyagatham", "Harshanam", "Vajram", "Siddhi", "Vyathipatham", "Variyan", "Parigam", "Sivam", "Siddham", "Sadhyam", "Subham", "Subhram", "Bramyam", "Aindram", "Vaithruthi"]
    karans = ["Bavam", "Balavam", "Kaulavam", "Saithulai", "Karasai", "Vanisai", "Batthirai", "Saguni", "Chathushpadam", "Nagavam", "Kimsthukkinnam"]
    months = ['Chithirai', 'Vaikasi', 'Aani', 'Aadi', 'Aavani', 'Purattasi', 'Aippasi', 'Karthigai', 'Margazhi', 'Thai', 'Maasi', 'Panguni']

    return {
        "tamil_date": f"{months[int(s_deg/30)%12]} {int(s_deg%30)+1}",
        "wara": ["Thingal", "Sevvai", "Budhan", "Vyalan", "Velli", "Sani", "Gnayiru"][date_obj.weekday()],
        "rise": s["sunrise"].strftime("%I:%M %p"), "set": s["sunset"].strftime("%I:%M %p"),
        "tithi": tithis[t_n % 30], "t_e": find_end_time(jd_ut, t_n, "t"),
        "nak": naks[n_n % 27], "n_e": find_end_time(jd_ut, n_n, "n"), "n_nx": naks[(n_n+1)%27],
        "yoga": yogas[y_n % 27], "karan": karans[k_n % 11],
        "shoolam": ["Kizhaku", "Vadaku", "Vadaku", "Therku", "Merku", "Kizhaku", "Merku"][date_obj.weekday()],
        "month_name": months[int(s_deg/30)%12],
        "rahu": ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][date_obj.weekday()],
        "yema": ["10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30", "13:30-15:00", "12:00-13:30"][date_obj.weekday()],
        "kuli": ["13:30-15:00", "12:00-13:30", "10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30"][date_obj.weekday()],
        "gowri": ["01:30-02:30 PM", "10:30-11:30 AM", "09:30-10:30 AM", "01:30-02:30 PM", "12:30-01:30 PM", "09:30-10:30 AM", "10:30-11:30 AM"][date_obj.weekday()]
    }

res = get_panchang_data(s_date, lat, lon)

# ---------------- 5. Display Table 1 ----------------
st.markdown(f"""
<table class="panchang-table">
    <tr><th colspan="2">Panchangam - {s_dist} ({res['wara']})</th></tr>
    <tr><td>📅 <b>Tamil Date</b></td><td><b>{res['tamil_date']}</b></td></tr>
    <tr><td>🌅 <b>Sunrise / Set</b></td><td><b>{res['rise']}</b> / {res['set']}</td></tr>
    <tr><td>🌙 <b>Tithi</b></td><td><b>{res['tithi']}</b> ({res['t_e']} varai)</td></tr>
    <tr><td>⭐ <b>Nakshatram</b></td><td><b>{res['nak']}</b> ({res['n_e']} varai)<br><small style='color:red'>Aduthu: {res['n_nx']}</small></td></tr>
    <tr><td>🌀 <b>Yogam / Karanam</b></td><td>{res['yoga']} / {res['karan']}</td></tr>
    <tr><td>📍 <b>Soolam / Pariharam</b></td><td>{res['shoolam']} / Paal</td></tr>
</table>
""", unsafe_allow_html=True)

# ---------------- 6. Subha Nerangal ----------------
st.markdown("<div class='meroon-header'>⏳ Subha & Asubha Nerangal</div>", unsafe_allow_html=True)
st.markdown(f"""
<table class="panchang-table">
    <tr style="background:#E8F5E9;"><td>🌟 <b>Nalla Neram</b></td><td><b>{res['gowri']}</b></td></tr>
    <tr style="background:#FFF5F5;"><td>🌑 <b>Rahu Kaalam</b></td><td><b>{res['rahu']}</b></td></tr>
    <tr style="background:#FFF5F5;"><td>🔥 <b>Yemagandam</b></td><td><b>{res['yema']}</b></td></tr>
    <tr style="background:#FFF5F5;"><td>🌀 <b>Kuligai</b></td><td><b>{res['kuli']}</b></td></tr>
</table>
""", unsafe_allow_html=True)

# ---------------- 7. Nithra Calendar Style Vratams ----------------
st.markdown("<div class='meroon-header'>🗓️ Nithra Calendar Visheshangal</div>", unsafe_allow_html=True)

vrat_logic = [
    # (Tithi, Nakshatra, Month, Symbol, Title, Desc)
    ("Amavasai", None, None, "🌑", "Amavasai", "Munorkaluku tharpanam seiya nalla naal."),
    ("Pournami", None, None, "🌕", "Pournami Viratham", "Girivalam matrum amman vazhipatuku sirappu."),
    ("Chathurthi", None, None, "🐘", "Sankadahara Chathurthi", "Vinayagar vazhipadu thadaigalai neekum."),
    ("Sashti", None, None, "🔱", "Sashti Viratham", "Murugan vazhipatuku ughandha naal."),
    ("Thirayodasi", None, None, "🐂", "Pradhosham", "Sivan kovil vazhipadu mananimathi tharum."),
    ("Ekadasi", None, None, "📿", "Ekadasi Viratham", "Perumal vazhipadu matrum upavasam."),
    (None, "Karthigai", None, "🔥", "Karthigai Viratham", "Muruganukana sirappu naal."),
    ("Amavasai", None, "Margazhi", "🐒", "Hanuman Jayanthi", "Hanumanukana sirappu vazhipadu.")
]

found_v = False
vrat_html = '<table class="vrat-table">'
for t, n, m, sym, title, desc in vrat_logic:
    if (t == res['tithi']) or (n == res['nak']) or (t == res['tithi'] and m == res['month_name']):
        found_v = True
        vrat_html += f"""
        <tr>
            <td class="symbol-style">{sym}</td>
            <td><b>{title}</b><br><small style='color:#666;'>{desc}</small></td>
        </tr>
        """
vrat_html += "</table>"

if found_v:
    st.markdown(vrat_html, unsafe_allow_html=True)
else:
    st.info("Indru kurippitta visheshangal yethum illai.")

# ---------------- 8. Chandrashtamam ----------------
st.markdown("<div class='meroon-header'>🌙 Chandrashtamam</div>", unsafe_allow_html=True)
naks_list = ["Aswini", "Barani", "Karthigai", "Rohini", "Mirugasiridam", "Thiruvathirai", "Punarpusam", "Pusam", "Ayilyam", "Magam", "Puram", "Uthiram", "Astham", "Chithirai", "Swathi", "Visagam", "Anusham", "Kettai", "Moolam", "Pooradam", "Uthiradam", "Thiruvonam", "Avittam", "Sathayam", "Poorattathi", "Uthirattathi", "Revathi"]
try:
    c_idx = naks_list.index(res['nak'])
    st.markdown(f"""
    <table class="panchang-table">
        <tr style="background:#FFF5F5;"><td>⚠️ <b>Chandrashtamam</b></td><td><b style="color:red;">{naks_list[(c_idx-16)%27]}</b> ({res['n_e']} varai)</td></tr>
    </table>
    """, unsafe_allow_html=True)
except: pass
