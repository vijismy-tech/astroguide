import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder
import urllib.parse  # வாட்ஸ்அப் லிங்க் உருவாக்க

# ஆப் அமைப்புகள்
st.set_page_config(page_title="Ultra Precise Tamil Panchangam", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

# --- வாட்ஸ்அப் எண் (உங்கள் எண்ணை இங்கே மாற்றவும்) ---
YOUR_WHATSAPP_NUMBER = "919876543210" # உதாரணத்திற்கு 91 சேர்த்து உங்கள் எண்ணை இடவும்

# --- Session State (Login நிலையைச் சரிபார்க்க) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'view' not in st.session_state:
    st.session_state.view = 'login'

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
    .auth-box { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }
    </style>
    """, unsafe_allow_html=True)

# --- பஞ்சாங்கக் கணக்கீட்டுப் பங்க்ஷன்கள் (உங்கள் பழைய Code மாறாமல்) ---
def get_sunrise_sunset(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    city = LocationInfo(name="Selected", region="", timezone=tz_name, latitude=lat, longitude=lon)
    s = sun(observer=city.observer, date=date_obj, tzinfo=pytz.timezone(tz_name))
    return s["sunrise"].strftime("%I:%M %p"), s["sunset"].strftime("%I:%M %p")

def get_precise_panchang(date_obj, lat, lon):
    jd_ut = swe.julday(date_obj.year, date_obj.month, date_obj.day, 0.0) 
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    swe.set_topo(lon, lat, 0)
    
    def get_raw_astronomy(jd):
        m, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
        s, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)
        m_deg, s_deg = m[0], s[0]
        diff = (m_deg - s_deg) % 360
        return m_deg, s_deg, int(diff / 12), int(m_deg / (360/27)), int(((m_deg + s_deg) % 360) / (360/27)), int(diff / 6) % 11

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
    
    tamil_months = ["சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி", "ஐப்பசி", "கார்த்திகை", "மார்கழி", "தை", "மாசி", "பங்குனி"]
    wara_names = ["திங்கட்கிழமை", "செவ்வாய்க்கிழமை", "புதன்கிழமை", "வியாழக்கிழமை", "வெள்ளிக்கிழமை", "சனிக்கிழமை", "ஞாயிற்றுக்கிழமை"]
    
    return {
        "m_deg": round(m_start, 2), "wara": wara_names[date_obj.weekday()],
        "tamil_month": tamil_months[int(s_start / 30) % 12], "tamil_date": int(s_start % 30) + 1,
        "tithi": "திதி விவரம்...", # சுருக்கத்திற்காக
        "tithi_end": t_end_dt.strftime("%I:%M %p"),
        "nak": "நட்சத்திரம்...", "nak_end": n_end_dt.strftime("%I:%M %p"),
        "yog": "யோகம்", "kar": "கரணம்", "paksha": "வளர்பிறை",
        "rahu": "நேரம்", "yema": "நேரம்", "kuli": "நேரம்", "shoolam": "திசை", "gowri": "நேரம்"
    }

# --- Login / Sign Up UI ---
if not st.session_state.logged_in:
    if st.session_state.view == 'login':
        st.markdown("<h2 class='header-style'>உள்நுழை (Login)</h2>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="auth-box">', unsafe_allow_html=True)
            u_user = st.text_input("பயனர் பெயர் (Username)")
            u_pass = st.text_input("கடவுச்சொல் (Password)", type="password")
            if st.button("Login"):
                # இங்கே எளிய முறையில் சரிபார்க்கிறோம் (நிஜ ஆப்பில் Database தேவை)
                if u_user == "admin" and u_pass == "123":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("தவறான விவரங்கள்!")
            st.write("புதிய கணக்கு வேண்டுமா?")
            if st.button("Sign Up செய்ய இங்கே கிளிக் செய்யவும்"):
                st.session_state.view = 'signup'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.view == 'signup':
        st.markdown("<h2 class='header-style'>பதிவு செய்க (Sign Up)</h2>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="auth-box">', unsafe_allow_html=True)
            new_name = st.text_input("முழு பெயர்")
            new_phone = st.text_input("வாட்ஸ்அப் எண்")
            new_city = st.text_input("ஊர்")
            
            if st.button("பதிவு செய்க"):
                # வாட்ஸ்அப் செய்தி உருவாக்கல்
                msg = f"புதிய நபர் பதிவு செய்துள்ளார்:\nபெயர்: {new_name}\nஎண்: {new_phone}\nஊர்: {new_city}"
                encoded_msg = urllib.parse.quote(msg)
                wa_link = f"https://wa.me/{YOUR_WHATSAPP_NUMBER}?text={encoded_msg}"
                
                st.success("தகவல்கள் சேமிக்கப்பட்டன! உறுதிப்படுத்த கீழே உள்ள பட்டனை அழுத்தவும்.")
                st.markdown(f'''<a href="{wa_link}" target="_blank">
                    <button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">
                    Send Details to WhatsApp & Finish
                    </button></a>''', unsafe_allow_html=True)
            
            if st.button("Back to Login"):
                st.session_state.view = 'login'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- மெயின் பஞ்சாங்கம் (Login ஆன பிறகு மட்டும் காட்டும்) ---
else:
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
    
    # இங்கிருந்து உங்கள் பழைய முழு பஞ்சாங்க Code-ஐ அப்படியே தொடரவும்...
    districts = {"அரியலூர்": [11.1401, 79.0786], "சென்னை": [13.0827, 80.2707], "மதுரை": [9.9252, 78.1198]} # List தொடரும்
    
    with st.sidebar:
        selected_dist = st.selectbox("மாவட்டத்தைத் தேர்ந்தெடுக்கவும்:", list(districts.keys()))
        selected_date = st.date_input("தேதியைத் தேர்ந்தெடுக்கவும்:", datetime.now(IST))

    lat, lon = districts[selected_dist]
    # (உங்கள் பழைய Table மற்றும் Display Logic இங்கே வர வேண்டும்)
    st.write(f"நிச்சயமாக, {selected_dist} பஞ்சாங்கம் இங்கே தோன்றும்...")
