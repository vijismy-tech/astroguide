import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz

# ஆப் அமைப்புகள்
st.set_page_config(page_title="Corrected Tamil Panchangam", layout="wide")
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
    .special-note { background-color: #FFF9C4; padding: 15px; border-radius: 10px; border-left: 5px solid #FBC02D; margin-bottom: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

districts = {
    "அரியலூர்": [11.1401, 79.0786], "சென்னை": [13.0827, 80.2707], "கோயம்புத்தூர்": [11.0168, 76.9558],
    "மதுரை": [9.9252, 78.1198], "திருச்சிராப்பள்ளி": [10.7905, 78.7047], "திருநெல்வேலி": [8.7139, 77.7567],
    "சேலம்": [11.6643, 78.1460], "தஞ்சாவூர்": [10.7870, 79.1378], "வேலூர்": [12.9165, 79.1325]
}

def get_accurate_data(date_obj, lat_val, lon_val):
    # அட்சரேகை மற்றும் தீர்க்கரேகையை float ஆக மாற்றுதல்
    lat, lon = float(lat_val), float(lon_val)
    
    # ஆண்டு, மாதம், தேதி ஆகியவற்றை Integer ஆக மாற்றுதல் (Error fix)
    year, month, day = int(date_obj.year), int(date_obj.month), int(date_obj.day)
    
    # 0.0 UT = 5:30 AM IST
    jd_ut = swe.julday(year, month, day, 0.0)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_topo(lon, lat, 0)

    def get_astronomy_values(jd):
        m, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
        s, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)
        
        # லக்கின கணக்கீடு - Sidereal Ascendant
        res, ascmc = swe.houses(jd, lat, lon, b'P')
        ayan = swe.get_ayanamsa_ut(jd)
        ascendant = (res[0] - ayan) % 360  
        
        diff = (m[0] - s[0]) % 360
        t_idx = int(diff / 12)
        n_idx = int(m[0] / (360/27))
        return m[0], s[0], t_idx, n_idx, ascendant

    # --- பழைய பாகை கணக்கீடு (35 Iterations) ---
    def find_boundary(jd_base, current_idx, calc_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid = (low + high) / 2
            m, s, t, n, _ = get_astronomy_values(jd_base + mid)
            val = n if calc_type == "nak" else t
            if val == current_idx: low = mid
            else: high = mid
        return datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)

    m_deg, s_deg, t_now, n_now, lakkina_deg = get_astronomy_values(jd_ut)
    t_end_time = find_boundary(jd_ut, t_now, "tithi")

    # சூரிய உதயம்/அஸ்தமனம்
    rise_res = swe.rise_trans(jd_ut, swe.SUN, lon, lat, 0, swe.CALC_RISE)
    set_res = swe.rise_trans(jd_ut, swe.SUN, lon, lat, 0, swe.CALC_SET)
    sunrise = (datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=rise_res[1]-jd_ut)).strftime("%I:%M %p")
    sunset = (datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=set_res[1]-jd_ut)).strftime("%I:%M %p")

    # தமிழ் தேதி
    tamil_months = ["சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி", "ஐப்பசி", "கார்த்திகை", "மார்கழி", "தை", "மாசி", "பங்குனி"]
    month_idx = int(s_deg / 30)
    tamil_date = int(s_deg % 30) + 1

    # லக்கினம்
    raasi_names = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]
    current_lakkina = raasi_names[int(lakkina_deg / 30)]
    lakkina_balance = round(30 - (lakkina_deg % 30), 2)

    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    wara = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][date_obj.weekday()]

    return {
        "tamil_full": f"{tamil_months[month_idx]} {tamil_date}",
        "sunrise": sunrise, "sunset": sunset,
        "wara": wara, "tithi": tithis[t_now % 30], "t_end": t_end_time.strftime("%I:%M %p"),
        "lakkina": current_lakkina, "lakkina_rem": lakkina_balance, "m_deg": round(m_deg, 2)
    }

# --- UI ---
st.markdown("<h1 class='header-style'>🔱 தமிழ்நாடு திருக்கணிதப் பஞ்சாங்கம்</h1>", unsafe_allow_html=True)

with st.sidebar:
    selected_dist = st.selectbox("மாவட்டத்தைத் தேர்ந்தெடுக்கவும்:", list(districts.keys()))
    selected_date = st.date_input("தேதியைத் தேர்ந்தெடுக்கவும்:", datetime.now(IST))

try:
    lat, lon = districts[selected_dist]
    p = get_accurate_data(selected_date, lat, lon)

    st.markdown(f"<div class='special-note'>📅 தமிழ் தேதி: {p['tamil_full']} | கிழமை: {p['wara']}</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <table class="panchang-table">
        <tr><th>அங்கம்</th><th>விவரம் ({selected_dist})</th></tr>
        <tr><td>🌅 <b>சூரிய உதயம் / அஸ்தமனம்</b></td><td>உதயம்: {p['sunrise']} | அஸ்தமனம்: {p['sunset']}</td></tr>
        <tr><td>🌙 <b>திதி சஞ்சாரம்</b></td><td><b>{p['tithi']}</b> (முடிவு: {p['t_end']})</td></tr>
        <tr><td>☸️ <b>லக்கின விபரம்</b></td><td>உதய லக்கினம்: <b>{p['lakkina']}</b><br><span style='color: #666; font-size: 0.85em;'>லக்கின இருப்பு: {p['lakkina_rem']}°</span></td></tr>
        <tr><td>📊 <b>நிலவின் பாகை</b></td><td>{p['m_deg']}° (திருக்கணித நிலை)</td></tr>
    </table>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"கணக்கீட்டில் பிழை ஏற்பட்டுள்ளது. (விவரம்: {e})")
