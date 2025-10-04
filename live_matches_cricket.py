# pages/live_matches.py
import streamlit as st
import requests
from datetime import datetime
import time

# -------------------------------
# 1) API Key and Host
# -------------------------------
CRICBUZZ_API_KEY = "4c78fe9d51msh3442ef83e518a7fp1db088jsna5390947b494"
CRICBUZZ_HOST = "cricbuzz-cricket.p.rapidapi.com"


# -------------------------------
# 2) Cricbuzz API class
# -------------------------------
class CricbuzzAPI:
    def __init__(self):
        self.headers = {
            "x-rapidapi-key": CRICBUZZ_API_KEY,
            "x-rapidapi-host": CRICBUZZ_HOST
        }
        self.base_url = "https://cricbuzz-cricket.p.rapidapi.com"

    def get_live_matches(self):
        try:
            url = f"{self.base_url}/matches/v1/live"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    def get_scorecard(self, match_id: str):
        try:
            url = f"{self.base_url}/mcenter/v1/{match_id}/scard"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None


# -------------------------------
# 3) Helper functions
# -------------------------------
def format_time(epoch_ms):
    try:
        return datetime.fromtimestamp(int(epoch_ms) / 1000).strftime("%d %b %Y, %I:%M %p")
    except:
        return "N/A"


def show_innings_scorecard(api: CricbuzzAPI, match_id: str):
    data = api.get_scorecard(match_id)
    if not data or "scorecard" not in data:
        st.warning("No scorecard available.")
        return

    for i, innings in enumerate(data["scorecard"], start=1):
        st.subheader(f"📊 Inning {i} - {innings.get('batteamname','')}")

        # Batting
        batsmen_list = []
        for batsman in innings.get("batsman", []):
            batsmen_list.append([
                batsman.get("name", ""),
                batsman.get("runs", 0),
                batsman.get("balls", 0),
                batsman.get("fours", 0),
                batsman.get("sixes", 0),
                batsman.get("strkrate", 0),
                batsman.get("outdec", "")
            ])

        if batsmen_list:
            st.write("### 🏏 Batting")
            st.table([["Name", "Runs", "Balls", "4s", "6s", "SR", "Out"]] + batsmen_list)

        # Bowling
        bowlers_list = []
        for bowler in innings.get("bowler", []):
            bowlers_list.append([
                bowler.get("name", ""),
                bowler.get("overs", 0),
                bowler.get("maidens", 0),
                bowler.get("runs", 0),
                bowler.get("wickets", 0),
                bowler.get("economy", 0)
            ])

        if bowlers_list:
            st.write("### 🎯 Bowling")
            st.table([["Name", "Overs", "Maidens", "Runs", "Wickets", "Economy"]] + bowlers_list)

        st.markdown("---")


# -------------------------------
# 4) Main Streamlit page
# -------------------------------
def show_live_matches():
    st.title("🏏 Live Cricket Matches (Auto-refresh every 30s)")

    api = CricbuzzAPI()
    data = api.get_live_matches()
    if not data:
        st.warning("No live matches found.")
        return

    series_options = {}
    for type_match in data.get("typeMatches", []):
        match_type = type_match.get("matchType", "Unknown")
        for series in type_match.get("seriesMatches", []):
            series_info = series.get("seriesAdWrapper", {})
            if "matches" in series_info:
                series_name = series_info.get("seriesName", "Unknown Series")
                key = f"{series_name} ({match_type})"
                series_options[key] = series_info["matches"]

    if not series_options:
        st.warning("No live series available.")
        return

    selected_series = st.selectbox("Select a Live Series", list(series_options.keys()))
    matches = series_options[selected_series]

    for match in matches:
        match_info = match.get("matchInfo", {})
        match_score = match.get("matchScore", {})

        team1 = match_info.get("team1", {}).get("teamName", "Team 1")
        team2 = match_info.get("team2", {}).get("teamName", "Team 2")
        match_id = match_info.get("matchId", "")

        st.subheader(f"🆚 {team1} vs {team2}")
        st.write(f"**Match:** {match_info.get('matchDesc', '')} ({match_info.get('matchFormat', '')})")
        st.write(f"**Status:** {match_info.get('status', '')}")
        st.write(f"**State:** {match_info.get('stateTitle', '')}")

        venue = match_info.get("venueInfo", {})
        st.write(f"**Venue:** {venue.get('ground', '')}, {venue.get('city', '')}")
        st.write(f"**Start Time:** {format_time(match_info.get('startDate'))}")
        st.write(f"**End Time:** {format_time(match_info.get('endDate'))}")

        # Scores
        if "team1Score" in match_score:
            t1 = match_info.get("team1", {}).get("teamSName", "Team 1")
            t1_inn = match_score.get("team1Score", {}).get("inngs1", {})
            st.success(f"{t1}: {t1_inn.get('runs', 0)}/{t1_inn.get('wickets', 0)} "
                       f"in {t1_inn.get('overs', 0)} overs")

        if "team2Score" in match_score:
            t2 = match_info.get("team2", {}).get("teamSName", "Team 2")
            t2_inn = match_score.get("team2Score", {}).get("inngs1", {})
            st.success(f"{t2}: {t2_inn.get('runs', 0)}/{t2_inn.get('wickets', 0)} "
                       f"in {t2_inn.get('overs', 0)} overs")

        if st.button(f"📑 View Scorecard - {team1} vs {team2}", key=f"btn_{match_id}"):
            show_innings_scorecard(api, match_id)

        st.markdown("---")

    # 🔄 Auto-refresh every 30 seconds
    st.empty()
    time.sleep(30)
    st.experimental_rerun()


# -------------------------------
# 5) Run
# -------------------------------
if __name__ == "__main__":
    show_live_matches()
