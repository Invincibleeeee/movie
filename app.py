import requests
import streamlit as st
import os
import re
import json
from dotenv import load_dotenv
load_dotenv()   # loads .env file into os.environ
import time

# =============================
# CONFIG
# =============================
API_BASE = "http://127.0.0.1:8000"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")   # set in .env or system env

st.set_page_config(
    page_title="CineVault",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================
# THEME CSS
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --bg:        #080808;
  --bg2:       #101010;
  --bg3:       #181818;
  --bg4:       #222222;
  --red:       #e50914;
  --red2:      #ff1a1a;
  --red-dim:   rgba(229,9,20,0.12);
  --red-glow:  rgba(229,9,20,0.35);
  --gold:      #f5c518;
  --white:     #ffffff;
  --grey1:     #e5e5e5;
  --grey2:     #aaaaaa;
  --grey3:     #555555;
  --grey4:     #2a2a2a;
  --border:    rgba(255,255,255,0.07);
  --border-r:  rgba(229,9,20,0.45);
  --r:         8px;
  --r2:        14px;
}

/* ── Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
  background: var(--bg) !important;
  color: var(--white) !important;
  font-family: 'Inter', sans-serif !important;
}

/* ── Hide all Streamlit chrome ── */
#MainMenu, header[data-testid="stHeader"],
footer, [data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.viewerBadge_container__1QSob,
.styles_viewerBadge__1yB5_ { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
  padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 0 !important;
}
/* Remove sidebar resize handle shadow */
[data-testid="stSidebarResizeHandle"] { background: transparent !important; }

/* ── Main content padding ── */
.block-container {
  padding: 2rem 2.5rem 4rem !important;
  max-width: 1600px !important;
}

/* ── Headings ── */
h1, h2, h3 {
  font-family: 'Bebas Neue', sans-serif !important;
  letter-spacing: 0.05em !important;
  color: var(--white) !important;
}

/* ── Text inputs ── */
[data-testid="stTextInput"] input {
  background: var(--bg3) !important;
  color: var(--white) !important;
  border: 1.5px solid var(--grey4) !important;
  border-radius: var(--r) !important;
  padding: 0.7rem 1.1rem !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.95rem !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--red) !important;
  box-shadow: 0 0 0 3px var(--red-dim) !important;
  outline: none !important;
}
[data-testid="stTextInput"] label {
  color: var(--grey2) !important;
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
  background: var(--bg3) !important;
  color: var(--white) !important;
  border: 1.5px solid var(--grey4) !important;
  border-radius: var(--r) !important;
}
[data-testid="stSelectbox"] label {
  color: var(--grey2) !important;
  font-size: 0.78rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  font-weight: 600 !important;
}

/* ── Buttons — default red ── */
.stButton > button {
  background: var(--red) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--r) !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  padding: 0.55rem 1.2rem !important;
  transition: all 0.18s ease !important;
  cursor: pointer !important;
  white-space: nowrap !important;
}
.stButton > button:hover {
  background: var(--red2) !important;
  box-shadow: 0 4px 22px var(--red-glow) !important;
  transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Slider ── */
[data-testid="stSlider"] label {
  color: var(--grey2) !important;
  font-size: 0.78rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  font-weight: 600 !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
  background: var(--red) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

/* ── Images ── */
[data-testid="stImage"] img { border-radius: var(--r) !important; display: block; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--red); border-radius: 3px; }

/* ════════════════════════════════
   SIDEBAR CUSTOM LAYOUT
════════════════════════════════ */
.sb-wrap {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 0;
}
.sb-top {
  padding: 22px 20px 18px;
  border-bottom: 1px solid var(--border);
}
.sb-logo {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2rem;
  letter-spacing: 0.14em;
  color: var(--red);
  text-shadow: 0 0 30px var(--red-glow);
  line-height: 1;
  margin-bottom: 4px;
}
.sb-logo span { color: var(--white); }
.sb-tagline {
  color: var(--grey3);
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-weight: 500;
}
.sb-section-label {
  color: var(--grey3);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  padding: 18px 20px 8px;
}
.sb-user-card {
  margin: 12px 16px;
  background: var(--red-dim);
  border: 1px solid var(--border-r);
  border-radius: var(--r2);
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.sb-avatar {
  width: 36px; height: 36px;
  background: var(--red);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}
.sb-uname {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--white);
  line-height: 1.2;
}
.sb-urole {
  font-size: 0.7rem;
  color: var(--grey2);
}
.sb-stats {
  margin: 0 16px 12px;
  display: flex;
  gap: 8px;
}
.sb-stat-box {
  flex: 1;
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 8px 10px;
  text-align: center;
}
.sb-stat-num {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.4rem;
  color: var(--red);
  line-height: 1;
}
.sb-stat-label {
  font-size: 0.62rem;
  color: var(--grey3);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 2px;
}
.sb-guest-card {
  margin: 12px 16px;
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--r2);
  padding: 14px;
  text-align: center;
}
.sb-guest-icon {
  font-size: 2rem;
  margin-bottom: 6px;
}
.sb-guest-text {
  color: var(--grey2);
  font-size: 0.8rem;
  margin-bottom: 10px;
  line-height: 1.4;
}
.sb-divider {
  height: 1px;
  background: var(--border);
  margin: 4px 16px;
}
.sb-footer {
  margin-top: auto;
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  color: var(--grey3);
  font-size: 0.68rem;
  text-align: center;
  letter-spacing: 0.06em;
}

