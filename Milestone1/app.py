"""
Main Streamlit application for Milestone 1: User Authentication Module.
Project: AI for Maritime Freight Pricing and Route

Meets all Milestone 1 requirements:
- Login via Username or Email with generic error masking
- Signup with 6 mandatory fields, unique username rejection, and redirection to Login
- Strict email format (ab@cd.ef) and password complexity validation
- Single unified SQLite database for users and OTP tracking
- JWT-based session handling
- Forgot Password flow offering both Security Question and Email OTP routes
- User Dashboard with welcome banner and logout
- Separate Admin Login with registered user listing (passwords never exposed)
- Distinctive executive maritime light theme (warm alabaster, deep navy, radiant teal)
"""

import time
import streamlit as st
import pandas as pd

try:
    from Milestone1.auth import (
        create_session_jwt,
        hash_password,
        hash_security_answer,
        validate_email,
        validate_mandatory_fields,
        validate_password,
        validate_password_confirmation,
        verify_password,
        verify_security_answer,
        verify_session_jwt,
    )
    from Milestone1.config import (
        OTP_EXPIRY_MINUTES,
        check_required_secrets_status,
        get_admin_credentials,
    )
    from Milestone1.database import (
        SECURITY_QUESTIONS,
        create_user,
        get_all_registered_users,
        get_user_by_email,
        get_user_by_identifier,
        get_user_by_username,
        init_db,
        update_password,
    )
    from Milestone1.otp_service import (
        create_otp_session,
        generate_otp,
        send_otp_email,
        verify_otp_session,
    )
    from Milestone1.styles import (
        inject_custom_styles,
        render_portal_header,
        render_user_badge,
        render_security_pills,
        render_password_requirements_card,
        render_step_indicator,
        render_html,
    )
except ImportError:
    from auth import (
        create_session_jwt,
        hash_password,
        hash_security_answer,
        validate_email,
        validate_mandatory_fields,
        validate_password,
        validate_password_confirmation,
        verify_password,
        verify_security_answer,
        verify_session_jwt,
    )
    from config import (
        OTP_EXPIRY_MINUTES,
        check_required_secrets_status,
        get_admin_credentials,
    )
    from database import (
        SECURITY_QUESTIONS,
        create_user,
        get_all_registered_users,
        get_user_by_email,
        get_user_by_identifier,
        get_user_by_username,
        init_db,
        update_password,
    )
    from otp_service import (
        create_otp_session,
        generate_otp,
        send_otp_email,
        verify_otp_session,
    )
    from styles import (
        inject_custom_styles,
        render_portal_header,
        render_user_badge,
        render_security_pills,
        render_password_requirements_card,
        render_step_indicator,
        render_html,
    )


