import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz

# ஆப் அமைப்புகள்
st.set_page_config(page_title="Ultra Precise Drik Panchangam", layout="wide")
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
    .degree-info { color: #1B5E20; font-size: 0.9em; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

def get_moon_degree_panchang(date_obj):
    # திருக்கணித முறைப்படி துல்லியமான நேரக் கணக்கீடு
    # UTC நள்ளிரவு (0:00 AM) = 5:30 AM IST
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 0.0) 
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    def get_raw_data(jd):
        # நிலவு மற்றும் சூரியனின் பாகைகளைத் துல்லியமாகப் பெறுதல்
        m, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
        s, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)
        m_deg = m[0]
        s_deg = s[0]
        # திதி கணக்கீடு: (Moon - Sun) % 360 / 12
        diff = (m_deg - s_deg) % 360
        t_idx = int(diff / 12)
        # நட்சத்திர கணக்கீடு: Moon / (360/27)
        n_idx = int(m_deg / (13.333333333333334))
        return m_deg, s_deg, t_idx, n_idx

    m_start, s_start, tithi_now, nak_now = get_raw_data(jd_ut)

    # முடிவு நேரத்தைக் கண்டறிய (High-Precision Binary Search)
    def find_end_moment(jd_start, current_idx, calc_type):
        low = 0.0
        high = 1.25 # 30 மணிநேரம் வரை தேடுதல்
        for _ in range(35): # 35 முறை சுழற்சி செய்தால் வினாடி அளவிலான துல்லியம் கிடைக்கும்
            mid = (low + high) / 2
            _, _, t_val, n_val = get_raw_data(jd_start + mid)
            val = n_val if calc_type == "nak" else t_val
            if val == current_idx: low = mid
            else: high = mid
        
        # 0.0 UT என்பது 5:30 AM IST. அதனுடன் 'low' நாட்களைக் கூட்டுகிறோம்.
        exact_dt = datetime.combine(date_obj, datetime.min.time()) + timedelta(hours=5.5) + timedelta(days=low)
        return exact_dt

    t_end_dt = find_end_moment(jd_ut, tithi_now, "tithi")
    n_end_dt = find_end_moment(jd_ut, nak_now, "nak")

    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]

    return {
        "m_deg": round(m_start, 2),
        "s_deg": round(s_start, 2),
        "tithi": tithis[tithi_now % 30],
        "tithi_end": t_end_dt.strftime("%d-%m-%Y %I:%M %p"),
        "next_tithi": tithis[(tithi_now + 1) % 30],
        "nak": naks[nak_now % 27],
        "nak_end": n_end_dt.strftime("%d-%m-%Y %I:%M %p"),
        "next_nak": naks[(nak_now + 1) % 27]
    }

# --- UI ---
st.markdown("<h1 class='header-style'>🔱 திருக்கணித பாகை கணக்கீடு (Ultra Accurate)</h1>", unsafe_allow_html=True)

with st.sidebar:
    selected_date = st.date_input("🗓️ தேதியைத் தேர்ந்தெடுக்கவும்:", datetime.now(IST))

res = get_moon_degree_panchang(selected_date)

st.markdown(f"""
<table class="panchang-table">
    <tr><th>அங்கம்</th><th>விவரம் (IST - இந்திய நேரப்படி)</th></tr>
    <tr><td>🌙 <b>திதி சஞ்சாரம்</b></td><td>
        <b>{res['tithi']}</b><br>
        🕒 முடிவு: {res['tithi_end']}<br>
        ➡️ அடுத்து: {res['next_tithi']}
    </td></tr>
    <tr><td>⭐ <b>நட்சத்திர சஞ்சாரம்</b></td><td>
        <b>{res['nak']}</b><br>
        🕒 முடிவு: {res['nak_end']}<br>
        ➡️ அடுத்து: {res['next_nak']}
    </td></tr>
    <tr><td>📊 <b>வானியல் பாகை (Degrees)</b></td><td>
        <span class="degree-info">நிலவு: {res['m_deg']}° | சூரியன்: {res['s_deg']}°</span>
    </td></tr>
</table>
""", unsafe_allow_html=True)

st.success("இந்தக் கணக்கீடு நிலவின் பாகை (Moon Degree) மற்றும் சூரியனின் பாகை இடையிலான வித்தியாசத்தைக் கொண்டு $12^{\circ}$ விதியின்படி செய்யப்பட்டுள்ளது.")