/* ════════════════════════════════
   TOP NAVBAR
════════════════════════════════ */
.cv-navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0 18px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 24px;
  gap: 16px;
}
.cv-navbar-brand {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2rem;
  letter-spacing: 0.14em;
  color: var(--red);
  text-shadow: 0 0 30px var(--red-glow);
  white-space: nowrap;
  flex-shrink: 0;
}
.cv-navbar-brand span { color: var(--white); }
.cv-navbar-search {
  flex: 1;
  max-width: 520px;
}
.cv-navbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.cv-user-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--red-dim);
  border: 1px solid var(--border-r);
  border-radius: 24px;
  padding: 6px 14px 6px 8px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--red);
}
.cv-user-badge-avatar {
  width: 24px; height: 24px;
  background: var(--red);
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
}

/* ════════════════════════════════
   SEARCH BAR
════════════════════════════════ */
.cv-search-wrap {
  position: relative;
  margin-bottom: 24px;
}
.cv-search-wrap [data-testid="stTextInput"] input {
  font-size: 1rem !important;
  padding: 0.85rem 1.2rem 0.85rem 3rem !important;
  border-radius: 40px !important;
  border: 1.5px solid var(--grey4) !important;
  background: var(--bg3) !important;
}
.cv-search-wrap [data-testid="stTextInput"] input:focus {
  border-color: var(--red) !important;
  box-shadow: 0 0 0 4px var(--red-dim) !important;
}
.cv-search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--grey3);
  font-size: 1rem;
  pointer-events: none;
  z-index: 10;
}

/* ════════════════════════════════
   SECTION HEADER
════════════════════════════════ */
.cv-section {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.5rem;
  letter-spacing: 0.08em;
  color: var(--white);
  margin: 0 0 16px 0;
  padding: 0;
}
.cv-section::before {
  content: '';
  display: block;
  width: 4px;
  height: 1.4em;
  background: var(--red);
  border-radius: 2px;
  flex-shrink: 0;
  box-shadow: 0 0 10px var(--red-glow);
}

/* Category pills */
.cv-cat-pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.cv-cat-pill {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 5px 14px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--grey2);
  cursor: pointer;
  letter-spacing: 0.04em;
  transition: all 0.15s;
  text-transform: capitalize;
}
.cv-cat-pill.active {
  background: var(--red) !important;
  border-color: var(--red) !important;
  color: white !important;
  box-shadow: 0 2px 12px var(--red-glow);
}

/* ════════════════════════════════
   MOVIE CARD
════════════════════════════════ */
.cv-card {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--r2);
  overflow: hidden;
  transition: transform 0.22s cubic-bezier(.34,1.56,.64,1),
              border-color 0.2s, box-shadow 0.2s;
  position: relative;
}
.cv-card:hover {
  transform: scale(1.04) translateY(-5px);
  border-color: var(--red);
  box-shadow: 0 16px 40px rgba(229,9,20,0.22);
  z-index: 10;
}
.cv-card-img-wrap {
  position: relative;
  overflow: hidden;
}
.cv-card-overlay {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 50%;
  background: linear-gradient(transparent, rgba(0,0,0,0.85));
  pointer-events: none;
}
.cv-card-title {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--grey1);
  padding: 8px 10px 10px;
  line-height: 1.35;
  height: 2.8rem;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.cv-card-stars {
  text-align: center;
  font-size: 0.68rem;
  color: var(--gold);
  padding: 0 10px 6px;
  letter-spacing: 1px;
}
/* Open button inside card */
.cv-card .stButton > button {
  width: 100% !important;
  border-radius: 0 !important;
  font-size: 0.72rem !important;
  padding: 0.38rem 0.5rem !important;
  letter-spacing: 0.1em !important;
  background: rgba(229,9,20,0.85) !important;
}
.cv-card .stButton > button:hover {
  background: var(--red) !important;
  border-radius: 0 !important;
}

