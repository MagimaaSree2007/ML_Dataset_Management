
import streamlit as st

from auth import register_user, login_user
from reports import show_dashboard
from datasets import upload_dataset, view_datasets
from versions import add_version, view_versions
from preprocessing import preprocessing_page, view_preprocessing
from models import model_management, view_models
from performance import performance_management, view_performance
from organization import organization_page


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="MLDMS | Dataset Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# LIGHT BLUE AND WHITE THEME
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #F2F8FF;
    color: #183153;
}

/* Main content */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #E3F1FF;
    border-right: 1px solid #C9E2FF;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #174A7E;
}

/* Headings */
h1, h2, h3 {
    color: #174A7E !important;
    font-weight: 700 !important;
}

/* Buttons */
.stButton > button {
    background-color: #75B9F8;
    color: #10365C;
    border: 1px solid #75B9F8;
    border-radius: 9px;
    padding: 0.55rem 1.2rem;
    font-weight: 600;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background-color: #4CA3F2;
    color: white;
    border-color: #4CA3F2;
}

/* Inputs */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: white;
    border-radius: 8px;
    border: 1px solid #C5DDF5;
}

/* Select boxes */
.stSelectbox > div > div {
    background-color: white;
    border-radius: 8px;
}

/* Cards */
.feature-card {
    background-color: white;
    border: 1px solid #D7E9FB;
    border-radius: 14px;
    padding: 24px;
    min-height: 165px;
    margin-bottom: 16px;
    box-shadow: 0 4px 15px rgba(64, 130, 190, 0.06);
}

.feature-card h3 {
    color: #2166A5 !important;
    font-size: 19px;
    margin-bottom: 10px;
}

.feature-card p {
    color: #58718B;
    font-size: 14px;
    line-height: 1.6;
}

