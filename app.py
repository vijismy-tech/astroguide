import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz

# ஆப் அமைப்புகள்
st.set_page_config(page_title="Ultra Precise Tamil Panchangam", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

# --- CSS வடிவமைப்பு (Design மாறவில்லை) ---
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
    </style>
    """, unsafe_allow_html=True)

districts = {
    "அரியலூர்": [11.1401, 79.0786], "சென்னை": [13.0827, 80.2707], "கோயம்புத்தூர்": [11.0168, 76.9558],
    "மதுரை": [9.9252, 78.1198], "திருச்சிராப்பள்ளி": [10.7905, 78.7047], "திருநெல்வேலி": [8.7139, 77.7567],
    "சேலம்": [11.6643, 78.1460], "தஞ்சாவூர்": [10.7870, 79.1378], "வேலூர்": [12.9165, 79.1325]
}

def get_precise_panchang(date_obj, lat_val, lon_val):
    lat, lon = float(lat_val), float(lon_val)
    y, m, d = int(date_obj.year), int(date_obj.month), int(date_obj.day)
    
    # 0.0 UT = 5:30 AM IST
    jd_ut = swe.julday(y, m, d, 0.0)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_topo(lon, lat, 0.0)

    def get_raw_astronomy(jd):
        m_res, _ = swe.calc_ut(jd, 1, int(swe.FLG_SIDEREAL))
        s_res, _ = swe.calc_ut(jd, 0, int(swe.FLG_SIDEREAL))
        m_deg, s_deg = m_res[0], s_res[0]
        diff = (m_deg - s_deg) % 360
        return m_deg, s_deg, int(diff / 12), int(m_deg / (360/27)), int(((m_deg + s_deg) % 360) / (360/27)), int(diff / 6) % 11

    # --- உங்கள் 35-Iteration பாகை கணக்கீடு ---
    def find_boundary(jd_base, current_idx, calc_type):
        low, high = 0.0, 1.3 
        for _ in range(35):
            mid = (low + high) / 2
            m, s, t, n, y, k = get_raw_astronomy(jd_base + mid)
            val = n if calc_type == "nak" else t
            if val == current_idx: low = mid
            else: high = mid
        return datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)

    # சூரிய உதயம் கணக்கிடும் திருத்தப்பட்ட முறை (Robust Method)
    # இது சூரியன் அடிவானத்திற்கு மேலே வரும் துல்லியமான நேரத்தைக் கண்டறியும்
    res = swe.rise_trans(jd_ut, 0, lon, lat, 0, int(swe.CALC_RISE | swe.BIT_DISC_CENTER))
    sunrise_jd = res[1]
    
    # அஸ்தமனம்
    res_set = swe.rise_trans(jd_ut, 0, lon, lat, 0, int(swe.CALC_SET | swe.BIT_DISC_CENTER))
    sunset_jd = res_set[1]

    # JD-யை IST நேரமாக மாற்றுதல்
    sunrise_dt = datetime(2000, 1, 1) + timedelta(days=sunrise_jd - 2451544.5 + 0.229167) # UT to IST adjustment
    # துல்லியமான மாற்று முறை
    sunrise_ist = (datetime.combine(date_obj, datetime.min.time()) + timedelta(days=sunrise_jd - jd_ut) + timedelta(hours=5, minutes=30)).strftime("%I:%M %p")
    sunset_ist = (datetime.combine(date_obj, datetime.min.time()) + timedelta(days=sunset_jd - jd_ut) + timedelta(hours=5, minutes=30)).strftime("%I:%M %p")

    m_start, s_start, t_now, n_now, y_now, k_now = get_raw_astronomy(jd_ut)
    t_end_dt = find_boundary(jd_ut, t_now, "tithi")

    tamil_months = ["சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி", "ஐப்பசி", "கார்த்திகை", "மார்கழி", "தை", "மாசி", "பங்குனி"]
    t_month = tamil_months[int(s_start / 30) % 12]
    t_date = int(s_start % 30) + 1

    return {
        "m_deg": round(m_start, 2), "sunrise": sunrise_ist, "sunset": sunset_ist,
        "tamil": f"{t_month} {t_date}", "wara": ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][date_obj.weekday()],
        "tithi": ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"][t_now % 30],
        "t_end": t_end_dt.strftime("%I:%M %p")
    }

# --- UI ---
st.markdown("<h1 class='header-style'>🔱 திருக்கணிதப் பஞ்சாங்கம் - சூரிய உதயம்</h1>", unsafe_allow_html=True)

with st.sidebar:
    selected_dist = st.selectbox("மாவட்டத்தைத் தேர்ந்தெடுக்கவும்:", list(districts.keys()))
    selected_date = st.date_input("தேதியைத் தேர்ந்தெடுக்கவும்:", datetime.now(IST))

try:
    lat, lon = districts[selected_dist]
    p = get_precise_panchang(selected_date, lat, lon)

    st.markdown(f"""
    <table class="panchang-table">
        <tr><th>அங்கம்</th><th>விவரம் ({selected_dist})</th></tr>
        <tr><td>🌅 <b>சூரிய உதயம்</b></td><td><b>{p['sunrise']}</b></td></tr>
        <tr><td>🌇 <b>சூரிய அஸ்தமனம்</b></td><td><b>{p['sunset']}</b></td></tr>
        <tr><td>📅 <b>தமிழ் தேதி</b></td><td>{p['tamil']}</td></tr>
        <tr><td>🌙 <b>திதி</b></td><td><b>{p['tithi']}</b> (முடிவு: {p['t_end']})</td></tr>
        <tr><td>📊 <b>நிலவின் பாகை</b></td><td>{p['m_deg']}°</td></tr>
    </table>
    """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"கணக்கீட்டில் பிழை: {e}")