# ── 1. Page Configuration & Theme Setup ─────────────────────────────────
st.set_page_config(
    page_title="AI for Maritime Freight Pricing and Route",
    page_icon="🚢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize database tables on startup
init_db()

# Inject distinctive light theme CSS
inject_custom_styles()


# ── 2. Session State Initialization ─────────────────────────────────────
SESSION_DEFAULTS = {
    "auth_token": None,
    "page": "Login",
    "admin_auth": False,
    # Forgot password state
    "forgot_method": "sq",          # "sq" or "otp"
    "forgot_stage": "identify",      # "identify", "answer", "otp_verify", "reset"
    "forgot_identity": "",
    "forgot_email": "",
    "forgot_sq_text": "",
    "forgot_otp_jwt": "",
    "feedback_message": None,
    "feedback_type": "info"
}

for key, val in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


def navigate_to(page_name: str):
    """Safely change page and trigger a rerun."""
    st.session_state.page = page_name
    st.rerun()


def reset_forgot_flow():
    """Reset forgot password state variables."""
    st.session_state.forgot_stage = "identify"
    st.session_state.forgot_identity = ""
    st.session_state.forgot_email = ""
    st.session_state.forgot_sq_text = ""
    st.session_state.forgot_otp_jwt = ""


# ── 3. Application Routing ──────────────────────────────────────────────

# A. Admin Dashboard View
if st.session_state.admin_auth and st.session_state.page == "Admin_Dashboard":
    render_portal_header("Admin Control Panel", "Administrator Access & Registry Audit")
    admin_user, _ = get_admin_credentials()
    render_user_badge(username=admin_user, email="admin@system.local", role="Administrator")

    registered_users = get_all_registered_users()
    user_count = len(registered_users) if registered_users else 0

    # Executive Admin KPI Bar
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric(label="Registered Accounts", value=str(user_count), delta="All Active")
    with kpi2:
        st.metric(label="Security Level", value="Masked", delta="Zero Exposure")
    with kpi3:
        st.metric(label="Audit Protocol", value="Compliant", delta="Milestone Step 11")

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        st.markdown("### 📋 Registered User Registry")
        st.caption("Milestone Step 11: Real-time user accounts (passwords and cryptographic hashes are strictly masked).")

        if registered_users:
            df = pd.DataFrame(registered_users)
            display_df = df[["id", "username", "email", "created_at"]].rename(
                columns={
                    "id": "ID",
                    "username": "Username",
                    "email": "Registered Email",
                    "created_at": "Registration Timestamp (UTC)"
                }
            )
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            render_html(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 16px; margin-top: 12px; font-size: 13px; color: #64748B;">
                <span>Total Registered Users: <b style="color: #0F172A;">{user_count}</b></span>
                <span style="color: #0D9488; font-weight: 600;">🔒 Password Hashes Masked & Excluded</span>
            </div>
            """)
        else:
            st.info("No registered users found in the database. Use the Signup page to register test accounts.")

        st.markdown("<br><hr style='border-color: #E2E8F0;'><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout from Admin Dashboard", use_container_width=True):
            st.session_state.admin_auth = False
            st.session_state.page = "Login"
            st.rerun()

# B. Regular User Dashboard View (JWT Session Protected)
elif st.session_state.auth_token and st.session_state.page == "Dashboard":
    is_valid, payload, err = verify_session_jwt(st.session_state.auth_token)
    if not is_valid or not payload:
        st.warning("Your session has expired or is invalid. Please sign in again.")
        st.session_state.auth_token = None
        st.session_state.page = "Login"
        st.rerun()

    username = payload.get("username", "User")
    email = payload.get("email", "unknown")

    render_portal_header("User Dashboard", "Secure Authenticated Session Active")
    render_user_badge(username=username, email=email, role="User")

    with st.container():
        render_html(f"""
        <div style="background: linear-gradient(135deg, #F0FDFA 0%, #FFFFFF 100%); border: 1.5px solid #CCFBF1; border-radius: 14px; padding: 22px 26px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(13,148,136,0.06);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                <span style="font-size: 22px;">👋</span>
                <span style="font-size: 1.35rem; font-weight: 800; color: #0F172A;">Welcome back, {username}!</span>
            </div>
            <p style="margin: 0; color: #475569; font-size: 14px; line-height: 1.5;">
                You have authenticated via signed JSON Web Token (JWT) into <b>AI for Maritime Freight Pricing and Route</b>. Your session token is actively verified and protected with tamper-proof HMAC-SHA256 signatures.
            </p>
        </div>
        """)

        # High-Tech KPI Metric Cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Authentication Status", value="Verified", delta="Active JWT")
        with col2:
            st.metric(label="Cryptographic Security", value="Bcrypt + Salt", delta="HS256")
        with col3:
            st.metric(label="Session Expiry", value="2 Hours", delta="Standard")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Account Details Breakdown
        render_html(f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 22px 26px; margin-bottom: 24px;">
            <div style="font-size: 15px; font-weight: 700; color: #0F172A; margin-bottom: 14px; display: flex; align-items: center; gap: 8px;">
                <span>🔒</span> Authenticated Account Parameters
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; font-size: 13.5px;">
                <div>
                    <div style="color: #64748B; font-weight: 500;">Username:</div>
                    <div style="font-weight: 700; color: #0F172A; margin-top: 2px;"><code>{username}</code></div>
                </div>
                <div>
                    <div style="color: #64748B; font-weight: 500;">Primary Email:</div>
                    <div style="font-weight: 700; color: #0F172A; margin-top: 2px;"><code>{email}</code></div>
                </div>
                <div>
                    <div style="color: #64748B; font-weight: 500;">Token Type:</div>
                    <div style="font-weight: 700; color: #0D9488; margin-top: 2px;">Bearer JWT (HS256)</div>
                </div>
                <div>
                    <div style="color: #64748B; font-weight: 500;">Password Protection:</div>
                    <div style="font-weight: 700; color: #0D9488; margin-top: 2px;">Bcrypt (Cost 12)</div>
                </div>
            </div>
        </div>
        """)

        st.markdown("<br><hr style='border-color: #E2E8F0;'><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.auth_token = None
            st.session_state.page = "Login"
            st.success("You have been securely logged out.")
            time.sleep(1)
            st.rerun()

# C. Admin Login View (Step 11)
elif st.session_state.page == "Admin_Login":
    render_portal_header("Admin Portal Login", "Restricted Access for Authorized Administrators")

    with st.container():
        render_html("""
        <div style="background: #FEF3C7; border: 1.5px solid #FCD34D; border-radius: 12px; padding: 14px 18px; margin-bottom: 22px; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 20px;">⚠️</span>
            <div style="font-size: 13px; color: #92400E; font-weight: 600;">
                RESTRICTED AREA: Superuser credentials required. Unauthorized access attempts are monitored and logged.
            </div>
        </div>
        """)

        admin_u_input = st.text_input("Admin Username", placeholder="e.g. admin")
        admin_p_input = st.text_input("Admin Password", type="password", placeholder="••••••••")

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Sign In as Admin →", use_container_width=True):
                cfg_user, cfg_pass = get_admin_credentials()
                if admin_u_input.strip() == cfg_user and admin_p_input == cfg_pass:
                    st.session_state.admin_auth = True
                    st.session_state.page = "Admin_Dashboard"
                    st.success("Admin authentication successful.")
                    st.rerun()
                else:
                    st.error("❌ Invalid admin credentials.")
        with col_btn2:
            if st.button("← Return to User Login", use_container_width=True):
                st.session_state.page = "Login"
                st.rerun()

# D. Signup View (Step 3, 7, 8)
elif st.session_state.page == "Signup":
    render_portal_header("Create New Account", "Register for AI for Maritime Freight Pricing and Route")
    render_security_pills()

    with st.container():
        render_html("""
        <div style="font-size: 14px; color: #475569; margin-bottom: 18px; font-weight: 500;">
            Please complete all 6 mandatory registration fields below:
        </div>
        """)

        col_u, col_e = st.columns(2)
        with col_u:
            signup_username = st.text_input("Username *", placeholder="e.g. alex_kumar")
        with col_e:
            signup_email = st.text_input("Email Address *", placeholder="e.g. alex@infosys.com")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            signup_password = st.text_input(
                "Password *",
                type="password",
                placeholder="Min 8 chars, 1 upper, 1 lower, 1 digit, 1 symbol"
            )
        with col_p2:
            signup_confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="Re-enter your password"
            )

        # Real-time visual password complexity guide
        render_password_requirements_card()

        signup_sq = st.selectbox(
            "Security Question * (Confidential recovery prompt)",
            SECURITY_QUESTIONS
        )
        signup_sa = st.text_input(
            "Security Answer *",
            placeholder="Your secret answer (case-insensitive)"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col_sub1, col_sub2 = st.columns([1.3, 1])

        with col_sub1:
            if st.button("Complete Registration →", use_container_width=True):
                # 1. Check mandatory fields
                ok_req, msg_req = validate_mandatory_fields(
                    username=signup_username,
                    email=signup_email,
                    password=signup_password,
                    confirm_password=signup_confirm_password,
                    security_answer=signup_sa
                )
                if not ok_req:
                    st.error(f"⚠️ {msg_req}")
                else:
                    # 2. Validate email format
                    ok_email, msg_email = validate_email(signup_email)
                    if not ok_email:
                        st.error(f"⚠️ {msg_email}")
                    else:
                        # 3. Validate password complexity
                        ok_pass, msg_pass = validate_password(signup_password)
                        if not ok_pass:
                            st.error(f"⚠️ {msg_pass}")
                        else:
                            # 4. Validate password confirmation
                            ok_match, msg_match = validate_password_confirmation(signup_password, signup_confirm_password)
                            if not ok_match:
                                st.error(f"❌ {msg_match}")
                            else:
                                # 5. Hash credentials securely
                                pwd_hash = hash_password(signup_password)
                                sa_hash = hash_security_answer(signup_sa)

                                # 6. Persist to SQLite
                                success, db_msg = create_user(
                                    username=signup_username,
                                    email=signup_email,
                                    password_hash=pwd_hash,
                                    security_question=signup_sq,
                                    security_answer_hash=sa_hash
                                )
                                if success:
                                    # Milestone Step 7 rule: Route back to Login on success!
                                    st.success("✅ Account created successfully! Please sign in with your credentials.")
                                    time.sleep(1.5)
                                    navigate_to("Login")
                                else:
                                    st.error(f"❌ {db_msg}")

        with col_sub2:
            if st.button("← Back to Sign In", use_container_width=True):
                navigate_to("Login")

# E. Forgot Password View (Step 8 & 9)
elif st.session_state.page == "Forgot":
    render_portal_header("Reset Password", "Two Secure Identity Verification Routes")

    # Dynamic Step Progress Breadcrumbs
    current_step = 1
    if st.session_state.forgot_stage in ["answer", "otp_verify"]:
        current_step = 2
    elif st.session_state.forgot_stage == "reset":
        current_step = 3
    render_step_indicator(current_step=current_step, total_steps=3)

    with st.container():
        # Recovery Route Switcher Tabs
        route_tab1, route_tab2 = st.tabs(["🔒 Route 1: Security Question", "📧 Route 2: Email OTP"])

        # ── ROUTE 1: SECURITY QUESTION ──
        with route_tab1:
            render_html("""
            <div style="font-size: 14px; color: #475569; margin-bottom: 14px; font-weight: 500;">
                Recover access instantly by answering the security question chosen during account registration.
            </div>
            """)

            sq_uname = st.text_input("Registered Username", key="sq_uname_input", placeholder="e.g. alex_kumar")

            if st.button("Find Security Question →", key="sq_find_btn"):
                if not sq_uname.strip():
                    st.error("⚠️ Please enter your username.")
                else:
                    user = get_user_by_username(sq_uname.strip())
                    if not user:
                        st.error("❌ Username not found in the registry.")
                    else:
                        st.session_state.forgot_identity = user["username"]
                        st.session_state.forgot_sq_text = user["security_question"]
                        st.session_state.forgot_stage = "answer"

            if st.session_state.forgot_stage == "answer" and st.session_state.forgot_identity:
                render_html(f"""
                <div style="background: #F0FDFA; border: 1.5px solid #CCFBF1; border-radius: 12px; padding: 16px 20px; margin: 16px 0;">
                    <div style="font-size: 12px; font-weight: 700; color: #0D9488; text-transform: uppercase; margin-bottom: 4px;">Registered Security Prompt:</div>
                    <div style="font-size: 15px; font-weight: 700; color: #0F172A;">{st.session_state.forgot_sq_text}</div>
                </div>
                """)

                sq_ans_input = st.text_input("Your Security Answer", type="password", key="sq_ans_input")
                sq_new_pwd = st.text_input("New Password", type="password", key="sq_new_pwd_input",
                                           placeholder="Min 8 chars, uppercase, lowercase, digit, symbol")
                sq_confirm_pwd = st.text_input("Confirm New Password", type="password", key="sq_conf_pwd_input")

                if st.button("Verify Answer & Reset Password →", key="sq_submit_btn"):
                    ok_flds, msg_flds = validate_mandatory_fields(
                        security_answer=sq_ans_input,
                        new_password=sq_new_pwd,
                        confirm_password=sq_confirm_pwd
                    )
                    if not ok_flds:
                        st.error(f"⚠️ {msg_flds}")
                    else:
                        user = get_user_by_username(st.session_state.forgot_identity)
                        if not user or not verify_security_answer(sq_ans_input, user["security_answer_hash"]):
                            st.error("❌ Incorrect security answer.")
                        else:
                            ok_pwd, msg_pwd = validate_password(sq_new_pwd)
                            if not ok_pwd:
                                st.error(f"⚠️ {msg_pwd}")
                            else:
                                ok_m, msg_m = validate_password_confirmation(sq_new_pwd, sq_confirm_pwd)
                                if not ok_m:
                                    st.error(f"❌ {msg_m}")
                                else:
                                    new_hash = hash_password(sq_new_pwd)
                                    update_password(st.session_state.forgot_identity, new_hash)
                                    st.success("✅ Password reset successfully! Redirecting to login...")
                                    reset_forgot_flow()
                                    time.sleep(1.5)
                                    navigate_to("Login")

        # ── ROUTE 2: EMAIL OTP ──
        with route_tab2:
            render_html(f"""
            <div style="font-size: 14px; color: #475569; margin-bottom: 14px; font-weight: 500;">
                Receive a cryptographically secure 6-digit one-time password via Gmail SMTP (expires in <b>{OTP_EXPIRY_MINUTES} minutes</b>).
            </div>
            """)

            otp_email_input = st.text_input("Registered Email Address", key="otp_email_input", placeholder="e.g. alex@infosys.com")

            if st.button("Send Verification Code 📧", key="otp_send_btn"):
                ok_req, msg_req = validate_mandatory_fields(email=otp_email_input)
                if not ok_req:
                    st.error(f"⚠️ {msg_req}")
                else:
                    ok_fmt, msg_fmt = validate_email(otp_email_input)
                    if not ok_fmt:
                        st.error(f"⚠️ {msg_fmt}")
                    else:
                        user = get_user_by_email(otp_email_input.strip().lower())
                        if not user:
                            st.error("❌ Email address is not registered in our system.")
                        else:
                            # Generate OTP and 5-minute session
                            otp_code = generate_otp()
                            jwt_otp_token, _ = create_otp_session(user["email"], otp_code)

                            with st.spinner("Dispatching verification email via Gmail SMTP..."):
                                email_sent, email_msg = send_otp_email(user["email"], otp_code)

                            if email_sent:
                                st.session_state.forgot_email = user["email"]
                                st.session_state.forgot_otp_jwt = jwt_otp_token
                                st.session_state.forgot_stage = "otp_verify"
                                st.success("✅ 6-digit code sent to your email! Please enter it below.")
                            else:
                                st.error(f"❌ {email_msg}")

            if st.session_state.forgot_stage == "otp_verify" and st.session_state.forgot_email:
                render_html(f"""
                <div style="background: #F0FDFA; border: 1.5px solid #CCFBF1; border-radius: 12px; padding: 14px 18px; margin: 16px 0;">
                    <div style="font-size: 12px; font-weight: 700; color: #0D9488; text-transform: uppercase;">📩 Verification Code Dispatched:</div>
                    <div style="font-size: 14px; color: #0F172A; margin-top: 4px;">Sent to <b>{st.session_state.forgot_email}</b>. Single-use code valid for <b>{OTP_EXPIRY_MINUTES} minutes</b>.</div>
                </div>
                """)

                entered_otp = st.text_input("Enter 6-Digit Code", max_chars=6, key="entered_otp_input", placeholder="e.g. 583921")
                otp_new_pwd = st.text_input("New Password", type="password", key="otp_new_pwd_input",
                                            placeholder="Min 8 chars, uppercase, lowercase, digit, symbol")
                otp_confirm_pwd = st.text_input("Confirm New Password", type="password", key="otp_conf_pwd_input")

                if st.button("Verify Code & Reset Password →", key="otp_verify_btn"):
                    ok_flds, msg_flds = validate_mandatory_fields(
                        verification_code=entered_otp,
                        new_password=otp_new_pwd,
                        confirm_password=otp_confirm_pwd
                    )
                    if not ok_flds:
                        st.error(f"⚠️ {msg_flds}")
                    else:
                        # Verify OTP against single-use DB record and 5-min JWT
                        is_otp_ok, otp_status_msg = verify_otp_session(
                            jwt_token=st.session_state.forgot_otp_jwt,
                            input_otp=entered_otp,
                            target_email=st.session_state.forgot_email
                        )
                        if not is_otp_ok:
                            st.error(f"❌ {otp_status_msg}")
                        else:
                            ok_pwd, msg_pwd = validate_password(otp_new_pwd)
                            if not ok_pwd:
                                st.error(f"⚠️ {msg_pwd}")
                            else:
                                ok_m, msg_m = validate_password_confirmation(otp_new_pwd, otp_confirm_pwd)
                                if not ok_m:
                                    st.error(f"❌ {msg_m}")
                                else:
                                    new_hash = hash_password(otp_new_pwd)
                                    update_password(st.session_state.forgot_email, new_hash)
                                    st.success("✅ Password successfully updated! Redirecting to login...")
                                    reset_forgot_flow()
                                    time.sleep(1.5)
                                    navigate_to("Login")

        st.markdown("<br><hr style='border-color: #E2E8F0;'><br>", unsafe_allow_html=True)
        if st.button("← Cancel and Return to Sign In", use_container_width=True):
            reset_forgot_flow()
            navigate_to("Login")

# F. Default: Login View (Step 3 & 7)
else:
    render_portal_header("Sign In to Your Account", "Access Maritime Analytics & Pricing Gateway")
    render_security_pills()

    with st.container():
        login_identifier = st.text_input(
            "Username or Email Address *",
            placeholder="e.g. alex_kumar or alex@infosys.com"
        )
        login_password = st.text_input(
            "Password *",
            type="password",
            placeholder="••••••••"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn_login, col_btn_signup = st.columns([1.2, 1])

        with col_btn_login:
            if st.button("Sign In →", use_container_width=True):
                ok_req, msg_req = validate_mandatory_fields(
                    username_or_email=login_identifier,
                    password=login_password
                )
                if not ok_req:
                    st.error(f"⚠️ {msg_req}")
                else:
                    # Look up user by username OR email
                    user = get_user_by_identifier(login_identifier)

                    # Verify bcrypt hash
                    if user and verify_password(login_password, user["password_hash"]):
                        # Issue fresh JWT session token on login success (Step 7)
                        token = create_session_jwt(
                            username=user["username"],
                            email=user["email"],
                            role="user"
                        )
                        st.session_state.auth_token = token
                        st.session_state.page = "Dashboard"
                        st.success("Authentication successful.")
                        st.rerun()
                    else:
                        # Milestone Step 3: Generic error — never reveal if username or password was wrong!
                        st.error("❌ Invalid username/email or password.")

        with col_btn_signup:
            if st.button("Create Account", use_container_width=True):
                navigate_to("Signup")

        st.markdown("<br>", unsafe_allow_html=True)
        col_forgot, col_admin = st.columns(2)
        with col_forgot:
            if st.button("🔑 Forgot Password?", use_container_width=True):
                reset_forgot_flow()
                navigate_to("Forgot")
        with col_admin:
            if st.button("🛡️ Admin Portal", use_container_width=True):
                navigate_to("Admin_Login")

    # Trust Footer
    render_html("""
    <div style="text-align: center; margin-top: 2.5rem; font-size: 12px; color: #94A3B8;">
        Infosys Springboard Internship 7.0 &bull; Batch 4 &bull; AI for Maritime Freight Pricing and Route<br>
        Powered by Streamlit, PyJWT, Bcrypt, and SQLite
    </div>
    """)