/* Hero section */
.hero {
    background: linear-gradient(120deg, #DDF0FF, #F7FBFF);
    border: 1px solid #C6E4FF;
    border-radius: 20px;
    padding: 45px 35px;
    margin-bottom: 28px;
}

.hero h1 {
    font-size: 40px;
    line-height: 1.2;
    color: #174A7E !important;
}

.hero p {
    color: #496985;
    font-size: 17px;
    line-height: 1.7;
}

/* Divider and footer */
hr {
    border-color: #D5E7F7;
}

.footer {
    text-align: center;
    color: #7189A0;
    font-size: 12px;
    padding: 25px 0;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #D7E9FB;
    padding: 16px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "Home"

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Dashboard"


# --------------------------------------------------
# COMMON FUNCTIONS
# --------------------------------------------------
def show_brand():
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px;">
        <div style="
            background:#BFE2FF;
            border-radius:10px;
            padding:10px;
            font-size:24px;">
            📊
        </div>
        <div>
            <div style="font-size:23px;font-weight:800;color:#174A7E;">
                MLDMS
            </div>
            <div style="font-size:12px;color:#66829B;">
                ML Dataset Management System
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_footer():
    st.markdown("""
    <div class="footer">
        ML Dataset Management System · Organize data. Track versions. Manage models.
    </div>
    """, unsafe_allow_html=True)


def go_to(page):
    st.session_state.auth_page = page


# --------------------------------------------------
# PUBLIC LANDING PAGE
# --------------------------------------------------
def landing_page():
    show_brand()
    st.write("")

    nav1, nav2, nav3 = st.columns([6, 1, 1])

    with nav2:
        if st.button("Log in", use_container_width=True):
            go_to("Login")
            st.rerun()

    with nav3:
        if st.button("Get started", use_container_width=True):
            go_to("Register")
            st.rerun()

    st.write("")

    st.markdown("""
    <div class="hero">
        <div style="color:#438BC8;font-weight:700;margin-bottom:12px;">
            YOUR DATA WORKSPACE
        </div>
        <h1>Manage machine learning datasets<br>
        with confidence.</h1>
        <p>
            A centralized workspace to upload datasets, maintain versions,
            record preprocessing steps, manage ML models, and track model
            performance.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start managing your datasets →"):
        go_to("Register")
        st.rerun()

    st.write("")
    st.subheader("Everything your ML workflow needs")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📁 Dataset Management</h3>
            <p>Upload, organize, and access datasets in one workspace.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🕒 Version History</h3>
            <p>Maintain dataset versions and keep track of changes.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>⚙️ Preprocessing</h3>
            <p>Record preprocessing operations applied to datasets.</p>
        </div>
        """, unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 Model Management</h3>
            <p>Maintain records of machine learning models.</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="feature-card">
            <h3>📈 Performance Tracking</h3>
            <p>Record and review model evaluation metrics.</p>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <div class="feature-card">
            <h3>👥 Team Workspace</h3>
            <p>Organize work and manage team membership.</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    <div class="hero">
        <h2>One workspace for your ML data lifecycle</h2>
        <p>
            Upload your data, maintain dataset history, document
            preprocessing, and keep model performance records organized.
        </p>
    </div>
    """, unsafe_allow_html=True)

    show_footer()


# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------
def login_page():
    show_brand()
    st.write("")

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown("""
        <div class="hero">
            <h1>Welcome back!</h1>
            <p>
                Sign in to access your datasets, preprocessing records,
                models, and performance reports.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.subheader("Log in to MLDMS")

        with st.form("login_form"):
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button(
                "Log in",
                use_container_width=True
            )

        if submitted:
            if not email or not password:
                st.warning("Please enter your email and password.")
            else:
                try:
                    user = login_user(email, password)

                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.selected_page = "Dashboard"
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

                except Exception as e:
                    st.error(f"Login failed: {e}")

        st.write("Don't have an account?")
        if st.button("Create an account"):
            go_to("Register")
            st.rerun()

    show_footer()


# --------------------------------------------------
# REGISTRATION PAGE
# --------------------------------------------------
def register_page():
    show_brand()
    st.write("")

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown("""
        <div class="hero">
            <h1>Create your workspace account.</h1>
            <p>
                Start organizing datasets and keeping your machine learning
                project records in one place.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.subheader("Create an account")

        with st.form("register_form"):
            name = st.text_input("Full name")
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )
            submitted = st.form_submit_button(
                "Create account",
                use_container_width=True
            )

        if submitted:
            if not name or not email or not password or not confirm_password:
                st.warning("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                try:
                    result = register_user(name, email, password)

                    if result:
                        st.success("Registration completed. You can now log in.")
                    else:
                        st.info(
                            "Please check whether the email is already "
                            "registered and review your registration function."
                        )

                except Exception as e:
                    st.error(f"Registration failed: {e}")

        if st.button("Already have an account? Log in"):
            go_to("Login")
            st.rerun()

    show_footer()


# --------------------------------------------------
# MAIN APPLICATION
# --------------------------------------------------
def application_page():
    user = st.session_state.user

    # Support the user ID from the logged-in user's record.
    user_id = user["user_id"]

    with st.sidebar:
        show_brand()
        st.divider()

        st.caption("MAIN MENU")

        pages = [
            "Dashboard",
            "Company Workspace",
            "Upload Dataset",
            "Dataset Library",
            "Add Dataset Version",
            "Version History",
            "Preprocessing",
            "Preprocessing History",
            "Model Management",
            "Model Library",
            "Performance Management",
            "Performance Library",
        ]

        selected_page = st.radio(
            "Navigation",
            pages,
            key="main_navigation",
            index=(
                pages.index(st.session_state.selected_page)
                if st.session_state.selected_page in pages
                else 0
            )
        )

        st.session_state.selected_page = selected_page

        st.divider()
        st.caption("SIGNED IN AS")
        st.write(user.get("name", user.get("email", "User")))
        st.caption(user.get("email", ""))

        if st.button("Log out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.auth_page = "Home"
            st.rerun()

    st.markdown(
        f"""
        <div style="
            background:#FFFFFF;
            border:1px solid #D7E9FB;
            border-radius:12px;
            padding:18px 22px;
            margin-bottom:22px;">
            <div style="font-size:13px;color:#64829D;">
                ML DATASET MANAGEMENT SYSTEM
            </div>
            <div style="
                font-size:27px;
                font-weight:800;
                color:#174A7E;">
                {selected_page}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Route to the existing project modules.
    if selected_page == "Dashboard":
        show_dashboard()

    elif selected_page == "Company Workspace":
        organization_page()

    elif selected_page == "Upload Dataset":
        # FIX: upload_dataset requires the logged-in user's ID.
        upload_dataset(user_id)

    elif selected_page == "Dataset Library":
        view_datasets()

    elif selected_page == "Add Dataset Version":
        add_version()

    elif selected_page == "Version History":
        view_versions()

    elif selected_page == "Preprocessing":
        preprocessing_page()

    elif selected_page == "Preprocessing History":
        view_preprocessing()

    elif selected_page == "Model Management":
        model_management()

    elif selected_page == "Model Library":
        view_models()

    elif selected_page == "Performance Management":
        performance_management()

    elif selected_page == "Performance Library":
        view_performance()

    show_footer()


# --------------------------------------------------
# APP ROUTING
# --------------------------------------------------
if st.session_state.logged_in:
    application_page()

else:
    # Hide the application sidebar on public pages.
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none;
        }
        button[data-testid="collapsedControl"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.auth_page == "Login":
        login_page()

    elif st.session_state.auth_page == "Register":
        register_page()

    else:
        landing_page()
