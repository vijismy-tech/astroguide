def get_precise_panchang(city_name, date_obj):
    # ... (munbu ulla geocoder matrum jd calculations) ...

    # Tithi names list
    tithis = ["Prathami", "Dwitiya", "Thritiya", "Chathurthi", "Panchami", "Shasthi", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Pournami", "Prathami (K)", "Dwitiya (K)", "Thritiya (K)", "Chathurthi (K)", "Panchami (K)", "Shasthi (K)", "Saptami (K)", "Ashtami (K)", "Navami (K)", "Dashami (K)", "Ekadashi (K)", "Dwadashi (K)", "Trayodashi (K)", "Chaturdashi (K)", "Amavasai"]

    # 1. Kaalaiyil (Sunrise) ulla thithi
    m_start, s_start = get_moon_sun(jd_start)
    curr_tithi_idx = int(((m_start - s_start) % 360) / 12)
    
    # 2. Thithi mudiyum neram (End Time) kaanbathu
    # Iterative calculation moolam thulliyamaana 'End Time'
    step = 0.01 # Approx 15 mins
    temp_jd = jd_start
    while int(((swe.calc_ut(temp_jd, swe.MOON, swe.FLG_SIDEREAL)[0][0] - swe.calc_ut(temp_jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]) % 360) / 12) == curr_tithi_idx:
        temp_jd += step
        if temp_jd > jd_start + 1: break # Max 24 hours
    
    end_dt = datetime.combine(date_obj, datetime.min.time()) + timedelta(days=(temp_jd - jd_start) + 0.229)
    tithi_end_time = end_dt.strftime("%I:%M %p")

    # 3. Adutha thithi (Next Tithi)
    next_tithi_idx = (curr_tithi_idx + 1) % 30
    
    return {
        "curr_tithi": tithis[curr_tithi_idx],
        "tithi_end": tithi_end_time,
        "next_tithi": tithis[next_tithi_idx],
        "is_next_day": end_dt.day > date_obj.day
    }

# --- UI Display logic ---
st.markdown(f"""
<div class="panchang-box">
    <h3 style="color: #4B0082;">🌙 Thithi Vibaram</h3>
    <p class="label-text">Indraya Thithi:</p>
    <p class="value-text">{res['curr_tithi']}</p>
    <p class="time-text">Mudiyum Neram: Indru {res['tithi_end']} varai</p>
    
    <div style="margin-top:15px; padding:10px; border-top:1px dashed #ccc;">
        <p style="color:#666; font-size:0.9em;">Adutha Thithi: <b>{res['next_tithi']}</b></p>
        <p style="color:#666; font-size:0.9em;">Thodangum Neram: <b>{res['tithi_end']}</b></p>
    </div>
</div>
""", unsafe_allow_html=True)
