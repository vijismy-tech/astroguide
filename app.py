import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder

# ---------- 1. ஆப் அமைப்புகள் & நவீன CSS வடிவமைப்பு ----------
st.set_page_config(page_title="AstroGuide திருக்கணிதப் பஞ்சாங்கம்", layout="wide")
IST = pytz.timezone('Asia/Kolkata')

st.markdown("""
    <style>
    /* முழு பக்க பின்னணி - மென்மையான சந்தன நிறம் */
    .stApp { background-color: #FFF9F2; }
    
    /* அனைத்து எழுத்துக்களும் கருப்பு நிறத்தில் தெளிவாக இருக்க */
    h1, h2, h3, p, span, div, label, td, th { 
        color: #2D2D2D !important; 
        font-family: 'Segoe UI', Roboto, sans-serif; 
    }
    
    /* மெயின் தலைப்பு - ஸ்டைலான மெரூன் பெட்டி */
    .header-style { 
        background: linear-gradient(135deg, #8B0000 0%, #B22222 100%);
        color: white !important; 
        text-align: center; 
        padding: 15px; 
        border-radius: 0px 0px 20px 20px; 
        font-size: 1.4em; 
        font-weight: bold;
        margin: -60px -20px 20px -20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    /* கச்சிதமான ஒயிட் கார்டு (Main Box) */
    .main-box { 
        max-width: 420px; 
        margin: auto; 
        padding: 12px; 
        background: #FFFFFF; 
        border-radius: 12px; 
        border: 1px solid #E0E0E0; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        margin-bottom: 10px; 
    }
    
    /* உட்பிரிவு தலைப்புகள் (Subheaders) */
    .meroon-header { 
        color: #8B0000 !important; 
        font-size: 1.05em; 
        font-weight: bold; 
        border-left: 4px solid #8B0000;
        padding-left: 10px;
        margin: 15px 0px 10px 0px;
        display: flex;
        align-items: center;
    }
    
    /* பஞ்சாங்க அட்டவணை வடிவமைப்பு */
    .panchang-table { 
        width: 100%; 
        border-collapse: collapse; 
        background: white; 
        border-radius: 8px;
        overflow: hidden;
        font-size: 0.85em; 
    }
    .panchang-table td { 
        padding: 8px 12px; 
        border-bottom: 1px solid #F1F1F1; 
        font-weight: 500;
    }
    .panchang-table b { color: #8B0000; }

    /* பட்டன் ஸ்டைல் */
    .stButton>button {
        width: 100%;
        background-color: #8B0000;
        color: white !important;
        border-radius: 8px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)
