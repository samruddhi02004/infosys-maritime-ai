"""
Design system and custom CSS styles for Milestone 1.

Palette:
- Background: Warm White (#FAF9F6)
- Heading Text: Deep Navy (#0F172A)
- Body Text: Slate Navy (#1E293B)
- Muted Text: Steel Slate (#64748B)
- Primary Accent: Deep Teal (#0D9488)
- Hover Accent: Dark Teal (#0F766E)
- Soft Accent: Mint/Teal Tint (#F0FDFA / #CCFBF1)
- Card & Container: Pure White (#FFFFFF) with #E2E8F0 border
"""

import streamlit as st

THEME_COLORS = {
    "bg_main": "#FAF9F6",
    "bg_card": "#FFFFFF",
    "bg_soft": "#F8FAFC",
    "bg_teal_light": "#F0FDFA",
    "text_heading": "#0F172A",
    "text_main": "#1E293B",
    "text_muted": "#64748B",
    "accent_primary": "#0D9488",
    "accent_hover": "#0F766E",
    "accent_border": "#CCFBF1",
    "border_light": "#E2E8F0",
    "border_focus": "#0D9488",
    "success": "#10B981",
    "danger": "#EF4444",
    "warning": "#F59E0B"
}


def inject_custom_styles():
    """Inject cohesive light theme CSS styling into the Streamlit app."""
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global Reset & Base Typography */
        html, body, [data-testid="stAppViewContainer"] {{
            background-color: {THEME_COLORS['bg_main']} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: {THEME_COLORS['text_main']} !important;
        }}

        [data-testid="stHeader"] {{
            background: transparent !important;
        }}

        footer {{
            visibility: hidden !important;
            display: none !important;
        }}

        /* Headings */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            color: {THEME_COLORS['text_heading']} !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }}

        /* Main Container Width & Spacing */
        .block-container {{
            padding-top: 2.5rem !important;
            padding-bottom: 3.5rem !important;
            max-width: 960px !important;
        }}

        /* Card Container Styling */
        .portal-card {{
            background: {THEME_COLORS['bg_card']};
            border: 1px solid {THEME_COLORS['border_light']};
            border-radius: 14px;
            padding: 32px 36px;
            box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.05), 0 2px 4px -2px rgba(15, 23, 42, 0.05);
            margin-bottom: 24px;
        }}

        /* Streamlit Native Bordered Containers */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {THEME_COLORS['bg_card']} !important;
            border: 1px solid {THEME_COLORS['border_light']} !important;
            border-radius: 14px !important;
            padding: 28px !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04) !important;
        }}

        /* Form Labels */
        label, [data-testid="stWidgetLabel"] p {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 13.5px !important;
            font-weight: 600 !important;
            color: {THEME_COLORS['text_heading']} !important;
            margin-bottom: 6px !important;
        }}

        /* Inputs */
        div[data-baseweb="input"] {{
            background-color: {THEME_COLORS['bg_card']} !important;
            border: 1.5px solid {THEME_COLORS['border_light']} !important;
            border-radius: 9px !important;
            transition: all 0.2s ease-in-out !important;
        }}

        div[data-baseweb="input"]:focus-within {{
            border-color: {THEME_COLORS['accent_primary']} !important;
            box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
        }}

        input {{
            font-family: 'Inter', sans-serif !important;
            color: {THEME_COLORS['text_main']} !important;
            font-size: 14.5px !important;
        }}

        /* Select box */
        div[data-baseweb="select"] > div {{
            background-color: {THEME_COLORS['bg_card']} !important;
            border: 1.5px solid {THEME_COLORS['border_light']} !important;
            border-radius: 9px !important;
        }}

        /* Buttons */
        div[data-testid="stButton"] button {{
            background-color: {THEME_COLORS['accent_primary']} !important;
            color: #FFFFFF !important;
            border: 1px solid {THEME_COLORS['accent_primary']} !important;
            border-radius: 9px !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            height: 44px !important;
            padding: 0 20px !important;
            box-shadow: 0 2px 4px rgba(13, 148, 136, 0.2) !important;
            transition: all 0.2s ease !important;
            width: 100% !important;
        }}

        div[data-testid="stButton"] button:hover {{
            background-color: {THEME_COLORS['accent_hover']} !important;
            border-color: {THEME_COLORS['accent_hover']} !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(13, 148, 136, 0.25) !important;
        }}

        /* Secondary / Outline Button Styling (Used for Cancel / Back) */
        div[data-testid="stButton"].secondary-btn button {{
            background-color: #FFFFFF !important;
            color: {THEME_COLORS['text_muted']} !important;
            border: 1.5px solid {THEME_COLORS['border_light']} !important;
            box-shadow: none !important;
        }}
        div[data-testid="stButton"].secondary-btn button:hover {{
            background-color: {THEME_COLORS['bg_soft']} !important;
            color: {THEME_COLORS['text_heading']} !important;
            border-color: #CBD5E1 !important;
        }}

        /* Alerts and Status Messages */
        div[data-testid="stAlert"] {{
            border-radius: 10px !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 14px !important;
            padding: 12px 16px !important;
        }}

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background-color: #FFFFFF !important;
            border-right: 1px solid {THEME_COLORS['border_light']} !important;
        }}

        /* Data Tables */
        div[data-testid="stDataFrame"] {{
            border: 1px solid {THEME_COLORS['border_light']};
            border-radius: 10px;
            overflow: hidden;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_portal_header(title: str, subtitle: str = "Infosys Springboard Internship 7.0 &bull; Milestone 1"):
    """Render a clean, distinctive portal header with teal icon and navy typography."""
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; background-color: #F0FDFA; border: 1.5px solid #CCFBF1; border-radius: 14px; margin-bottom: 12px;">
            <span style="font-size: 26px; color: #0D9488;">🛡️</span>
        </div>
        <h1 style="font-size: 1.85rem; margin: 0 0 6px 0; color: #0F172A;">Infosys Authentication Portal</h1>
        <p style="color: #64748B; font-size: 14px; margin: 0; font-weight: 500;">{subtitle}</p>
        <div style="display: inline-block; margin-top: 10px; padding: 4px 14px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 20px; font-size: 12px; font-weight: 600; color: #0D9488;">
            {title}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_user_badge(username: str, email: str, role: str = "User"):
    """Render user profile badge in the dashboard header."""
    role_color = "#0D9488" if role.lower() == "user" else "#6366F1"
    role_bg = "#F0FDFA" if role.lower() == "user" else "#EEF2FF"
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px 24px; margin-bottom: 24px; box-shadow: 0 2px 4px rgba(15,23,42,0.03);">
        <div>
            <div style="font-size: 13px; color: #64748B; font-weight: 500;">Logged in as:</div>
            <div style="font-size: 18px; font-weight: 700; color: #0F172A;">{username} <span style="font-size: 14px; font-weight: 400; color: #64748B;">({email})</span></div>
        </div>
        <div style="background: {role_bg}; color: {role_color}; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; border: 1px solid {role_color}33;">
            ● {role.upper()}
        </div>
    </div>
    """, unsafe_allow_html=True)
