import streamlit as st

from dataclasses import dataclass

from typing import List, Dict, Optional

from datetime import datetime, date, timedelta
import random





# ============================================================

# BASIC CONFIG

# ============================================================



st.set_page_config(

    page_title="Qubic Behavioral Feedback Engine",

    layout="wide",

    initial_sidebar_state="expanded",

)



# ============================================================

# USER STATE & BEHAVIOR ENGINE HELPERS (DEMO)

# ============================================================

def render_auth_gate() -> bool:
    """
    Login / signup gate shown once per session before everything else.
    Returns True if the gate is being shown (and main app should NOT run yet).
    """
    if "auth_done" not in st.session_state:
        st.session_state["auth_done"] = False

    # If user already chose an option, skip gate
    if st.session_state["auth_done"]:
        return False

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Sign in to Crowdlike")
    st.markdown(
        "To personalize XP, coins, and streaks for this session, start with a quick login, "
        "signup, or continue as a guest."
    )

    st.markdown(
        """
<div class="card-hero">
  <div>
    <span class="chip">Behavioral feedback engine</span>
    <span class="chip">Hackathon build</span>
    <span class="chip">Session-only data</span>
  </div>
  <p class="subtext">
    Crowdlike turns your simulated on-chain behavior into XP, streaks and metrics.
    This demo does not touch real wallets – it just shows the feedback layer.
  </p>
</div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    # Log in → skip intro, go directly to Login page
    with col1:
        if st.button("Log in", use_container_width=True):
            st.session_state["auth_done"] = True
            st.session_state["intro_done"] = True  # go straight into the app
            navigate_to("login")

    # Sign up → skip intro, go directly to Register page
    with col2:
        if st.button("Sign up", use_container_width=True):
            st.session_state["auth_done"] = True
            st.session_state["intro_done"] = True  # go straight into the app
            navigate_to("register")

    # Continue as guest → still show intro afterwards
    with col3:
        if st.button("Continue as guest", use_container_width=True):
            # quick guest profile + a tiny XP hello
            set_user_profile("Guest", "guest@example.com")
            grant_xp(5, "Guest entry", "Continued as guest from auth gate")
            st.session_state["auth_done"] = True
            # DO NOT set intro_done here → they will see the intro screen

    st.markdown(
        "<p class='subtext'>You can always change account details later from the sidebar.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # If any of the buttons fired, auth_done is now True and on next rerun we skip this gate.
    return not st.session_state["auth_done"]


def render_crowdlike_intro() -> bool:
    """
    Intro screen shown once per session before the main app.
    Returns True if the intro is being shown (and main app should NOT run yet).
    """
    if "intro_done" not in st.session_state:
        st.session_state["intro_done"] = False

    # If already passed intro, skip it
    if st.session_state["intro_done"]:
        return False

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Title + tagline
    st.markdown("### Crowdlike")
    st.markdown("#### Qubic behavioral feedback engine by *Cats can fly too!*")

    # Hero card with chips
    st.markdown(
        """
<div class="card-hero">
  <div>
    <span class="chip">Hackathon prototype</span>
    <span class="chip">Session only</span>
    <span class="chip">Built on Qubic</span>
  </div>
  <p class="subtext">
    Turn raw on-chain decisions into XP, streaks, and behavior metrics –
    this demo runs locally, with synthetic data only.
  </p>
</div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_r = st.columns([2, 1])

    # Left side: quick explanation
    with col_l:
        st.markdown("#### What you can explore")
        st.write("- **Home dashboard** – XP, coins, streaks, last scenario snapshot.")
        st.write("- **Behavior Metrics Lab** – synthetic TES/BSS/BMS/CFS-style metrics.")
        st.write("- **Scenario runs** – log outcomes for different behavior archetypes.")
        st.write("- **Wallet & trading desk** – coin ↔ token flows (no real funds).")
        st.write("- **Shop & achievements** – how soft rewards and milestones feel.")

        st.markdown("#### Who this is for")
        st.write("- Qubic users who want **feedback** on their behavior.")
        st.write("- Hackathon judges who want a **5-minute tour** of the engine.")

    # Right side: fast-path buttons
    with col_r:
        st.markdown("#### Fast paths")
        if st.button("Open dashboard →", use_container_width=True):
            st.session_state["intro_done"] = True
            navigate_to("home_dashboard")

        if st.button("Jump to Metrics Lab →", use_container_width=True):
            st.session_state["intro_done"] = True
            navigate_to("metrics_lab")

        if st.button("See invest case →", use_container_width=True):
            st.session_state["intro_done"] = True
            navigate_to("invest_case")

        st.caption("You can always move around using the sidebar inside the app.")

    st.write("---")

    # Generic “let me in” button
    if st.button("Just let me click around the prototype →", use_container_width=True):
        st.session_state["intro_done"] = True
        navigate_to("landing_public")

    st.markdown(
        """
<p class="subtext">
All numbers reset on refresh. To make Crowdlike real, connect wallet data,
Qubic events, and launch it through Nostromo.
</p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # If any of the buttons fired, intro_done is True and next rerun will go to main()
    return not st.session_state["intro_done"]



def init_user_state():

    if "user_state" not in st.session_state:

        st.session_state.user_state = {

            "username": "Guest",      # simple "login"

            "xp": 0,                  # total XP

            "coins": 0,               # soft currency, earned from XP

            "gems": 0,                # reserved for future use

            "tests_taken": 0,
            "test_history": [],       # list of dicts with test attempts
            "xp_events": [],          # list of dicts with XP events
            "days_active": [],        # list of ISO dates when user did something
            "daily_tasks_done": {},   # mapping of YYYY-MM-DD -> list of completed task ids
            "token_balance": 0.0,     # simulated token holdings
            "token_trades": [],       # list of token buy/sell events
            "ai_chat_history": [],    # session-only AI helper conversation
        }




def get_user_state():

    init_user_state()

    return st.session_state.user_state





def level_from_xp(xp: int) -> int:

    """Very simple level curve: 1000 XP per level."""

    return xp // 1000 + 1





def record_activity_day():

    """Mark that the user was active today (for streak computation)."""

    state = get_user_state()

    today_str = date.today().isoformat()

    if today_str not in state["days_active"]:

        state["days_active"].append(today_str)

        state["days_active"].sort()





def compute_streak(days_active):

    """Compute a simple 'current streak in days' from the list of active dates."""

    if not days_active:

        return 0

    dates = sorted(date.fromisoformat(d) for d in days_active)

    today = date.today()

    streak = 0

    cursor = today

    while cursor in dates:

        streak += 1

        cursor = cursor - timedelta(days=1)

    return streak







def grant_xp(amount: int, source: str, description: str):

    """Add XP, derive some coins, and log an XP event."""

    if amount <= 0:

        return

    state = get_user_state()

    state["xp"] += amount

    # Simple rule: earn 1 coin per 10 XP

    state["coins"] += amount // 10

    event = {

        "ts": datetime.utcnow().isoformat(timespec="seconds"),

        "source": source,

        "amount": int(amount),

        "description": description,

    }

    state["xp_events"].append(event)

    record_activity_day()





def record_test_attempt(test_id: str, name: str, subject: str, correct: int, total: int, time_sec: int):

    """Store a test attempt and award XP based on percentage (up to 200 XP)."""

    state = get_user_state()

    total = max(total, 1)

    correct = max(0, min(correct, total))

    percent = round((correct / total) * 100.0, 1)



    # XP rule: up to 200 XP per test based on percent

    xp_gain = int(percent * 2)

    grant_xp(xp_gain, "Test", f"{name} ({subject})")



    attempt = {

        "timestamp": datetime.utcnow().isoformat(timespec="seconds"),

        "test_id": test_id,

        "name": name,

        "subject": subject,

        "correct": correct,

        "total": total,

        "percent": percent,

        "time_sec": int(time_sec),

        "xp_gained": xp_gain,

    }

    state["test_history"].append(attempt)

    state["tests_taken"] += 1

    record_activity_day()



def set_current_scenario(page_id: str, name: str, subject: str):
    """Remember the active scenario/test metadata for simulation."""
    st.session_state.current_test_id = page_id
    st.session_state.current_test_name = name
    st.session_state.current_test_subject = subject
    record_activity_day()


def log_token_trade(action: str, amount: float, price: float, coin_delta: int, token_delta: float):
    """Log a token trade into state."""
    state = get_user_state()
    entry = {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
        "action": action,
        "amount": round(amount, 2),
        "price": round(price, 2),
        "coin_delta": int(coin_delta),
        "token_delta": round(token_delta, 2),
    }
    state["token_trades"].append(entry)


def set_user_profile(username: str, email: str = None):
    state = get_user_state()
    if username:
        state["username"] = username
    if email:
        state["email"] = email
    record_activity_day()


def ensure_chat_history():
    """Make sure the lightweight AI chat buffer exists."""
    state = get_user_state()
    history = state.get("ai_chat_history")
    if not isinstance(history, list):
        history = []
        state["ai_chat_history"] = history
    return history




def get_last_test_attempt():

    state = get_user_state()

    if not state["test_history"]:

        return None

    return state["test_history"][-1]





def get_last_attempt_for_test(test_id: str):

    state = get_user_state()

    for attempt in reversed(state["test_history"]):

        if attempt["test_id"] == test_id:

            return attempt

    return None





def get_xp_by_day():

    """Return dict { 'YYYY-MM-DD': total_xp } based on xp_events."""

    state = get_user_state()

    by_day = {}

    for e in state["xp_events"]:

        ts = e["ts"]

        if "T" in ts:

            day = ts.split("T")[0]

        else:

            day = ts[:10]

        by_day.setdefault(day, 0)

        by_day[day] += int(e.get("amount", 0))

    return by_day





def get_subject_xp_breakdown():

    """Use 'subject' in test_history as behavior channels for now."""

    state = get_user_state()

    breakdown = {}

    for a in state["test_history"]:

        subj = a.get("subject", "General behavior")

        if subj not in breakdown:

            breakdown[subj] = {"xp": 0, "tests": 0}

        breakdown[subj]["xp"] += int(a.get("xp_gained", 0))

        breakdown[subj]["tests"] += 1

    return breakdown





def compute_best_streak(days_active):
    """Longest streak of consecutive active days."""
    if not days_active:
        return 0
    dates_list = sorted(date.fromisoformat(d) for d in days_active)

    best = 1

    current = 1

    for i in range(1, len(dates_list)):

        if dates_list[i] == dates_list[i - 1] + timedelta(days=1):

            current += 1

            if current > best:

                best = current

        else:

            current = 1
    return best


def ensure_daily_task_state():
    """Guarantee the per-day mission tracking structure exists."""
    state = get_user_state()
    if "daily_tasks_done" not in state or not isinstance(state["daily_tasks_done"], dict):
        state["daily_tasks_done"] = {}
    return state["daily_tasks_done"]


def render_demo_disclaimer(note: str = None):
    """Consistent session notice for behavior-like stats and rewards."""
    message = note or (
        "All scores, XP, coins, and missions shown here are generated for this session only "
        "and reset on refresh. Connect a backend to persist real activity."
    )
    st.markdown(f"*{message}*")


def compute_achievements_catalog(state):
    """
    Build a simple achievements list from XP, tests taken and streak.
    Returns (achievements, best_streak).
    """
    xp = state["xp"]
    tests = state["tests_taken"]
    days = state["days_active"]
    streak_current = compute_streak(days)
    streak_best = compute_best_streak(days)
    xp_by_day = get_xp_by_day()

    achievements = []


    def _achievement(id_, name, desc, unlocked, progress):

        achievements.append(

            {

                "id": id_,

                "name": name,

                "description": desc,

                "unlocked": unlocked,

                "progress": progress,

            }

        )



    # XP-based achievements

    _achievement(

        "xp_1000",

        "First 1,000 Behavior XP",

        "Reach 1,000 XP from simulated behavior runs.",

        xp >= 1000,

        f"{xp}/1000 XP",

    )

    _achievement(

        "xp_5000",

        "Serious Behavior Grinder",

        "Reach 5,000 XP in this session.",

        xp >= 5000,

        f"{xp}/5000 XP",

    )



    # Test/scenario count achievements

    _achievement(

        "tests_3",

        "Tried 3 Scenarios",

        "Record results for at least 3 scenarios.",

        tests >= 3,

        f"{tests}/3 scenarios",

    )

    _achievement(

        "tests_10",

        "Scenario Explorer",

        "Record results for at least 10 scenarios.",

        tests >= 10,

        f"{tests}/10 scenarios",

    )



    # Streak achievements

    _achievement(

        "streak_3",

        "3-Day Discipline Streak",

        "Be active on 3 consecutive days.",

        streak_best >= 3,

        f"Best streak: {streak_best}/3 days",

    )

    _achievement(
        "streak_7",
        "7-Day Commitment",
        "Be active on 7 consecutive days.",
        streak_best >= 7,
        f"Best streak: {streak_best}/7 days",
    )

    # Weekend activity achievement
    active_dates = [date.fromisoformat(d) for d in days]
    active_set = set(active_dates)
    weekend_unlocked = any(
        d.weekday() == 5 and (d + timedelta(days=1)) in active_set for d in active_dates
    )
    weekend_progress = "Seen Sat+Sun active day pair" if weekend_unlocked else "No Sat+Sun pair yet"
    _achievement(
        "weekend_warrior",
        "Weekend Warrior",
        "Be active on both Saturday and Sunday (streak marker).",
        weekend_unlocked,
        weekend_progress,
    )

    # Momentum builder: XP on 5 of last 7 days
    today = date.today()
    active_days_last7 = 0
    for offset in range(7):
        d_str = (today - timedelta(days=offset)).isoformat()
        if xp_by_day.get(d_str, 0) > 0 or d_str in days:
            active_days_last7 += 1
    _achievement(
        "momentum_builder",
        "Momentum Builder",
        "Gain XP on 5 out of the last 7 days.",
        active_days_last7 >= 5,
        f"{active_days_last7}/5 active days in last 7",
    )

    return achievements, streak_best




# ============================================================

# GLOBAL BLACKâ-'ANDâ-'WHITE CSS

# ============================================================



st.markdown(

    """

<style>

:root {
    --accent: #0d6efd;
    --accent-light: #f2f6ff;
}

/* Global reset: black text, white background */

html, body, .stApp {

    background-color: #ffffff !important;

    color: #000000 !important;

    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;

}



/* Remove Streamlit default shadows / rounding / color accents */

div, section, header, footer, main {

    border-radius: 0 !important;

    box-shadow: none !important;

}



/* Top bar */

.top-bar {

    width: 100%;

    border-bottom: 1px solid var(--accent);

    padding: 8px 16px;

    display: flex;

    flex-direction: row;

    align-items: center;

    justify-content: space-between;

    background: linear-gradient(90deg, #ffffff 0%, var(--accent-light) 100%);

    box-sizing: border-box;

}

.top-bar-left {

    font-weight: bold;

    font-size: 16px;

}

.top-bar-right a {

    margin-left: 16px;

    font-size: 13px;

    color: var(--accent);

    text-decoration: none;

}

.top-bar-right a.active {

    text-decoration: underline;

    font-weight: 600;

}



/* Main container */

.main-container {

    max-width: 1000px;

    margin: 24px auto 60px auto;

}



/* Section titles */

.section-title {

    font-size: 14px;

    text-transform: uppercase;

    letter-spacing: 0.16em;

    margin-bottom: 4px;

    color: #000000;

}



/* Subtle description text */

.subtext {

    font-size: 13px;

    color: #333333;

}



/* Cards (no rounding, no shadow, just borders) */

.card {

    border: 1px solid #d6e3ff;

    padding: 16px;

    margin-bottom: 16px;

    background-color: #ffffff;

}

.card-hero {
    border: 1px solid var(--accent);
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-light) 100%);
    padding: 20px;
    margin-bottom: 16px;
}

.chip {
    display: inline-block;
    padding: 4px 10px;
    border: 1px solid var(--accent);
    background-color: var(--accent-light);
    font-size: 12px;
    margin-right: 6px;
}



/* Buttons */

button, .stButton>button {

    border-radius: 0 !important;

    border: 1px solid var(--accent) !important;

    background-color: var(--accent-light) !important;

    color: #000000 !important;

    font-size: 13px !important;

    padding: 6px 16px !important;

}



/* Primary button (we emulate with a class) */

.btn-primary {

    border-radius: 0;

    border: 1px solid var(--accent);

    background-color: var(--accent);

    color: #ffffff;

    font-size: 13px;

    padding: 6px 16px;

}



/* Links */

a, a:visited {

    color: var(--accent);

}



/* Inputs */

input, textarea, select {

    border-radius: 0 !important;

    border: 1px solid var(--accent) !important;

    background-color: #ffffff !important;

    color: #000000 !important;

    font-size: 13px !important;

}



/* Tables */

table {

    border-collapse: collapse;

    width: 100%;

    font-size: 13px;

}

th, td {

    border: 1px solid #000000;

    padding: 6px 8px;

    text-align: left;

}



/* Progress bar container */

.progress-container {

    width: 100%;

    border: 1px solid #000000;

    height: 12px;

    box-sizing: border-box;

}

.progress-fill {

    height: 100%;

    background-color: #777777;

}



/* Simple footer */

.footer {

    border-top: 1px solid #000000;

    padding: 8px 16px;

    font-size: 12px;

    color: #777777;

    margin-top: 32px;

}

</style>

""",

    unsafe_allow_html=True,

)



# ============================================================

# PAGE REGISTRY

# ============================================================



@dataclass

class Page:

    id: str

    label: str

    section: str

    template: str

    meta: Dict[str, str] = None



PAGES: List[Page] = []



def add_page(id: str, label: str, section: str, template: str, meta: Dict[str, str] = None):

    PAGES.append(Page(id=id, label=label, section=section, template=template, meta=meta or {}))


# Simple navigation helper so in-page buttons can jump to other views
def get_page_by_id(page_id: str) -> Optional[Page]:
    return next((p for p in PAGES if p.id == page_id), None)


def navigate_to(page_id: str):
    """Persist desired section/page in session state and trigger a rerun."""
    page = get_page_by_id(page_id)
    if not page:
        return
    st.session_state["nav_section"] = page.section
    st.session_state["nav_page_label"] = page.label





# ------------------------------------------------------------

# 1â-"10 Entry & Auth

# ------------------------------------------------------------

add_page("landing_public", "Landing (Public)", "Entry & Auth", "landing")

add_page("login", "Login", "Entry & Auth", "login")

add_page("register", "Register / Sign Up", "Entry & Auth", "register")

add_page("verify_email", "Email Verification", "Entry & Auth", "simple_info")

add_page("forgot_password", "Forgot Password", "Entry & Auth", "forgot_password")

add_page("reset_password", "Reset Password", "Entry & Auth", "reset_password")

add_page("logged_out_upsell", "Logged-Out Upsell", "Entry & Auth", "simple_info")

add_page("terms", "Terms of Service", "Entry & Auth", "legal")

add_page("privacy", "Privacy Policy", "Entry & Auth", "legal")

add_page("cookie_consent", "Cookie / Data Consent", "Entry & Auth", "simple_info")

add_page("invest_case", "Why You Should Invest", "Onboarding & Home", "invest_case")
add_page("ai_assistant", "AI Coach / Helper", "Onboarding & Home", "ai_assistant")



# ------------------------------------------------------------

# 11â-"20 Onboarding & Home

# ------------------------------------------------------------

add_page("onboard_subjects", "Onboarding: Choose Subjects", "Onboarding & Home", "onboard_subjects")

add_page("onboard_goals", "Onboarding: Choose Study Goals", "Onboarding & Home", "onboard_goals")

add_page("onboard_placement", "Onboarding: Quick Placement Test", "Onboarding & Home", "test_detail")

add_page("welcome_tour", "Welcome Tour", "Onboarding & Home", "welcome_tour")

add_page("home_dashboard", "Home Dashboard", "Onboarding & Home", "home_dashboard")

add_page("subject_hub", "Subject Selection Hub", "Onboarding & Home", "subject_hub")

add_page("daily_tasks", "Daily Tasks / Missions", "Onboarding & Home", "daily_tasks")

add_page("streak_overview", "Streak Overview", "Onboarding & Home", "streak_overview")

add_page("notifications_center", "Notifications Center", "Onboarding & Home", "notifications_center")

add_page("announcements", "Announcements / Changelog", "Onboarding & Home", "simple_list")



# ------------------------------------------------------------

# 21â-"40 Account & Profile

# ------------------------------------------------------------

add_page("account_overview", "My Account Overview", "Account & Profile", "account_overview")

add_page("edit_account", "Edit Account Info", "Account & Profile", "settings_form")

add_page("change_password", "Change Password", "Account & Profile", "change_password")

add_page("two_factor", "Two-Factor Auth Setup", "Account & Profile", "settings_form")

add_page("linked_devices", "Linked Devices / Active Sessions", "Account & Profile", "simple_table")

add_page("delete_account", "Delete / Deactivate Account", "Account & Profile", "danger_confirm")

add_page("public_profile", "Public Profile View", "Account & Profile", "profile_public")

add_page("profile_customization", "Profile Customization Hub", "Account & Profile", "profile_customization")

add_page("profile_icon", "Profile Icon Selector", "Account & Profile", "simple_list")

add_page("profile_banner", "Profile Banner Selector", "Account & Profile", "simple_list")

add_page("profile_bio", "Profile Bio Editor", "Account & Profile", "settings_form")

add_page("profile_badges", "Profile Badges Management", "Account & Profile", "simple_table")

add_page("profile_privacy", "Profile Privacy Settings", "Account & Profile", "settings_form")

add_page("view_other_profile", "View Another Userâ-s Profile", "Account & Profile", "profile_public")

add_page("block_user", "Block / Unblock User", "Account & Profile", "settings_form")

add_page("friends_list", "Friends List", "Account & Profile", "simple_table")

add_page("friend_requests", "Friend Requests", "Account & Profile", "simple_table")

add_page("profile_visitors", "Recent Visitors to Profile", "Account & Profile", "simple_table")

add_page("profile_activity_log", "Profile Activity Log", "Account & Profile", "simple_table")

add_page("profile_theme_presets", "Profile Theme Presets", "Account & Profile", "simple_list")



# ------------------------------------------------------------

# 41â-"60 XP, Levels, Stats

# ------------------------------------------------------------

add_page("xp_overview", "XP Overview Dashboard", "XP & Stats", "xp_overview")

add_page("level_up_detail", "Level-Up Detail", "XP & Stats", "simple_info")

add_page("xp_history", "XP History Timeline", "XP & Stats", "simple_table")

add_page("xp_subject_breakdown", "Subject-Specific XP Breakdown", "XP & Stats", "simple_table")

add_page("xp_weekly_graph", "Weekly XP Graph", "XP & Stats", "simple_graph")

add_page("xp_monthly_graph", "Monthly XP Graph", "XP & Stats", "simple_graph")

add_page("lifetime_stats", "Lifetime Stats Overview", "XP & Stats", "simple_table")

add_page("achievements_list", "Achievements List", "XP & Stats", "simple_table")

add_page("achievement_detail", "Achievement Detail", "XP & Stats", "simple_info")

add_page("milestones_roadmap", "Milestones Roadmap", "XP & Stats", "simple_list")

add_page("streak_detail", "Streak Detail", "XP & Stats", "streak_overview")

add_page("streak_freeze", "Streak Freeze / Recovery", "XP & Stats", "settings_form")

add_page("goals_dashboard", "Goals Dashboard", "XP & Stats", "simple_table")

add_page("goal_edit", "Create / Edit Custom Goal", "XP & Stats", "settings_form")

add_page("leaderboards", "Leaderboards Overview", "XP & Stats", "simple_list")

add_page("leaderboard_global", "Global Leaderboard", "XP & Stats", "simple_table")

add_page("leaderboard_friends", "Friends-Only Leaderboard", "XP & Stats", "simple_table")

add_page("leaderboard_subject", "Subject-Based Leaderboard", "XP & Stats", "simple_table")

add_page("leaderboard_class", "School / Class Leaderboard", "XP & Stats", "simple_table")

add_page("personal_bests", "Personal Bests Summary", "XP & Stats", "simple_table")

add_page("metrics_lab", "Behavior Metrics Lab", "XP & Stats", "metrics_lab")



# ------------------------------------------------------------

# Behavior Scenarios (project-aligned)

# ------------------------------------------------------------

add_page("scenario_library", "Behavior Scenario Library", "Behavior Scenarios", "test_library")
add_page("scenario_calibration", "Scenario: Momentum Calibration", "Behavior Scenarios", "test_detail")
add_page("scenario_volatility", "Scenario: Volatility Stress Run", "Behavior Scenarios", "test_detail")
add_page("scenario_governance", "Scenario: Governance Vote Cycle", "Behavior Scenarios", "test_detail")
add_page("scenario_airdrop", "Scenario: Airdrop Farming Sprint", "Behavior Scenarios", "test_detail")
add_page("scenario_social", "Scenario: Social Hype Spike", "Behavior Scenarios", "test_detail")
add_page("scenario_execution", "Scenario: Execution Discipline Drill", "Behavior Scenarios", "test_detail")
add_page("scenario_run", "Scenario Run (Simulated)", "Behavior Scenarios", "test_taking")
add_page("scenario_results_summary", "Scenario Results Summary", "Behavior Scenarios", "test_results")
add_page("scenario_feedback", "Scenario Feedback / Reflection", "Behavior Scenarios", "settings_form")
add_page("scenario_share", "Share Scenario Outcome", "Behavior Scenarios", "simple_info")


# ------------------------------------------------------------

# 61â-"80 Test Library â-" General

# ------------------------------------------------------------

add_page("tests_all", "All Tests Library", "Test Library", "test_library")

add_page("tests_math", "Test Category: Math", "Test Library", "test_library")

add_page("tests_science", "Test Category: Science", "Test Library", "test_library")

add_page("tests_programming", "Test Category: Programming", "Test Library", "test_library")

add_page("tests_mixed", "Test Category: Mixed Random", "Test Library", "test_library")

add_page("tests_search", "Test Search Results", "Test Library", "test_library")

add_page("tests_filter_difficulty", "Filter Tests by Difficulty", "Test Library", "test_library")

add_page("tests_filter_length", "Filter Tests by Time Length", "Test Library", "test_library")

add_page("tests_saved", "Saved / Favorited Tests", "Test Library", "test_library")

add_page("tests_recent", "Recently Attempted Tests", "Test Library", "test_library")

add_page("tests_recommended", "Recommended Tests For You", "Test Library", "test_library")

add_page("tests_new", "New / Recently Added", "Test Library", "test_library")

add_page("tests_popular", "Popular This Week", "Test Library", "test_library")

add_page("test_detail_generic", "Test Detail (Generic)", "Test Library", "test_detail")

add_page("test_taking", "Test Taking (Generic)", "Test Library", "test_taking")

add_page("test_pause_resume", "Test Pause / Resume", "Test Library", "simple_info")

add_page("test_results_summary", "Test Results Summary", "Test Library", "test_results")

add_page("test_review_questions", "Question-by-Question Review", "Test Library", "simple_table")

add_page("test_feedback_rating", "Test Feedback / Rating", "Test Library", "settings_form")

add_page("test_share_results", "Share Test Results", "Test Library", "simple_info")



# ------------------------------------------------------------

# 81â-"105 Algebra 1 Tests

# ------------------------------------------------------------

algebra_tests = [

    "Intro to Variables",

    "Evaluating Expressions",

    "One-Step Equations",

    "Two-Step Equations",

    "Multi-Step Equations",

    "Equations with Fractions",

    "Inequalities Basics",

    "Compound Inequalities",

    "Graphing on the Coordinate Plane",

    "Slope and Rate of Change",

    "Slope-Intercept Form",

    "Point-Slope Form",

    "Standard Form Linear Equations",

    "Systems (Substitution)",

    "Systems (Elimination)",

    "Systems Word Problems",

    "Functions Basics",

    "Function Notation",

    "Linear vs Nonlinear Functions",

    "Exponents and Powers",

    "Scientific Notation",

    "Polynomials Basics",

    "Factoring Quadratics",

    "Quadratic Formula",

]

add_page("algebra_hub", "Algebra 1 Subject Hub", "Algebra 1", "simple_list")



for idx, name in enumerate(algebra_tests):

    slug = f"alg_test_{idx+1}"

    add_page(

        slug,

        f"Algebra Test: {name}",

        "Algebra 1",

        "test_detail",

        meta={"test_name": name, "subject": "Algebra 1"},

    )



# ------------------------------------------------------------

# 106â-"130 Physics & Science Tests

# ------------------------------------------------------------

physics_tests = [

    "Units and Measurements",

    "Motion in One Dimension",

    "Speed vs Velocity",

    "Acceleration Basics",

    "Newtonâ-s Laws",

    "Forces and Free-Body Diagrams",

    "Work and Energy",

    "Power",

    "Momentum and Collisions",

    "Simple Machines",

    "Waves Basics",

    "Sound Waves",

    "Light and Optics",

    "Electricity Basics",

    "Circuits",

    "Magnetism",

    "Thermodynamics Basics",

    "Density and Buoyancy",

    "Pressure and Fluids",

    "Atoms and Elements",

    "Periodic Table",

    "Chemical Reactions",

    "Earth and Space Science",

    "Scientific Method",

]

add_page("physics_hub", "Physics Subject Hub", "Physics & Science", "simple_list")



for idx, name in enumerate(physics_tests):

    slug = f"phys_test_{idx+1}"

    add_page(

        slug,

        f"Science Test: {name}",

        "Physics & Science",

        "test_detail",

        meta={"test_name": name, "subject": "Physics & Science"},

    )



# ------------------------------------------------------------

# 131â-"150 Practice & Training Modes

# ------------------------------------------------------------

add_page("practice_hub", "Practice Hub", "Practice & Training", "simple_list")

add_page("practice_quick5", "Quick 5-Question Drill", "Practice & Training", "test_taking")

add_page("practice_speedrun", "Timed Speed-Run Mode", "Practice & Training", "test_taking")

add_page("practice_endless", "Endless Practice Mode", "Practice & Training", "test_taking")

add_page("practice_errors", "Error Review Mode", "Practice & Training", "simple_table")

add_page("practice_bookmarks", "Bookmark Question Review", "Practice & Training", "simple_table")

add_page("flashcards_home", "Flashcards Mode Home", "Practice & Training", "simple_list")

add_page("flashcards_session", "Flashcards Session", "simple", "simple_info")

add_page("spaced_repetition", "Spaced Repetition Planner", "Practice & Training", "settings_form")

add_page("custom_practice_builder", "Custom Practice Set Builder", "Practice & Training", "settings_form")

add_page("daily_warmup", "Daily Warm-Up Quiz", "Practice & Training", "test_taking")

add_page("weekly_challenge", "Weekly Challenge Quiz", "Practice & Training", "test_taking")

add_page("boss_battle", "Boss Battle Test (Hard Mixed)", "Practice & Training", "test_taking")

add_page("practice_by_difficulty", "Practice By Difficulty", "Practice & Training", "simple_list")

add_page("practice_by_type", "Practice By Question Type", "Practice & Training", "simple_list")

add_page("practice_history", "Practice History List", "Practice & Training", "simple_table")

add_page("practice_session_detail", "Practice Session Detail", "Practice & Training", "test_results")

add_page("practice_streak_detail", "Practice Streak Detail", "Practice & Training", "streak_overview")

add_page("practice_suggested_after_test", "Suggested Practice After Test", "Practice & Training", "simple_list")

add_page("practice_vs_past_self", "Practice Versus Past Self", "Practice & Training", "simple_table")



# ------------------------------------------------------------

# 151â-"170 Shop & Currency

# ------------------------------------------------------------

add_page("shop_home", "Shop Home", "Shop & Currency", "shop_page")

add_page("currency_overview", "Currency Overview", "Shop & Currency", "simple_table")

add_page("shop_themes", "Themes Shop", "Shop & Currency", "shop_page")

add_page("shop_icons", "Icons / Avatars Shop", "Shop & Currency", "shop_page")

add_page("shop_banners", "Banners Shop", "Shop & Currency", "shop_page")

add_page("shop_title_badges", "Title Badges Shop", "Shop & Currency", "shop_page")

add_page("shop_streak_freezes", "Streak Freezes Shop", "Shop & Currency", "shop_page")

add_page("shop_xp_boosts", "XP Boosts Shop", "Shop & Currency", "shop_page")

add_page("shop_practice_packs", "Extra Practice Packs Shop", "Shop & Currency", "shop_page")

add_page("shop_custom_slots", "Custom Test Slots Shop", "Shop & Currency", "shop_page")

add_page("shop_limited_offers", "Limited-Time Offers Shop", "Shop & Currency", "shop_page")

add_page("shop_recommended", "Recommended Items For You", "Shop & Currency", "shop_page")

add_page("token_trading", "Token Trading Desk", "Shop & Currency", "token_trading")

add_page("wallet_dashboard", "Wallet & Market Overview", "Shop & Currency", "wallet_dashboard")
add_page("shop_transactions", "Transaction History", "Shop & Currency", "simple_table")

add_page("shop_purchase_confirm", "Purchase Confirmation", "Shop & Currency", "simple_info")

add_page("shop_gift_items", "Gift Items To Friend", "Shop & Currency", "settings_form")

add_page("shop_redeem_code", "Redeem Promo Code", "Shop & Currency", "settings_form")

add_page("shop_earn_currency", "Earn Currency Tasks List", "Shop & Currency", "simple_list")

add_page("shop_daily_reward", "Daily Free Reward Claim", "Shop & Currency", "simple_info")

add_page("shop_refund_form", "Refund / Purchase Problem", "Shop & Currency", "settings_form")

add_page("shop_parental_controls", "Parental Purchase Controls", "Shop & Currency", "settings_form")



# ------------------------------------------------------------

# 171â-"185 Social & Competition

# ------------------------------------------------------------

add_page("social_hub", "Social Hub", "Social & Competition", "simple_list")

add_page("friends_activity", "Friends Activity Feed", "Social & Competition", "simple_list")

add_page("global_activity", "Global Activity Feed", "Social & Competition", "simple_list")

add_page("dm_inbox", "Direct Messages Inbox", "Social & Competition", "simple_table")

add_page("dm_conversation", "Direct Message Conversation", "Social & Competition", "simple_info")

add_page("create_study_group", "Create Study Group", "Social & Competition", "settings_form")

add_page("study_group_lobby", "Study Group Lobby", "Social & Competition", "simple_info")

add_page("study_group_chat", "Study Group Chat", "Social & Competition", "simple_list")

add_page("group_test_lobby", "Group Test Session Lobby", "Social & Competition", "test_detail")

add_page("group_test_results", "Group Test Results Comparison", "Social & Competition", "test_results")

add_page("community_challenges", "Community Challenges List", "Social & Competition", "simple_list")

add_page("join_challenge", "Join Community Challenge", "Social & Competition", "settings_form")

add_page("past_challenge_results", "Past Challenge Results", "Social & Competition", "simple_table")

add_page("report_user_content", "Report User / Content", "Social & Competition", "settings_form")

add_page("community_guidelines", "Community Guidelines", "Social & Competition", "legal")



# ------------------------------------------------------------

# 186â-"195 Settings & System

# ------------------------------------------------------------

add_page("settings_home", "Settings Home", "Settings & System", "settings_list")

add_page("settings_display", "Display Settings", "Settings & System", "settings_form")

add_page("settings_notifications", "Notification Settings", "Settings & System", "settings_form")

add_page("settings_sound", "Sound / Haptics Settings", "Settings & System", "settings_form")

add_page("settings_language", "Language Settings", "Settings & System", "settings_form")

add_page("settings_data_privacy", "Data and Privacy Settings", "Settings & System", "settings_form")

add_page("settings_security", "Security Settings", "Settings & System", "settings_form")

add_page("settings_storage", "Storage / Cache Management", "Settings & System", "simple_table")

add_page("settings_shortcuts", "Keyboard Shortcuts Help", "Settings & System", "simple_list")

add_page("settings_integrations", "Connected Apps / Integrations", "Settings & System", "simple_table")



# ------------------------------------------------------------

# 196â-"200 Admin & Dev

# ------------------------------------------------------------

add_page("admin_dashboard", "Admin Dashboard", "Admin & Dev", "simple_table")

add_page("admin_question_bank", "Question Bank Manager", "Admin & Dev", "simple_table")

add_page("admin_test_editor", "Test Creation and Editing", "Admin & Dev", "settings_form")

add_page("admin_reports_queue", "User Reports Moderation Queue", "Admin & Dev", "simple_table")

add_page("admin_system_status", "System Status / Logs", "Admin & Dev", "simple_table")





# ============================================================

# TOP BAR

# ============================================================



def render_top_bar(active_page_label: str):

    st.markdown(

        f"""

<div class="top-bar">

  <div class="top-bar-left">

    Qubic Behavioral Feedback Engine

  </div>

  <div class="top-bar-right">

    <div class="chip">{active_page_label}</div>

  </div>

</div>

        """,

        unsafe_allow_html=True,

    )

    nav_items = [
        ("Landing", "landing_public"),
        ("Home", "home_dashboard"),
        ("Daily Tasks", "daily_tasks"),
        ("XP & Achievements", "achievements_list"),
        ("Wallet", "wallet_dashboard"),
        ("Shop", "shop_home"),
        ("Notifications", "notifications_center"),
        ("Invest", "invest_case"),
    ]
    cols = st.columns(len(nav_items))
    for (label, target), col in zip(nav_items, cols):
        col.button(label, on_click=navigate_to, args=(target,), use_container_width=True, key=f"topnav_{label}")





# ============================================================

# TEMPLATE RENDERERS

# ============================================================

def tpl_login(page: Page):

    render_top_bar(page.label)

    with st.container():

        st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Login")

    st.write("Sign in to personalize XP, coins and test history for this session.")

    st.write("")

    st.markdown('<div class="card-hero">', unsafe_allow_html=True)
    if st.button("Sign in with Google"):
        faux_email = "you@example.com"
        set_user_profile("Google User", faux_email)
        grant_xp(15, "Login", "Google quick sign-in bonus")
        st.success("Signed in with Google (placeholder). XP +15.")
    st.markdown("</div>", unsafe_allow_html=True)

    email = st.text_input("Email")

    password = st.text_input("Password", type="password")

    remember = st.checkbox("Remember me")

    col1, col2 = st.columns([1, 1])

    with col1:

        if st.button("Log In"):

            username = email.strip() or "Guest"

            state = get_user_state()

            state["username"] = username
            state["email"] = email.strip() if email else state.get("email", "you@example.com")

            grant_xp(10, "Login", "Login bonus")

            st.success(f"Logged in as {username}. XP +10 to get you started.")

    with col2:

        st.write("")

    st.write("")

    action_cols = st.columns(2)
    action_cols[0].button("Forgot password", on_click=navigate_to, args=("forgot_password",), use_container_width=True)
    action_cols[1].button("Create an account", on_click=navigate_to, args=("register",), use_container_width=True)
    st.button("Skip to dashboard", on_click=navigate_to, args=("home_dashboard",), use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)



#=================================

def tpl_register(page: Page):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Create an account")

    st.write("Create credentials so your behavioral profile can be personalized. In this session data stays locally; hook up your backend to persist it.")



    username = st.text_input("Username")

    email = st.text_input("Email")

    password = st.text_input("Password", type="password")

    confirm = st.text_input("Confirm Password", type="password")

    st.checkbox("I agree to the Terms and Privacy Policy")



    if st.button("Sign Up"):
        state = get_user_state()
        chosen = username.strip() or email.strip() or "Member"
        state["username"] = chosen
        if email:
            state["email"] = email.strip()
        st.success(f"Account created for {chosen}. You can jump into the dashboard now.")
        st.button("Go to dashboard", on_click=navigate_to, args=("home_dashboard",), use_container_width=True, key="register_to_home")
    st.markdown("---")
    st.markdown('<div class="card-hero">', unsafe_allow_html=True)
    if st.button("Quick start as guest"):
        set_user_profile("Guest", email or "guest@example.com")
        grant_xp(10, "Signup", "Guest quick start bonus")
        st.success("Guest profile initialized. XP +10. Jump into the dashboard.")
        st.button("Open dashboard", on_click=navigate_to, args=("home_dashboard",), use_container_width=True, key="guest_to_home")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)






def tpl_landing(page: Page):
    render_top_bar(page.label)
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Main hero
    st.markdown("## Understand your on-chain behavior. Shape your future.")
    st.markdown(
        '<div class="card-hero">Design your behavioral loop with XP, streaks, coins, and scenario feedback. Connect data when ready.</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "The **Qubic Behavioral Feedback Engine** turns actions into scores, XP, and streaks so you "
        "can see how your habits evolve and what to adjust next. This instance runs in-session; connect "
        "a backend to persist your progress."
    )

    cta1, cta2, cta3 = st.columns(3)
    cta1.button("Start onboarding", on_click=navigate_to, args=("onboard_subjects",), use_container_width=True)
    cta2.button("Open dashboard", on_click=navigate_to, args=("home_dashboard",), use_container_width=True)
    cta3.button("See XP & achievements", on_click=navigate_to, args=("achievements_list",), use_container_width=True)
    st.button("Run a random simulation", on_click=navigate_to, args=("metrics_lab",), use_container_width=True)
    st.button("Why invest in this engine?", on_click=navigate_to, args=("invest_case",), use_container_width=True)

    st.write("---")
    st.markdown("### How this engine thinks")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Behavior Metrics**")
        st.write(
            "We compute TES, BSS, BMS, CFS, and event-level XP so you can see both macro momentum and "
            "micro-behavior changes."
        )
    with c2:
        st.markdown("**Feedback Loop**")
        st.write(
            "You take actions (simulated sessions), the system logs them, and the dashboard "
            "feeds back streaks, XP and summaries to nudge better decisions."
        )
    with c3:
        st.markdown("**Engagement Layer**")
        st.write(
            "Streaks, XP, coins, shop items and summaries are intentionally designed to keep you committed "
            "without dark patterns."
        )

    st.write("---")
    st.markdown(
        '''
<div class="footer">
  Session-only build of the Qubic Behavioral Feedback Engine UI. Connect real data sources to persist your outcomes.
</div>
        ''',
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

def tpl_onboard_subjects(page: Page):

    render_top_bar(page.label)

    state = get_user_state()

    current = state.get("onboard_focus", [])



    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Choose your behavior focus")

    st.write(

        "Tell the engine what kind of on-chain behavior you care about. "

        "This does not change any real wallet; it shapes how we summarize your runs."

    )



    options = [

        ("calm_holder", "Calm Qubic Holder", "Occasional rebalancing, low churn."),

        ("active_trader", "Active Short-Term Trader", "Frequent moves, lots of emotional load."),

        ("launchpad_farmer", "Launchpad / Airdrop Farmer", "Chasing new Qubic opportunities."),

        ("governance_user", "Governance & Protocol User", "Focused on proposals and long-term impact."),

    ]



    new_selection = []

    for key, title, desc in options:

        checked = st.checkbox(

            f"{title} - {desc}",

            value=(key in current),

        )

        if checked:

            new_selection.append(key)



    if st.button("Save behavior focus"):

        state["onboard_focus"] = new_selection

        record_activity_day()

        st.success("Behavior focus saved for this session.")



    st.markdown("</div>", unsafe_allow_html=True)





def tpl_simple_info(page: Page, title: str = None, body: str = None):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown(f"### {title or page.label}")

    st.write(body or "Static informational page placeholder.")

    st.markdown("</div>", unsafe_allow_html=True)





def tpl_legal(page: Page):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown(f"### {page.label}")

    st.write("Long-form text content would go here. This is a simple placeholder.")

    for i in range(5):

        st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer pretium felis ut urna.")

    st.markdown("</div>", unsafe_allow_html=True)





def tpl_home_dashboard(page: Page):
    render_top_bar(page.label)
    state = get_user_state()
    task_state = ensure_daily_task_state()
    level = level_from_xp(state["xp"])
    next_level_xp = level * 1000
    to_next = max(0, next_level_xp - state["xp"])
    streak = compute_streak(state["days_active"])
    tests_taken = state["tests_taken"]
    last_attempt = get_last_test_attempt()
    last_active_day = state["days_active"][-1] if state["days_active"] else "No activity yet"
    today = date.today()
    xp_by_day = get_xp_by_day()

    def _sum_xp(days_back: int, span: int) -> int:
        return sum(
            xp_by_day.get((today - timedelta(days=offset)).isoformat(), 0)
            for offset in range(days_back, days_back + span)
        )

    xp_last_7 = _sum_xp(0, 7)
    xp_prev_7 = _sum_xp(7, 7)
    if xp_last_7 > xp_prev_7:
        momentum_note = "Momentum is increasing. Keep stacking consistent runs."
    elif xp_last_7 == xp_prev_7 and xp_last_7 > 0:
        momentum_note = "Momentum is steady. A small stretch run could lift it."
    elif xp_last_7 == 0:
        momentum_note = "No XP in the last 7 days. Try one tiny run to restart momentum."
    else:
        momentum_note = "Momentum dipped a bit. A short, low-stress run can reset the curve."

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("### Home Dashboard")
    st.write(
        "Behavior HQ: track your on-chain habits, micro-missions, and momentum in one place."
    )
    st.write(f"Logged in as: **{state['username']}**")

    col_top = st.columns(2)
    with col_top[0]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Behavior Profile**")
        st.write(f"Level: {level}  |  XP: {state['xp']} (to next: {to_next})")
        st.write(f"Current streak: {streak} day(s)")
        st.write(f"Last active day: {last_active_day}")
        st.write(f"Coins: {state['coins']}  |  Gems: {state['gems']}  |  Tokens: {state.get('token_balance', 0.0)}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_top[1]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Behavior Momentum**")
        st.write(f"XP last 7 days: {xp_last_7}")
        st.write(f"XP previous 7 days: {xp_prev_7}")
        st.write(momentum_note)
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    col_cards = st.columns(2)
    with col_cards[0]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Today's Micro-Missions**")
        st.write("Tiny nudges to keep streaks alive. One tap per mission per day.")
        missions = [
            {"id": "calm_holder_day", "label": "Simulate 1 Calm Holder day", "xp": 25},
            {"id": "stress_trader", "label": "Run 1 High-Stress Trader scenario", "xp": 30},
            {"id": "review_runs", "label": "Review your last 3 runs", "xp": 20},
        ]
        today_key = today.isoformat()
        done_today = set(task_state.get(today_key, []))
        completed_count = 0
        for mission in missions:
            already_done = mission["id"] in done_today
            checked = st.checkbox(
                mission["label"],
                value=already_done,
                key=f"home_mission_{mission['id']}",
            )
            if checked and not already_done:
                grant_xp(mission["xp"], "Daily micro-mission", mission["label"])
                task_state.setdefault(today_key, []).append(mission["id"])
                done_today.add(mission["id"])
                st.success(f"+{mission['xp']} XP and coins logged.")
            if mission["id"] in done_today:
                completed_count += 1
        st.write(f"Completed today: {completed_count}/{len(missions)}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_cards[1]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Latest Scenario Snapshot**")
        if last_attempt:
            st.write(f"{last_attempt['name']} ({last_attempt['subject']})")
            st.write(f"Score: {last_attempt['correct']} / {last_attempt['total']} ({last_attempt['percent']}%)")
            st.write(f"XP gained: {last_attempt['xp_gained']} | Time: {last_attempt['time_sec']} s")
            st.write("Interpretation: use small, quick runs to keep the behavioral loop warm.")
        else:
            st.write("No scenarios recorded yet. Start a run to generate XP and momentum.")
        st.markdown("</div>", unsafe_allow_html=True)

    link_cols = st.columns(6)
    link_cols[0].button("Daily Tasks", on_click=navigate_to, args=("daily_tasks",), use_container_width=True, key="home_to_tasks")
    link_cols[1].button("XP Overview", on_click=navigate_to, args=("xp_overview",), use_container_width=True, key="home_to_xp")
    link_cols[2].button("Achievements", on_click=navigate_to, args=("achievements_list",), use_container_width=True, key="home_to_achievements")
    link_cols[3].button("Metrics Lab", on_click=navigate_to, args=("metrics_lab",), use_container_width=True, key="home_to_metrics")
    link_cols[4].button("Wallet", on_click=navigate_to, args=("wallet_dashboard",), use_container_width=True, key="home_to_wallet")
    link_cols[5].button("Shop", on_click=navigate_to, args=("shop_home",), use_container_width=True, key="home_to_shop")

    quick_cols = st.columns(3)
    quick_cols[0].button("Notifications", on_click=navigate_to, args=("notifications_center",), use_container_width=True, key="home_to_notifications")
    quick_cols[1].button("Announcements", on_click=navigate_to, args=("announcements",), use_container_width=True, key="home_to_announcements")
    quick_cols[2].button("Milestones", on_click=navigate_to, args=("milestones_roadmap",), use_container_width=True, key="home_to_milestones")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Quick Actions Hub**")
    action_cols = st.columns(4)
    action_cols[0].button("Run scenario", on_click=navigate_to, args=("scenario_library",), use_container_width=True, key="home_quick_scenario")
    action_cols[1].button("Random simulation", on_click=navigate_to, args=("metrics_lab",), use_container_width=True, key="home_quick_sim")
    action_cols[2].button("Token trading", on_click=navigate_to, args=("token_trading",), use_container_width=True, key="home_quick_trade")
    action_cols[3].button("Invest case", on_click=navigate_to, args=("invest_case",), use_container_width=True, key="home_quick_invest")
    st.write("Stay in flow: jump between scenarios, simulations, wallet, and invest case without dead ends.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Surface latest XP events inline for immediate feedback
    if state["xp_events"]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Latest activity pulse**")
        latest = list(reversed(state["xp_events"]))[:5]
        st.table({
            "When": [e["ts"] for e in latest],
            "Source": [e["source"] for e in latest],
            "XP": [e["amount"] for e in latest],
            "Description": [e["description"] for e in latest],
        })
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**Session Data Notice**")
    render_demo_disclaimer(
        "This interface runs locally for now; connect APIs and storage to sync your real activity."
    )
    st.markdown("</div>", unsafe_allow_html=True)


def tpl_invest_case(page: Page):
    """Why invest in this behavioral feedback engine."""
    render_top_bar(page.label)
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("### Why You Should Invest")
    st.markdown(
        '<div class="card-hero">A session-only prototype that proves engagement mechanics: XP, streaks, shop, wallet, and behavior scenarios. Connect data to turn it into a live product.</div>',
        unsafe_allow_html=True,
    )
    st.write("**Reasons to believe:**")
    st.write("- Proven engagement loop: streaks + XP + achievements keep users returning.")
    st.write("- Synthetic wallet/trading hooks ready to connect to real rails.")
    st.write("- Scenario library designed for on-chain behavior, not generic quizzes.")
    st.write("- Metrics lab generates behavioral TES/BSS/BMS signals from existing state.")
    st.write("- Simple token economy demo (coins/tokens) showing buy/sell/swap flows.")
    st.write("- Clean, blue-accent UI with low friction login/onboarding.")

    st.write("---")
    st.write("**Next steps for investors:**")
    bullets = [
        "Wire real data sources (wallets, events) to replace session-only storage.",
        "Tune XP curves and achievements using real cohorts.",
        "Connect payment rails for tokens/coins; secure auth (OAuth/Google).",
        "Deploy A/B experiments on missions and scenario difficulty.",
    ]
    for b in bullets:
        st.write(f"- {b}")

    st.write("---")
    st.markdown("#### Product pillars")
    st.write("- **Engage:** XP, streaks, missions, achievements, shop, wallet.")
    st.write("- **Reflect:** Metrics lab, scenario results, milestones, announcements.")
    st.write("- **Act:** Scenario runs, trading desk, swap, daily tasks, notifications.")
    st.write("- **Grow:** Leaderboards, personal bests, recommendations (hooks ready).")

    st.write("---")
    nav = st.columns(4)
    nav[0].button("Open dashboard", on_click=navigate_to, args=("home_dashboard",), use_container_width=True)
    nav[1].button("Run simulation", on_click=navigate_to, args=("metrics_lab",), use_container_width=True)
    nav[2].button("Wallet & trading", on_click=navigate_to, args=("wallet_dashboard",), use_container_width=True)
    nav[3].button("Shop", on_click=navigate_to, args=("shop_home",), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)




def tpl_subject_hub(page: Page):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Subject Selection Hub")

    st.write("Pick what you want to focus on today.")



    subjects = ["Algebra 1", "Geometry", "Physics", "Programming", "Chemistry", "Mixed Random"]

    for s in subjects:

        st.write(f"- {s}")



    st.markdown("</div>", unsafe_allow_html=True)





def tpl_daily_tasks(page: Page):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Daily Tasks / Missions")

    st.write("Small missions to keep you moving forward.")



    tasks = [

        ("Complete 1 Algebra test", False),

        ("Review 5 missed questions", True),

        ("Earn 100 XP today", False),

    ]

    for name, done in tasks:

        st.checkbox(name, value=done)



    st.markdown("</div>", unsafe_allow_html=True)





def tpl_streak_overview(page: Page):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Streak Overview")

    st.write("Basic streak view placeholder with sample data.")



    data = {

        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],

        "Completed?": ["Yes", "Yes", "Yes", "Yes", "Yes", "No", "No"],

    }

    st.table(data)

    st.markdown("</div>", unsafe_allow_html=True)





def tpl_notifications_center(page: Page):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Notifications Center")

    st.write("Recent system messages, reminders and alerts.")

    st.write("- [Yesterday] Level-up to Level 7 - +500 XP.")

    st.write("- [2 days ago] New Algebra test added: Systems (Word Problems).")

    st.write("</div>", unsafe_allow_html=True)





def tpl_settings_form(page: Page, title: str = None):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown(f"### {title or page.label}")

    st.write("Simple settings-style form placeholder.")



    st.text_input("Sample text field", value="")

    st.checkbox("Enable sample option")

    st.selectbox("Sample mode", ["Off", "Low", "Medium", "High"])



    col1, col2 = st.columns(2)

    with col1:

        if st.button("Save changes"):

            st.success("Settings saved for this session.")

    with col2:

        if st.button("Reset"):

            st.info("Reset pressed.")



    st.markdown("</div>", unsafe_allow_html=True)





def tpl_change_password(page: Page):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Change Password")

    old = st.text_input("Old password", type="password")

    new = st.text_input("New password", type="password")

    confirm = st.text_input("Confirm new password", type="password")

    if st.button("Update password"):

        st.info("Session-only placeholder: no password change is executed.")

    st.markdown("</div>", unsafe_allow_html=True)





def tpl_danger_confirm(page: Page):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Delete / Deactivate Account")

    st.write("Be careful: this is a destructive action. In this session nothing actually happens.")

    st.text_area("Optional: tell us why you're leaving.")

    if st.button("I understand, delete my account"):

        st.warning("Session-only placeholder: account deletion not yet wired up.")

    st.markdown("</div>", unsafe_allow_html=True)





def tpl_simple_table(page: Page, title: str = None):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown(f"### {title or page.label}")

    st.write("Simple table placeholder (demo).")

    st.table(

        {

            "Column A": ["Row 1", "Row 2", "Row 3"],

            "Column B": ["Value 1", "Value 2", "Value 3"],

        }

    )

    st.markdown("</div>", unsafe_allow_html=True)





def tpl_simple_list(page: Page, title: str = None):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown(f"### {title or page.label}")

    st.write("Simple list placeholder. Replace with real content.")

    for i in range(1, 6):

        st.write(f"- Item {i}")

    st.markdown("</div>", unsafe_allow_html=True)





def tpl_account_overview(page: Page):

    render_top_bar(page.label)
    state = get_user_state()

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### My Account Overview")

    st.write("Basic summary of your account.")

    st.write(f"- Username: {state.get('username', 'user')}")

    st.write(f"- Email: {state.get('email', 'you@example.com')}")

    st.write(f"- Token balance: {state.get('token_balance', 0.0)}")

    st.write("- Joined: this session (persist once connected)")

    st.markdown("</div>", unsafe_allow_html=True)





def tpl_profile_public(page: Page):

    render_top_bar(page.label)
    state = get_user_state()

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Public Profile")

    st.write("This is how a public profile could look in minimal black & white.")

    st.write(f"- Username: {state.get('username', 'user')}")

    st.write("- Level: 7")

    st.write("- Favorite subjects: Algebra, Physics")

    st.markdown("</div>", unsafe_allow_html=True)





def tpl_profile_customization(page: Page):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Profile Customization Hub")

    st.write("Choose your icon, banner, and other appearance options.")

    st.text_input("Bio")

    st.selectbox("Default subject to show", ["Algebra", "Physics", "Programming"])

    st.button("Save appearance")

    st.markdown("</div>", unsafe_allow_html=True)





def tpl_xp_overview(page: Page):
    render_top_bar(page.label)
    state = get_user_state()
    level = level_from_xp(state["xp"])
    streak = compute_streak(state["days_active"])
    best_streak = compute_best_streak(state["days_active"])
    xp_by_day = get_xp_by_day()

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("### XP Overview")

    nav_row = st.columns(5)
    nav_row[0].button("Overview", use_container_width=True, disabled=True)
    nav_row[1].button("History", on_click=navigate_to, args=("xp_history",), use_container_width=True)
    nav_row[2].button("By subject", on_click=navigate_to, args=("xp_subject_breakdown",), use_container_width=True)
    nav_row[3].button("Weekly/Monthly", on_click=navigate_to, args=("xp_weekly_graph",), use_container_width=True)
    nav_row[4].button("Metrics Lab", on_click=navigate_to, args=("metrics_lab",), use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.write("**Username**")
        st.write(state["username"])
    with col2:

        st.write("**Level**")

        st.write(level)

    with col3:

        st.write("**Total XP**")

        st.write(state["xp"])

    with col4:
        st.write("**Current streak (days)**")
        st.write(f"{streak} (best: {best_streak})")

    st.write("---")
    st.markdown("#### XP events (latest 10)")
    if state["xp_events"]:
        events = list(reversed(state["xp_events"]))[:10]
        table = {

            "Time (UTC)": [e["ts"] for e in events],

            "Source": [e["source"] for e in events],

            "Amount": [e["amount"] for e in events],

            "Description": [e["description"] for e in events],

        }

        st.table(table)

    else:
        st.write("No XP events yet. Take a test (using the test taking page) to generate some.")

    st.write("---")
    st.markdown("#### Behavior story")
    active_days = len(state["days_active"])
    story_lines = []
    if active_days == 0:
        story_lines.append("No active days yet. Run one short scenario to start your momentum.")
    else:
        story_lines.append(
            f"Active on {active_days} day(s) with a best streak of {best_streak}."
        )
        # Top source insight
        source_totals = {}
        for e in state["xp_events"]:
            source_totals[e["source"]] = source_totals.get(e["source"], 0) + int(e["amount"])
        if source_totals:
            top_source = max(source_totals.items(), key=lambda x: x[1])[0]
            story_lines.append(f"Most XP comes from '{top_source}' right now (behavior channel lens).")
        # Recent momentum
        today = date.today()
        recent = []
        for offset in range(3):
            d = (today - timedelta(days=offset)).isoformat()
            recent.append(xp_by_day.get(d, 0))
        if all(v == 0 for v in recent):
            story_lines.append("The last 3 days show zero XP. Try a small micro-mission to reset.")
        elif recent[0] > recent[1] >= recent[2]:
            story_lines.append("Your last 3 days show rising XP that's an improving momentum pattern.")
        elif recent[0] < recent[1]:
            story_lines.append("Yesterday outperformed today. A tiny run can keep the slope positive.")
        else:
            story_lines.append("Steady output. Keep compounding small wins.")
    for line in story_lines:
        st.write(f"- {line}")

    st.write("---")
    st.markdown("#### ASCII XP sparkline (last 7 days)")
    spark_rows = []
    today = date.today()
    for offset in range(6, -1, -1):
        d = today - timedelta(days=offset)
        d_str = d.isoformat()
        xp = xp_by_day.get(d_str, 0)
        if xp == 0:
            bucket = "."
        elif xp <= 50:
            bucket = "#"
        elif xp <= 100:
            bucket = "##"
        elif xp <= 200:
            bucket = "###"
        else:
            bucket = "####"
        spark_rows.append(f"{d.strftime('%a')}: {bucket} ({xp} XP)")
    if spark_rows:
        for row in spark_rows:
            st.text(row)
    else:
        st.write("No XP data yet to show a sparkline.")

    link_row = st.columns(3)
    link_row[0].button("XP history", on_click=navigate_to, args=("xp_history",), use_container_width=True)
    link_row[1].button("XP by subject", on_click=navigate_to, args=("xp_subject_breakdown",), use_container_width=True)
    link_row[2].button("Achievements", on_click=navigate_to, args=("achievements_list",), use_container_width=True)
    st.button("Open shop to redeem coins", on_click=navigate_to, args=("shop_home",), use_container_width=True)
    render_demo_disclaimer("XP values here reflect the current session until persistence is wired up.")
    st.markdown("</div>", unsafe_allow_html=True)






def tpl_simple_graph(page: Page):

    # Minimal placeholder: just show a small trend table

    tpl_simple_table(page, title=page.label)





def tpl_test_library(page: Page):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)



    st.markdown(f"### {page.label}")

    st.write(

        "In the full product, this would be a catalog of **behavior scenarios** you can simulate: "

        "different trading styles, risk profiles, and decision patterns on Qubic."

    )



    st.write("Below are core scenarios you can run right now:")

    scenarios = [
        ("Calm Long-Term Holder", "Infrequent moves, strong conviction, low churn.", "Medium"),
        ("Hyperactive Short-Term Trader", "Frequent trades, high churn, high emotional load.", "High"),
        ("Launchpad & Airdrop Farmer", "Hopping between new tokens and opportunities.", "High"),
        ("Governance Steward", "Proposal participation, long-horizon alignment.", "Medium"),
        ("Social Hype Spike", "Rapid attention swings driven by social signals.", "High"),
    ]

    for idx, (title, desc, difficulty) in enumerate(scenarios):
        cols = st.columns([5, 3, 2, 2])
        with cols[0]:
            st.markdown(f"**{title}**")
            st.write(desc)
        with cols[1]:
            st.write(f"Difficulty: {difficulty}")
        with cols[2]:
            st.write("Channel: Behavior")
        with cols[3]:
            if st.button("Start", key=f"start_lib_{idx}"):
                set_current_scenario(f"scenario_{idx}", title, "Behavior")
                navigate_to("scenario_run")
            if st.button("View detail", key=f"detail_lib_{idx}"):
                target_id = "scenario_calibration"
                if idx == 1:
                    target_id = "scenario_volatility"
                elif idx == 2:
                    target_id = "scenario_airdrop"
                elif idx == 3:
                    target_id = "scenario_governance"
                elif idx == 4:
                    target_id = "scenario_social"
                navigate_to(target_id)

    st.write(
        "Pick a scenario detail to see requirements, then run it via **Scenario Run (Simulated)** "
        "to generate XP, streak days, and achievements tied to behavior rather than academics."
    )

    st.markdown("</div>", unsafe_allow_html=True)



def tpl_test_detail(page: Page):

    render_top_bar(page.label)

    meta = page.meta or {}

    name = meta.get("test_name", page.label)

    subject = meta.get("subject", "General")



    state = get_user_state()

    last_attempt = get_last_attempt_for_test(page.id)



    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown(f"### Scenario: {name}")

    st.write(f"Behavior channel: {subject}")

    st.write("Description: Scenario parameters and prompts are simulated here for planning and reflection.")



    st.write("**Info**")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write("Tasks/steps: 3-5 (simulated)")

    with col2:

        st.write("Estimated time: 10-20 min")

    with col3:

        st.write("Difficulty: Medium")



    st.write("**Requirements**")

    st.write("- Define your guardrails (risk, time, emotional budget)")

    st.write("- Set a simple success criteria for this run")



    st.write("**Key signals to watch**")

    st.write("- Momentum vs discipline tension")

    st.write("- Emotional spike triggers")

    st.write("- XP gain vs churn")



    st.write("---")

    st.markdown("#### Your history on this test (demo)")

    if last_attempt:

        st.write(f"Last score: {last_attempt['correct']} / {last_attempt['total']} ({last_attempt['percent']}%)")

        st.write(f"Last XP gained: {last_attempt['xp_gained']}")

        st.write(f"Last taken: {last_attempt['timestamp']}")

    else:

        st.write("You have not recorded a result for this test yet in this session.")



    st.write("---")

    col1, col2 = st.columns([1, 1])

    with col1:

        if st.button("Start scenario", key=f"start_{page.id}"):

            # In this session, "starting" remembers which scenario is current

            set_current_scenario(page.id, name, subject)

            st.info(

                "Scenario started. Open **Scenario Run (Simulated)** to log the outcome and XP."

            )

    with col2:

        if st.button("Practice similar questions", key=f"practice_{page.id}"):

            st.info("In a full app, this would open a tailored practice set for this topic.")



    st.markdown("</div>", unsafe_allow_html=True)







def tpl_test_taking(page: Page):

    render_top_bar(page.label)

    state = get_user_state()

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Scenario Run (Simulated)")



    test_id = st.session_state.get("current_test_id")

    test_name = st.session_state.get("current_test_name", "No test selected")

    test_subject = st.session_state.get("current_test_subject", "General")



    if not test_id:

        st.write("No active scenario.")

        st.write("Open any scenario detail page and press **Start scenario** first.")

        st.markdown("</div>", unsafe_allow_html=True)

        return



    st.write(f"Active scenario: **{test_name}** ({test_subject})")

    st.write("Instead of step-by-step flow, this lets you simulate the final outcome for XP and streaks.")



    col1, col2 = st.columns(2)

    with col1:

        total = st.number_input("Total questions", min_value=1, max_value=50, value=15, step=1)

        correct = st.number_input("Correct answers", min_value=0, max_value=50, value=13, step=1)

        if correct > total:

            st.warning("Correct cannot exceed total; it will be clipped when saved.")

    with col2:

        minutes = st.number_input("Time taken (minutes)", min_value=1, max_value=180, value=15, step=1)

        st.write("This run will award XP based on your percentage score (up to 200 XP).")



    if st.button("Save simulated result"):

        record_test_attempt(

            test_id=test_id,

            name=test_name,

            subject=test_subject,

            correct=int(correct),

            total=int(total),

            time_sec=int(minutes * 60),

        )

        st.success(

            "Result saved for this session. Open **Scenario Results Summary** to see the breakdown and XP gained."

        )

    if st.button("Quick random outcome"):
        total_rand = random.randint(5, 20)
        correct_rand = random.randint(0, total_rand)
        minutes_rand = random.randint(3, 20)
        record_test_attempt(
            test_id=test_id,
            name=test_name,
            subject=test_subject,
            correct=int(correct_rand),
            total=int(total_rand),
            time_sec=int(minutes_rand * 60),
        )
        st.success(
            f"Random outcome saved: {correct_rand}/{total_rand} in {minutes_rand} min. XP and coins updated."
        )

    st.write("---")
    links = st.columns(3)
    links[0].button("View results", on_click=navigate_to, args=("test_results_summary",), use_container_width=True)
    links[1].button("Scenario library", on_click=navigate_to, args=("scenario_library",), use_container_width=True)
    links[2].button("Metrics lab", on_click=navigate_to, args=("metrics_lab",), use_container_width=True)



    st.markdown("</div>", unsafe_allow_html=True)



def tpl_test_results(page: Page):
    render_top_bar(page.label)
    state = get_user_state()
    last_attempt = get_last_test_attempt()

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("### Scenario Results Summary")

    if not last_attempt:
        st.write("No scenario results recorded in this session yet.")
        st.write("Open a scenario detail, start it, and log a simulated result in **Scenario Run (Simulated)**.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.write(f"**Last scenario:** {last_attempt['name']} ({last_attempt['subject']})")
    st.write(f"Taken at (UTC): {last_attempt['timestamp']}")

    st.write("")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.write("**Score**")
        st.write(f"{last_attempt['correct']} / {last_attempt['total']}")
    with col2:
        st.write("**Percentage**")
        st.write(f"{last_attempt['percent']}%")
    with col3:
        st.write("**XP earned**")
        st.write(f"+{last_attempt['xp_gained']} XP")
    with col4:
        st.write("**Time taken**")
        st.write(f"{last_attempt['time_sec']} s")

    st.write("")
    # Simple psychological messaging / near-miss feedback
    pct = last_attempt["percent"]
    if pct >= 95:
        st.write("You absolutely crushed this - you're very close to mastery on this topic.")
    elif 80 <= pct < 95:
        st.write("So close to perfection. A bit more focused practice could push this to 100%.")
    elif 50 <= pct < 80:
        st.write("Solid foundation. Target a few weak areas to unlock a big jump next time.")
    else:
        st.write("Tough run. Treat this as a learning rep-small, calm repetitions build confidence.")

    render_demo_disclaimer("Scenario results and XP are stored for this session.")
    st.markdown("</div>", unsafe_allow_html=True)


def tpl_shop_page(page: Page):
    render_top_bar(page.label)
    state = get_user_state()

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f"### {page.label}")

    st.markdown(
        f"**Balance:** {state['coins']} coins | {state['gems']} gems (earned from your XP). "
        "Cosmetic placeholder until payment rails are connected."
    )

    st.write("---")

    st.write("Filters:")

    categories = {
        "All": None,
        "Themes": "theme",
        "Boosts": "boost",
        "Cosmetics": "icons_pack archetype_skins banner".split(),
        "Streak tools": "streak_freeze".split(),
    }
    selected_cat = st.selectbox("Category", list(categories.keys()), index=0)
    show_affordable = st.checkbox("Show only affordable items", value=False)

    st.write("---")
    st.write("Shop items:")

    items = [
        {"id": "theme_mono", "name": "Monochrome Theme", "desc": "Strict black & white UI mode.", "price": 200, "tag": "theme"},
        {"id": "theme_blueprint", "name": "Blueprint Theme", "desc": "Light-blue accent layout inspired by technical diagrams.", "price": 240, "tag": "theme"},
        {"id": "boost_xp_2x", "name": "XP Boost x2 (1 day)", "desc": "Double XP from tests for 24h (placeholder).", "price": 300, "tag": "boost"},
        {"id": "icons_pack", "name": "Custom Icon Pack", "desc": "Extra profile icons (cosmetic).", "price": 150, "tag": "cosmetic"},
        {"id": "banner_set", "name": "Banner Set", "desc": "Header banners to personalize your profile.", "price": 180, "tag": "cosmetic"},
        {"id": "streak_freeze", "name": "Streak Freeze", "desc": "Protect your streak once when you miss a day. Cosmetic placeholder.", "price": 220, "tag": "streak"},
        {"id": "momentum_insight", "name": "Momentum Insight Pack", "desc": "Unlock extra textual insights on XP Overview for the next week.", "price": 180, "tag": "boost"},
        {"id": "archetype_skins", "name": "Behavior Archetype Skins", "desc": "Cosmetic avatars: Calm Holder, Hyper Trader, Governance Steward.", "price": 260, "tag": "cosmetic"},
    ]

    for item in items:
        if show_affordable and state["coins"] < item["price"]:
            continue
        tag = item["tag"]
        if selected_cat != "All":
            allowed = categories[selected_cat]
            if allowed is None:
                pass
            elif isinstance(allowed, list):
                if tag not in allowed and item["id"] not in allowed:
                    continue
            elif allowed and allowed not in item["id"] and allowed != tag:
                continue

        cols = st.columns([3, 5, 2, 2])

        with cols[0]:

            st.write(item["name"])

        with cols[1]:

            st.write(item["desc"])

        with cols[2]:

            st.write(item["price"])

        with cols[3]:

            if st.button("Buy", key=f"buy_{item['id']}"):
                if state["coins"] >= item["price"]:
                    state["coins"] -= item["price"]
                    record_activity_day()
                    st.success(f"Purchased {item['name']}.")
                else:
                    st.warning("Not enough coins.")
    st.write(
        "In a real implementation, these items would be governed by on-chain logic and Nostromo-launched tokens. "
        "Here they're cosmetic placeholders so you can design the flow."
    )
    link_row = st.columns(3)
    link_row[0].button("Back to dashboard", on_click=navigate_to, args=("home_dashboard",), use_container_width=True)
    link_row[1].button("View XP impact", on_click=navigate_to, args=("xp_overview",), use_container_width=True)
    link_row[2].button("Token trading desk", on_click=navigate_to, args=("token_trading",), use_container_width=True)
    render_demo_disclaimer("Purchases adjust your session coins; connect payments to make them real.")

    st.markdown("</div>", unsafe_allow_html=True)


def generate_ai_reply(message: str, state: Dict) -> str:
    """Small heuristic responder that reflects current session stats."""
    streak = compute_streak(state["days_active"])
    last = get_last_test_attempt()
    xp = state["xp"]
    coins = state["coins"]
    tokens = state.get("token_balance", 0.0)

    lower = message.lower()
    lines = []
    if "quest" in lower or "mission" in lower:
        lines.append("Try this micro-quest to keep momentum:")
        lines.append("- Run one quick scenario to keep the streak alive.")
        lines.append("- Claim a daily task; they award fast XP.")
        lines.append("- Log a tiny token trade to stay fluent without heavy risk.")
    elif "xp" in lower or "level" in lower:
        lines.append(f"You are at {xp} XP. Aim for the next 1,000 XP band.")
        lines.append("Do one simulation in Metrics Lab, then one scenario run. Repeat daily.")
    elif "streak" in lower or "consisten" in lower:
        lines.append(f"Streak: {streak} day(s). Protect it with a 5-minute action today.")
        lines.append("Schedule tomorrow's action now; streaks thrive on pre-commitment.")
    elif "token" in lower or "trade" in lower or "wallet" in lower:
        lines.append(f"Tokens: {round(tokens,2)} | Coins: {coins}.")
        lines.append("Use small sizing; review recent trades and set one guardrail before your next swap.")
    else:
        lines.append("Snapshot of your session:")
        lines.append(f"- XP: {xp}, Coins: {coins}, Streak: {streak} day(s).")
        if last:
            lines.append(f"- Last scenario: {last['name']} at {last['percent']}% (+{last['xp_gained']} XP).")
        lines.append("Next best step: one simulation, one scenario, and log it.")
    return "\n".join(lines)


def tpl_ai_assistant(page: Page):
    """AI helper (session-only) that summarizes your state and suggests next steps."""
    render_top_bar(page.label)
    state = get_user_state()
    history = ensure_chat_history()

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("### AI Coach")
    st.write("Ask for quests, streak help, XP plans, or trading nudges. Responses use your session stats only (no external model).")
    st.caption("Session data only. Refresh to clear.")

    stats = st.columns(4)
    stats[0].metric("XP", state["xp"])
    stats[1].metric("Coins", state["coins"])
    stats[2].metric("Streak (days)", compute_streak(state["days_active"]))
    stats[3].metric("Tokens", round(state.get("token_balance", 0.0), 2))

    st.markdown("#### Quick prompts")
    prompts = [
        ("Daily quest", "Give me a small quest for today"),
        ("Keep streak", "How do I keep my streak alive?"),
        ("XP plan", "How can I level up faster this week?"),
        ("Trading drill", "Suggest a low-risk trading drill"),
    ]
    qcols = st.columns(len(prompts))
    for (label, prompt), col in zip(prompts, qcols):
        if col.button(label):
            history.append({"role": "user", "text": prompt})
            history.append({"role": "assistant", "text": generate_ai_reply(prompt, state)})
            record_activity_day()

    st.markdown("#### Chat")
    with st.form("ai_chat_form"):
        user_msg = st.text_input("Ask the coach", key="ai_chat_input")
        submitted = st.form_submit_button("Send")
        if submitted and user_msg.strip():
            history.append({"role": "user", "text": user_msg.strip()})
            history.append({"role": "assistant", "text": generate_ai_reply(user_msg, state)})
            if len(history) > 40:
                del history[: len(history) - 40]
            record_activity_day()

    if history:
        st.markdown("##### Conversation")
        for msg in history[-12:]:
            role = msg.get("role", "user").capitalize()
            st.markdown(f"**{role}:** {msg.get('text', '')}")
    else:
        st.info("No messages yet. Send a question to start.")

    st.write("---")
    nav = st.columns(3)
    nav[0].button("Daily Tasks", on_click=navigate_to, args=("daily_tasks",), use_container_width=True)
    nav[1].button("Metrics Lab", on_click=navigate_to, args=("metrics_lab",), use_container_width=True)
    nav[2].button("Token Trading", on_click=navigate_to, args=("token_trading",), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def tpl_settings_list(page: Page):

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Settings")

    st.write("Choose a category on the left (in a full app this would highlight sections).")

    st.write("- Display")

    st.write("- Notifications")

    st.write("- Account")

    st.write("- Security")

    st.write("- Data")

    st.markdown("</div>", unsafe_allow_html=True)





# ============================================================

# TEMPLATE DISPATCH

# ============================================================







TEMPLATE_DISPATCH = {

    "landing": tpl_landing,

    "login": tpl_login,

    "register": tpl_register,

    "simple_info": tpl_simple_info,

    "legal": tpl_legal,

    "home_dashboard": tpl_home_dashboard,

    "subject_hub": tpl_subject_hub,

    "daily_tasks": tpl_daily_tasks,

    "streak_overview": tpl_streak_overview,

    "notifications_center": tpl_notifications_center,

    "settings_form": tpl_settings_form,

    "change_password": tpl_change_password,

    "danger_confirm": tpl_danger_confirm,

    "simple_table": tpl_simple_table,

    "simple_list": tpl_simple_list,

    "account_overview": tpl_account_overview,

    "profile_public": tpl_profile_public,
    "profile_customization": tpl_profile_customization,
    "xp_overview": tpl_xp_overview,
    "simple_graph": tpl_simple_graph,
    "test_library": tpl_test_library,
    "test_detail": tpl_test_detail,

    "test_taking": tpl_test_taking,
    "test_results": tpl_test_results,
    "shop_page": tpl_shop_page,
    "settings_list": tpl_settings_list,
    "onboard_subjects": tpl_onboard_subjects,
}


# ============================================================

# ENHANCED BEHAVIORAL PAGES (ADDâ-'ON BLOCK)

# ============================================================

# This block upgrades a lot of existing pages into true

# Qubic behavioral / XP / streak views, WITHOUT deleting

# anything above. It just:

#  - adds new template functions

#  - overrides TEMPLATE_DISPATCH for some templates

#  - patches PAGES[].template for XP & announcements pages

# ============================================================





def tpl_onboard_goals(page: Page):

    """Behavior-oriented goals onboarding."""

    render_top_bar(page.label)

    state = get_user_state()

    goals = state.get("behavior_goals", {})



    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Set your behavior goals")

    st.write(

        "These goals are **for you**, not for the app. The engine will just reflect back XP, "

        "streaks and summaries against what you say you care about."

    )



    goal1 = st.text_input(

        "Goal 1  reduce or change what?",

        value=goals.get("goal1", "Reduce random impulsive trades."),

    )

    goal2 = st.text_input(

        "Goal 2 maintain or increase what?",

        value=goals.get("goal2", "Maintain a consistent weekly plan."),

    )

    risk_tolerance = st.slider(

        "Risk comfort",

        min_value=1,

        max_value=10,

        value=goals.get("risk", 5),

    )

    note = st.text_area(

        "Optional note to your future self",

        value=goals.get("note", ""),

        help="This would normally not be shared just a reminder of why you care.",

    )



    if st.button("Save goals"):

        state["behavior_goals"] = {

            "goal1": goal1,

            "goal2": goal2,

            "risk": risk_tolerance,

            "note": note,

        }

        record_activity_day()

        st.success("Behavior goals saved for this session.")



    st.markdown("</div>", unsafe_allow_html=True)





def tpl_welcome_tour(page: Page):

    """Explains how the behavioral engine works."""

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Welcome tour")

    st.write(

        "This is a small tour of how this UI behaves like a **Qubic Behavioral Feedback Engine**, "

        "using XP, coins, streaks and synthetic scenarios."

    )



    st.markdown("#### Where to go in the sidebar")

    st.write("- **Home Dashboard**  summary of XP, coins, streak and last scenario run.")

    st.write("- **XP Overview Dashboard**  raw XP numbers and recent events.")

    st.write("- **XP History / Breakdown**  see XP by day and by behavior channel.")

    st.write("- **Test Taking (Generic)**  used here as a *scenario run* simulator.")

    st.write("- **Test Results Summary**  perâ-'scenario feedback, XP and nearâ-'miss messaging.")

    st.write("- **Shop**  coins = engagement currency you earn from XP (no real value).")

    st.write("- **Streak Overview & Achievements**  long 'term consistency, streaks, milestones.")



    st.write("")

    st.write(

        "Everything in this environment is **synthetic** no real wallets, no real trades, "

        "no financial advice. It's all about **feedback loops** and **psychology**, not money."

    )



    st.markdown("</div>", unsafe_allow_html=True)





def tpl_subject_hub_v2(page: Page):

    """Behavior focus hub instead of 'school subjects'."""

    render_top_bar(page.label)

    state = get_user_state()

    selected = state.get("onboard_focus", [])



    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Behavior Focus Hub")



    if not selected:

        st.write(

            "You havenâ-t told the engine what you care about yet. "

            "Go to **Onboarding: Choose Subjects** and pick behavior focus areas."

        )

        st.markdown("</div>", unsafe_allow_html=True)

        return



    labels = {

        "calm_holder": "Calm Qubic Holder",

        "active_trader": "Active Shortâ-'Term Trader",

        "launchpad_farmer": "Launchpad / Airdrop Farmer",

        "governance_user": "Governance & Protocol User",

    }



    st.write("You told us you care most about these behavior tracks:")

    for key in selected:

        st.write(f"- {labels.get(key, key)}")



    st.write(

        "Use these as **lenses** when you look at XP, streaks and scenario results. "

        "For example, an 'Active Short-Term Trader' might want high XP but low emotional strain."

    )



    st.markdown("</div>", unsafe_allow_html=True)





def tpl_daily_tasks_v2(page: Page):
    """Daily behavior missions instead of 'do 1 algebra test'."""
    render_top_bar(page.label)
    state = get_user_state()
    task_state = ensure_daily_task_state()
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("### Daily behavior missions")

    st.write(
        "Tiny wins each day are how you build behavior momentum. Check off a mission once per day to "
        "earn small XP and keep your streak warm."
    )

    missions = [
        {"id": "calm_holder_run", "label": "Run a Calm Holder scenario", "xp": 25},
        {"id": "stress_trader_run", "label": "Run a High-Stress Trader scenario", "xp": 30},
        {"id": "xp_check", "label": "Open XP Overview and reflect for 30 seconds", "xp": 15},
    ]

    today_key = date.today().isoformat()
    done_today = set(task_state.get(today_key, []))
    completed = 0

    st.write(f"Today's missions completed: {len(done_today)}/{len(missions)}")
    for mission in missions:
        already_done = mission["id"] in done_today
        checked = st.checkbox(
            mission["label"],
            value=already_done,
            key=f"daily_task_{mission['id']}",
        )
        if checked and not already_done:
            grant_xp(mission["xp"], "Daily mission", mission["label"])
            task_state.setdefault(today_key, []).append(mission["id"])
            done_today.add(mission["id"])
            st.success(f"+{mission['xp']} XP logged.")
        if mission["id"] in done_today:
            completed += 1

    st.write(
        "In a full version, these would tie to on-chain signals and governance actions. "
        "Here they just illustrate how daily nudges keep the feedback loop alive."
    )
    link_row = st.columns(3)
    link_row[0].button("View streaks", on_click=navigate_to, args=("streak_overview",), use_container_width=True)
    link_row[1].button("XP history", on_click=navigate_to, args=("xp_history",), use_container_width=True)
    link_row[2].button("Achievements", on_click=navigate_to, args=("achievements_list",), use_container_width=True)
    render_demo_disclaimer("Session data only for now; connect your data source to persist completions.")
    st.markdown("</div>", unsafe_allow_html=True)




def tpl_streak_overview_v2(page: Page):
    """Real streaks based on days_active, plus best streak."""
    render_top_bar(page.label)
    state = get_user_state()
    streak_current = compute_streak(state["days_active"])
    streak_best = compute_best_streak(state["days_active"])

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("### Streak overview")

    st.write(f"Current streak: **{streak_current}** day(s)")
    st.write(f"Best streak in this session: **{streak_best}** day(s)")

    st.write("---")
    st.markdown("#### Last 30 days activity (X = active, . = inactive)")

    today = date.today()
    active_set = {d for d in state["days_active"]}
    active_last_30 = 0
    lines = []
    for offset in range(29, -1, -1):
        d = today - timedelta(days=offset)
        d_str = d.isoformat()
        mark = "X" if d_str in active_set else "."
        if mark == "X":
            active_last_30 += 1
        lines.append(f"{d_str}: {mark}")
    for line in lines:
        st.text(line)
    st.write(f"Active days in last 30: {active_last_30}/30")

    st.write(
        "Streak psychology: streaks make consistency tangible, but losing one isn't failure it just "
        "resets the counter. A tiny action today restarts the line."
    )
    link_row = st.columns(3)
    link_row[0].button("Daily missions", on_click=navigate_to, args=("daily_tasks",), use_container_width=True)
    link_row[1].button("View XP", on_click=navigate_to, args=("xp_overview",), use_container_width=True)
    link_row[2].button("See milestones", on_click=navigate_to, args=("milestones_roadmap",), use_container_width=True)
    render_demo_disclaimer("Streaks are based on your activity in this session; connect persistence to lock them in.")

    st.markdown("</div>", unsafe_allow_html=True)




def tpl_notifications_center_v2(page: Page):

    """Notifications driven by XP events and scenario history."""

    render_top_bar(page.label)

    state = get_user_state()

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Notifications Center")
    nav_row = st.columns(2)
    nav_row[0].button("Notifications", use_container_width=True, disabled=True)
    nav_row[1].button("Announcements", on_click=navigate_to, args=("announcements",), use_container_width=True)



    st.write(

        "These notifications are generated from XP events and scenario results in this session. "
        "In a real Qubic deployment they'd connect to actual on-chain behavior."

    )



    if not state["xp_events"] and not state["test_history"]:

        st.write("No notifications yet. Run at least one scenario to see activity here.")

        st.markdown("</div>", unsafe_allow_html=True)

        return



    st.markdown("#### Recent XP events")

    if state["xp_events"]:

        events = list(reversed(state["xp_events"]))[:10]

        for e in events:

            st.write(f"- [{e['ts']}] +{e['amount']} XP | {e['description']}")

    else:

        st.write("No XP events logged yet.")



    st.write("---")

    st.markdown("#### Recent scenario results")

    if state["test_history"]:

        attempts = list(reversed(state["test_history"]))[:5]

        for a in attempts:

            st.write(

                f"- [{a['timestamp']}] {a['name']} | {a['percent']}% | +{a['xp_gained']} XP"

            )

    else:

        st.write("No scenario results recorded yet.")



    st.button("Open announcements / changelog", on_click=navigate_to, args=("announcements",), use_container_width=True)
    render_demo_disclaimer("Notifications reflect this session only until you connect live data.")


    st.markdown("</div>", unsafe_allow_html=True)





def tpl_announcements(page: Page):

    """Simple hard-coded changelog placeholder."""

    render_top_bar(page.label)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Announcements / Changelog")
    nav_row = st.columns(2)
    nav_row[0].button("Announcements", use_container_width=True, disabled=True)
    nav_row[1].button("Notifications", on_click=navigate_to, args=("notifications_center",), use_container_width=True)



    st.write("- v0.1 Initial Qubic behavior UI with XP, coins and streaks.")

    st.write("- v0.2 Added behavior focus onboarding and goals.")

    st.write("- v0.3 Wired scenario results into XP, lifetime stats and shop coins.")

    st.write("- v0.4 Started converting 'tests' into behavior archetype scenarios.")



    st.write("")

    st.write(

        "In a real hackathon submission, this page would track actual engine iterations: "

        "new metrics (TES/BSS/BMS/CFS), Qubic protocol hooks, and Nostromo launch readiness."

    )



    st.markdown("</div>", unsafe_allow_html=True)





# ------------------------ XP & STATS PAGES ------------------------





def tpl_xp_history(page: Page):

    """XP events + XP by day."""

    render_top_bar(page.label)

    state = get_user_state()

    by_day = get_xp_by_day()



    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### XP History Timeline")



    if not state["xp_events"]:

        st.write("No XP events yet. Log in and run a scenario to generate XP.")

        st.markdown("</div>", unsafe_allow_html=True)

        return



    st.markdown("#### Latest XP events")

    events = list(reversed(state["xp_events"]))[:20]

    table_events = {

        "Time (UTC)": [e["ts"] for e in events],

        "Source": [e["source"] for e in events],

        "Amount": [e["amount"] for e in events],

        "Description": [e["description"] for e in events],

    }

    st.table(table_events)



    st.write("---")

    st.markdown("#### XP by day (aggregated)")



    days_sorted = sorted(by_day.keys())

    table_days = {

        "Date": days_sorted,

        "XP": [by_day[d] for d in days_sorted],

    }

    st.table(table_days)



    st.markdown("</div>", unsafe_allow_html=True)





def tpl_xp_subject_breakdown(page: Page):

    """Treat 'subject' as a behavior channel for this session."""

    render_top_bar(page.label)

    state = get_user_state()

    breakdown = get_subject_xp_breakdown()



    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Behavior Channel XP Breakdown")



    if not breakdown:

        st.write("No scenario results yet. Save at least one result with the Test Taking page.")

        st.markdown("</div>", unsafe_allow_html=True)

        return



    rows = {

        "Behavior channel (subject field)": [],

        "XP": [],

        "Scenarios run": [],

    }

    for subj, info in breakdown.items():

        rows["Behavior channel (subject field)"].append(subj)

        rows["XP"].append(info["xp"])

        rows["Scenarios run"].append(info["tests"])



    st.table(rows)

    st.write(

        "Right now we reuse the `subject` label as a behavior channel. "

        "In the real engine these channels would be explicit dimensions like 'risk', 'frequency', 'conviction'."

    )



    st.markdown("</div>", unsafe_allow_html=True)





def tpl_xp_weekly_graph(page: Page):

    """XP over the last 7 days (table style)."""

    render_top_bar(page.label)

    by_day = get_xp_by_day()

    today = date.today()



    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Weekly XP Graph")



    if not by_day:

        st.write("No XP data yet for this week.")

        st.markdown("</div>", unsafe_allow_html=True)

        return



    rows = {"Day": [], "Date": [], "XP": []}

    for offset in range(6, -1, -1):

        d = today - timedelta(days=offset)

        d_str = d.isoformat()

        rows["Day"].append(d.strftime("%a"))

        rows["Date"].append(d_str)

        rows["XP"].append(by_day.get(d_str, 0))



    st.table(rows)

    st.write(

        "This is a minimal blackâ-'andâ-'white representation of XP over the last 7 days. "

        "Higher XP means more behavioral activity or stronger scenario results."

    )



    st.markdown("</div>", unsafe_allow_html=True)





def tpl_xp_monthly_graph(page: Page):

    """XP over the last 30 days (table style)."""

    render_top_bar(page.label)

    by_day = get_xp_by_day()

    today = date.today()

    start = today - timedelta(days=29)



    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Monthly XP Graph")



    if not by_day:

        st.write("No XP data yet for this month.")

        st.markdown("</div>", unsafe_allow_html=True)

        return



    rows = {"Date": [], "XP": []}

    cur = start

    while cur <= today:

        d_str = cur.isoformat()

        rows["Date"].append(d_str)

        rows["XP"].append(by_day.get(d_str, 0))

        cur = cur + timedelta(days=1)



    st.table(rows)

    st.write(

        "In a full UI this might be a line chart with tooltips; here it stays as a table to keep "

        "the pure blackâ-'andâ-'white spec."

    )



    st.markdown("</div>", unsafe_allow_html=True)





def tpl_lifetime_stats(page: Page):
    """Session lifetime stats based on your current state."""
    render_top_bar(page.label)
    state = get_user_state()
    streak_current = compute_streak(state["days_active"])
    streak_best = compute_best_streak(state["days_active"])



    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Lifetime Stats (this session)")



    st.table(

        {

            "Metric": [

                "Total XP",

                "Total coins",

                "Scenarios recorded",

                "XP events",

                "Active days",

                "Current streak (days)",

                "Best streak (days)",

            ],

            "Value": [

                state["xp"],

                state["coins"],

                state["tests_taken"],

                len(state["xp_events"]),

                len(state["days_active"]),

                streak_current,

                streak_best,

            ],

        }

    )



    st.write(

        "In production this would represent real Qubic behavior over months/years, not just this session. "

        "Here we just show how the **feedback layer** might summarize your journey."
    )

    st.markdown("</div>", unsafe_allow_html=True)


def tpl_achievements(page: Page):
    """Behavioral achievements rendered with progress and clear framing."""
    render_top_bar(page.label)
    state = get_user_state()
    catalog, best_streak = compute_achievements_catalog(state)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("### Achievements")
    st.write(
        "These mini-achievements turn repeated actions into visible milestones. "
        "Inspired by streak mechanics and micro-goals from apps like Duolingo/WHOOP."
    )

    rows = {
        "Name": [],
        "Description": [],
        "Status": [],
        "Progress": [],
    }
    for ach in catalog:
        rows["Name"].append(ach["name"])
        rows["Description"].append(ach["description"])
        rows["Status"].append("[UNLOCKED]" if ach["unlocked"] else "[LOCKED]")
        rows["Progress"].append(ach["progress"])

    st.table(rows)
    st.write(f"Best streak seen so far: {best_streak} day(s).")
    link_row = st.columns(3)
    link_row[0].button("Achievement list", on_click=navigate_to, args=("achievements_list",), use_container_width=True)
    link_row[1].button("Milestones roadmap", on_click=navigate_to, args=("milestones_roadmap",), use_container_width=True)
    link_row[2].button("View details", on_click=navigate_to, args=("achievement_detail",), use_container_width=True)
    st.button("Jump to invest case", on_click=navigate_to, args=("invest_case",), use_container_width=True)
    render_demo_disclaimer("Achievements unlock based on the actions you take in this session.")
    st.markdown("</div>", unsafe_allow_html=True)


def tpl_achievements_list(page: Page):
    """Show all achievements plus their progress."""
    render_top_bar(page.label)
    state = get_user_state()
    catalog, best_streak = compute_achievements_catalog(state)


    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Achievements directory")
    st.caption(f"Best streak so far: {best_streak} day(s).")

    nav_row = st.columns(3)
    nav_row[0].button("List", use_container_width=True, disabled=True)
    nav_row[1].button("Overview", on_click=navigate_to, args=("achievements",), use_container_width=True)
    nav_row[2].button("Milestones", on_click=navigate_to, args=("milestones_roadmap",), use_container_width=True)



    rows = {

        "ID": [],

        "Achievement": [],

        "Status": [],

        "Progress": [],

    }

    for ach in catalog:

        rows["ID"].append(ach["id"])

        rows["Achievement"].append(ach["name"])

        rows["Status"].append("Unlocked" if ach["unlocked"] else "Locked")

        rows["Progress"].append(ach["progress"])



    st.table(rows)

    ids = [a["id"] for a in catalog]

    if ids:

        selected = st.selectbox("View details for:", ids)

        st.session_state.selected_achievement_id = selected

        st.write("Now open **Achievement Detail** in the sidebar to see more.")

    else:

        st.write("No achievements defined (this would be unusual).")



    link_row = st.columns(2)
    link_row[0].button("Milestones roadmap", on_click=navigate_to, args=("milestones_roadmap",), use_container_width=True)
    link_row[1].button("Achievement detail", on_click=navigate_to, args=("achievement_detail",), use_container_width=True)
    render_demo_disclaimer("Achievements are unlocked based on what you do in this session.")

    st.markdown("</div>", unsafe_allow_html=True)





def tpl_achievement_detail(page: Page):

    """Detail view for a single achievement."""

    render_top_bar(page.label)

    state = get_user_state()

    catalog, best_streak = compute_achievements_catalog(state)



    selected_id = st.session_state.get("selected_achievement_id")

    if not selected_id and catalog:

        selected_id = catalog[0]["id"]



    ach = None

    for a in catalog:

        if a["id"] == selected_id:

            ach = a

            break



    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Achievement Detail")



    if not ach:

        st.write("No achievement selected yet. Open the Achievements List first.")

        st.markdown("</div>", unsafe_allow_html=True)

        return



    st.markdown(f"**{ach['name']}**")

    st.write(ach["description"])

    st.write("")

    st.write(f"**Status:** {'Unlocked' if ach['unlocked'] else 'Locked'}")

    st.write(f"**Progress:** {ach['progress']}")



    st.write("")

    if not ach["unlocked"]:

        st.write(

            "You can unlock achievements by running more scenarios, earning XP and "
            "building streaks. Everything here reflects your current session data "
            "until you connect live sources."

        )

    link_row = st.columns(2)
    link_row[0].button("Back to list", on_click=navigate_to, args=("achievements_list",), use_container_width=True)
    link_row[1].button("See roadmap", on_click=navigate_to, args=("milestones_roadmap",), use_container_width=True)
    render_demo_disclaimer("Achievement detail reflects the activity in this session.")
    st.markdown("</div>", unsafe_allow_html=True)





def tpl_milestones_roadmap(page: Page):

    """Simple roadmap based on locked achievements."""

    render_top_bar(page.label)

    state = get_user_state()

    catalog, best_streak = compute_achievements_catalog(state)



    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### Milestones Roadmap")



    st.write(

        "Each locked achievement can be read as a **milestone**. This page just lists them in plain form."

    )



    rows = {

        "Achievement": [],

        "Requirement summary": [],

    }



    for ach in catalog:

        if ach["unlocked"]:

            continue

        rows["Achievement"].append(ach["name"])

        rows["Requirement summary"].append(ach["description"])



    if rows["Achievement"]:

        st.table(rows)

    else:

        st.write("You have unlocked all achievements available in this session.")



    st.markdown("</div>", unsafe_allow_html=True)



def tpl_metrics_lab(page: Page):
    """Behavior metrics and random simulation."""
    render_top_bar(page.label)
    state = get_user_state()
    streak_current = compute_streak(state["days_active"])
    streak_best = compute_best_streak(state["days_active"])

    # Lightweight derived metrics (placeholders)
    tes = round(state["xp"] / 120 + streak_current * 2, 1)  # Tension/Energy Score placeholder
    bss = len(state["xp_events"]) + streak_best  # Behavior Stability Score placeholder
    bms = round((state["tests_taken"] + streak_current) * 1.5, 1)  # Behavior Momentum Score placeholder
    cfs = max(0, 100 - streak_current * 3)  # Cognitive fatigue surrogate placeholder

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("### Behavior Metrics Lab")
    st.write("View synthetic metrics and run a random simulation that updates XP, coins, and token balance.")
    st.write("Metrics auto-update after simulations; persist by connecting your data sources.")

    metrics = {
        "TES": tes,
        "BSS": bss,
        "BMS": bms,
        "CFS": cfs,
        "XP": state["xp"],
        "Coins": state["coins"],
        "Token balance": round(state.get("token_balance", 0.0), 2),
        "Current streak": streak_current,
        "Best streak": streak_best,
    }
    st.table({"Metric": list(metrics.keys()), "Value": list(metrics.values())})

    if st.button("Run random simulation"):
        xp_gain = random.randint(50, 200)
        grant_xp(xp_gain, "Simulation", "Random behavior simulation")
        token_delta = round(random.uniform(-20, 50), 2)
        state["token_balance"] = round(state.get("token_balance", 0.0) + token_delta, 2)
        record_activity_day()
        st.success(f"Simulation complete: +{xp_gain} XP, token balance change {token_delta}.")

    st.write("---")
    actions = st.columns(5)
    actions[0].button("Open XP Overview", on_click=navigate_to, args=("xp_overview",), use_container_width=True)
    actions[1].button("Run scenario", on_click=navigate_to, args=("scenario_run",), use_container_width=True)
    actions[2].button("Go to shop", on_click=navigate_to, args=("shop_home",), use_container_width=True)
    actions[3].button("Token trading", on_click=navigate_to, args=("token_trading",), use_container_width=True)
    actions[4].button("Invest case", on_click=navigate_to, args=("invest_case",), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def tpl_token_trading(page: Page):
    """Simple token buy/sell simulation using coins."""
    render_top_bar(page.label)
    state = get_user_state()
    token_balance = state.get("token_balance", 0.0)
    coins = state["coins"]

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("### Token Trading Desk")
    st.write(f"Coins: {coins} | Token balance: {round(token_balance, 2)}")

    price = st.number_input("Current token price (coins)", min_value=1, max_value=1000, value=50, step=1)
    st.line_chart({"price": [price * x for x in [0.9, 0.95, 1.0, 1.05, 1.1]]})
    buy_amount = st.number_input("Amount to buy", min_value=0.0, max_value=10000.0, value=0.0, step=1.0)
    sell_amount = st.number_input("Amount to sell", min_value=0.0, max_value=10000.0, value=0.0, step=1.0)

    col_buy, col_sell = st.columns(2)
    with col_buy:
        if st.button("Buy tokens"):
            cost = buy_amount * price
            if cost <= coins and buy_amount > 0:
                state["coins"] -= int(cost)
                state["token_balance"] = round(token_balance + buy_amount, 2)
                log_token_trade("buy", buy_amount, price, -int(cost), buy_amount)
                record_activity_day()
                st.success(f"Bought {buy_amount} tokens for {int(cost)} coins.")
            else:
                st.warning("Not enough coins or invalid amount.")
    with col_sell:
        if st.button("Sell tokens"):
            proceeds = sell_amount * price
            if sell_amount <= token_balance and sell_amount > 0:
                state["coins"] += int(proceeds)
                state["token_balance"] = round(token_balance - sell_amount, 2)
                log_token_trade("sell", sell_amount, price, int(proceeds), -sell_amount)
                record_activity_day()
                st.success(f"Sold {sell_amount} tokens for {int(proceeds)} coins.")
            else:
                st.warning("Not enough tokens or invalid amount.")

    st.write("---")
    if state.get("token_trades"):
        st.markdown("#### Recent trades")
        recent = list(reversed(state["token_trades"]))[:5]
        st.table({
            "Time": [t["timestamp"] for t in recent],
            "Action": [t["action"] for t in recent],
            "Amount": [t["amount"] for t in recent],
            "Price": [t["price"] for t in recent],
            "Coin Δ": [t["coin_delta"] for t in recent],
            "Token Δ": [t["token_delta"] for t in recent],
        })

    st.button("Back to shop home", on_click=navigate_to, args=("shop_home",), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def tpl_wallet_dashboard(page: Page):
    """Wallet overview with quick trade/swap and market hints."""
    render_top_bar(page.label)
    state = get_user_state()
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("### Wallet & Market Overview")

    balances = st.columns(3)
    balances[0].metric("Coins", state["coins"])
    balances[1].metric("Tokens", round(state.get("token_balance", 0.0), 2))
    balances[2].metric("XP", state["xp"])
    st.write("Use swap/trade to move value; open scenarios to influence XP and streaks.")

    st.write("---")
    col_price, col_action = st.columns([2, 1])
    with col_price:
        st.markdown("#### Market pulse (synthetic)")
        base = 50
        series = [base * m for m in [0.94, 0.97, 1.0, 1.02, 1.06, 1.04, 1.08]]
        st.line_chart({"predicted": series})
        st.write("Simple synthetic forecast; connect real feeds for production.")
    with col_action:
        st.markdown("#### Quick swap")
        swap_price = st.number_input("Swap price (coins per token)", min_value=1, max_value=1000, value=50, step=1, key="swap_price")
        swap_amount = st.number_input("Tokens to buy via swap", min_value=0.0, max_value=10000.0, value=0.0, step=1.0, key="swap_amount")
        if st.button("Execute swap"):
            cost = swap_amount * swap_price
            if cost <= state["coins"] and swap_amount > 0:
                state["coins"] -= int(cost)
                state["token_balance"] = round(state.get("token_balance", 0.0) + swap_amount, 2)
                log_token_trade("swap_buy", swap_amount, swap_price, -int(cost), swap_amount)
                record_activity_day()
                st.success(f"Swapped {int(cost)} coins for {swap_amount} tokens.")
            else:
                st.warning("Not enough coins or invalid amount.")

    st.write("---")
    st.markdown("#### What people like you tried (synthetic)")
    st.table({
        "Action": ["Held through volatility", "Scaled in slowly", "Took partial profits", "Paused trading"],
        "Outcome": ["Lower churn", "Moderate XP growth", "Coin increase", "Streak preserved"],
    })

    st.write("---")
    st.markdown("#### Fast links")
    fast = st.columns(4)
    fast[0].button("Trading desk", on_click=navigate_to, args=("token_trading",), use_container_width=True)
    fast[1].button("Metrics lab", on_click=navigate_to, args=("metrics_lab",), use_container_width=True)
    fast[2].button("Scenario run", on_click=navigate_to, args=("scenario_run",), use_container_width=True)
    fast[3].button("Invest case", on_click=navigate_to, args=("invest_case",), use_container_width=True)

    st.write("---")
    links = st.columns(3)
    links[0].button("Open trading desk", on_click=navigate_to, args=("token_trading",), use_container_width=True)
    links[1].button("Run metrics lab", on_click=navigate_to, args=("metrics_lab",), use_container_width=True)
    links[2].button("Go to shop", on_click=navigate_to, args=("shop_home",), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================

# WIRE NEW TEMPLATES INTO DISPATCH & PAGES

# ============================================================



# Override / add templates in the dispatcher

TEMPLATE_DISPATCH.update(

    {

        # Onboarding & home

        "onboard_goals": tpl_onboard_goals,

        "welcome_tour": tpl_welcome_tour,

        "subject_hub": tpl_subject_hub_v2,

        "daily_tasks": tpl_daily_tasks_v2,

        "streak_overview": tpl_streak_overview_v2,

        "notifications_center": tpl_notifications_center_v2,

        "announcements": tpl_announcements,

        # XP & stats

        "xp_history": tpl_xp_history,

        "xp_subject_breakdown": tpl_xp_subject_breakdown,

        "xp_weekly_graph": tpl_xp_weekly_graph,
        "xp_monthly_graph": tpl_xp_monthly_graph,
        "lifetime_stats": tpl_lifetime_stats,
        "achievements_list": tpl_achievements,
        "achievement_detail": tpl_achievement_detail,
        "milestones_roadmap": tpl_milestones_roadmap,
        "metrics_lab": tpl_metrics_lab,
        "token_trading": tpl_token_trading,
        "invest_case": tpl_invest_case,
        "wallet_dashboard": tpl_wallet_dashboard,
        "ai_assistant": tpl_ai_assistant,
    }
)


# Patch the PAGES registry so these IDs use the new template keys

_template_overrides = {

    "xp_history": "xp_history",

    "xp_subject_breakdown": "xp_subject_breakdown",

    "xp_weekly_graph": "xp_weekly_graph",

    "xp_monthly_graph": "xp_monthly_graph",

    "lifetime_stats": "lifetime_stats",

    "achievements_list": "achievements_list",

    "achievement_detail": "achievement_detail",

    "milestones_roadmap": "milestones_roadmap",

    "announcements": "announcements",

}

for _p in PAGES:

    if _p.id in _template_overrides:

        _p.template = _template_overrides[_p.id]





# ============================================================

# NAVIGATION (SIDEBAR)

# ============================================================



def main():

    # Always ensure user_state exists for this session

    init_user_state()



    # Sections in a deterministic order

    sections_order = [

        "Entry & Auth",

        "Onboarding & Home",

        "Account & Profile",

        "XP & Stats",

        "Behavior Scenarios",

        "Shop & Currency",

        "Social & Competition",

        "Settings & System",

        "Admin & Dev",

    ]

    sections = [s for s in sections_order if any(p.section == s for p in PAGES)]

    if "nav_section" not in st.session_state:
        st.session_state["nav_section"] = sections[0]
    if "nav_page_label" not in st.session_state:
        first_section_pages = [p for p in PAGES if p.section == st.session_state["nav_section"]]
        st.session_state["nav_page_label"] = first_section_pages[0].label if first_section_pages else ""



    with st.sidebar:

        st.markdown("### Pages")

        selected_section = st.selectbox("Section", sections, key="nav_section")

        section_pages = [p for p in PAGES if p.section == selected_section]

        labels = [p.label for p in section_pages]

        if st.session_state.get("nav_page_label") not in labels and labels:
            st.session_state["nav_page_label"] = labels[0]

        selected_label = st.selectbox("Page", labels, key="nav_page_label")

        active_page = next(p for p in section_pages if p.label == selected_label)



    # Render the chosen page

    renderer = TEMPLATE_DISPATCH.get(active_page.template)

    if renderer is None:

        tpl_simple_info(active_page, title=active_page.label, body="Template not yet implemented.")

    else:

        if renderer in (tpl_settings_form, tpl_simple_info, tpl_simple_table, tpl_simple_list):

            renderer(active_page)

        else:

            renderer(active_page)



if __name__ == "__main__":
    # 1) Auth gate (login / signup / guest)
    needs_auth = render_auth_gate()

    # If auth gate is still showing, stop here
    if not needs_auth:
        # 2) Crowdlike intro gate (unless intro_done already True)
        showing_intro = render_crowdlike_intro()
        # 3) Main multipage app
        if not showing_intro:
            main()
