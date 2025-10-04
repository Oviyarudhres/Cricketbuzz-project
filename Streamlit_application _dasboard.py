import streamlit as st
import sys
import os

st.set_page_config(
    page_title="🏏 Cricbuzz Ultimate Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Theme + Navigation
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎨 Theme & Navigation</h2>", unsafe_allow_html=True)
    theme_choice = st.radio(
        "Select Theme:",
        ["🌞 Sporty Day", "🌙 Classic Night", "🌈 Neon IPL"]
    )
    st.markdown("<hr>", unsafe_allow_html=True)
    page = st.selectbox(
        "Go to:",
        ["🏠 Home", "⚡ Live Matches", "📊 Top Stats", "🔍 SQL Analytics", "🛠️ CRUD Operations"]
    )

# --- THEME SETTINGS ---
if theme_choice == "🌞 Sporty Day":
    bg_color = "linear-gradient(135deg, #d9fdd3, #fafff0)"
    header_bg = "linear-gradient(135deg, #1e9600, #fff200, #ff0000)"
    card_bg = "#ffffff"
    card_shadow = "rgba(0,0,0,0.2)"
    text_color = "#212121"
    accent = "#ff5722"
    ball_animation = """
        @keyframes hitBall {
            0% { left: -60px; top: 35%; transform: rotate(0deg); }
            40% { left: 50%; top: 15%; transform: rotate(180deg); }
            100% { left: 110%; top: 35%; transform: rotate(360deg); }
        }
    """
elif theme_choice == "🌙 Classic Night":
    bg_color = "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
    header_bg = "linear-gradient(135deg, #232526, #414345)"
    card_bg = "rgba(255,255,255,0.08)"
    card_shadow = "rgba(0,0,0,0.9)"
    text_color = "#f1f1f1"
    accent = "#00e676"
    ball_animation = """
        @keyframes floatBall {
            0% { transform: translate(-50%, 0px); }
            50% { transform: translate(-50%, 25px); }
            100% { transform: translate(-50%, 0px); }
        }
    """
else:  # Neon IPL
    bg_color = "#0a0f2c"
    header_bg = "linear-gradient(135deg, #ff00ff, #00ffff, #ff8c00)"
    card_bg = "rgba(0,0,0,0.3)"
    card_shadow = "rgba(0,255,255,0.7)"
    text_color = "#fff"
    accent = "#ff00ff"
    ball_animation = """
        @keyframes neonBall {
            0% { left: -60px; transform: rotate(0deg); }
            50% { left: 50%; transform: rotate(180deg); }
            100% { left: 110%; transform: rotate(360deg); }
        }
    """

# --- Inject CSS + Animations ---
st.markdown(f"""
<style>
    .stApp {{
        background: {bg_color};
        font-family: 'Poppins', sans-serif;
        color: {text_color};
    }}

    /* Main Header */
    .main-header {{
        text-align: center;
        padding: 2.5rem;
        background: {header_bg};
        border-radius: 20px;
        color: {text_color};
        font-weight: bold;
        box-shadow: 0 8px 25px {card_shadow};
        position: relative;
        overflow: hidden;
    }}

    .main-header h1 {{
        font-size: 3rem;
        { 'background: linear-gradient(90deg, #ff0080, #ff8c00, #40e0d0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-size: 300% 300%; animation: neonText 5s ease infinite;' if theme_choice=="🌈 Neon IPL" else '' }
    }}

    @keyframes neonText {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Cricket Ball Animation */
    .cricket-ball {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
        position: absolute;
        top: 40%;
        { 'background: radial-gradient(circle, #ff00ff 40%, #8b00ff 90%); box-shadow: 0 0 20px #ff00ff, 0 0 40px #ff00ff inset;' if theme_choice=="🌈 Neon IPL" else '' }
        { 'background: radial-gradient(circle, #ff0000 40%, #8b0000 90%); box-shadow: 0 0 15px ' + accent + ';' if theme_choice=="🌞 Sporty Day" else '' }
        { 'background: radial-gradient(circle, #ffffff 40%, #888 90%); box-shadow: 0 0 15px ' + accent + ';' if theme_choice=="🌙 Classic Night" else '' }
        animation: { 'neonBall' if theme_choice=="🌈 Neon IPL" else 'hitBall' if theme_choice=="🌞 Sporty Day" else 'floatBall' } 4s linear infinite;
    }}

    /* Feature Cards */
    .feature-card {{
        background: {card_bg};
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 0 15px {card_shadow};
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 2px solid rgba(255,255,255,0.1);
    }}
    .feature-card:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 40px {accent};
        border: 2px solid {accent};
    }}
    .feature-card h4 {{
        margin-top: 0.5rem;
        color: {accent};
        text-shadow: 0 0 5px {accent}, 0 0 15px {accent};
    }}

    {ball_animation}
</style>
""", unsafe_allow_html=True)

# Floating ball
st.markdown('<div class="cricket-ball"></div>', unsafe_allow_html=True)

# Add current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your custom modules
from live_matches_cricket import show_live_matches
from top_stats import show_top_stats
from sql_queries_cricket_api import show_sql_queries
from crud_operations import show_crud_operations

# ---------------- MAIN ----------------
def main():
    st.markdown(f"""
    <div class="main-header">
        <h1>🏏 Cricbuzz Ultimate Dashboard</h1>
        <p>⚡ Real-Time Cricket Analytics & Stats</p>
    </div>
    """, unsafe_allow_html=True)

    if page == "🏠 Home":
        show_home()
    elif page == "⚡ Live Matches":
        show_live_matches()
    elif page == "📊 Top Stats":
        show_top_stats()
    elif page == "🔍 SQL Analytics":
        show_sql_queries()
    elif page == "🛠️ CRUD Operations":
        show_crud_operations()

def show_home():
    st.subheader("✨ Dashboard Features")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="feature-card">🏏<h4>Live Matches</h4><p>Real-time scores</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card">📊<h4>Top Stats</h4><p>Players & Records</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card">🔍<h4>SQL Analytics</h4><p>Custom queries</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="feature-card">🛠️<h4>CRUD Ops</h4><p>Manage data</p></div>', unsafe_allow_html=True)

    st.markdown("---")

if __name__ == "__main__":
    main()
