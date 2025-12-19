import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. App Amaippu & CSS ----------
st.set_page_config(page_title="Dynamic Astro Jaamakol", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    .stApp { background-color: #FFFDF9; }
    .header-style { background: #4A0000; color: white !important; text-align: center; padding: 10px; border-radius: 8px; font-size: 1.3em; font-weight: bold; margin-bottom: 15px; }
    
    .chart-container { display: flex; flex-direction: column; align-items: center; justify-content: center; margin: auto; max-width: 650px; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .jam-chart { width: 100%; border-collapse: collapse; border: 2.5px solid #4A0000; table-layout: fixed; }
    .jam-chart td { border: 1.5px solid #4A0000; height: 100px; vertical-align: top; padding: 5px; position: relative; }
    
    .outer-top, .outer-bottom { display: flex; justify-content: space-around; width: 100%; padding: 10px 40px; color: #660066; font-weight: bold; font-size: 0.9em; }
    .outer-side-container { display: flex; align-items: center; width: 100%; }
    .outer-left, .outer-right { display: flex; flex-direction: column; justify-content: space-around; height: 350px; padding: 0 20px; color: #660066; font-weight: bold; font-size: 0.9em; }

    .inner-planets { color: #000; font-weight: bold; font-size: 0.8em; line-height: 1.2; }
    .special-marker { color: #D32F2F; font-weight: bold; font-size: 0.85em; display: block; margin-top: 3px; }
    .jam-info-box { text-align: center; background: #fdf2e9; border-radius: 5px; padding: 5px; margin-bottom: 10px; border: 1px solid #e67e22; width: 100%; }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. Input Section ----------------
districts = {"Chennai": [13.08, 80.27], "Madurai": [9.93, 78.12], "Trichy": [10.79, 78.70], "Coimbatore": [11.02, 76.96], "Nellai": [8.71, 77.76], "Salem": [11.66, 78.15]}
st.markdown("<div class='header-style'>🔱 Dynamic Thirukanitha Jaamakol Prasannam</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1,1,1])
with c1: s_dist = st.selectbox("Oor:", list(districts.keys()))
with c2: s_date = st.date_input("Thethi:", datetime.now(IST).date())
with c3: s_time = st.time_input("Neram (Dynamic):", datetime.now(IST).time())

lat, lon = districts[s_dist]

# ---------------- 3. Logic (Dynamic Math) ----------------
def get_dynamic_jamakkol(date_obj, time_obj, lat, lon):
    # Combine date and time
    dt_combined = datetime.combine(date_obj, time_obj)
    tz_find = TimezoneFinder()
    tz_name = tz_find.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    tz = pytz.timezone(tz_name)
    now = tz.localize(dt_combined)
    
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=tz)
    sunrise, sunset = s["sunrise"], s["sunset"]
    
    # 1. Jamam Neram & Type
    is_day = sunrise <= now <= sunset
    if is_day:
        duration = (sunset - sunrise).total_seconds() / 8
        elapsed = (now - sunrise).total_seconds()
        j_type = "Pagal"
    else:
        # Night calculation logic
        if now < sunrise:
            prev_sunset = sun(observer=city.observer, date=date_obj - timedelta(days=1), tzinfo=tz)["sunset"]
            duration = (sunrise - prev_sunset).total_seconds() / 8
            elapsed = (now - prev_sunset).total_seconds()
        else:
            next_sunrise = sun(observer=city.observer, date=date_obj + timedelta(days=1), tzinfo=tz)["sunrise"]
            duration = (next_sunrise - sunset).total_seconds() / 8
            elapsed = (now - sunset).total_seconds()
        j_type = "Iravu"

    cur_jam = min(int(elapsed / duration) + 1, 8)

    # 2. Kocharam (Inner Planets) - Swiss Ephemeris
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0 + now.second/3600.0 - 5.5)

    inner = {}
    p_map = {0:"Suri", 1:"Chan", 2:"Sev", 3:"Budh", 4:"Guru", 5:"Suk", 6:"Sani", 10:"Rahu"}
    for pid, name in p_map.items():
        res, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        idx = int(res[0]/30)
        p_str = f"{name} {int(res[0]%30)}"
        if idx not in inner: inner[idx] = []
        inner[idx].append(p_str)
        if pid == 10: # Kethu
            k_idx = (idx + 6) % 12
            if k_idx not in inner: inner[k_idx] = []
            inner[k_idx].append(f"Kethu {int(res[0]%30)}")

    # 3. Jaama Grahangal (Outer - Dynamic Order)
    jam_order = ["Suri", "Suk", "Budh", "Chan", "Sani", "Guru", "Sev", "Rahu"]
    wk_day = now.weekday() # 0=Mon...6=Sun
    # Jaamakol starts with Day Lord (Sunday Suri, Monday Chan, etc.)
    wk_map = {6:"Suri", 0:"Chan", 1:"Sev", 2:"Budh", 3:"Guru", 4:"Suk", 5:"Sani"}
    start_p = wk_map[wk_day]
    start_idx = jam_order.index(start_p)
    
    # Current Jam Planet
    current_planet = jam_order[(start_idx + (cur_jam - 1)) % 8]

    # Placing Outer Planets starting from Sun Sign
    sun_pos = swe.calc_ut(jd_ut, 0, swe.FLG_SIDEREAL)[0][0]
    sun_sign = int(sun_pos / 30)
    
    outer_res = [""] * 12
    for i in range(8):
        p_name = jam_order[(start_idx + i) % 8]
        target_idx = (sun_sign + i) % 12
        outer_res[target_idx] = p_name

    # 4. Udayam, Arudam, Kavippu
    j_prog = (elapsed % duration) / duration
    u_deg = ((sun_sign + (cur_jam - 1)) * 30 + (j_prog * 30)) % 360
    a_deg = ((sun_sign + cur_jam) * 30) % 360
    k_deg = (u_deg + (sun_pos % 30)) % 360

    return {
        "inner": inner, "outer": outer_res,
        "jam_info": f"{j_type} {cur_jam}-m Jamam ({current_planet})",
        "u": [int(u_deg/30), int(u_deg%30)], "a": [int(a_deg/30), int(a_deg%30)], "k": [int(k_deg/30), int(k_deg%30)],
        "time": now.strftime("%I:%M:%S %p")
    }

res = get_dynamic_jamakkol(s_date, s_time, lat, lon)

# ---------------- 4. Display ----------------
def get_in(i):
    txt = "<div class='inner-planets'>" + " ".join(res['inner'].get(i, [])) + "</div>"
    if i == res['u'][0]: txt += f"<span class='special-marker' style='color:red;'>Utha-{res['u'][1]}</span>"
    if i == res['a'][0]: txt += f"<span class='special-marker' style='color:blue;'>Aru-{res['a'][1]}</span>"
    if i == res['k'][0]: txt += f"<span class='special-marker' style='color:#7B3F00;'>Kavi-{res['k'][1]}</span>"
    return txt

st.markdown(f"""
<div class="chart-container">
    <div class="jam-info-box">
        <b>{res['time']}</b> | {res['jam_info']}
    </div>
    <div class="outer-top">
        <span>{res['outer'][11]}</span><span>{res['outer'][0]}</span><span>{res['outer'][1]}</span><span>{res['outer'][2]}</span>
    </div>
    <div class="outer-side-container">
        <div class="outer-left"><span>{res['outer'][10]}</span><span>{res['outer'][9]}</span></div>
        <table class="jam-chart">
            <tr><td>{get_in(11)}</td><td>{get_in(0)}</td><td>{get_in(1)}</td><td>{get_in(2)}</td></tr>
            <tr><td>{get_in(10)}</td><td colspan="2" rowspan="2" style="text-align:center; background:#FFF9F0; font-size:1.1em; color:#4A0000;"><b>JAAMAKOL</b></td><td>{get_in(3)}</td></tr>
            <tr><td>{get_in(9)}</td><td>{get_in(4)}</td></tr>
            <tr><td>{get_in(8)}</td><td>{get_in(7)}</td><td>{get_in(6)}</td><td>{get_in(5)}</td></tr>
        </table>
        <div class="outer-right"><span>{res['outer'][3]}</span><span>{res['outer'][4]}</span></div>
    </div>
    <div class="outer-bottom">
        <span>{res['outer'][8]}</span><span>{res['outer'][7]}</span><span>{res['outer'][6]}</span><span>{res['outer'][5]}</span>
    </div>
</div>
""", unsafe_allow_html=True)
