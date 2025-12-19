# ---------------- 3. ஜாமக்கோள் லாஜிக் (துல்லியமான பாகை கணக்கீடு) ----------------
def get_jamakkol_data(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    tz = pytz.timezone(tz_name)
    current_time = datetime.now(tz)
    
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=tz)
    sunrise = s["sunrise"]
    sunset = s["sunset"]
    
    # ஜாமம் கணக்கீடு
    day_duration = (sunset - sunrise).total_seconds() / 8
    elapsed = (current_time - sunrise).total_seconds()
    current_jam = int(elapsed / day_duration) + 1 if elapsed > 0 else 1
    if current_jam > 8: current_jam = 8

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_ut = swe.julday(current_time.year, current_time.month, current_time.day, 
                       current_time.hour + current_time.minute/60.0 - 5.5)

    def format_deg(deg):
        d = int(deg % 30)
        m = int((deg % 1) * 60)
        return f"{d}°{m}'"

    # 1. கிரகங்களின் பாகை
    transit_data = {}
    p_names = {0:"சூரி", 1:"சந்", 2:"செவ்", 3:"புத", 4:"குரு", 5:"சுக்", 6:"சனி", 10:"ராகு"}
    for pid, name in p_names.items():
        pos, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        idx = int(pos[0]/30)
        p_info = f"{name}({format_deg(pos[0])})"
        if idx not in transit_data: transit_data[idx] = []
        transit_data[idx].append(p_info)
        if pid == 10: # கேது
            k_deg = (pos[0] + 180) % 360
            k_info = f"கேது({format_deg(k_deg)})"
            k_idx = int(k_deg/30)
            if k_idx not in transit_data: transit_data[k_idx] = []
            transit_data[k_idx].append(k_info)

    # 2. உதயம் (Udayam Degree)
    # ஒரு ஜாமத்திற்கு உதயம் 30 பாகை நகரும் (தோராயமாக)
    jam_progress = (elapsed % day_duration) / day_duration
    sun_pos, _ = swe.calc_ut(jd_ut, 0, swe.FLG_SIDEREAL)
    sunrise_rasi = int(sun_pos[0] / 30)
    
    udayam_raw_deg = ((sunrise_rasi + (current_jam - 1)) * 30) + (jam_progress * 30)
    udayam_idx = int((udayam_raw_deg / 30) % 12)
    
    # 3. ஆருடம் (Arudam Degree)
    arudam_raw_deg = ((sunrise_rasi + (current_jam)) * 30)
    arudam_idx = int((arudam_raw_deg / 30) % 12)

    # 4. கவிப்பு (Kavippu Degree)
    # கவிப்பு சூரியனின் பாகையைத் தொடும் புள்ளியில் இருக்கும்
    kavippu_raw_deg = (udayam_raw_deg + (sun_pos[0] % 30)) % 360
    kavippu_idx = int(kavippu_raw_deg / 30)

    return {
        "transit": transit_data,
        "jam": current_jam,
        "udayam": [udayam_idx, format_deg(udayam_raw_deg)],
        "arudam": [arudam_idx, format_deg(arudam_raw_deg)],
        "kavippu": [kavippu_idx, format_deg(kavippu_raw_deg)],
        "time": current_time.strftime("%I:%M %p")
    }

res = get_jamakkol_data(s_date, lat, lon)

# ---------------- 4. ஜாமக்கோள் கட்டம் (பாகைகளுடன்) ----------------
st.markdown(f"<div class='meroon-header'>🕒 ஜாமம்: {res['jam']} | தொடு பாகை பிரசன்னம்</div>", unsafe_allow_html=True)



def get_box_content(i):
    content = ""
    # கிரகங்கள் + பாகை
    for p in res['transit'].get(i, []):
        content += f"<span class='jam-planet'>{p}</span>"
    
    # உதயம், ஆருடம், கவிப்பு பாகைகளுடன்
    if i == res['udayam'][0]: 
        content += f"<span class='special-label'>[உதயம் {res['udayam'][1]}]</span>"
    if i == res['arudam'][0]: 
        content += f"<span class='special-label'>[ஆருடம் {res['arudam'][1]}]</span>"
    if i == res['kavippu'][0]: 
        content += f"<span class='special-label' style='color:blue;'>[கவிப்பு {res['kavippu'][1]}]</span>"
    return content

# (இங்கு உங்கள் பழைய ஜாமக்கோள் கட்டம் (Table) குறியீட்டைப் பயன்படுத்தவும்)