/* ════════════════════════════════
   DETAILS PAGE
════════════════════════════════ */
.cv-back-btn .stButton > button {
  background: var(--bg3) !important;
  border: 1px solid var(--border) !important;
  color: var(--grey1) !important;
  font-size: 0.78rem !important;
  border-radius: 6px !important;
}
.cv-back-btn .stButton > button:hover {
  background: var(--bg4) !important;
  border-color: var(--grey3) !important;
  box-shadow: none !important;
  transform: none !important;
}
.cv-details-panel {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--r2);
  padding: 28px 32px;
}
.cv-movie-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2.6rem;
  letter-spacing: 0.06em;
  color: var(--white);
  line-height: 1.05;
  margin-bottom: 14px;
}
.cv-pills { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 18px; }
.cv-pill {
  background: var(--bg4);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--grey2);
  letter-spacing: 0.04em;
}
.cv-pill.red {
  background: var(--red-dim);
  border-color: var(--border-r);
  color: var(--red);
}
.cv-overview {
  color: var(--grey2);
  font-size: 0.95rem;
  line-height: 1.75;
  border-top: 1px solid var(--border);
  padding-top: 16px;
  margin-top: 4px;
}
.cv-backdrop {
  border-radius: var(--r2);
  width: 100%;
  max-height: 300px;
  object-fit: cover;
  margin-bottom: 20px;
  display: block;
}

/* ════════════════════════════════
   STAR RATING
════════════════════════════════ */
.cv-rating-wrap {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 14px;
  margin-top: 12px;
  text-align: center;
}
.cv-rating-label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--grey3);
  margin-bottom: 8px;
}
.cv-rating-done {
  background: var(--red-dim);
  border: 1px solid var(--border-r);
  border-radius: var(--r);
  padding: 8px 12px;
  color: var(--red);
  font-size: 0.82rem;
  font-weight: 600;
  margin-top: 8px;
  text-align: center;
}

/* ════════════════════════════════
   AUTH PAGE
════════════════════════════════ */
.cv-auth-page {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.cv-auth-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--r2);
  padding: 44px 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 24px 80px rgba(0,0,0,0.7);
}
.cv-auth-logo {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2.2rem;
  letter-spacing: 0.14em;
  color: var(--red);
  text-shadow: 0 0 30px var(--red-glow);
  text-align: center;
  display: block;
  margin-bottom: 4px;
}
.cv-auth-logo span { color: var(--white); }
.cv-auth-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.8rem;
  text-align: center;
  letter-spacing: 0.06em;
  color: var(--white);
  margin: 12px 0 4px;
}
.cv-auth-sub {
  text-align: center;
  color: var(--grey3);
  font-size: 0.82rem;
  margin-bottom: 28px;
}

/* ════════════════════════════════
   INFO / ERROR BANNERS
════════════════════════════════ */
.cv-info {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 12px 16px;
  color: var(--grey2);
  font-size: 0.88rem;
}
.cv-error {
  background: rgba(229,9,20,0.08);
  border: 1px solid var(--border-r);
  border-radius: var(--r);
  padding: 12px 16px;
  color: #ff7070;
  font-size: 0.88rem;
}
.cv-success {
  background: rgba(34,197,94,0.08);
  border: 1px solid rgba(34,197,94,0.3);
  border-radius: var(--r);
  padding: 8px 14px;
  color: #4ade80;
  font-size: 0.8rem;
  margin-bottom: 12px;
}

/* ════════════════════════════════
   CHATBOT
════════════════════════════════ */
.cv-chat-header {
  background: linear-gradient(135deg, var(--red), #a00);
  padding: 14px 18px;
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.1rem;
  letter-spacing: 0.08em;
  color: white;
  border-radius: var(--r) var(--r) 0 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.cv-msg-user {
  background: var(--red-dim);
  border: 1px solid var(--border-r);
  border-radius: 14px 14px 2px 14px;
  padding: 10px 14px;
  color: var(--white);
  font-size: 0.88rem;
  line-height: 1.55;
  margin-left: auto;
  max-width: 85%;
  word-wrap: break-word;
}
.cv-msg-bot {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 14px 14px 14px 2px;
  padding: 10px 14px;
  color: var(--grey2);
  font-size: 0.88rem;
  line-height: 1.6;
  max-width: 92%;
  word-wrap: break-word;
}
.cv-msg-bot strong { color: var(--white); }
.cv-typing { display: flex; gap: 5px; padding: 12px 14px; align-items: center; }
.cv-typing span {
  width: 7px; height: 7px;
  background: var(--red);
  border-radius: 50%;
  animation: typingBounce 1.2s infinite;
}
.cv-typing span:nth-child(2) { animation-delay: 0.2s; }
.cv-typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}
.cv-chat-mini-card {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s, transform 0.2s;
}
.cv-chat-mini-card:hover { border-color: var(--red); transform: translateY(-2px); }
.cv-chat-mini-title {
  font-size: 0.72rem;
  color: var(--white);
  padding: 5px 7px;
  font-weight: 500;
  height: 2.2rem;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* ── Category pill buttons in home view ── */
div.cv-pill-btn .stButton > button {
  background: #1a1a1a !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  color: #aaa !important;
  border-radius: 20px !important;
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  padding: 0.42rem 0.7rem !important;
  letter-spacing: 0.05em !important;
  text-transform: none !important;
  transition: all 0.15s !important;
  white-space: nowrap !important;
}
div.cv-pill-btn .stButton > button:hover {
  background: #2a2a2a !important;
  border-color: rgba(255,255,255,0.2) !important;
  color: #fff !important;
  box-shadow: none !important;
  transform: none !important;
}
div.cv-pill-btn-active .stButton > button {
  background: #e50914 !important;
  border: 1px solid #e50914 !important;
  color: #fff !important;
  border-radius: 20px !important;
  font-size: 0.75rem !important;
  font-weight: 700 !important;
  padding: 0.42rem 0.7rem !important;
  letter-spacing: 0.05em !important;
  text-transform: none !important;
  box-shadow: 0 2px 12px rgba(229,9,20,0.4) !important;
  white-space: nowrap !important;
}
div.cv-pill-btn-active .stButton > button:hover {
  background: #ff1a1a !important;
  transform: none !important;
}

/* ── Sidebar category nav buttons ── */
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  border: none !important;
  color: #666 !important;
  text-align: left !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  padding: 0.5rem 1rem !important;
  border-radius: 8px !important;
  text-transform: none !important;
  letter-spacing: 0.02em !important;
  transition: background 0.15s, color 0.15s !important;
  box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255,255,255,0.05) !important;
  color: #ccc !important;
  box-shadow: none !important;
  transform: none !important;
}
/* Sign in/out buttons in sidebar keep red */
[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-secondary"] {
  background: var(--red) !important;
  color: #fff !important;
}

