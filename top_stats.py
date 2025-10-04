import streamlit as st
import http.client
import json
import requests
import urllib.parse

# ---------------- API CONFIG ----------------
API_KEY = "4c78fe9d51msh3442ef83e518a7fp1db088jsna5390947b494"  # <-- Replace with your key or load from .env

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': "cricbuzz-cricket.p.rapidapi.com"
}
BASE_URL = "cricbuzz-cricket.p.rapidapi.com"

# ---------------- Helper Functions ----------------
def search_players(query: str):
    """Search players by name"""
    safe_query = urllib.parse.quote(query.strip())  # clean + encode query
    conn = http.client.HTTPSConnection(BASE_URL)
    conn.request("GET", f"/stats/v1/player/search?plrN={safe_query}", headers=HEADERS)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    try:
        return json.loads(data.decode("utf-8"))
    except:
        return {}

def get_player_details(player_id: int):
    """Get full profile of a player"""
    conn = http.client.HTTPSConnection(BASE_URL)
    conn.request("GET", f"/stats/v1/player/{player_id}", headers=HEADERS)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    try:
        return json.loads(data.decode("utf-8"))
    except:
        return {}

def get_player_stats(player_id: int, stat_type="batting"):
    """Fetch batting or bowling stats"""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/{stat_type}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return {}

def convert_to_table(stats_json):
    """Convert Cricbuzz stats JSON to simple table format"""
    if not stats_json or "headers" not in stats_json or "values" not in stats_json:
        return [], []
    headers = stats_json["headers"]
    rows = [row["values"] for row in stats_json["values"]]
    return headers, rows

# ---------------- Streamlit UI ----------------
def show_top_stats():
    st.title("📊 Player Stats & Profile")

    # Input Player Name
    player_name = st.text_input("Enter player name (e.g. Kohli, Dhoni, Smith):")

    if player_name:
        results = search_players(player_name)

        if "player" in results and results["player"]:
            # Dropdown to select exact player
            player_options = {p["name"]: p for p in results["player"]}
            selected_name = st.selectbox("Select a player:", list(player_options.keys()))
            selected_player = player_options[selected_name]
            player_details = get_player_details(selected_player["id"])

            tabs = st.tabs(["📌 Profile", "🏏 Batting Stats", "🎯 Bowling Stats"])

            # ---------- PROFILE ----------
            with tabs[0]:
                st.write(f"### {selected_player['name']} ({selected_player['teamName']})")
                st.write(f"📅 DOB: {selected_player.get('dob', 'N/A')}")

                # Player Image
                if "image" in player_details:
                    img_url = player_details["image"].replace("http://", "https://")
                    st.image(img_url, width=150)
                elif "faceImageId" in selected_player and selected_player["faceImageId"]:
                    img_url = f"https://www.cricbuzz.com/a/img/v1/152x152/i1/c{selected_player['faceImageId']}.jpg"
                    st.image(img_url, width=150)
                else:
                    st.image("https://placehold.co/150x150/800000/FFFFFF?text=No+Image", width=150)

                if player_details:
                    st.subheader("Player Details")
                    st.write(f"**Role:** {player_details.get('role', 'N/A')}")
                    st.write(f"**Batting Style:** {player_details.get('bat', 'N/A')}")
                    st.write(f"**Bowling Style:** {player_details.get('bowl', 'N/A')}")
                    st.write(f"**Teams:** {player_details.get('teams', 'N/A')}")
                    st.write(f"**Birth Place:** {player_details.get('birthPlace', 'N/A')}")

                    # Career Debut Info
                    st.subheader("Career Debut Information")
                    conn = http.client.HTTPSConnection(BASE_URL)
                    conn.request("GET", f"/stats/v1/player/{selected_player['id']}/career", headers=HEADERS)
                    res = conn.getresponse()
                    career_data = res.read()
                    conn.close()

                    try:
                        career_json = json.loads(career_data.decode("utf-8"))
                        if "values" in career_json and career_json["values"]:
                            career_rows = []
                            for f in career_json["values"]:
                                row_data = [f.get("name"), f.get("debut"), f.get("lastPlayed")]
                                career_rows.append(row_data)

                            if career_rows:
                                st.table([["Format", "Debut", "Last Played"]] + career_rows)
                            else:
                                st.warning("No career debut information available.")
                        else:
                            st.warning("No career debut information available.")
                    except:
                        st.warning("Could not load career debut information.")

                    if "webURL" in player_details:
                        st.markdown(f"[🔗 View on Cricbuzz]({player_details['webURL']})")

            # ---------- BATTING STATS ----------
            with tabs[1]:
                st.subheader("Batting Stats")
                batting_stats = get_player_stats(selected_player["id"], "batting")
                headers, rows = convert_to_table(batting_stats)
                if rows:
                    st.table([headers] + rows)
                else:
                    st.warning("No batting stats available.")

            # ---------- BOWLING STATS ----------
            with tabs[2]:
                st.subheader("Bowling Stats")
                bowling_stats = get_player_stats(selected_player["id"], "bowling")
                headers, rows = convert_to_table(bowling_stats)
                if rows:
                    st.table([headers] + rows)
                else:
                    st.warning("No bowling stats available.")

        else:
            st.warning("No players found. Try another name.")

# ---------------- Run App ----------------
if __name__ == "__main__":
    show_top_stats()
