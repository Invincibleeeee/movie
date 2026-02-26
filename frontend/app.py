import requests
import streamlit as st
import os
import re
import json
from dotenv import load_dotenv
load_dotenv()
import time

# =============================
# CONFIG
# =============================
API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000").rstrip("/")
TMDB_IMG = "https://image.tmdb.org/t/p/w500"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

st.set_page_config(
    page_title="CineVault",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================
# THEME CSS — NETFLIX PREMIUM
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── ROOT VARIABLES ── */
:root {
  --bg:       #0f0f0f;
  --bg2:      #141414;
  --bg3:      #181818;
  --bg4:      #1c1c1c;
  --bg5:      #242424;
  --red:      #e50914;
  --red2:     #b20710;
  --red-lit:  #ff3d3d;
  --gold:     #f5c518;
  --white:    #ffffff;
  --grey1:    #e5e5e5;
  --grey2:    #a0a0a0;
  --grey3:    #505050;
  --grey4:    #282828;
  --border:   rgba(255,255,255,0.07);
  --border2:  rgba(255,255,255,0.12);
  --glass-bg: rgba(15,15,15,0.85);
  --glass-border: rgba(255,255,255,0.08);
  --r:        10px;
  --r2:       6px;
  --card-glow: 0 0 20px rgba(229,9,20,0.25);
  --premium-shadow: 0 20px 60px rgba(0,0,0,0.6);
}

/* ── ANIMATIONS ── */
@keyframes fadeUp {
  from { opacity:0; transform:translateY(24px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes fadeIn {
  from { opacity:0; }
  to   { opacity:1; }
}
@keyframes scaleIn {
  from { opacity:0; transform:scale(0.92); }
  to   { opacity:1; transform:scale(1); }
}
@keyframes slideDown {
  from { opacity:0; transform:translateY(-12px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes pulseRed {
  0%,100% { box-shadow: 0 0 0 0 rgba(229,9,20,0); }
  50%     { box-shadow: 0 0 24px 4px rgba(229,9,20,0.25); }
}
@keyframes shimmer {
  0%   { background-position:-200% 0; }
  100% { background-position:200% 0; }
}
@keyframes typing {
  0%,60%,100% { transform:translateY(0); opacity:0.3; }
  30% { transform:translateY(-8px); opacity:1; }
}
@keyframes gradientShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* ══════════════════════════════════
   GLOBAL RESET & BASE
══════════════════════════════════ */
*, *::before, *::after { box-sizing:border-box; }

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main .block-container {
  background:#0f0f0f !important;
  color:#e5e5e5 !important;
  font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif !important;
}

/* Hide ALL Streamlit chrome + sidebar */
#MainMenu, header[data-testid="stHeader"],
footer, [data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.viewerBadge_container__1QSob,
.styles_viewerBadge__1yB5_,
[data-testid="stHeader"],
[data-testid="stSidebar"],
section[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
button[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] { display:none !important; }

/* Remove background from all Streamlit containers */
[data-testid="stVerticalBlock"] > div,
.element-container,
[data-testid="stHorizontalBlock"],
[data-testid="column"] {
  background:transparent !important;
}

/* ── Main content area ── */
.block-container {
  padding: 0.5rem 3rem 4rem !important;
  max-width: 1440px !important;
}

/* ── Headings ── */
h1, h2, h3 {
  font-family:'Bebas Neue',sans-serif !important;
  letter-spacing:0.05em !important;
  color:#ffffff !important;
}

/* ══════════════════════════════════
   SCROLLBAR
══════════════════════════════════ */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#0f0f0f; }
::-webkit-scrollbar-thumb { background:#333; border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:#e50914; }

/* ══════════════════════════════════
   TOP NAVBAR — PREMIUM
══════════════════════════════════ */
.cv-navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0 14px;
  background: rgba(15,15,15,0.85);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(255,255,255,0.05);
  margin-bottom: 0;
  animation: slideDown 0.4s ease;
  transition: all 0.3s ease;
}
.cv-logo {
  display: flex;
  align-items: baseline;
  gap: 6px;
  cursor: pointer;
  text-decoration: none;
}
.cv-logo-icon {
  font-size: 1.6rem;
  line-height: 1;
}
.cv-logo-text {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2rem;
  letter-spacing: 0.14em;
  color: #e50914;
  line-height: 1;
}
.cv-logo-text span {
  color: #fff;
}

/* Nav link buttons */
div.nav-link .stButton > button {
  background: transparent !important;
  border: none !important;
  color: #888 !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  padding: 8px 4px !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  border-radius: 0 !important;
  border-bottom: 2px solid transparent !important;
  transition: color 0.2s ease, border-color 0.2s ease !important;
}
div.nav-link .stButton > button:hover {
  color: #e5e5e5 !important;
  background: transparent !important;
  border-bottom-color: rgba(229,9,20,0.35) !important;
  transform: none !important;
  box-shadow: none !important;
}
div.nav-link-active .stButton > button {
  background: transparent !important;
  border: none !important;
  color: #fff !important;
  font-size: 0.82rem !important;
  font-weight: 700 !important;
  padding: 8px 4px !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  border-radius: 0 !important;
  border-bottom: 2px solid #e50914 !important;
}
div.nav-link-active .stButton > button:hover {
  background: transparent !important;
  transform: none !important;
  box-shadow: none !important;
}

/* Nav sign-in button */
div.nav-signin .stButton > button {
  background: #e50914 !important;
  border: none !important;
  color: #fff !important;
  font-size: 0.78rem !important;
  font-weight: 700 !important;
  padding: 7px 22px !important;
  border-radius: 4px !important;
  text-transform: none !important;
  letter-spacing: 0.02em !important;
}
div.nav-signin .stButton > button:hover {
  background: #b20710 !important;
  transform: none !important;
  box-shadow: none !important;
}

/* Nav sign-out button */
div.nav-signout .stButton > button {
  background: transparent !important;
  border: 1px solid #333 !important;
  color: #999 !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  padding: 6px 14px !important;
  border-radius: 4px !important;
  text-transform: none !important;
}
div.nav-signout .stButton > button:hover {
  border-color: #e50914 !important;
  color: #e50914 !important;
  background: transparent !important;
  transform: none !important;
  box-shadow: none !important;
}

/* Nav user badge */
.nav-user {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #ccc;
}
.nav-user-avatar {
  width: 30px; height: 30px;
  background: linear-gradient(135deg, #e50914, #b20710);
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 800;
}

/* ══════════════════════════════════
   TEXT INPUTS — NETFLIX STYLE
══════════════════════════════════ */
[data-testid="stTextInput"] input {
  background: #111 !important;
  color: #fff !important;
  border: 2px solid #333 !important;
  border-radius: 4px !important;
  padding: 14px 16px !important;
  font-size: 0.95rem !important;
  font-weight: 400 !important;
  transition: border-color 0.2s ease !important;
  caret-color: #e50914 !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: #e50914 !important;
  box-shadow: 0 0 0 1px #e50914 !important;
  outline: none !important;
  background: #111 !important;
}
[data-testid="stTextInput"] input::placeholder {
  color: #555 !important;
}
[data-testid="stTextInput"] label {
  color: #666 !important;
  font-size: 0.7rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
}

/* ══════════════════════════════════
   SELECTBOX — DARK
══════════════════════════════════ */
[data-testid="stSelectbox"] > div > div {
  background: #111 !important;
  color: #fff !important;
  border: 2px solid #333 !important;
  border-radius: 4px !important;
}
[data-testid="stSelectbox"] label {
  color: #666 !important;
  font-size: 0.7rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.12em !important;
  font-weight: 700 !important;
}

/* ══════════════════════════════════
   BUTTONS — NETFLIX RED
══════════════════════════════════ */
.stButton > button {
  background: #e50914 !important;
  color: #fff !important;
  border: none !important;
  border-radius: 4px !important;
  font-family: 'Inter',sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.82rem !important;
  letter-spacing: 0.04em !important;
  padding: 10px 24px !important;
  transition: background 0.2s ease !important;
  cursor: pointer !important;
  text-transform: none !important;
}
.stButton > button:hover {
  background: #b20710 !important;
  box-shadow: none !important;
  transform: none !important;
}
.stButton > button:active {
  background: #8c060d !important;
  transform: scale(0.98) !important;
}

/* ── Slider ── */
[data-testid="stSlider"] label {
  color: #666 !important;
  font-size: 0.7rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.12em !important;
  font-weight: 700 !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
  background: #e50914 !important;
}

/* ── Divider / HR ── */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── Images ── */
[data-testid="stImage"] img {
  border-radius: 4px !important;
  display: block;
}

/* ══════════════════════════════════
   SEARCH BAR — NETFLIX PROMINENT
══════════════════════════════════ */
.nf-search-area {
  max-width: 800px;
  margin: 0 auto 40px;
  animation: fadeUp 0.5s ease both;
}
.nf-search-area [data-testid="stTextInput"] input {
  font-size: 1.08rem !important;
  padding: 18px 28px !important;
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  background: rgba(20,20,20,0.9) !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;
  font-weight: 400 !important;
  transition: all 0.3s ease !important;
}
.nf-search-area [data-testid="stTextInput"] input:focus {
  border-color: rgba(229,9,20,0.5) !important;
  box-shadow: 0 0 0 3px rgba(229,9,20,0.12),
              0 12px 40px rgba(0,0,0,0.5),
              0 0 60px rgba(229,9,20,0.06) !important;
  background: rgba(15,15,15,0.95) !important;
}

/* ══════════════════════════════════
   SECTION HEADERS — BIG & BOLD
══════════════════════════════════ */
.nf-section-title {
  font-family: 'Bebas Neue',sans-serif;
  font-size: 1.9rem;
  letter-spacing: 0.07em;
  color: #fff;
  margin: 6px 0 22px 0;
  padding: 0;
  display: flex;
  align-items: center;
  gap: 14px;
  animation: fadeUp 0.4s ease both;
}
.nf-section-title::before {
  content: '';
  width: 4px;
  height: 30px;
  background: linear-gradient(180deg, #e50914, #b20710);
  border-radius: 2px;
  flex-shrink: 0;
}

/* ══════════════════════════════════
   MOVIE CARD — NETFLIX POSTER STYLE
══════════════════════════════════ */
.nf-card {
  background: #181818;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  transition: transform 0.4s cubic-bezier(0.25,0.46,0.45,0.94),
              box-shadow 0.4s ease,
              border-color 0.4s ease;
  animation: fadeUp 0.5s ease both;
  cursor: pointer;
  border: 1px solid transparent;
}
.nf-card:hover {
  transform: translateY(-10px) scale(1.03);
  box-shadow: 0 24px 50px rgba(0,0,0,0.85),
              0 0 30px rgba(229,9,20,0.15);
  border-color: rgba(229,9,20,0.35);
  z-index: 20;
}
.nf-card-title {
  font-size: 0.78rem;
  font-weight: 600;
  color: #ccc;
  padding: 10px 10px 8px;
  line-height: 1.35;
  height: 2.6rem;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
/* Make the Open button inside cards look like a slim bar */
.nf-card .stButton > button {
  width: 100% !important;
  border-radius: 0 !important;
  font-size: 0.72rem !important;
  padding: 8px 8px !important;
  letter-spacing: 0.08em !important;
  background: #e50914 !important;
  font-weight: 700 !important;
}
.nf-card .stButton > button:hover {
  background: #ff0a16 !important;
}
.nf-card-stars {
  text-align:center;
  font-size:0.7rem;
  color:#f5c518;
  padding:2px 8px;
  letter-spacing:2px;
}
.nf-card-placeholder {
  height: 220px;
  background: linear-gradient(135deg,#181818,#111);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-size: 2.5rem;
}
/* Stagger animation for cards */
.nf-card:nth-child(1) { animation-delay:0s; }
.nf-card:nth-child(2) { animation-delay:0.05s; }
.nf-card:nth-child(3) { animation-delay:0.1s; }
.nf-card:nth-child(4) { animation-delay:0.15s; }
.nf-card:nth-child(5) { animation-delay:0.2s; }
.nf-card:nth-child(6) { animation-delay:0.25s; }

/* ══════════════════════════════════
   HERO BANNER — CINEMATIC
══════════════════════════════════ */
.nf-hero {
  position: relative;
  width: 100%;
  height: 520px;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 32px;
  animation: scaleIn 0.7s ease both;
  box-shadow: 0 30px 80px rgba(0,0,0,0.5);
}
.nf-hero-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.nf-hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to right,
    rgba(0,0,0,0.92) 0%,
    rgba(0,0,0,0.6) 40%,
    rgba(0,0,0,0.1) 70%,
    rgba(0,0,0,0.4) 100%
  );
}
.nf-hero-overlay::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 160px;
  background: linear-gradient(transparent, #0f0f0f);
}
.nf-hero-content {
  position: absolute;
  bottom: 48px;
  left: 48px;
  max-width: 500px;
  z-index: 2;
}
.nf-hero-label {
  display: inline-block;
  background: #e50914;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  padding: 4px 12px;
  border-radius: 2px;
  margin-bottom: 14px;
}
.nf-hero-title {
  font-family: 'Bebas Neue',sans-serif;
  font-size: 3.6rem;
  letter-spacing: 0.05em;
  color: #fff;
  line-height: 1.05;
  margin-bottom: 16px;
  text-shadow: 0 6px 30px rgba(0,0,0,0.9);
}
.nf-hero-desc {
  font-size: 0.9rem;
  color: #bbb;
  line-height: 1.6;
  margin-bottom: 20px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.nf-hero-meta {
  display: flex;
  gap: 16px;
  align-items: center;
}
.nf-hero-badge {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 4px;
  padding: 6px 14px;
  font-size: 0.78rem;
  font-weight: 600;
  color: #ccc;
}
.nf-hero-badge.red {
  background: rgba(229,9,20,0.15);
  border-color: rgba(229,9,20,0.3);
  color: #e50914;
}

/* (category pills removed — using top nav only) */

/* ══════════════════════════════════
   DETAILS PAGE — CINEMATIC
══════════════════════════════════ */
.nf-back-btn .stButton > button {
  background: transparent !important;
  border: 1px solid #333 !important;
  color: #aaa !important;
  font-size: 0.78rem !important;
  border-radius: 4px !important;
  padding: 8px 20px !important;
}
.nf-back-btn .stButton > button:hover {
  background: #111 !important;
  border-color: #555 !important;
  color: #fff !important;
  transform: none !important;
  box-shadow: none !important;
}
.nf-details-info {
  background: rgba(14,14,14,0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 36px 40px;
  animation: fadeUp 0.5s ease 0.1s both;
}
.nf-movie-title {
  font-family:'Bebas Neue',sans-serif;
  font-size: 3.4rem;
  letter-spacing: 0.03em;
  color: #fff;
  line-height: 1;
  margin-bottom: 16px;
}
.nf-tags { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:20px; }
.nf-tag {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 4px;
  padding: 5px 14px;
  font-size: 0.76rem;
  font-weight: 600;
  color: #999;
}
.nf-tag.red {
  background: rgba(229,9,20,0.12);
  border-color: rgba(229,9,20,0.25);
  color: #e50914;
}
.nf-overview {
  color: #999;
  font-size: 0.95rem;
  line-height: 1.8;
  border-top: 1px solid rgba(255,255,255,0.06);
  padding-top: 20px;
  margin-top: 8px;
}
.nf-backdrop {
  border-radius: 8px;
  width: 100%;
  max-height: 420px;
  object-fit: cover;
  margin-bottom: 28px;
  display: block;
  mask-image: linear-gradient(to bottom, black 50%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, black 50%, transparent 100%);
  animation: fadeIn 0.6s ease;
}
.nf-poster-wrap {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 8px 40px rgba(0,0,0,0.6);
}

/* ══════════════════════════════════
   STAR RATING
══════════════════════════════════ */
.nf-rating-box {
  background: #0a0a0a;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
  padding: 20px;
  margin-top: 16px;
  text-align: center;
}
.nf-rating-label {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #444;
  margin-bottom: 8px;
}
.nf-rating-done {
  background: rgba(229,9,20,0.08);
  border: 1px solid rgba(229,9,20,0.2);
  border-radius: 6px;
  padding: 10px 14px;
  color: #e50914;
  font-size: 0.82rem;
  font-weight: 700;
  margin-top: 10px;
  text-align: center;
}

/* ══════════════════════════════════
   AUTH PAGE
══════════════════════════════════ */
.nf-auth-card {
  background: rgba(14,14,14,0.85);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 48px 44px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 24px 80px rgba(0,0,0,0.7);
  animation: fadeUp 0.4s ease;
}
.nf-auth-logo {
  font-family:'Bebas Neue',sans-serif;
  font-size: 2.8rem;
  letter-spacing: 0.2em;
  color: #e50914;
  text-align: center;
  display: block;
  margin-bottom: 4px;
}
.nf-auth-logo span { color:#fff; }
.nf-auth-heading {
  font-family:'Bebas Neue',sans-serif;
  font-size: 2.2rem;
  text-align: center;
  letter-spacing: 0.06em;
  color: #fff;
  margin: 16px 0 6px;
}
.nf-auth-sub {
  text-align: center;
  color: #555;
  font-size: 0.84rem;
  margin-bottom: 36px;
}

/* ══════════════════════════════════
   INFO / ERROR / SUCCESS
══════════════════════════════════ */
.nf-info {
  background: #111;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 6px;
  padding: 14px 18px;
  color: #888;
  font-size: 0.86rem;
}
.nf-error {
  background: rgba(229,9,20,0.06);
  border: 1px solid rgba(229,9,20,0.2);
  border-radius: 6px;
  padding: 14px 18px;
  color: #ff6b6b;
  font-size: 0.86rem;
}
.nf-success {
  background: rgba(34,197,94,0.06);
  border: 1px solid rgba(34,197,94,0.2);
  border-radius: 6px;
  padding: 10px 16px;
  color: #4ade80;
  font-size: 0.82rem;
  margin-bottom: 14px;
}

/* ══════════════════════════════════
   CHATBOT PANEL
══════════════════════════════════ */
.nf-chat-panel {
  background: rgba(14,14,14,0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 24px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.7);
  animation: fadeUp 0.4s ease;
}
.nf-chat-header {
  background: linear-gradient(90deg, #e50914, #b20710);
  padding: 16px 22px;
  display: flex;
  align-items: center;
  gap: 14px;
}
.nf-chat-avatar {
  width: 40px; height: 40px;
  background: rgba(255,255,255,0.15);
  border-radius: 50%;
  display: flex; align-items:center; justify-content:center;
  font-size: 1.1rem;
  flex-shrink: 0;
}
.nf-chat-name {
  font-family:'Bebas Neue',sans-serif;
  font-size: 1.15rem;
  letter-spacing:0.1em;
  color:#fff;
  line-height:1;
}
.nf-chat-status {
  font-size:0.62rem;
  color:rgba(255,255,255,0.7);
  letter-spacing:0.06em;
  margin-top:3px;
}

/* Chat FAB button — scoped to .chat-fab-wrap only */
.chat-fab-wrap .stButton > button {
  border-radius: 50% !important;
  width: 54px !important;
  height: 54px !important;
  padding: 0 !important;
  font-size: 1.2rem !important;
  min-height: 54px !important;
  background: linear-gradient(135deg, #e50914, #b20710) !important;
  box-shadow: 0 6px 24px rgba(229,9,20,0.4) !important;
  animation: pulseRed 2.5s ease-in-out infinite !important;
  transition: all 0.3s ease !important;
}
.chat-fab-wrap .stButton > button:hover {
  transform: scale(1.12) !important;
  background: linear-gradient(135deg, #ff1a27, #e50914) !important;
  box-shadow: 0 8px 32px rgba(229,9,20,0.5) !important;
}

/* ── User badge in header ── */
.nf-user-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: #111;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 8px 16px 8px 10px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #ccc;
}
.nf-user-badge-avatar {
  width: 28px; height: 28px;
  background: linear-gradient(135deg,#e50914,#b20710);
  border-radius: 6px;
  display: inline-flex;
  align-items:center; justify-content:center;
  color: white;
  font-size: 0.7rem;
  font-weight: 800;
}

/* ── Divider ── */
.nf-divider {
  height: 1px;
  background: rgba(255,255,255,0.06);
  margin: 36px 0;
}

/* ── Expander ── */
[data-testid="stExpander"] {
  background: #111 !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: 6px !important;
}

/* ══════════════════════════════════
   TOP NAV BAR — WORKING BUTTONS
══════════════════════════════════ */

/* ══════════════════════════════════
   HERO CTA BUTTONS
══════════════════════════════════ */
.nf-hero-cta-wrap .stButton > button {
  background: rgba(255,255,255,0.08) !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;
  border: 1px solid rgba(255,255,255,0.15) !important;
  color: #fff !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  padding: 12px 24px !important;
  border-radius: 10px !important;
  transition: all 0.3s ease !important;
  letter-spacing: 0.02em !important;
}
.nf-hero-cta-wrap .stButton > button:hover {
  background: rgba(255,255,255,0.14) !important;
  border-color: rgba(255,255,255,0.3) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3) !important;
}
.nf-hero-cta-wrap.primary .stButton > button {
  background: #e50914 !important;
  border: none !important;
  font-weight: 700 !important;
  letter-spacing: 0.04em !important;
}
.nf-hero-cta-wrap.primary .stButton > button:hover {
  background: #ff1a27 !important;
  box-shadow: 0 8px 30px rgba(229,9,20,0.35) !important;
  transform: translateY(-2px) !important;
}

/* ══════════════════════════════════
   LANDING TAGLINE
══════════════════════════════════ */
.nf-landing-tagline {
  text-align: center;
  padding: 36px 0 8px;
  animation: fadeUp 0.5s ease both;
}
.nf-landing-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2.6rem;
  letter-spacing: 0.08em;
  color: #fff;
  line-height: 1.15;
  margin-bottom: 10px;
}
.nf-landing-sub {
  font-size: 0.88rem;
  color: #555;
  font-weight: 400;
  letter-spacing: 0.02em;
}

/* ══════════════════════════════════
   GRADIENT SEPARATOR
══════════════════════════════════ */
.nf-gradient-line {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(229,9,20,0.3), transparent);
  margin-bottom: 20px;
}

/* ══════════════════════════════════
   RATING BOX GLASS
══════════════════════════════════ */
.nf-rating-box {
  background: rgba(14,14,14,0.8) !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;
}

/* ══════════════════════════════════
   CARD BUTTON POLISH
══════════════════════════════════ */
.nf-card .stButton > button {
  background: linear-gradient(135deg, #e50914, #b20710) !important;
  border-radius: 0 0 8px 8px !important;
}


</style>
""", unsafe_allow_html=True)

# =============================
# STATE + ROUTING
# =============================
defaults = {
    "view": "home",
    "selected_tmdb_id": None,
    "auth_mode": "login",
    "logged_in": False,
    "username": "",
    "token": "",
    "ratings": {},
    "auth_error": "",
    "show_auth": False,
    "auth_debug": "",
    "chat_open": False,
    "chat_history": [],
    "chat_input_key": 0,
    "active_category": "trending",
    "grid_cols": 6,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

qp_view = st.query_params.get("view")
qp_id   = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass


# =============================
# TOKEN VALIDATION ON LOAD
# =============================
def _verify_token():
    token = st.session_state.get("token", "")
    if not token or not st.session_state.get("logged_in"):
        return
    try:
        r = requests.get(
            f"{API_BASE}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if r.status_code == 401:
            st.session_state.logged_in = False
            st.session_state.username  = ""
            st.session_state.token     = ""
    except Exception:
        pass

_verify_token()


def goto_home():
    st.session_state.view = "home"
    st.session_state.selected_tmdb_id = None
    st.query_params["view"] = "home"
    try:
        del st.query_params["id"]
    except Exception:
        pass


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))


# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=30)
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


def auth_headers() -> dict:
    token = st.session_state.get("token", "")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def api_post(path: str, json_body: dict | None = None, data: dict | None = None, use_auth: bool = False):
    headers = auth_headers() if use_auth else {}
    try:
        r = requests.post(f"{API_BASE}{path}", json=json_body, data=data, headers=headers, timeout=25)
        if r.status_code >= 400:
            try:
                body = r.json()
                detail = body.get("detail", body)
            except Exception:
                detail = r.text[:300]
            return None, f"[HTTP {r.status_code}] {detail}"
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, f"Cannot reach server at {API_BASE}. Is the backend running?"
    except requests.exceptions.Timeout:
        return None, "Request timed out. Backend may be starting up (Render cold start)."
    except Exception as e:
        return None, f"Request failed: {type(e).__name__}: {e}"


def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    keyword_l = keyword.strip().lower()
    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append({
                "tmdb_id": int(tmdb_id),
                "title": title,
                "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                "release_date": m.get("release_date", ""),
            })
    elif isinstance(data, list):
        raw_items = []
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append({
                "tmdb_id": int(tmdb_id),
                "title": title,
                "poster_url": poster_url,
                "release_date": m.get("release_date", ""),
            })
    else:
        return [], []

    matched = [x for x in raw_items if keyword_l in x["title"].lower()]
    final_list = matched if matched else raw_items

    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    cards = [{"tmdb_id": x["tmdb_id"], "title": x["title"], "poster_url": x["poster_url"]}
             for x in final_list[:limit]]
    return suggestions, cards


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append({
                "tmdb_id": tmdb["tmdb_id"],
                "title": tmdb.get("title") or x.get("title") or "Untitled",
                "poster_url": tmdb.get("poster_url"),
            })
    return cards


# =============================
# CHATBOT — GROQ + TMDB
# =============================

CHAT_SYSTEM_PROMPT = """You are CineBot, a friendly movie recommendation assistant for CineVault.
Your job is to understand the user's mood, feelings, or preferences through conversation and suggest great movies.

Rules:
- Be warm, conversational, and concise (2-4 sentences max per reply)
- Always end your message with 3-5 specific movie recommendations
- Format recommendations EXACTLY like this at the end of every reply:
  MOVIES: ["Movie Title 1", "Movie Title 2", "Movie Title 3"]
- Use real, well-known movie titles that actually exist
- Match movies to the user's mood/request precisely
- If the user hasn't given enough info, ask one focused question about their mood or preference
- Never include MOVIES: if you're still asking a clarifying question"""


def groq_chat(messages: list) -> str:
    if not GROQ_API_KEY:
        return "MOVIES: []"
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": CHAT_SYSTEM_PROMPT}] + messages,
                "temperature": 0.8,
                "max_tokens": 400,
            },
            timeout=20,
        )
        if r.status_code != 200:
            return f"Sorry, I ran into an issue (HTTP {r.status_code}). Try again!"
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Sorry, I couldn't connect to the AI ({type(e).__name__}). Check your GROQ_API_KEY."


def extract_movie_titles(text: str) -> list[str]:
    match = re.search(r'MOVIES:\s*(\[.*?\])', text, re.DOTALL)
    if not match:
        return []
    try:
        titles = json.loads(match.group(1))
        return [t.strip() for t in titles if isinstance(t, str) and t.strip()]
    except Exception:
        return []


def clean_bot_text(text: str) -> str:
    return re.sub(r'MOVIES:\s*\[.*?\]', '', text, flags=re.DOTALL).strip()


def fetch_chat_movie_cards(titles: list[str]) -> list[dict]:
    cards = []
    for title in titles:
        try:
            r = requests.get(
                f"{API_BASE}/tmdb/search",
                params={"query": title, "page": 1},
                timeout=10,
            )
            if r.status_code == 200:
                results = r.json().get("results", [])
                if results:
                    m = results[0]
                    poster_path = m.get("poster_path")
                    cards.append({
                        "tmdb_id": int(m["id"]),
                        "title": m.get("title") or title,
                        "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    })
        except Exception:
            pass
    return cards


def render_chatbot():
    """Floating chatbot panel."""
    _, fab_col = st.columns([9, 1])
    with fab_col:
        st.markdown("<div class='chat-fab-wrap'>", unsafe_allow_html=True)
        fab_icon = "✕" if st.session_state.chat_open else "💬"
        if st.button(fab_icon, key="chat_fab", help="CineBot — AI Movie Recommendations"):
            st.session_state.chat_open = not st.session_state.chat_open
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.chat_open:
        return

    # Chat panel
    st.markdown("""
    <div class='nf-chat-panel'>
      <div class='nf-chat-header'>
        <div class='nf-chat-avatar'>🎬</div>
        <div>
          <div class='nf-chat-name'>CINEBOT</div>
          <div class='nf-chat-status'>● Online · Powered by Llama 3</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not GROQ_API_KEY:
        st.markdown(
            f"<div class='nf-error'>⚠️ GROQ_API_KEY not set. Add <code>GROQ_API_KEY=your_key</code> to your .env and restart.</div>",
            unsafe_allow_html=True,
        )
        return

    # Greeting
    if not st.session_state.chat_history:
        st.markdown("""
        <div style='padding:12px 0 20px;animation:fadeUp 0.4s ease;'>
          <div style='
            display:inline-block;
            background:#111;
            border:1px solid rgba(255,255,255,0.06);
            border-radius:2px 16px 16px 16px;
            padding:20px 24px;
            max-width:85%;
            color:#888;
            font-size:0.9rem;
            line-height:1.7;
          '>
            👋 Hey there! I'm <strong style='color:#fff;'>CineBot</strong>.<br>
            Tell me your mood, a genre, or a vibe — I'll find the perfect movie for you.<br>
            <span style='color:#444;font-size:0.76rem;font-style:italic;'>Try: "something cozy for a rainy night" or "mind-bending sci-fi"</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Render conversation
    for msg in st.session_state.chat_history:
        role  = msg["role"]
        text  = msg["content"]
        cards = msg.get("cards", [])
        msg_idx = msg.get("_idx", 0)

        if role == "user":
            st.markdown(f"""
            <div style='display:flex;justify-content:flex-end;margin:12px 0;animation:fadeUp 0.3s ease;'>
              <div style='
                background:rgba(229,9,20,0.1);
                border:1px solid rgba(229,9,20,0.2);
                border-radius:16px 16px 2px 16px;
                padding:14px 18px;
                max-width:75%;
                color:#eee;
                font-size:0.86rem;
                line-height:1.6;
                word-break:break-word;
              '>{text}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='display:flex;align-items:flex-start;gap:12px;margin:12px 0;animation:fadeUp 0.3s ease;'>
              <div style='
                width:30px;height:30px;
                background:#e50914;
                border-radius:50%;
                display:flex;align-items:center;justify-content:center;
                font-size:0.7rem;
                flex-shrink:0;
                margin-top:2px;
              '>🎬</div>
              <div style='
                background:#111;
                border:1px solid rgba(255,255,255,0.06);
                border-radius:2px 16px 16px 16px;
                padding:14px 18px;
                max-width:82%;
                color:#999;
                font-size:0.86rem;
                line-height:1.7;
                word-break:break-word;
              '>{text}</div>
            </div>
            """, unsafe_allow_html=True)

            if cards:
                st.markdown("<div style='padding-left:42px;margin:-4px 0 8px;'>", unsafe_allow_html=True)
                card_cols = st.columns(min(len(cards), 5))
                for ci, card in enumerate(cards[:5]):
                    with card_cols[ci]:
                        st.markdown("<div style='background:#111;border:1px solid rgba(255,255,255,0.04);border-radius:6px;overflow:hidden;'>", unsafe_allow_html=True)
                        if card.get("poster_url"):
                            st.image(card["poster_url"], use_column_width=True)
                        else:
                            st.markdown("<div style='height:80px;background:#181818;display:flex;align-items:center;justify-content:center;color:#333;font-size:1.2rem;'>🎬</div>", unsafe_allow_html=True)
                        if st.button("Open", key=f"cc_{msg_idx}_{ci}_{card['tmdb_id']}", use_container_width=True):
                            st.session_state.chat_open = False
                            goto_details(card["tmdb_id"])
                            st.rerun()
                        st.markdown(f"<div style='font-size:0.68rem;color:#777;padding:4px 8px 6px;height:2rem;overflow:hidden;'>{card['title']}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # Divider
    st.markdown("<div style='height:1px;background:rgba(255,255,255,0.04);margin:16px 0 14px;'></div>", unsafe_allow_html=True)

    # Input
    inp_col, send_col, clear_col = st.columns([6, 1, 1])
    with inp_col:
        user_input = st.text_input(
            "msg",
            placeholder="What mood are you in tonight?",
            key=f"chat_input_{st.session_state.chat_input_key}",
            label_visibility="collapsed",
        )
    with send_col:
        send = st.button("Send", key="chat_send", use_container_width=True)
    with clear_col:
        if st.button("New", key="chat_clear", use_container_width=True):
            st.session_state.chat_history   = []
            st.session_state.chat_input_key += 1
            st.rerun()

    if send and user_input.strip():
        user_text = user_input.strip()
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_text,
            "cards": [],
            "_idx": len(st.session_state.chat_history),
        })
        groq_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.chat_history
        ]
        with st.spinner(""):
            raw_response = groq_chat(groq_messages)
        titles    = extract_movie_titles(raw_response)
        clean_txt = clean_bot_text(raw_response)
        cards     = fetch_chat_movie_cards(titles) if titles else []
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": clean_txt,
            "cards": cards,
            "_idx": len(st.session_state.chat_history),
        })
        st.session_state.chat_input_key += 1
        st.rerun()

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)


# =============================
# STAR RATING COMPONENT
# =============================
def star_rating_widget(tmdb_id: int, title: str):
    current = st.session_state.ratings.get(tmdb_id, 0)
    labels = {0: "Rate this movie", 1: "Terrible", 2: "Meh", 3: "Good", 4: "Great", 5: "Masterpiece!"}

    st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
    st.markdown("<div class='nf-rating-label'>Your Rating</div>", unsafe_allow_html=True)

    cols = st.columns([1, 1, 1, 1, 1, 2])
    for i, col in enumerate(cols[:5], start=1):
        with col:
            star_label = "★" if i <= current else "☆"
            if st.button(
                star_label,
                key=f"star_{tmdb_id}_{i}",
                help=f"{i} star{'s' if i>1 else ''}",
            ):
                if not st.session_state.logged_in:
                    st.session_state.show_auth  = True
                    st.session_state.auth_error = "Please sign in to rate movies."
                    st.rerun()
                st.session_state.ratings[tmdb_id] = i
                st.rerun()

    if current > 0:
        st.markdown(
            f"<div class='nf-rating-done'>⭐ You rated this {current}/5 — {labels[current]}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='nf-rating-label'>{labels[current]}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


# =============================
# POSTER GRID — NETFLIX STYLE
# =============================
def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.markdown("<div class='nf-info'>No movies to show.</div>", unsafe_allow_html=True)
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols, gap="small")
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1
            tmdb_id = m.get("tmdb_id")
            title   = m.get("title", "Untitled")
            poster  = m.get("poster_url")
            rating  = st.session_state.ratings.get(tmdb_id, 0)

            with colset[c]:
                st.markdown("<div class='nf-card'>", unsafe_allow_html=True)
                if poster:
                    st.image(poster, use_column_width=True)
                else:
                    st.markdown(
                        "<div class='nf-card-placeholder'>🎬</div>",
                        unsafe_allow_html=True,
                    )
                if rating > 0:
                    stars_display = "★" * rating + "☆" * (5 - rating)
                    st.markdown(
                        f"<div class='nf-card-stars'>{stars_display}</div>",
                        unsafe_allow_html=True,
                    )
                if st.button("▶ Play", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}", use_container_width=True):
                    if tmdb_id:
                        goto_details(tmdb_id)
                        st.rerun()
                st.markdown(
                    f"<div class='nf-card-title'>{title}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)


# =============================
# AUTH MODAL
# =============================
def render_auth():
    st.markdown("<br>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1.4, 1])
    with center:
        mode = st.session_state.auth_mode

        st.markdown(f"""
        <div class='nf-auth-card'>
          <span class='nf-auth-logo'>CINE<span>VAULT</span></span>
          <div class='nf-auth-heading'>{'Welcome Back' if mode=='login' else 'Join CineVault'}</div>
          <div class='nf-auth-sub'>{'Sign in to rate and track your movies' if mode=='login' else 'Create a free account'}</div>
        </div>""", unsafe_allow_html=True)

        if st.session_state.auth_error:
            st.markdown(
                f"<div class='nf-error'>{st.session_state.auth_error}</div>",
                unsafe_allow_html=True,
            )
            if st.session_state.get("auth_debug"):
                with st.expander("🔍 Debug — raw server response"):
                    st.code(st.session_state.auth_debug, language="text")
            st.markdown("<br>", unsafe_allow_html=True)

        # Backend connectivity check
        try:
            _hc = requests.get(f"{API_BASE}/health", timeout=6)
            if _hc.status_code == 200:
                st.markdown(
                    "<div class='nf-success'>✅ Server connected</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='nf-info' style='margin-bottom:12px;'>⚠️ Server responded with HTTP {_hc.status_code}</div>",
                    unsafe_allow_html=True,
                )
        except requests.exceptions.ConnectionError:
            st.markdown(
                f"<div class='nf-error' style='margin-bottom:12px;'>🔴 Cannot reach backend at <code>{API_BASE}</code>. Auth will not work until the server is running.</div>",
                unsafe_allow_html=True,
            )
        except Exception as _e:
            st.markdown(
                f"<div class='nf-info' style='margin-bottom:12px;'>⚠️ Server check failed: {_e}</div>",
                unsafe_allow_html=True,
            )

        username = st.text_input("Username", key="auth_username", placeholder="Enter username")
        password = st.text_input("Password", type="password", key="auth_password", placeholder="Enter password")

        if mode == "signup":
            password2 = st.text_input("Confirm Password", type="password", key="auth_password2", placeholder="Repeat password")
            email     = st.text_input("Email (optional)", key="auth_email", placeholder="you@example.com")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "Sign In" if mode == "login" else "Create Account",
                use_container_width=True,
            ):
                st.session_state.auth_error = ""
                u = username.strip()
                p = password.strip()

                if not u or not p:
                    st.session_state.auth_error = "Please fill in all fields."
                    st.rerun()

                elif mode == "login":
                    resp, err = api_post(
                        "/auth/login",
                        data={"username": u, "password": p},
                    )
                    if err:
                        st.session_state.auth_error = f"Login failed: {err}"
                        st.session_state.auth_debug = err
                    else:
                        st.session_state.token      = resp["access_token"]
                        st.session_state.username   = resp["username"]
                        st.session_state.logged_in  = True
                        st.session_state.show_auth  = False
                        st.session_state.auth_error = ""
                    st.rerun()

                else:
                    p2    = st.session_state.get("auth_password2", "").strip()
                    email = st.session_state.get("auth_email", "").strip()

                    if not p2:
                        st.session_state.auth_error = "Please confirm your password."
                        st.rerun()
                    elif p != p2:
                        st.session_state.auth_error = "Passwords do not match."
                        st.rerun()
                    else:
                        resp, err = api_post(
                            "/auth/register",
                            json_body={"username": u, "password": p, "email": email or None},
                        )
                        if err:
                            st.session_state.auth_error = f"Registration failed: {err}"
                            st.session_state.auth_debug = err
                            st.rerun()
                        else:
                            login_resp, login_err = api_post(
                                "/auth/login",
                                data={"username": u, "password": p},
                            )
                            if login_err:
                                st.session_state.auth_error = "Registered! Please sign in manually."
                                st.session_state.auth_mode  = "login"
                            else:
                                st.session_state.token      = login_resp["access_token"]
                                st.session_state.username   = login_resp["username"]
                                st.session_state.logged_in  = True
                                st.session_state.show_auth  = False
                                st.session_state.auth_error = ""
                            st.rerun()

        with col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_auth  = False
                st.session_state.auth_error = ""
                st.rerun()

        if mode == "login":
            st.markdown(
                "<div style='text-align:center;margin-top:18px;color:#555;font-size:0.85rem;'>New to CineVault?</div>",
                unsafe_allow_html=True,
            )
            if st.button("Create an account →", use_container_width=True):
                st.session_state.auth_mode  = "signup"
                st.session_state.auth_error = ""
                st.rerun()
        else:
            st.markdown(
                "<div style='text-align:center;margin-top:18px;color:#555;font-size:0.85rem;'>Already have an account?</div>",
                unsafe_allow_html=True,
            )
            if st.button("Sign in →", use_container_width=True):
                st.session_state.auth_mode  = "login"
                st.session_state.auth_error = ""
                st.rerun()


grid_cols = 6  # fixed grid columns


# =============================
# AUTH PAGE OVERRIDE
# =============================
if st.session_state.show_auth:
    render_auth()
    st.stop()


# =============================
# CHATBOT (floating)
# =============================
render_chatbot()

# ═══════════════════════════════════════════════════════════
#  TOP NAVIGATION BAR
# ═══════════════════════════════════════════════════════════
_active = st.session_state.active_category

# Build the right-side HTML
if st.session_state.logged_in:
    _ini = st.session_state.username[:2].upper()
    _right_html = f"""<div class='nav-user'>
      <span class='nav-user-avatar'>{_ini}</span> {st.session_state.username}
    </div>"""
else:
    _right_html = ""

st.markdown(f"""
<div class='cv-navbar'>
  <div class='cv-logo'>
    <span class='cv-logo-icon'>🎬</span>
    <span class='cv-logo-text'>CINE<span>VAULT</span></span>
  </div>
  {_right_html}
</div>
<div class='nf-gradient-line'></div>""", unsafe_allow_html=True)

# Navigation buttons row
_nav_items = [
    ("trending", "Trending"),
    ("popular", "Popular"),
    ("top_rated", "Top Rated"),
    ("now_playing", "Now Playing"),
    ("upcoming", "Upcoming"),
]

_ncols = st.columns([1]*len(_nav_items) + [2])
for _col, (_ck, _cl) in zip(_ncols[:len(_nav_items)], _nav_items):
    with _col:
        _css = "nav-link-active" if _active == _ck else "nav-link"
        st.markdown(f"<div class='{_css}'>", unsafe_allow_html=True)
        if st.button(_cl, key=f"nav_{_ck}", use_container_width=True):
            st.session_state.active_category = _ck
            goto_home()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Right-most column: Sign In / Sign Out
with _ncols[-1]:
    _rc1, _rc2 = st.columns([3, 2])
    with _rc2:
        if st.session_state.logged_in:
            st.markdown("<div class='nav-signout'>", unsafe_allow_html=True)
            if st.button("Sign Out", key="nav_signout"):
                api_post("/auth/logout", use_auth=True)
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.token = ""
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='nav-signin'>", unsafe_allow_html=True)
            if st.button("Sign In", key="nav_signin"):
                st.session_state.show_auth = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)


# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":

    # Landing tagline
    st.markdown("""
    <div class='nf-landing-tagline'>
      <div class='nf-landing-title'>Discover Your Next Favorite Film</div>
      <div class='nf-landing-sub'>Search by title, or browse categories above</div>
    </div>
    """, unsafe_allow_html=True)

    # Search bar
    st.markdown("<div class='nf-search-area'>", unsafe_allow_html=True)
    typed = st.text_input(
        "search",
        placeholder="🔍  Search movies — Inception, Parasite, The Dark Knight...",
        label_visibility="collapsed",
        key="home_search",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if typed.strip():
        if len(typed.strip()) < 2:
            st.markdown("<div class='nf-info'>Type at least 2 characters.</div>", unsafe_allow_html=True)
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})
            if err or data is None:
                st.markdown(f"<div class='nf-error'>Search failed: {err}</div>", unsafe_allow_html=True)
            else:
                suggestions, cards = parse_tmdb_search_to_cards(data, typed.strip(), limit=24)
                if suggestions:
                    labels = ["— Pick a movie —"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Suggestions", labels, index=0, label_visibility="collapsed")
                    if selected != "— Pick a movie —":
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                        st.rerun()
                else:
                    st.markdown("<div class='nf-info'>No suggestions found.</div>", unsafe_allow_html=True)

                st.markdown(f"<div class='nf-section-title'>Results for \"{typed}\"</div>", unsafe_allow_html=True)
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")
        st.stop()

    # Load movies (category is set by top nav)
    home_category = st.session_state.active_category
    home_cards, err = api_get_json("/home", params={"category": home_category, "limit": 24})
    if err or not home_cards:
        st.markdown(f"<div class='nf-error'>Home feed failed: {err or 'Unknown error'}</div>", unsafe_allow_html=True)
        st.stop()

    # ── HERO BANNER — First movie featured large ──
    hero = home_cards[0] if home_cards else None
    if hero:
        hero_id = hero.get("tmdb_id")
        hero_detail = None
        if hero_id:
            hero_detail, _ = api_get_json(f"/movie/id/{hero_id}")

        backdrop_url = ""
        overview = ""
        vote = ""
        genres_str = ""
        if hero_detail:
            backdrop_url = hero_detail.get("backdrop_url", "")
            overview = hero_detail.get("overview", "")
            vote = hero_detail.get("vote_average", "")
            genres_list = hero_detail.get("genres", [])
            genres_str = " · ".join([g["name"] for g in genres_list[:3]])

        hero_title = hero.get("title", "")
        hero_poster = hero.get("poster_url", "")
        hero_img = backdrop_url or hero_poster or ""

        if hero_img:
            st.markdown(f"""
            <div class='nf-hero'>
              <img src='{hero_img}' class='nf-hero-img' alt='{hero_title}'/>
              <div class='nf-hero-overlay'></div>
              <div class='nf-hero-content'>
                <div class='nf-hero-label'>Featured Today</div>
                <div class='nf-hero-title'>{hero_title}</div>
                {"<div class='nf-hero-desc'>" + overview + "</div>" if overview else ""}
                <div class='nf-hero-meta'>
                  {"<div class='nf-hero-badge red'>⭐ " + f"{vote:.1f}" + "</div>" if vote else ""}
                  {"<div class='nf-hero-badge'>" + genres_str + "</div>" if genres_str else ""}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Hero CTA buttons
            _cta1, _cta2, _ = st.columns([1.2, 1.2, 5])
            with _cta1:
                st.markdown("<div class='nf-hero-cta-wrap primary'>", unsafe_allow_html=True)
                if st.button("▶  More Info", key="hero_more_info", use_container_width=True):
                    goto_details(hero_id)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with _cta2:
                st.markdown("<div class='nf-hero-cta-wrap'>", unsafe_allow_html=True)
                if st.button("💬 Try CineBot", key="hero_cinebot", use_container_width=True):
                    st.session_state.chat_open = True
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # Section header
    cat_display = home_category.replace("_", " ").title()
    cat_icon = {"trending": "🔥", "popular": "⚡", "top_rated": "🏆", "now_playing": "🎞", "upcoming": "🚀"}.get(home_category, "🎬")
    st.markdown(f"<div class='nf-section-title'>{cat_icon} {cat_display}</div>", unsafe_allow_html=True)

    # Grid (skip hero movie)
    grid_cards = home_cards[1:] if hero else home_cards
    poster_grid(grid_cards, cols=grid_cols, key_prefix="home_feed")


# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.markdown("<div class='nf-info'>No movie selected.</div>", unsafe_allow_html=True)
        if st.button("← Back to Home"):
            goto_home()
            st.rerun()
        st.stop()

    # Back button
    st.markdown("<div class='nf-back-btn'>", unsafe_allow_html=True)
    if st.button("← Back to Home", key="det_back"):
        goto_home()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Load details
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.markdown(f"<div class='nf-error'>Could not load details: {err or 'Unknown error'}</div>", unsafe_allow_html=True)
        st.stop()

    # Backdrop
    if data.get("backdrop_url"):
        st.markdown(f"<img src='{data['backdrop_url']}' class='nf-backdrop'/>", unsafe_allow_html=True)

    # Main layout
    left, right = st.columns([1, 2.8], gap="large")

    with left:
        st.markdown("<div class='nf-poster-wrap'>", unsafe_allow_html=True)
        if data.get("poster_url"):
            st.image(data["poster_url"], use_column_width=True)
        else:
            st.markdown(
                "<div style='height:400px;background:#111;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#333;font-size:3rem;'>🎬</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Star rating
        st.markdown("<div class='nf-rating-box'>", unsafe_allow_html=True)
        star_rating_widget(tmdb_id, data.get("title", ""))
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='nf-details-info'>", unsafe_allow_html=True)

        title   = data.get("title", "Untitled")
        release = (data.get("release_date") or "")[:4] or "—"
        genres  = data.get("genres", [])
        vote    = data.get("vote_average")

        st.markdown(f"<div class='nf-movie-title'>{title}</div>", unsafe_allow_html=True)

        # Tags
        tags_html = "<div class='nf-tags'>"
        tags_html += f"<span class='nf-tag red'>📅 {release}</span>"
        if vote:
            tags_html += f"<span class='nf-tag red'>⭐ {vote:.1f}</span>"
        for g in genres:
            tags_html += f"<span class='nf-tag'>{g['name']}</span>"
        tags_html += "</div>"
        st.markdown(tags_html, unsafe_allow_html=True)

        st.markdown(
            f"<div class='nf-overview'>{data.get('overview') or 'No overview available.'}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Recommendations
    st.markdown("<div class='nf-divider'></div>", unsafe_allow_html=True)

    query_title = (data.get("title") or "").strip()
    if query_title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": query_title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown("<div class='nf-section-title'>🔎 Similar Movies</div>", unsafe_allow_html=True)
            poster_grid(
                to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                cols=grid_cols,
                key_prefix="details_tfidf",
            )

            st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
            st.markdown("<div class='nf-section-title'>🎭 More Like This</div>", unsafe_allow_html=True)
            poster_grid(
                bundle.get("genre_recommendations", []),
                cols=grid_cols,
                key_prefix="details_genre",
            )
        else:
            st.markdown("<div class='nf-section-title'>🎭 More Like This</div>", unsafe_allow_html=True)
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(genre_only, cols=grid_cols, key_prefix="details_genre_fallback")
            else:
                st.markdown("<div class='nf-info'>No recommendations available right now.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='nf-info'>No title available for recommendations.</div>", unsafe_allow_html=True)
