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
    .special-note { background-color: #FFF9C4; padding: 15px; border-radius: 10px; border-left: 5px solid #FBC02D; margin-bottom: 20px; color: #5D4037; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# மாவட்டங்கள் தரவு
districts = {
    "அரியலூர்": [11.1401, 79.0786], "சென்னை": [13.0827, 80.2707], "கோயம்புத்தூர்": [11.0168, 76.9558],
    "கடலூர்": [11.7480, 79.7714], "தர்மபுரி": [12.1271, 78.1582], "திண்டுக்கல்": [10.3673, 77.9803],
    "ஈரோடு": [11.3410, 77.7172], "காஞ்சிபுரம்": [12.8342, 79.7036], "மதுரை": [9.9252, 78.1198],
    "நாகப்பட்டினம்": [10.7672, 79.8444], "நாமக்கல்": [11.2189, 78.1674], "புதுக்கோட்டை": [10.3797, 78.8202],
    "இராமநாதபுரம்": [9.3639, 78.8395], "சேலம்": [11.6643, 78.1460], "தஞ்சாவூர்": [10.7870, 79.1378],
    "திருச்சிராப்பள்ளி": [10.7905, 78.7047], "திருநெல்வேலி": [8.7139, 77.7567], "வேலூர்": [12.9165, 79.1325]
}

def get_precise_panchang(date_obj, lat_val, lon_val):
    # அட்சரேகை மற்றும் தீர்க்கரேகையை float ஆக மாற்றுதல்
    lat, lon = float(lat_val), float(lon_val)
    
    # ஆண்டின் தரவுகளை Integer ஆக மாற்றுதல் (TypeError fix)
    y, m, d = int(date_obj.year), int(date_obj.month), int(date_obj.day)
    
    jd_ut = swe.julday(y, m, d, 0.0) 
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_topo(lon, lat, 0.0)

    # கிரகக் குறியீடுகள் (Constants) கண்டிப்பாக Integer ஆக இருக்க வேண்டும்
    SUN = 0
    MOON = 1
    FLAG_SID = int(swe.FLG_SIDEREAL)
    RISE = int(swe.CALC_RISE)
    SET = int(swe.CALC_SET)

    def get_raw_astronomy(jd):
        # நிலவு மற்றும் சூரியன் பாகைகள்
        m_res, _ = swe.calc_ut(jd, MOON, FLAG_SID)
        s_res, _ = swe.calc_ut(jd, SUN, FLAG_SID)
        m_deg, s_deg = m_res[0], s_res[0]
        
        diff = (m_deg - s_deg) % 360
        t_idx = int(diff / 12)
        n_idx = int(m_deg / (360/27))
        y_idx = int(((m_deg + s_deg) % 360) / (360/27))
        k_idx = int(diff / 6) % 11
        return m_deg, s_deg, t_idx, n_idx, y_idx, k_idx

    # --- உங்கள் 35-Iteration துல்லியமான பாகை கணக்கீடு ---
    def find_boundary(jd_base, current_idx, calc_type):
        low, high = 0.0, 1.3 
        for _ in range(35):
            mid = (low + high) / 2
            _, _, t, n, _, _ = get_raw_astronomy(jd_base + mid)
            val = n if calc_type == "nak" else t
            if val == current_idx: low = mid
            else: high = mid
        return datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)

    m_start, s_start, t_now, n_now, y_now, k_now = get_raw_astronomy(jd_ut)
    t_end_dt = find_boundary(jd_ut, t_now, "tithi")
    n_end_dt = find_boundary(jd_ut, n_now, "nak")

    # --- சூரிய உதயம் / அஸ்தமனம் (TypeError தவிர்க்கப்பட்டது) ---
    rise_res = swe.rise_trans(jd_ut, SUN, lon, lat, 0, RISE)
    set_res = swe.rise_trans(jd_ut, SUN, lon, lat, 0, SET)
    sunrise = (datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=float(rise_res[1])-jd_ut)).strftime("%I:%M %p")
    sunset = (datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.
