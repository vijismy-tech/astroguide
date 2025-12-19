# ---------------- 4. ஜாமக்கோள் கணித லாஜிக் (சரியான கிரக நிலைகளுடன்) ----------------
def get_jamakkol_details(date_obj, lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon) or "Asia/Kolkata"
    tz = pytz.timezone(tz_name)
    current_time = datetime.now(tz)
    
    city = LocationInfo(latitude=lat, longitude=lon, timezone=tz_name)
    s = sun(observer=city.observer, date=date_obj, tzinfo=tz)
    sunrise, sunset = s["sunrise"], s["sunset"]
    
    # ஜாமம் கணக்கீடு (8 ஜாமங்கள்)
    day_dur = (sunset - sunrise).total_seconds() / 8
    elapsed = (current_time - sunrise).total_seconds()
    cur_jam = int(elapsed / day_dur) + 1 if elapsed > 0 else 1
    if cur_jam > 8: cur_jam = 8

    # Swiss Ephemeris Lahiri Ayanamsa அமைப்பு
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    # நேரத்தை UT-க்கு மாற்றுதல் (IST to UT: -5.5 hours)
    jd_ut = swe.julday(current_time.year, current_time.month, current_time.day, 
                       current_time.hour + current_time.minute/60.0 - 5.5)

    def f_deg(deg):
        return f"{int(deg % 30)}°{int((deg % 1) * 60)}'"

    # கிரகங்களின் துல்லியமான பாகை மற்றும் வக்ர நிலை கணக்கீடு
    transit = {}
    p_names = {0:"சூரி", 1:"சந்", 2:"செவ்", 3:"புத", 4:"குரு", 5:"சுக்", 6:"சனி", 10:"ராகு"}
    
    for pid, name in p_names.items():
        # வக்ர நிலை அறிய swe.calc_ut பயன்படுத்துகிறோம்
        res, _ = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL)
        pos = res[0]
        speed = res[3] # வேகம் (மறைமுகமாக வக்ர நிலை அறிய)
        
        idx = int(pos / 30)
        vakra_mark = "(வ)" if speed < 0 else "" # வக்ரம் இருந்தால் (வ) என்று காட்டும்
        
        p_info = f"{name}{vakra_mark}({f_deg(pos)})"
        
        if idx not in transit: transit[idx] = []
        transit[idx].append(p_info)
        
        if pid == 10: # கேது (ராகுவுக்கு நேர் 180 டிகிரியில்)
            k_deg = (pos + 180) % 360
            k_idx = int(k_deg / 30)
            k_info = f"கேது({f_deg(k_deg)})"
            if k_idx not in transit: transit[k_idx] = []
            transit[k_idx].append(k_info)

    # உதய ஆருட கவிப்பு பாகை கணக்கீடு
    sun_res, _ = swe.calc_ut(jd_ut, 0, swe.FLG_SIDEREAL)
    sun_pos = sun_res[0]
    sun_sign = int(sun_pos / 30)
    jam_prog = (elapsed % day_dur) / day_dur
    
    # உதய பாகை: சூரியன் நின்ற ராசியிலிருந்து ஜாமத்தின் நகர்வு
    u_raw = ((sun_sign + (cur_jam - 1)) * 30 + (jam_prog * 30)) % 360
    # ஆருட பாகை: ஜாம எண்ணிக்கைக்கு ஏற்ப ராசி மாற்றம்
    a_raw = ((sun_sign + cur_jam) * 30) % 360
    # கவிப்பு பாகை: உதய பாகை + சூரியனின் ஸ்புடம் (பாகை)
    k_raw = (u_raw + (sun_pos % 30)) % 360

    return {
        "transit": transit, "jam": cur_jam,
        "udayam": [int((u_raw/30)%12), f_deg(u_raw)],
        "arudam": [int((a_raw/30)%12), f_deg(a_raw)],
        "kavippu": [int((k_raw/30)%12), f_deg(k_raw)],
        "time": current_time.strftime("%I:%M %p")
    }
