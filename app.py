import streamlit as st
from datetime import datetime

# ஆப் கட்டமைப்பு
st.set_page_config(page_title="Astro Guide Pro", layout="wide")

# --- நவீன CSS வடிவமைப்பு ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFDF5; }
    .main-title { color: #800000; text-align: center; font-family: 'Tamil'; font-weight: 900; margin-bottom: 20px; }
    
    /* தகவல்கள் அடங்கிய மென்மையான கார்டு */
    .glass-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #D4AF37; /* தங்க நிற பார்டர் */
        box-shadow: 0 8px 32px 0 rgba(184, 134, 11, 0.1);
        margin: 10px;
    }

    .info-label { color: #5D4037; font-size: 1.1em; font-weight: bold; }
    .info-value { color: #1B5E20; font-size: 1.3em; font-weight: 800; }
    .highlight-box { 
        background-color: #FFF9C4; 
        padding: 10px; 
        border-radius: 10px; 
        border-left: 5px solid #FBC02D; 
        margin-top: 10px;
    }
    .good-time { color: #D84315; font-weight: bold; font-size: 1.2em; }
    </style>
    """, unsafe_allow_html=True)

# --- தலைப்பு ---
st.markdown("<h1 class='main-title'>🌟 அஸ்ட்ரோ கைடு - முக்கிய பஞ்சாங்கம்</h1>", unsafe_allow_html=True)

# --- இன்றைய தகவல்கள் (நீங்கள் கேட்ட விவரங்கள்) ---
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color: #B8860B;">📅 இன்றைய நாள் விபரம்</h3>
        <p class="info-label">தேதி:</p>
        <p class="info-value">டிசம்பர் 18, 2025</p>
        <p class="info-label">தமிழ் மாதம்:</p>
        <p class="info-value">விசுவாவசு வருடம், மார்கழி 3</p>
        <p class="info-label">கிழமை:</p>
        <p class="info-value">வியாழக்கிழமை</p>
        <div class="highlight-box">
            <p style="margin:0; color:#4E342E;">✨ <b>யோகம்:</b> சித்த யோகம் (இன்று முழுவதும்)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color: #B8860B;">🌙 திதி & நட்சத்திரம்</h3>
        <p class="info-label">இன்றைய திதி:</p>
        <p class="info-value">சதுர்த்தசி</p>
        <p style="color:#757575; font-size:0.9em;">(திரியோதசி அதிகாலை 03:51 வரை இருந்தது)</p>
        <hr>
        <p class="info-label">இன்றைய நட்சத்திரம்:</p>
        <p class="info-value">கேட்டை</p>
        <p style="color:#757575; font-size:0.9em;">(அனுஷம் இரவு 09:34 வரை இருந்தது)</p>
    </div>
    """, unsafe_allow_html=True)

# --- நல்ல நேரம் பகுதி ---
st.markdown(f"""
    <div class="glass-card" style="text-align: center; border-color: #4CAF50;">
        <h3 style="color: #2E7D32;">⌛ நல்ல நேரம் (Subha Horai)</h3>
        <p class="good-time">காலை 10:45 முதல் 11:45 வரை</p>
        <p style="color: #666;">இன்று விசேஷமான காரியங்களைச் செய்ய இந்த நேரத்தைப் பயன்படுத்தலாம்.</p>
    </div>
    """, unsafe_allow_html=True)

# --- அடிக்குறிப்பு ---
st.markdown("<p style='text-align:center; color:#9E9E9E; font-size:0.8em;'>கணித முறை: திருக்கணிதம் | இடம்: சென்னை (உள்ளூர் நேரப்படி)</p>", unsafe_allow_html=True)
