"""
Design system and custom CSS styles for Milestone 1: User Authentication Module.
Project: AI for Maritime Freight Pricing and Route

Theme:
- Background: Warm Alabaster with subtle radial ambient glow (#FAF9F6)
- Heading Typography: Plus Jakarta Sans (#0F172A)
- Body Typography: Inter (#1E293B)
- Accent: Deep Teal (#0D9488) to Maritime Cyan (#0EA5E9) gradient
- Card Surface: Pure White (#FFFFFF) with refined multi-layer elevation and border (#E2E8F0)
"""

import streamlit as st

THEME_COLORS = {
    "bg_main": "#FAF9F6",
    "bg_card": "#FFFFFF",
    "bg_soft": "#F8FAFC",
    "bg_teal_light": "#F0FDFA",
    "bg_teal_subtle": "#CCFBF1",
    "text_heading": "#0F172A",
    "text_main": "#1E293B",
    "text_muted": "#64748B",
    "accent_primary": "#0D9488",
    "accent_hover": "#0F766E",
    "accent_cyan": "#0EA5E9",
    "accent_border": "#CCFBF1",
    "border_light": "#E2E8F0",
    "border_focus": "#0D9488",
    "success": "#10B981",
    "danger": "#EF4444",
    "warning": "#F59E0B"
}


def render_html(html_str: str):
    """Safely render HTML without markdown parser interference."""
    collapsed = " ".join([line.strip() for line in html_str.splitlines() if line.strip()])
    if hasattr(st, "html"):
        try:
            st.html(collapsed)
            return
        except Exception:
            pass
    st.markdown(collapsed, unsafe_allow_html=True)


