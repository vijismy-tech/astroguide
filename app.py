import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz

# ஆப் அமைப்புகள்
st.set_page_config(page_title="Professional IST Panchangam", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

# --- CSS ஸ்டைலிங் (Fixed Syntax) ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    .header-style { color: #8B0000; text-align: center; font-family: 'Tamil'; font-weight: bold; margin-bottom: 20px; }
    .panchang-table {
        width: 100%; border-collapse: collapse; background: white;
        border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .panchang-table th { background-color: #8B0000; color: white; padding: 15px; text-align: left; border: 1px solid #700000; }
    .panchang-table td { padding: 12px 15px; border: 1px solid #eee; color: #333; font-weight: 500; }
    .panchang-table tr:nth-child(even) { background-color: #FFFBF0; }
    .status-tag { padding: 4px 10px; border-radius: 5px; font-weight: bold; font-size: 0.9em; }
    .waxing { background-color: #E8F5E9; color: #2E7D32; }
    .waning { background-color: #FFEBEE; color: #C62828; }
    </style>
    """, unsafe_allow_html=True)

def get_detailed_ist_panchang(date_obj):
    jd = swe.julday(date_obj.year, date_obj.month, date_obj.day, 5.5)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    m_pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
    s_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    
    naks = ["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிடம்", "திருவாதிரை", "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்", "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"]
    tithis = ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "பௌர்ணமி", "பிரதமை (தேய்பிறை)", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி", "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி", "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்த்தசி", "அமாவாசை"]
    yogams = ["விஷ்கம்பம்", "ப்ரீதி", "ஆயுஷ்மான்", "சௌபாக்கியம்", "சோபனம்", "அதிகண்டம்", "சுகர்மம்", "திருதி", "சூலம்", "கண்டம்", "விருத்தி", "துருவம்", "வியாகாதம்", "ஹர்ஷணம்", "வஜ்ரம்", "சித்தி", "வியதீபாதம்", "வரியான்", "பரிகம்", "சிவம்", "சித்தம்", "சாத்தியம்", "சுபம்", "சுப்பிரம்", "பிராமியம்", "ஐந்தரம்", "வைதிருதி"]

    nak_idx = int(m_pos / (360/27))
    tithi_idx = int(((m_pos - s_pos) % 360) / 12)
    yog_idx = int(((m_pos + s_pos) % 360) / (360/27))

    # நேரக் கணக்கீடு
    def calc_end_time(jd_start, current_val, calc_type):
        temp_jd = jd_start
        step = 0.01 
        while True:
            m = swe.calc_ut(temp_jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
            s = swe.calc_ut(temp_jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
            val = int(m / (360/27)) if calc_type == "nak" else int(((m - s) % 360) / 12)
            if val != current_val: break
            temp_jd += step
            if temp_jd > jd_start + 1.2: break
        calc_dt = datetime.combine(date_obj, datetime.min.time()) + timedelta(days=(temp_jd - jd_start) + 0.229)
        return calc_dt.strftime("%I:%M %p")

    nak_end = calc_end_time(jd, nak_idx, "nak")
    tithi_end = calc_end_time(jd, tithi_idx, "tithi")

    day_idx = date_obj.weekday()
    rahu = ["07:30-09:00", "15:00-16:30", "12:00-13:30", "13:30-15:00", "10:30-12:00", "09:00-10:30", "16:30-18:00"][day_idx]
    yema = ["10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30", "13:30-15:00", "12:00-13:30"][day_idx]
    kuli = ["13:30-15:00", "12:00-13:30", "10:30-12:00", "09:00-10:30", "07:30-09:00", "06:00-07:30", "15:00-16:30"][day_idx]

    return {
        "wara": ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"][day_idx],
        "tithi": tithis[tithi_idx % 30], "tithi_end": tithi_end, "next_tithi": tithis[(tithi_idx + 1) % 30],
        "nak": naks[nak_idx], "nak_end": nak_end, "next_nak": naks[(nak_idx + 1) % 27],
        "paksha": "வளர்பிறை" if tithi_idx < 15 else "தேய்பிறை",
        "rahu": rahu, "yema": yema, "kuli": kuli,
        "yogam": yogams[yog_idx], "raasi": ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"][int(m_pos/30)]
    }

# --- UI ---
st.markdown("<h1 class='header-style'>🔱 அஸ்ட்ரோ கைடு - துல்லிய இந்திய பஞ்சாங்கம்</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🗓️ காலண்டர்")
    selected_date = st.date_input("தேதியைத் தேர்ந்தெடுக்கவும்:", datetime.now(IST))

p = get_detailed_ist_panchang(selected_date)

# HTML Table Construction
paksha_class = "waxing" if p['paksha'] == "வளர்பிறை" else "waning"

table_html = f"""
<table class="panchang-table">
    <tr><th>அங்கம்</th><th>விளக்கம் (Asia/Kolkata நேரப்படி)</th></tr>
    <tr><td>📅 <b>வாரம் & பக்கம்</b></td><td>{p['wara']} | <span class="status-tag {paksha_class}">{p['paksha']}</span></td></tr>
    <tr><td>🌙 <b>திதி சஞ்சாரம்</b></td><td><b>{p['tithi']}</b> (இன்று {p['tithi_end']} வரை), பிறகு <b>{p['next_tithi']}</b></td></tr>
    <tr><td>⭐ <b>நстройство சஞ்சாரம்</b></td><td><b>{p['nak']}
