import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz

# ஆப் அமைப்புகள்
st.set_page_config(page_title="Tamil Nadu Precise Drik Panchangam", layout="wide")
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

# தமிழ்நாட்டின் மாவட்டங்கள் மற்றும் அவற்றின் ஆயத்தொலைவுகள் (Coordinates)
districts = {
    "அரியலூர்": [11.1401, 79.0786], "செங்கல்பட்டு": [12.6841, 79.9836], "சென்னை": [13.0827, 80.2707],
    "கோயம்புத்தூர்": [11.0168, 76.9558], "கடலூர்": [11.7480, 79.7714], "தர்மபுரி": [12.1271, 78.1582],
    "திண்டுக்கல்": [10.3673, 77.9803], "ஈரோடு": [11.3410, 77.7172], "கள்ளக்குறிச்சி": [11.7383, 78.9639],
    "காஞ்சிபுரம்": [12.8342, 79.7036], "கன்னியாகுமரி": [8.0883, 77.5385], "கரூர்": [10.9601, 78.0766],
    "கிருஷ்ணகிரி": [12.5266, 78.2148], "மதுரை": [9.9252, 78.1198], "மயிலாடுதுறை": [11.1018, 79.6521],
    "நாகப்பட்டினம்": [10.7672, 79.8444], "நாமக்கல்": [11.2189, 78.1674], "நீலகிரி": [11.4102, 76.6950],
    "பெரம்பலூர்": [11.2342, 78.8820], "புதுக்கோட்டை": [10.3797, 78.8202], "இராமநாதபுரம்": [9.3639, 78.8395],
    "இராணிப்பேட்டை": [12.9271, 79.3327], "சேலம்": [11.6643, 78.1460], "சிவகங்கை": [9.8433, 78.4807],
    "தென்காசி": [8.9595, 77.3115], "தஞ்சாவூர்": [10.7870, 79.1378], "தேனி": [10.0104, 77.4768],
    "தூத்துக்குடி": [8.8042, 78.1348], "திருச்சிராப்பள்ளி": [10.7905, 78.7047], "திருநெல்வேலி": [8.7139, 77.7567],
    "திருப்பத்தூர்": [12.4934, 78.5678], "திருப்பூர்": [11.1085, 77.3411], "திருவள்ளூர்": [13.1209, 79.9145],
    "திருவண்ணாமலை": [12.2253, 79.0747], "திருவாரூர்": [10.7722, 79.6362], "வேலூர்": [12.9165, 79.1325],
    "விழுப்புரம்": [11.9401, 79.4861], "விருதுநகர்": [9.5872, 77.9514]
}

def get_precise_districts_panchang(date_obj, lat, lon):
    # 0.0 UT = 5:30 AM IST
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 0.0) 
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_topo(lon, lat, 0) # மாவட்டத்திற்கு ஏற்ற அட்சரேகை திருத்தம்

    def get_raw_astronomy(jd):
        m, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
        s, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)
        m_deg, s_deg = m[0], s[0]
        diff = (m_deg - s_deg) % 360
        t_idx = int(diff / 12)
        n_idx = int(m_deg / (360/27))
        y_idx = int(((m_deg + s_deg) % 360) / (360/27))
        k_idx = int(diff / 6) % 11
        return m_deg, s_deg, t_idx, n_idx, y_idx, k_idx

    m_start, s_start, t_now, n_now, y_now, k_now = get_raw_astronomy(jd_ut)

    def find_end_time(jd_base, current_idx, calc_type):
        low, high = 0.0, 1.3
        for _ in range(35):
            mid = (low + high) / 2
            _, _, t, n, _, _ = get_raw_astronomy(jd_base + mid)
            val = n if calc_type == "nak" else t
            if val == current_idx: low = mid
            else: high = mid
        return datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)

    t_end = find_end_time(jd_ut, t_now, "tithi")
    n_end = find_end_time(jd_ut, n_now, "nak")

    naks = ["அஸ்வினி",
