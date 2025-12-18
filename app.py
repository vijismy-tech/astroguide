import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz

# ஆப் அமைப்புகள்
st.set_page_config(page_title="Tamil Precise Drik Panchangam", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

# --- CSS வடிவமைப்பு ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    .header-style { color: #8B0000; text-align: center; font-family: 'Tamil'; font-weight: bold; margin-bottom: 20px; }
    .panchang-table {
        width: 100%; border-collapse: collapse; background: white;
        border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .panchang-table th { background-color: #8B0000; color: white; padding: 15px; text-align: left; }
    .panchang-table td { padding: 12px 15px; border: 1px solid #eee; color: #333; font-weight: 600; }
    .sub-text { color: #666; font-size: 0.85em; font-weight: normal; }
    .special-note { background-color: #FFF9C4; padding: 15px; border-radius: 10px; border-left: 5px solid #FBC02D; margin-bottom: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

districts = {
    "அரியலூர்": [11.1401, 79.0786], "சென்னை": [13.0827, 80.2707], "கோயம்புத்தூர்": [11.0168, 76.9558],
    "மதுரை": [9.9252, 78.1198], "திருச்சிராப்பள்ளி": [10.7905, 78.7047], "திருநெல்வேலி": [8.7139, 77.7567],
    "சேலம்": [11.6643, 78.1460], "தஞ்சாவூர்": [10.7870, 79.1378], "வேலூர்": [12.9165, 79.1325]
}

def get_complete_precise_panchang(date_obj, lat, lon):
    # 0.0 UT = 5:30 AM IST
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 0.0)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_topo(lon, lat, 0)

    def get_astronomy(jd):
        m, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
        s, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)
        # லக்கின கணக்கீடு
        res, _ = swe.houses_ex(jd, lat, lon, b'P')
        ascendant = res[0]
        
        diff = (m[0] - s[0]) % 360
        t_idx = int(diff / 12)
        n_idx = int(m[0] / (360/27))
        return m[0], s[0], t_idx, n_idx, ascendant

    # --- பழைய பாகை கணக்கீடு (35 Iterations) ---
    def find_boundary(jd_base, current_idx, calc_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid = (low + high) / 2
            m, s, t, n, _ = get_astronomy(jd_base + mid)
            val = n if calc_type == "nak" else t
            if val == current_idx: low = mid
            else: high = mid
        return datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)

    m_deg, s_deg, t_now, n_now, lakkina_deg = get_astronomy(jd_ut)
    t_end = find_boundary(jd_ut, t_now, "tithi")

    # சூரிய உதயம் & அஸ்தமனம்
    rise_res = swe.rise_trans(jd_ut, swe.SUN, lon, lat, 0, swe.CALC_RISE)
    set_res = swe.rise_trans(jd_ut, swe.SUN, lon, lat, 0, swe.CALC_SET)
    
    sunrise = (datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=rise_res[1]-jd_ut)).strftime("%I:%M %p")
    sunset = (datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=set_res[1]-jd_ut)).strftime("%I:%M %p")

    # தமிழ் மாதம் & தேதி (எளிய கணக்கீடு - சூரிய பாகை அடிப்படையில்)
    tamil_months = ["சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி", "ஐப்பசி", "கார்த்திகை", "மார்கழி", "தை", "மாசி", "பங்குனி"]
    month_idx = int((s_deg / 30))
    tamil_date = int((s_deg % 30)) + 1

    # லக்கினப் பெயர்
    raasi_names = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]
    current_lakkina = raasi_names[int(lakkina_deg / 30)]
    lakkina_balance = round(30 - (lakkina_deg % 30), 2)

    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    wara = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][date_obj.weekday()]

    return {
        "tamil_full": f"{tamil_months[month_idx]} {tamil_date}", "sunrise": sunrise, "sunset": sunset,
        "lakkina": current_lakkina, "lakkina_rem": lakkina_balance, "wara": wara,
        "tithi": tithis[t_now % 30], "t_end": t_end.strftime("%I:%M %p"), "m_deg": round(m_deg, 2)
    }

# --- UI ---
st.markdown("<h1 class='header-style'>🔱 திருக்கணித பஞ்சாங்கம் - லக்கின விபரம்</h1>", unsafe_allow_html=True)

with st.sidebar:
    selected_dist = st.selectbox("மாவட்டத்தைத் தேர்ந்தெடுக்கவும்:", list(districts.keys()))
    selected_date = st.date_input("தேதியைத் தேர்ந்தெடுக்கவும்:", datetime.now(IST))

lat, lon = districts[selected_dist]
p = get_complete_precise_panchang(selected_date, lat, lon)

st.markdown(f"<div class='special-note'>📅 தமிழ் தேதி: {p['tamil_full']} | கிழமை: {p['wara']}</div>", unsafe_allow_html=True)

st.markdown(f"""
<table class="panchang-table">
    <tr><th>அங்கம்</th><th>விவரம் ({selected_dist})</th></tr>
    <tr><td>🌅 <b>சூரிய உதயம் / அஸ்தமனம்</b></td><td>உதயம்: {p['sunrise']} | அஸ்தமனம்: {p['sunset']}</td></tr>
    <tr><td>🌙 <b>திதி</b></td><td><b>{p['tithi']}</b> (முடிவு: {p['t_end']})</td></tr>
    <tr><td>☸️ <b>லக்கின விபரம்</b></td><td>தற்போதைய லக்கினம்: <b>{p['lakkina']}</b><br><span class='sub-text'>லக்கின இருப்பு: {p['lakkina_rem']}°</span></td></tr>
    <tr><td>📊 <b>வானியல் பாகை</b></td><td>சந்திர பாகை: {p['m_deg']}°</td></tr>
</table>
""", unsafe_allow_html=True)