def inject_custom_styles():
    """Inject modern, executive light theme CSS styling into the Streamlit app."""
    css = f"""
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global Canvas & Subtle Radial Glow */
        html, body, [data-testid="stAppViewContainer"], .stApp {{
            background-color: {THEME_COLORS['bg_main']} !important;
            background-image: 
                radial-gradient(1000px 600px at 10% 10%, rgba(13, 148, 136, 0.04) 0%, transparent 70%),
                radial-gradient(900px 500px at 90% 90%, rgba(14, 165, 233, 0.04) 0%, transparent 60%) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: {THEME_COLORS['text_main']} !important;
            -webkit-font-smoothing: antialiased;
        }}

        [data-testid="stHeader"] {{
            background: transparent !important;
        }}

        footer {{
            visibility: hidden !important;
            display: none !important;
        }}

        /* Headings with Plus Jakarta Sans */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            color: {THEME_COLORS['text_heading']} !important;
            font-weight: 700 !important;
            letter-spacing: -0.025em !important;
        }}

        /* Main Container Width & Spacing */
        .block-container {{
            padding-top: 1.8rem !important;
            padding-bottom: 3.5rem !important;
            max-width: 860px !important;
        }}

        /* Streamlit Native Bordered Containers */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {THEME_COLORS['bg_card']} !important;
            border: 1px solid {THEME_COLORS['border_light']} !important;
            border-radius: 16px !important;
            padding: 30px !important;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.04), 0 8px 10px -6px rgba(15, 23, 42, 0.02) !important;
            transition: all 0.25s ease !important;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
            box-shadow: 0 14px 28px -5px rgba(15, 23, 42, 0.06), 0 10px 12px -6px rgba(15, 23, 42, 0.03) !important;
        }}

        /* Form Labels */
        label, [data-testid="stWidgetLabel"] p {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 13.5px !important;
            font-weight: 600 !important;
            color: {THEME_COLORS['text_heading']} !important;
            margin-bottom: 6px !important;
            letter-spacing: -0.01em !important;
        }}

        /* Input Controls */
        div[data-baseweb="input"] {{
            background-color: #FFFFFF !important;
            border: 1.5px solid {THEME_COLORS['border_light']} !important;
            border-radius: 10px !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}

        div[data-baseweb="input"]:focus-within {{
            border-color: {THEME_COLORS['accent_primary']} !important;
            box-shadow: 0 0 0 3.5px rgba(13, 148, 136, 0.16) !important;
        }}

        input {{
            font-family: 'Inter', sans-serif !important;
            color: {THEME_COLORS['text_main']} !important;
            font-size: 14.5px !important;
        }}

        /* Select box */
        div[data-baseweb="select"] > div {{
            background-color: #FFFFFF !important;
            border: 1.5px solid {THEME_COLORS['border_light']} !important;
            border-radius: 10px !important;
            transition: all 0.2s ease !important;
        }}
        div[data-baseweb="select"]:focus-within > div {{
            border-color: {THEME_COLORS['accent_primary']} !important;
            box-shadow: 0 0 0 3.5px rgba(13, 148, 136, 0.16) !important;
        }}

        /* Buttons Styling */
        div[data-testid="stButton"] button {{
            background: linear-gradient(135deg, {THEME_COLORS['accent_primary']} 0%, {THEME_COLORS['accent_hover']} 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid {THEME_COLORS['accent_primary']} !important;
            border-radius: 10px !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            height: 45px !important;
            padding: 0 20px !important;
            box-shadow: 0 3px 6px rgba(13, 148, 136, 0.2) !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            width: 100% !important;
            letter-spacing: 0.01em !important;
        }}

        div[data-testid="stButton"] button:hover {{
            transform: translateY(-1.5px) !important;
            box-shadow: 0 6px 14px rgba(13, 148, 136, 0.3) !important;
            filter: brightness(1.05) !important;
        }}

        div[data-testid="stButton"] button:active {{
            transform: translateY(0px) !important;
            box-shadow: 0 2px 4px rgba(13, 148, 136, 0.2) !important;
        }}

        /* Streamlit Tabs */
        div[data-testid="stTabs"] button[role="tab"] {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            color: {THEME_COLORS['text_muted']} !important;
            padding: 10px 18px !important;
            border-radius: 8px 8px 0 0 !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
            color: {THEME_COLORS['accent_primary']} !important;
            border-bottom-color: {THEME_COLORS['accent_primary']} !important;
        }}

        /* Alerts and Status Messages */
        div[data-testid="stAlert"] {{
            border-radius: 12px !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 14px !important;
            padding: 14px 18px !important;
            border-left: 4px solid !important;
            box-shadow: 0 2px 4px rgba(15, 23, 42, 0.03) !important;
        }}

        /* Metrics */
        div[data-testid="stMetric"] {{
            background: #FFFFFF;
            border: 1px solid {THEME_COLORS['border_light']};
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 2px 5px rgba(15, 23, 42, 0.03);
        }}
        div[data-testid="stMetricLabel"] p {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            color: {THEME_COLORS['text_muted']} !important;
        }}
        div[data-testid="stMetricValue"] {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 700 !important;
            color: {THEME_COLORS['text_heading']} !important;
        }}

        /* Data Tables */
        div[data-testid="stDataFrame"] {{
            border: 1px solid {THEME_COLORS['border_light']};
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
        }}
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_portal_header(title: str, subtitle: str = "Infosys Springboard Internship 7.0 &bull; Batch 4"):
    """Render a premium executive portal header with radiant maritime icon badge and live security pill."""
    html = f"""
    <div style="text-align: center; margin-bottom: 1.8rem; padding: 0.5rem 0;">
        <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 14px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 30px; font-size: 11.5px; font-weight: 600; color: #0D9488; box-shadow: 0 1px 3px rgba(15,23,42,0.04); margin-bottom: 14px;">
            <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background-color: #10B981; box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);"></span>
            <span>MARITIME FREIGHT INTELLIGENCE GATEWAY &bull; 256-BIT ENCRYPTION</span>
        </div>
        <div style="display: flex; justify-content: center; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; justify-content: center; width: 58px; height: 58px; background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%); border: 1.5px solid #99F6E4; border-radius: 16px; box-shadow: 0 8px 16px -2px rgba(13, 148, 136, 0.15);">
                <span style="font-size: 28px;">🚢</span>
            </div>
        </div>
        <h1 style="font-size: 1.85rem; margin: 0 0 4px 0; color: #0F172A; font-weight: 800; letter-spacing: -0.03em;">
            AI for Maritime Freight Pricing and Route
        </h1>
        <p style="color: #64748B; font-size: 13.5px; margin: 0 0 10px 0; font-weight: 500;">
            {subtitle}
        </p>
        <div style="display: inline-block; padding: 4px 14px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 20px; font-size: 11.5px; font-weight: 700; color: #0D9488; letter-spacing: 0.02em; text-transform: uppercase; box-shadow: 0 1px 2px rgba(15,23,42,0.04);">
            {title}
        </div>
    </div>
    """
    render_html(html)


def render_user_badge(username: str, email: str, role: str = "User"):
    """Render an executive profile card in the dashboard header with user initials and status dot."""
    role_color = "#0D9488" if role.lower() == "user" else "#6366F1"
    role_bg = "#F0FDFA" if role.lower() == "user" else "#EEF2FF"
    initials = "".join([part[0].upper() for part in username.split()[:2]]) if username else "U"
    
    html = f"""
    <div style="display: flex; align-items: center; justify-content: space-between; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 18px 24px; margin-bottom: 22px; box-shadow: 0 4px 12px rgba(15,23,42,0.03); position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; bottom: 0; width: 4px; background: {role_color};"></div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, {role_color} 0%, #065F46 100%); color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; box-shadow: 0 4px 8px rgba(13,148,136,0.25);">
                {initials}
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 17px; font-weight: 700; color: #0F172A;">{username}</span>
                    <span style="font-size: 11.5px; background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; border-radius: 12px; padding: 1px 7px; font-weight: 600;">✓ Verified</span>
                </div>
                <div style="font-size: 13px; color: #64748B; font-weight: 500; margin-top: 2px;">{email}</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="background: {role_bg}; color: {role_color}; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; border: 1px solid {role_color}33; display: flex; align-items: center; gap: 6px;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background-color: {role_color};"></span>
                {role.upper()}
            </div>
        </div>
    </div>
    """
    render_html(html)


def render_security_pills():
    """Render a row of trust badges highlighting compliance and cryptographic standards."""
    html = """
    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-bottom: 20px;">
        <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 20px; font-size: 11.5px; color: #475569; font-weight: 500; box-shadow: 0 1px 2px rgba(15,23,42,0.03);">
            <span>🔒</span> <b>Bcrypt Hashed & Salted</b>
        </div>
        <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 20px; font-size: 11.5px; color: #475569; font-weight: 500; box-shadow: 0 1px 2px rgba(15,23,42,0.03);">
            <span>⏱️</span> <b>2-Hour Signed JWT Session</b>
        </div>
        <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 20px; font-size: 11.5px; color: #475569; font-weight: 500; box-shadow: 0 1px 2px rgba(15,23,42,0.03);">
            <span>🛡️</span> <b>Zero Credential Exposure</b>
        </div>
    </div>
    """
    render_html(html)


def render_password_requirements_card():
    """Render a visual password complexity checklist for the signup flow."""
    html = """
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 18px; margin: 12px 0 18px 0;">
        <div style="font-size: 12px; font-weight: 700; color: #0F172A; text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            <span>🛡️</span> Password Complexity Standard (Milestone 1)
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 6px; font-size: 12px; color: #64748B;">
            <div style="display: flex; align-items: center; gap: 5px;">
                <span style="color: #0D9488; font-weight: bold;">✓</span> Min 8 Characters
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <span style="color: #0D9488; font-weight: bold;">✓</span> 1 Uppercase (A-Z)
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <span style="color: #0D9488; font-weight: bold;">✓</span> 1 Lowercase (a-z)
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <span style="color: #0D9488; font-weight: bold;">✓</span> 1 Number (0-9)
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <span style="color: #0D9488; font-weight: bold;">✓</span> 1 Symbol (!@#$...)
            </div>
        </div>
    </div>
    """
    render_html(html)


def render_step_indicator(current_step: int, total_steps: int = 3, labels: list = None):
    """Render a clean step-by-step breadcrumb progress bar for recovery flows."""
    if labels is None:
        labels = ["Identify Account", "Verify Identity", "Update Password"]
    
    pills_html = ""
    for i, label in enumerate(labels, start=1):
        is_active = i == current_step
        is_done = i < current_step
        
        bg = "#0D9488" if (is_active or is_done) else "#F1F5F9"
        color = "#FFFFFF" if (is_active or is_done) else "#64748B"
        border = "#0D9488" if (is_active or is_done) else "#E2E8F0"
        check_icon = "✓ " if is_done else f"{i}. "
        
        pills_html += f"""<div style="display: flex; align-items: center; gap: 6px; padding: 6px 14px; background: {bg}; color: {color}; border: 1px solid {border}; border-radius: 20px; font-size: 12px; font-weight: 600;"><span>{check_icon}</span><span>{label}</span></div>"""
        if i < total_steps:
            pills_html += """<span style="color: #CBD5E1; font-size: 14px;">➔</span>"""

    html = f"""
    <div style="display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 10px; margin-bottom: 22px; padding: 10px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; box-shadow: 0 1px 3px rgba(15,23,42,0.03);">
        {pills_html}
    </div>
    """
    render_html(html)