/* Chatbot FAB button */
div[data-testid="column"]:last-child .stButton > button {
  border-radius: 50% !important;
  width: 44px !important;
  height: 44px !important;
  padding: 0 !important;
  font-size: 1.1rem !important;
  min-height: 44px !important;
}

/* ── Misc ── */
[data-testid="stVerticalBlock"] > div { background: transparent !important; }
.element-container { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# =============================
# STATE + ROUTING
# =============================
defaults = {
    "view": "home",
    "selected_tmdb_id": None,
    "auth_mode": "login",       # login | signup
    "logged_in": False,
    "username": "",
    "token": "",                # JWT Bearer token from /auth/login
    "ratings": {},              # {tmdb_id: star_count}
    "auth_error": "",
    "show_auth": False,
    "auth_debug": "",           # raw error string for debugging
    # ── Chatbot ──
    "chat_open": False,
    "chat_history": [],         # list of {"role": "user"|"assistant", "content": str, "cards": [...]}
    "chat_input_key": 0,        # increment to clear input widget
    "active_category": "trending",  # currently selected home feed category
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
# Verify stored token is still valid; clear it if not.
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
            # Token expired or invalid — silently log out
            st.session_state.logged_in = False
            st.session_state.username  = ""
            st.session_state.token     = ""
    except Exception:
        pass  # Network issue — keep the user logged in optimistically

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
    """Return Authorization header if the user is logged in."""
    token = st.session_state.get("token", "")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def api_post(path: str, json_body: dict | None = None, data: dict | None = None, use_auth: bool = False):
    """POST helper — returns (response_json, error_str)."""
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
    """Call Groq API with llama-3.3-70b-versatile. Returns assistant text."""
    if not GROQ_API_KEY:
        return "MOVIES: []"  # fallback
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
    """Parse MOVIES: ["Title 1", "Title 2"] from assistant response."""
    match = re.search(r'MOVIES:\s*(\[.*?\])', text, re.DOTALL)
    if not match:
        return []
    try:
        titles = json.loads(match.group(1))
        return [t.strip() for t in titles if isinstance(t, str) and t.strip()]
    except Exception:
        return []


def clean_bot_text(text: str) -> str:
    """Remove the MOVIES: [...] line from display text."""
    return re.sub(r'MOVIES:\s*\[.*?\]', '', text, flags=re.DOTALL).strip()


def fetch_chat_movie_cards(titles: list[str]) -> list[dict]:
    """Fetch TMDB poster cards for a list of titles."""
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
    """Floating chatbot panel — clean chat interface."""
    # FAB button — top right corner via columns
    _, fab_col = st.columns([9, 1])
    with fab_col:
        fab_icon = "✕" if st.session_state.chat_open else "💬"
        if st.button(fab_icon, key="chat_fab", help="CineBot — AI Movie Recommendations"):
            st.session_state.chat_open = not st.session_state.chat_open
            st.rerun()

    if not st.session_state.chat_open:
        return

    st.markdown("""
    <div style='height:1px;background:rgba(255,255,255,0.06);margin:4px 0 0;'></div>
    <div style='
      background:#0f0f0f;
      border:1px solid rgba(255,255,255,0.08);
      border-radius:16px;
      overflow:hidden;
      margin-bottom:24px;
      box-shadow: 0 8px 40px rgba(0,0,0,0.6);
    '>
      <div style='
        background:linear-gradient(90deg,#1a0a0a,#0f0f0f);
        border-bottom:1px solid rgba(255,255,255,0.06);
        padding:16px 20px;
        display:flex;
        align-items:center;
        gap:12px;
      '>
        <div style='
          width:38px;height:38px;
          background:#e50914;
          border-radius:50%;
          display:flex;align-items:center;justify-content:center;
          font-size:1.1rem;
          box-shadow:0 0 14px rgba(229,9,20,0.5);
          flex-shrink:0;
        '>🎬</div>
        <div>
          <div style='font-family:Bebas Neue,sans-serif;font-size:1.1rem;letter-spacing:0.1em;color:#fff;line-height:1;'>CineBot</div>
          <div style='font-size:0.68rem;color:#4ade80;letter-spacing:0.04em;margin-top:2px;'>● Online · Powered by Llama 3</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not GROQ_API_KEY:
        st.markdown(
            f"<div class='cv-error'>⚠️ GROQ_API_KEY not set. Add <code>GROQ_API_KEY=your_key</code> to your .env and restart.</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Chat messages area ──
    # Greeting
    if not st.session_state.chat_history:
        st.markdown("""
        <div style='padding:6px 0 14px;'>
          <div style='
            display:inline-block;
            background:#181818;
            border:1px solid rgba(255,255,255,0.07);
            border-radius:16px 16px 16px 4px;
            padding:14px 18px;
            max-width:88%;
            color:#aaa;
            font-size:0.9rem;
            line-height:1.65;
          '>
            👋 Hey there! I'm <strong style='color:#fff;'>CineBot</strong>.<br>
            Tell me your mood, a genre, or a vibe — I'll find the perfect movie for you.<br>
            <span style='color:#555;font-size:0.78rem;'>Try: "something cozy for a rainy night" or "mind-bending sci-fi"</span>
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
            <div style='display:flex;justify-content:flex-end;margin:10px 0;'>
              <div style='
                background:rgba(229,9,20,0.18);
                border:1px solid rgba(229,9,20,0.3);
                border-radius:16px 16px 4px 16px;
                padding:12px 16px;
                max-width:78%;
                color:#f0f0f0;
                font-size:0.88rem;
                line-height:1.6;
                word-break:break-word;
              '>{text}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='display:flex;align-items:flex-start;gap:10px;margin:10px 0;'>
              <div style='
                width:28px;height:28px;
                background:#1a0505;
                border:1px solid rgba(229,9,20,0.3);
                border-radius:50%;
                display:flex;align-items:center;justify-content:center;
                font-size:0.75rem;
                flex-shrink:0;
                margin-top:2px;
              '>🎬</div>
              <div style='
                background:#141414;
                border:1px solid rgba(255,255,255,0.07);
                border-radius:4px 16px 16px 16px;
                padding:12px 16px;
                max-width:84%;
                color:#b0b0b0;
                font-size:0.88rem;
                line-height:1.65;
                word-break:break-word;
              '>{text}</div>
            </div>
            """, unsafe_allow_html=True)

            # Movie cards in a subtle horizontal strip
            if cards:
                st.markdown("<div style='padding-left:38px;margin:-4px 0 8px;'>", unsafe_allow_html=True)
                card_cols = st.columns(min(len(cards), 5))
                for ci, card in enumerate(cards[:5]):
                    with card_cols[ci]:
                        st.markdown("""<div style='
                          background:#111;
                          border:1px solid rgba(255,255,255,0.07);
                          border-radius:10px;
                          overflow:hidden;
                          transition:border-color 0.2s;
                        '>""", unsafe_allow_html=True)
                        if card.get("poster_url"):
                            st.image(card["poster_url"], use_column_width=True)
                        else:
                            st.markdown("<div style='height:80px;background:#1a1a1a;display:flex;align-items:center;justify-content:center;color:#333;font-size:1.2rem;'>🎬</div>", unsafe_allow_html=True)
                        if st.button("Open", key=f"cc_{msg_idx}_{ci}_{card['tmdb_id']}", use_container_width=True):
                            st.session_state.chat_open = False
                            goto_details(card["tmdb_id"])
                            st.rerun()
                        st.markdown(f"""<div style='
                          font-size:0.68rem;color:#888;
                          padding:4px 6px 6px;
                          height:2rem;overflow:hidden;
                          display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
                        '>{card["title"]}</div>""", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # ── Divider before input ──
    st.markdown("<div style='height:1px;background:rgba(255,255,255,0.05);margin:12px 0 10px;'></div>", unsafe_allow_html=True)

    # ── Input row ──
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

    # ── Handle send ──
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

    st.markdown("<div style='margin-top:10px;'>", unsafe_allow_html=True)
    st.markdown("<div style='color:#b3b3b3;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.07em;font-weight:600;margin-bottom:6px;'>Your Rating</div>", unsafe_allow_html=True)

    cols = st.columns([1, 1, 1, 1, 1, 2])
    for i, col in enumerate(cols[:5], start=1):
        with col:
            star_label = "★" if i <= current else "☆"
            color = "#f5c518" if i <= current else "#444"
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
            f"<div class='cv-rating-done'>⭐ You rated this {current}/5 — {labels[current]}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='cv-rating-label'>{labels[current]}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


# =============================
# POSTER GRID
# =============================
def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.markdown("<div class='cv-info'>No movies to show.</div>", unsafe_allow_html=True)
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
                st.markdown("<div class='cv-card'>", unsafe_allow_html=True)
                if poster:
                    st.image(poster, use_column_width=True)
                else:
                    st.markdown(
                        "<div style='height:180px;background:#1e1e1e;display:flex;align-items:center;justify-content:center;color:#444;font-size:2rem;border-radius:10px 10px 0 0;'>🎬</div>",
                        unsafe_allow_html=True,
                    )
                if rating > 0:
                    stars_display = "★" * rating + "☆" * (5 - rating)
                    st.markdown(
                        f"<div style='text-align:center;color:#f5c518;font-size:0.7rem;padding:2px 4px;'>{stars_display}</div>",
                        unsafe_allow_html=True,
                    )
                if st.button("▶ Open", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)
                        st.rerun()
                st.markdown(
                    f"<div class='cv-card-title'>{title}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)


# =============================
# AUTH MODAL
# =============================
def render_auth():
    """Auth form that calls /auth/login or /auth/register on the backend."""
    st.markdown("<br>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1.4, 1])
    with center:
        mode = st.session_state.auth_mode

        st.markdown(f"""
        <div class='cv-auth-card'>
          <span class='cv-auth-logo'>Cine<span>Vault</span></span>
          <div class='cv-auth-title'>{'Welcome Back' if mode=='login' else 'Join CineVault'}</div>
          <div class='cv-auth-sub'>{'Sign in to rate and track your movies' if mode=='login' else 'Create a free account'}</div>
        </div>""", unsafe_allow_html=True)

        if st.session_state.auth_error:
            st.markdown(
                f"<div class='cv-error'>{st.session_state.auth_error}</div>",
                unsafe_allow_html=True,
            )
            if st.session_state.get("auth_debug"):
                with st.expander("🔍 Debug — raw server response"):
                    st.code(st.session_state.auth_debug, language="text")
            st.markdown("<br>", unsafe_allow_html=True)

        # ── Backend connectivity check ──
        try:
            _hc = requests.get(f"{API_BASE}/health", timeout=6)
            if _hc.status_code == 200:
                st.markdown(
                    "<div class='cv-success'>✅ Server connected</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='cv-info' style='margin-bottom:12px;'>⚠️ Server responded with HTTP {_hc.status_code}</div>",
                    unsafe_allow_html=True,
                )
        except requests.exceptions.ConnectionError:
            st.markdown(
                f"<div class='cv-error' style='margin-bottom:12px;'>🔴 Cannot reach backend at <code>{API_BASE}</code>. Auth will not work until the server is running.</div>",
                unsafe_allow_html=True,
            )
        except Exception as _e:
            st.markdown(
                f"<div class='cv-info' style='margin-bottom:12px;'>⚠️ Server check failed: {_e}</div>",
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
                    # POST /auth/login  (OAuth2 form — send as form data, not JSON)
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

                else:  # signup
                    p2    = st.session_state.get("auth_password2", "").strip()
                    email = st.session_state.get("auth_email", "").strip()

                    if not p2:
                        st.session_state.auth_error = "Please confirm your password."
                        st.rerun()
                    elif p != p2:
                        st.session_state.auth_error = "Passwords do not match."
                        st.rerun()
                    else:
                        # POST /auth/register
                        resp, err = api_post(
                            "/auth/register",
                            json_body={"username": u, "password": p, "email": email or None},
                        )
                        if err:
                            st.session_state.auth_error = f"Registration failed: {err}"
                            st.session_state.auth_debug = err   # store full error for debug display
                            st.rerun()
                        else:
                            # Auto-login after successful registration
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

        # Toggle login <-> signup
        if mode == "login":
            st.markdown(
                "<div style='text-align:center;margin-top:16px;color:#666;font-size:0.85rem;'>New to CineVault?</div>",
                unsafe_allow_html=True,
            )
            if st.button("Create an account →", use_container_width=True):
                st.session_state.auth_mode  = "signup"
                st.session_state.auth_error = ""
                st.rerun()
        else:
            st.markdown(
                "<div style='text-align:center;margin-top:16px;color:#666;font-size:0.85rem;'>Already have an account?</div>",
                unsafe_allow_html=True,
            )
            if st.button("Sign in →", use_container_width=True):
                st.session_state.auth_mode  = "login"
                st.session_state.auth_error = ""
                st.rerun()



# =============================
# SIDEBAR
# =============================
with st.sidebar:
    # ── Logo ──
    st.markdown("""
    <div class='sb-top'>
      <div class='sb-logo'>Cine<span>Vault</span></div>
      <div class='sb-tagline'>Discover · Rate · Explore</div>
    </div>
    """, unsafe_allow_html=True)

    # ── User / Guest section ──
    if st.session_state.logged_in:
        initials = st.session_state.username[:2].upper()
        rated_count = len(st.session_state.ratings)
        st.markdown(f"""
        <div class='sb-user-card'>
          <div class='sb-avatar'>{initials}</div>
          <div>
            <div class='sb-uname'>{st.session_state.username}</div>
            <div class='sb-urole'>Member</div>
          </div>
        </div>
        <div class='sb-stats'>
          <div class='sb-stat-box'>
            <div class='sb-stat-num'>{rated_count}</div>
            <div class='sb-stat-label'>Rated</div>
          </div>
          <div class='sb-stat-box'>
            <div class='sb-stat-num'>∞</div>
            <div class='sb-stat-label'>Watched</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True, key="sb_signout"):
            api_post("/auth/logout", use_auth=True)
            st.session_state.logged_in = False
            st.session_state.username  = ""
            st.session_state.token     = ""
            st.rerun()
    else:
        st.markdown("""
        <div class='sb-guest-card'>
          <div class='sb-guest-icon'>🎬</div>
          <div class='sb-guest-text'>Sign in to rate movies<br>and track your watchlist</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔐  Sign In / Sign Up", use_container_width=True, key="sb_signin"):
            st.session_state.show_auth = True
            st.rerun()

    # ── Navigation ──
    st.markdown("<div class='sb-section-label'>Navigation</div>", unsafe_allow_html=True)
    if st.button("🏠  Home", use_container_width=True, key="sb_home"):
        goto_home()
        st.rerun()

    # ── Feed Settings ──
    st.markdown("<div class='sb-section-label'>Browse</div>", unsafe_allow_html=True)
    cat_map = {"trending": "🔥 Trending", "popular": "⚡ Popular", "top_rated": "🏆 Top Rated", "now_playing": "🎞 Now Playing", "upcoming": "🚀 Upcoming"}
    for cat_key, cat_label in cat_map.items():
        is_active = st.session_state.active_category == cat_key
        btn_style = "sb-cat-active" if is_active else "sb-cat"
        if st.button(cat_label, key=f"sb_cat_{cat_key}", use_container_width=True):
            st.session_state.active_category = cat_key
            goto_home()
            st.rerun()
    home_category = st.session_state.active_category
    grid_cols = st.slider("Grid columns", 4, 8, 6, label_visibility="collapsed")

    # ── Footer ──
    st.markdown("<div class='sb-footer'>© 2025 CineVault · All rights reserved</div>", unsafe_allow_html=True)


# =============================
# AUTH PAGE OVERRIDE
# =============================
if st.session_state.show_auth:
    render_auth()
    st.stop()


# =============================
# CHATBOT (floating — rendered on every page)
# =============================
render_chatbot()

# =============================
# HEADER BAR
# =============================
nb_l, nb_r = st.columns([1, 2])
with nb_l:
    if st.session_state.logged_in:
        initials_h = st.session_state.username[:2].upper()
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:10px;padding:6px 0;'>
          <div class='cv-user-badge'>
            <span class='cv-user-badge-avatar'>{initials_h}</span>
            {st.session_state.username}
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        if st.button("🔐  Sign In", key="hdr_signin"):
            st.session_state.show_auth = True
            st.rerun()

with nb_r:
    pass  # search bar rendered below

st.markdown("<div style='height:1px;background:rgba(255,255,255,0.07);margin:10px 0 20px;'></div>", unsafe_allow_html=True)


# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":

    # ── Search bar ──
    st.markdown("<div class='cv-search-wrap'>", unsafe_allow_html=True)
    typed = st.text_input(
        "search",
        placeholder="  🔍   Search any movie — Inception, Parasite, The Dark Knight...",
        label_visibility="collapsed",
        key="home_search",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if typed.strip():
        if len(typed.strip()) < 2:
            st.markdown("<div class='cv-info'>Type at least 2 characters.</div>", unsafe_allow_html=True)
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})
            if err or data is None:
                st.markdown(f"<div class='cv-error'>Search failed: {err}</div>", unsafe_allow_html=True)
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
                    st.markdown("<div class='cv-info'>No suggestions found.</div>", unsafe_allow_html=True)

                st.markdown(f"<div class='cv-section'>Results for &ldquo;{typed}&rdquo;</div>", unsafe_allow_html=True)
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")
        st.stop()

    # ── Category pill buttons (real Streamlit buttons) ──
    home_category = st.session_state.active_category
    cat_map = [
        ("trending",    "🔥 Trending"),
        ("popular",     "⚡ Popular"),
        ("top_rated",   "🏆 Top Rated"),
        ("now_playing", "🎞 Now Playing"),
        ("upcoming",    "🚀 Upcoming"),
    ]
    pill_cols = st.columns(len(cat_map))
    for col, (cat_key, cat_label) in zip(pill_cols, cat_map):
        with col:
            is_active = home_category == cat_key
            # Show active pill with red background via a styled button container
            if is_active:
                st.markdown(f"<div class='cv-pill-btn-active'>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='cv-pill-btn'>", unsafe_allow_html=True)
            if st.button(cat_label, key=f"pill_{cat_key}", use_container_width=True):
                st.session_state.active_category = cat_key
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    home_category = st.session_state.active_category
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ── Section header ──
    cat_display = home_category.replace("_", " ").title()
    cat_icon = {"trending": "🔥", "popular": "⚡", "top_rated": "🏆", "now_playing": "🎞", "upcoming": "🚀"}.get(home_category, "🎬")
    st.markdown(f"<div class='cv-section'>{cat_icon} {cat_display}</div>", unsafe_allow_html=True)

    home_cards, err = api_get_json("/home", params={"category": home_category, "limit": 24})
    if err or not home_cards:
        st.markdown(f"<div class='cv-error'>Home feed failed: {err or 'Unknown error'}</div>", unsafe_allow_html=True)
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")


# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.markdown("<div class='cv-info'>No movie selected.</div>", unsafe_allow_html=True)
        if st.button("← Back to Home"):
            goto_home()
            st.rerun()
        st.stop()

    # ── Back button ──
    st.markdown("<div class='cv-back-btn'>", unsafe_allow_html=True)
    if st.button("← Back to Home", key="det_back"):
        goto_home()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Load details
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.markdown(f"<div class='cv-error'>Could not load details: {err or 'Unknown error'}</div>", unsafe_allow_html=True)
        st.stop()

    # ── Backdrop ──
    if data.get("backdrop_url"):
        st.markdown(f"<img src='{data['backdrop_url']}' class='cv-backdrop'/>", unsafe_allow_html=True)

    # ── Main layout ──
    left, right = st.columns([1, 2.8], gap="large")

    with left:
        if data.get("poster_url"):
            st.image(data["poster_url"], use_column_width=True)
        else:
            st.markdown(
                "<div style='height:340px;background:#181818;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#333;font-size:3rem;'>🎬</div>",
                unsafe_allow_html=True,
            )
        # Star rating
        st.markdown("<div class='cv-rating-wrap'>", unsafe_allow_html=True)
        star_rating_widget(tmdb_id, data.get("title", ""))
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='cv-details-panel'>", unsafe_allow_html=True)

        title   = data.get("title", "Untitled")
        release = (data.get("release_date") or "")[:4] or "—"
        genres  = data.get("genres", [])
        vote    = data.get("vote_average")

        st.markdown(f"<div class='cv-movie-title'>{title}</div>", unsafe_allow_html=True)

        # Pills
        pills_html = "<div class='cv-pills'>"
        pills_html += f"<span class='cv-pill red'>📅 {release}</span>"
        if vote:
            pills_html += f"<span class='cv-pill red'>⭐ {vote:.1f}</span>"
        for g in genres:
            pills_html += f"<span class='cv-pill'>{g['name']}</span>"
        pills_html += "</div>"
        st.markdown(pills_html, unsafe_allow_html=True)

        st.markdown(
            f"<div class='cv-overview'>{data.get('overview') or 'No overview available.'}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Recommendations ──
    st.markdown("<div style='height:2px;background:rgba(255,255,255,0.05);margin:32px 0 20px;'></div>", unsafe_allow_html=True)

    query_title = (data.get("title") or "").strip()
    if query_title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": query_title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown("<div class='cv-section'>🔎 Similar Movies</div>", unsafe_allow_html=True)
            poster_grid(
                to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                cols=grid_cols,
                key_prefix="details_tfidf",
            )

            st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
            st.markdown("<div class='cv-section'>🎭 More Like This</div>", unsafe_allow_html=True)
            poster_grid(
                bundle.get("genre_recommendations", []),
                cols=grid_cols,
                key_prefix="details_genre",
            )
        else:
            st.markdown("<div class='cv-section'>🎭 More Like This</div>", unsafe_allow_html=True)
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(genre_only, cols=grid_cols, key_prefix="details_genre_fallback")
            else:
                st.markdown("<div class='cv-info'>No recommendations available right now.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='cv-info'>No title available for recommendations.</div>", unsafe_allow_html=True)