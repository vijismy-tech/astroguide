import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz

# ஆப் அமைப்புகள்
st.set_page_config(page_title="Corrected Drik Panchangam", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

# --- CSS ஸ்டைலிங் ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    .header-style { color: #8B0000; text-align: center; font-family: 'Tamil'; font-weight: bold; margin-bottom: 20px; }
    .panchang-table {
        width: 100%; border-collapse: collapse; background: white;
        border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .panchang-table th { background-color: #8B0000; color: white; padding: 15px; text-align: left; }
    .panchang-table td { padding: 12px 15px; border: 1px solid #eee; color: #333; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

def get_accurate_panchang(date_obj):
    # சுவிஸ் எபிமெரிஸில் 12 மணிநேரக் குழப்பத்தைத் தவிர்க்க:
    # 5:30 AM IST என்பது முந்தைய நாள் 00:00 UTC. 
    # எனவே ஜூலியன் நாளை நள்ளிரவு 00:00 UT-க்கு அமைக்கிறோம்.
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 0.0) 
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    def get_data(jd):
        m, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
        s, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)
        return m[0], s[0]

    m_now, s_now = get_data(jd_ut)
    
    # தற்போதைய குறியீடுகள்
    nak_idx = int(m_now / (360/27))
    tithi_idx = int(((m_now - s_now) % 360) / 12)

    # வினாடி அளவு துல்லியத்தைக் கண்டறிய (Binary Search)
    def find_end(jd_start, current_idx, type_val):
        low = 0.0
        high = 1.1 # 26 மணிநேரம் வரை
        for _ in range(30):
            mid = (low + high) / 2
            m, s = get_data(jd_start + mid)
            val = int(m / (360/27)) if type_val == "nak" else int(((m - s) % 360) / 12)
            if val == current_idx: low = mid
            else: high = mid
        
        # நேரக் கணக்கீடு:
        # JD 0.0 என்பது IST-க்கு மாற்றும்போது சரியாக 5:30 AM-ல் தொடங்கும்.
        total_delta = timedelta(hours=5, minutes=30) + timedelta(days=low)
        final_time = datetime.combine(date_obj, datetime.min.time()) + total_delta
        return final_time.strftime("%I:%M %p")

    nak_end = find_end(jd_ut, nak_idx, "nak")
    tithi_end = find_end(jd_ut, tithi_idx, "tithi")

    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]

    return {
        "nak": naks[nak_idx], "nak_end": nak_end, "next_nak": naks[(nak_idx + 1) % 27],
        "tithi": tithis[tithi_idx % 30], "tithi_end": tithi_end, "next_tithi": tithis[(tithi_idx + 1) % 30]
    }

# --- UI ---
st.markdown("<h1 class='header-style'>🔱 திருக்கணிதப் பஞ்சாங்கம் (12-Hr Corrected)</h1>", unsafe_allow_html=True)

with st.sidebar:
    # இன்றைய தேதியை டீஃபால்ட்டாகக் காட்டுதல்
    today_ist = datetime.now(IST).date()
    selected_date = st.date_input("🗓️ தேதியைத் தேர்ந்தெடுக்கவும்:", today_ist)

res = get_accurate_panchang(selected_date)

st.markdown(f"""
<table class="panchang-table">
    <tr><th>அங்கம்</th><th>விவரம் (Drik Standard IST)</th></tr>
    <tr><td>🌙 <b>திதி</b></td><td><b>{res['tithi']}</b> (இன்று {res['tithi_end']} வரை), பிறகு <b>{res['next_tithi']}</b></td></tr>
    <tr><td>⭐ <b>நட்சத்திரம்</b></td><td><b>{res['nak']}</b> (இன்று {res['nak_end']} வரை), பிறகு <b>{res['next_nak']}</b></td></tr>
</table>
""", unsafe_allow_html=True)

st.success("12 மணிநேர நேர வித்தியாசம் இப்போது முழுமையாக நீக்கப்பட்டு, இந்திய நேரப்படி (IST) துல்லியமாக்கப்பட்டுள்ளது.")
