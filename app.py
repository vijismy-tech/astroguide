import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz

# ஆப் அமைப்புகள்
st.set_page_config(page_title="Ultra Precise Tamil Panchangam", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

# --- CSS வடிவமைப்பு (மாற்றப்படவில்லை) ---
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

# மாவட்டங்கள்
districts = {
    "அரியலூர்": [11.1401, 79.0786], "சென்னை": [13.0827, 80.2707], "கோயம்புத்தூர்": [11.0168, 76.9558],
    "மதுரை": [9.9252, 78.1198], "திருச்சிராப்பள்ளி": [10.7905, 78.7047], "திருநெல்வேலி": [8.7139, 77.7567],
    "சேலம்": [11.6643, 78.1460], "தஞ்சாவூர்": [10.7870, 79.1378], "வேலூர்": [12.9165, 79.1325]
}

def get_precise_panchang(date_obj, lat, lon):
    # எரர் வராமல் தடுக்க முழு எண்களாக (Integer) மாற்றுதல்
    y, m, d = int(date_obj.year), int(date_obj.month), int(date_obj.day)
    jd_ut = swe.julday(y, m, d, 0.0) 
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_topo(lon, lat, 0)

    # கிரகங்களின் ஐடிகள் (0-சூரியன், 1-சந்திரன்) - கண்டிப்பாக Integer ஆக இருக்க வேண்டும்
    SUN = 0
    MOON = 1
    FLAG = int(swe.FLG_SIDEREAL)

    def get_raw_astronomy(jd):
        m_pos, _ = swe.calc_ut(jd, MOON, FLAG)
        s_pos, _ = swe.calc_ut(jd, SUN, FLAG)
        m_deg, s_deg = m_pos[0], s_pos[0]
        
        diff = (m_deg - s_deg) % 360
        t_idx = int(diff / 12)
        n_idx = int(m_deg / (360/27))
        return m_deg, s_deg, t_idx, n_idx

    # --- உங்கள் 35-Iteration பாகை கணக்கீடு ---
    def find_boundary(jd_base, current_idx, calc_type):
        low, high = 0.0, 1.3 
        for _ in range(35):
            mid = (low + high) / 2
            m, s, t, n = get_raw_astronomy(jd_base + mid)
            val = n if calc_type == "nak" else t
            if val == current_idx: low = mid
            else: high = mid
        return datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)

    m_start, s_start, t_now, n_now = get_raw_astronomy(jd_ut)
    t_end_dt = find_boundary(jd_ut, t_now, "tithi")

    # --- சூரிய உதயம் / அஸ்தமனம் (எரர் வராத முறை) ---
    rise_res = swe.rise_trans(jd_ut, SUN, lon, lat, 0, int(swe.CALC_RISE))
    set_res = swe.rise_trans(jd_ut, SUN, lon, lat, 0, int(swe.CALC_SET))
    
    sunrise = (datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=float(rise_res[1])-jd_ut)).strftime("%I:%M %p")
    sunset = (datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=float(set_res[1])-jd_ut)).strftime("%I:%M %p")

    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    wara = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][int(date_obj.weekday())]
    
    return {
        "wara": wara, "sunrise": sunrise, "sunset": sunset,
        "tithi": tithis[t_now % 30], "tithi_end": t_end_dt.strftime("%I:%M %p"),
        "m_deg": round(m_start, 2)
    }

# --- UI ---
st.markdown("<h1 class='header-style'>🔱 துல்லிய சூரிய உதயம் கொண்ட பஞ்சாங்கம்</h1>", unsafe_allow_html=True)

with st.sidebar:
    selected_dist = st.selectbox("மாவட்டத்தைத் தேர்ந்தெடுக்கவும்:", list(districts.keys()))
    selected_date = st.date_input("தேதியைத் தேர்ந்தெடுக்கவும்:", datetime.now(IST))

try:
    lat, lon = districts[selected_dist]
    p = get_precise_panchang(selected_date, lat, lon)

    st.markdown(f"""
    <table class="panchang-table">
        <tr><th>அங்கம்</th><th>விவரம் ({selected_dist})</th></tr>
        <tr><td>🌅 <b>சூரிய உதயம் / அஸ்தமனம்</b></td><td>உதயம்: <b>{p['sunrise']}</b> | அஸ்தமனம்: <b>{p['sunset']}</b></td></tr>
        <tr><td>🌙 <b>திதி சஞ்சாரம்</b></td><td><b>{p['tithi']}</b> (முடிவு: {p['tithi_end']})</td></tr>
        <tr><td>📊 <b>நிலவின் பாகை</b></td><td>{p['m_deg']}° (திருக்கணிதம்)</td></tr>
    </table>
    """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"கணக்கீட்டில் பிழை: {e}")
