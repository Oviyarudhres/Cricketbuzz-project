import streamlit as st
import pymysql
import os
from dotenv import load_dotenv

# ----------------- Database Connection -----------------
def create_connection():
    """Create a database connection and return the connection object."""
    load_dotenv()
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "root")
    database = os.getenv("DB_NAME", "cricbuzz_db")

    conn = None
    try:
        conn = pymysql.connect(
            host=host,
            user="root",
            password="Oviya@0108",
            database="cricketss_api",
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor  # fetch as dicts
        )
        return conn
    except Exception as e:
        st.error(f"❌ Error connecting to MySQL database: {e}")
        return None


# ----------------- Run SQL -----------------
def run_query(conn, query):
    """Run a SQL query and return rows."""
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return rows
    except Exception as e:
        st.error(f"❌ Query Error: {e}")
        return None


# ----------------- 25 Queries -----------------
QUERIES = {
    "Q1: List all Indian players": """
        SELECT full_name AS player_name, playing_role, batting_style, bowling_style
        FROM players
        WHERE country = 'India';
    """,
    "Q2: Matches played in last 30 days": """
        SELECT match_desc, team1, team2, venue, start_date
        FROM recent_matches
        WHERE start_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        ORDER BY start_date DESC;
    """,
    "Q3: Top 10 ODI run scorers": """
        SELECT player_name, runs AS total_runs, average AS batting_avg
        FROM top_odi_runs
        ORDER BY total_runs DESC
        LIMIT 10;
    """,
    "Q4: Venues with capacity over 50,000 (largest first)": """
            SELECT venue_name AS stadium_name, city, country, capacity
            FROM venues
            WHERE CAST(REPLACE(REPLACE(capacity, ',', ''), '(including standing room)', '') AS UNSIGNED) >= 50000
            ORDER BY CAST(REPLACE(REPLACE(capacity, ',', ''), '(including standing room)', '') AS UNSIGNED) DESC;
    """,
    "Q5: Total matches won by each team (most wins first)": """
            SELECT match_winner AS team_name, COUNT(*) AS total_wins
            FROM combined_matches
            GROUP BY team_name
            ORDER BY total_wins DESC;
    """,
    "Q6: Top 5 wicket takers": """
        SELECT bowler_name, SUM(wickets) AS total_wickets
        FROM bowling_data
        GROUP BY bowler_name
        ORDER BY total_wickets DESC
        LIMIT 5;
    """,
    "Q7:Top 5 partnerships": """
        SELECT batter1_name, batter2_name, MAX(runs_partnership) AS partnership_runs
        FROM players_partnerships_data
        GROUP BY batter1_name, batter2_name
        ORDER BY partnership_runs DESC
        LIMIT 5;
    """,
    "Q8:Series that started in 2024": """
            SELECT series_name AS series, venue AS venue_name, match_format AS format, start_date AS match_date
            FROM series_matches
            WHERE YEAR(start_date) = 2024
            ORDER BY match_date;
    """,
    "Q9: Show allrounders with 1000+ runs & 50+ wickets": """
            SELECT name AS player_name, total_runs AS runs_scored, total_wickets AS wickets_taken
            FROM players
            WHERE playing_role LIKE '%Allrounder%'
              AND total_runs > 1000
              AND total_wickets > 50;
    """,
    "Q10: Last 20 completed matches (latest first)": """
            SELECT match_desc AS match_description,
                   team1 AS team_one,
                   team2 AS team_two,
                   SUBSTRING_INDEX(status, ' won by ', 1) AS winning_team,
                   SUBSTRING_INDEX(SUBSTRING_INDEX(status, ' won by ', -1), ' ', 1) AS victory_margin,
                   CASE
                       WHEN status LIKE '%won by%run%' THEN 'Runs'
                       WHEN status LIKE '%won by%wkt%' THEN 'Wickets'
                       ELSE NULL
                   END AS victory_type,
                   venue AS venue_name
            FROM recent_matches
            WHERE state = 'Complete'
            ORDER BY STR_TO_DATE(start_date, '%d-%m-%Y %H:%i') DESC
            LIMIT 20;
        """,
    "Q11: Players in >=2 formats: runs by format + overall avg": """
            SELECT player_name, test_runs, odi_runs, t20_runs,
                   ROUND(
                        (test_runs + odi_runs + t20_runs) / 
                        (
                            (CASE WHEN test_runs > 0 THEN 1 ELSE 0 END) + 
                            (CASE WHEN odi_runs > 0 THEN 1 ELSE 0 END) + 
                            (CASE WHEN t20_runs > 0 THEN 1 ELSE 0 END)
                        ), 
                   2) AS overall_batting_average
            FROM players_stats
            WHERE 
                (CASE WHEN test_runs > 0 THEN 1 ELSE 0 END) + 
                (CASE WHEN odi_runs > 0 THEN 1 ELSE 0 END) + 
                (CASE WHEN t20_runs > 0 THEN 1 ELSE 0 END) >= 2
            ORDER BY overall_batting_average DESC;
    """,
    "Q12: Home vs Away team wins": """
            SELECT team_stats.team AS team_name,
                   team_stats.home_or_away,
                   COUNT(*) AS total_wins
            FROM (
                SELECT team1 AS team,
                       CASE 
                           WHEN status LIKE CONCAT(team1, ' won%') AND series_name LIKE CONCAT('%tour of ', team1, '%') THEN 'Home'
                           WHEN status LIKE CONCAT(team1, ' won%') THEN 'Away'
                       END AS home_or_away
                FROM series_matches
                WHERE status LIKE '%won%'
                UNION ALL
                SELECT team2 AS team,
                       CASE 
                           WHEN status LIKE CONCAT(team2, ' won%') AND series_name LIKE CONCAT('%tour of ', team2, '%') THEN 'Home'
                           WHEN status LIKE CONCAT(team2, ' won%') THEN 'Away'
                       END AS home_or_away
                FROM series_matches
                WHERE status LIKE '%won%'
            ) AS team_stats
            WHERE home_or_away IS NOT NULL
            GROUP BY team_stats.team, team_stats.home_or_away
            ORDER BY team_stats.team, team_stats.home_or_away;
        """,
    
    "Q13: Batting partnerships with combined runs >= 100 in the same innings": """
            SELECT p1.match_id, p1.innings_no, p1.batter1_name AS batter1, p1.batter2_name AS batter2,
                   p1.runs_partnership + p2.runs_partnership AS combined_runs
            FROM players_partnerships_data p1
            JOIN players_partnerships_data p2
                ON p1.match_id = p2.match_id
               AND p1.innings_no = p2.innings_no
               AND p1.wicket_fallen + 1 = p2.wicket_fallen
            WHERE (p1.runs_partnership + p2.runs_partnership) >= 100
            ORDER BY p1.match_id, p1.innings_no, p1.wicket_fallen;
        """,
    "Q14: Bowling performance at venues for bowlers with >=2 matches and >=4 overs": """
            SELECT player_name, venue, COUNT(DISTINCT match_id) AS matches_played,
                   SUM(wickets) AS total_wickets,
                   ROUND(AVG(economy_rate), 2) AS avg_economy_rate
            FROM bowlers_bowling_venue_data
            WHERE overs >= 4
            GROUP BY player_name, venue
            HAVING COUNT(DISTINCT match_id) >= 2
            ORDER BY player_name, venue;
        """,
    "Q15: Players in >=2 formats: runs by format + overall avg": """
            SELECT player_name, test_runs, odi_runs, t20_runs,
                   ROUND(
                        (test_runs + odi_runs + t20_runs) / 
                        (
                            (CASE WHEN test_runs > 0 THEN 1 ELSE 0 END) + 
                            (CASE WHEN odi_runs > 0 THEN 1 ELSE 0 END) + 
                            (CASE WHEN t20_runs > 0 THEN 1 ELSE 0 END)
                        ), 
                   2) AS overall_batting_average
            FROM players_stats
            WHERE 
                (CASE WHEN test_runs > 0 THEN 1 ELSE 0 END) + 
                (CASE WHEN odi_runs > 0 THEN 1 ELSE 0 END) + 
                (CASE WHEN t20_runs > 0 THEN 1 ELSE 0 END) >= 2
            ORDER BY overall_batting_average DESC;
    """,
        
    "Q16: Last 20 completed matches (latest first)": """
            SELECT match_desc AS match_description,
                   team1 AS team_one,
                   team2 AS team_two,
                   SUBSTRING_INDEX(status, ' won by ', 1) AS winning_team,
                   SUBSTRING_INDEX(SUBSTRING_INDEX(status, ' won by ', -1), ' ', 1) AS victory_margin,
                   CASE
                       WHEN status LIKE '%won by%run%' THEN 'Runs'
                       WHEN status LIKE '%won by%wkt%' THEN 'Wickets'
                       ELSE NULL
                   END AS victory_type,
                   venue AS venue_name
            FROM recent_matches
            WHERE state = 'Complete'
            ORDER BY STR_TO_DATE(start_date, '%d-%m-%Y %H:%i') DESC
            LIMIT 20;
        """,
        
    "Q17: Toss decision impact: win % by toss choice": """
            WITH toss_results AS (
                SELECT toss_decision,
                       CASE WHEN toss_winner = match_winner THEN 1 ELSE 0 END AS toss_win_match
                FROM combined_matches
                WHERE toss_winner IS NOT NULL AND toss_decision IS NOT NULL
                  AND match_winner NOT LIKE 'Match drawn'
            )
            SELECT toss_decision,
                   COUNT(*) AS total_matches,
                   SUM(toss_win_match) AS won_after_toss,
                   ROUND(SUM(toss_win_match) * 100.0 / COUNT(*), 2) AS win_percentage
            FROM toss_results
            GROUP BY toss_decision;
        """,
    "Q18: Most economical bowlers (ODI & T20, min 10 matches, avg >=2 overs)": """
            WITH bowler_agg AS (
                SELECT player_id, player_name, COUNT(DISTINCT match_id) AS matches_played,
                       SUM(overs) AS total_overs, SUM(runs_conceded) AS total_runs, SUM(wickets) AS total_wickets,
                       SUM(overs) * 1.0 / COUNT(DISTINCT match_id) AS avg_overs_per_match,
                       SUM(runs_conceded) * 1.0 / SUM(overs) AS economy_rate
                FROM bowlers_bowling_venue_data
                GROUP BY player_id, player_name
                HAVING COUNT(DISTINCT match_id) >= 2 AND SUM(overs) * 1.0 / COUNT(DISTINCT match_id) >= 1
            ),
            ranked_bowlers AS (
                SELECT *, RANK() OVER (ORDER BY total_wickets DESC, economy_rate ASC) AS bowler_rank
                FROM bowler_agg
            )
            SELECT bowler_rank AS ranking, player_name, matches_played, total_overs, total_runs, total_wickets,
                   ROUND(economy_rate, 2) AS economy_rate
            FROM ranked_bowlers
            ORDER BY bowler_rank;
        """,
    "Q19:Bowling performance at venues for bowlers with >=2 matches and >=4 overs": """
            SELECT player_name, venue, COUNT(DISTINCT match_id) AS matches_played,
                   SUM(wickets) AS total_wickets,
                   ROUND(AVG(economy_rate), 2) AS avg_economy_rate
            FROM bowlers_bowling_venue_data
            WHERE overs >= 4
            GROUP BY player_name, venue
            HAVING COUNT(DISTINCT match_id) >= 2
            ORDER BY player_name, venue;
        """,
    "Q20: Matches & batting avg by format (players with >=20 matches)": """
            WITH player_format_stats AS (
                SELECT b.player_id, b.player_name, c.format,
                       COUNT(DISTINCT b.match_id) AS matches_played,
                       SUM(b.runs) AS total_runs,
                       SUM(CASE WHEN b.dismissal <> 'not out' THEN 1 ELSE 0 END) AS outs
                FROM batting_data b
                JOIN combined_matches c ON b.match_id = c.match_id
                GROUP BY b.player_id, b.player_name, c.format
            ),
            player_summary AS (
                SELECT player_id, player_name,
                       SUM(CASE WHEN format = 'Test' THEN matches_played ELSE 0 END) AS test_matches,
                       SUM(CASE WHEN format = 'ODI'  THEN matches_played ELSE 0 END) AS odi_matches,
                       SUM(CASE WHEN format = 'T20'  THEN matches_played ELSE 0 END) AS t20_matches,
                       ROUND(SUM(CASE WHEN format = 'Test' THEN total_runs ELSE 0 END) * 1.0 /
                             NULLIF(SUM(CASE WHEN format = 'Test' THEN outs ELSE 0 END), 0), 2) AS test_bat_avg,
                       ROUND(SUM(CASE WHEN format = 'ODI' THEN total_runs ELSE 0 END) * 1.0 /
                             NULLIF(SUM(CASE WHEN format = 'ODI' THEN outs ELSE 0 END), 0), 2) AS odi_bat_avg,
                       ROUND(SUM(CASE WHEN format = 'T20' THEN total_runs ELSE 0 END) * 1.0 /
                             NULLIF(SUM(CASE WHEN format = 'T20' THEN outs ELSE 0 END), 0), 2) AS t20_bat_avg
                FROM player_format_stats
                GROUP BY player_id, player_name
            )
            SELECT *
            FROM player_summary
            WHERE (test_matches + odi_matches + t20_matches) >= 10
            ORDER BY (test_matches + odi_matches + t20_matches) DESC;
        """,
    "Q21: Best batting partnerships (adjacent, >=5 partnerships)": """
            WITH partnership_stats AS (
                SELECT
                    batter1_name,
                    batter2_name,
                    COUNT(*) AS total_partnerships,
                    ROUND(AVG(runs_partnership), 2) AS avg_runs,
                    SUM(CASE WHEN runs_partnership > 50 THEN 1 ELSE 0 END) AS partnerships_over_50,
                    MAX(runs_partnership) AS highest_partnership,
                    ROUND(
                        CASE 
                            WHEN COUNT(*) = 0 THEN 0
                            ELSE SUM(CASE WHEN runs_partnership > 50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
                        END, 2
                    ) AS success_rate
                FROM players_partnerships_data
                GROUP BY batter1_name, batter2_name
                HAVING COUNT(*) >= 1
            ),
            ranked_partnerships AS (
                SELECT *,
                    ROW_NUMBER() OVER (ORDER BY success_rate DESC, avg_runs DESC, highest_partnership DESC) AS `ranking`
                FROM partnership_stats
            )
            SELECT *
            FROM ranked_partnerships
            WHERE `ranking` <= 20;
        """,
    "Q22: Head-to-head stats last 3 years (pairs with >=5 matches)": """
            WITH recent_matches AS (
                SELECT *
                FROM combined_matches
                WHERE match_date >= DATE_SUB(CURDATE(), INTERVAL 5 YEAR)
            ),
            team_pairs AS (
                SELECT 
                    LEAST(team1, team2) AS team_a,
                    GREATEST(team1, team2) AS team_b,
                    COUNT(*) AS matches_played
                FROM recent_matches
                GROUP BY LEAST(team1, team2), GREATEST(team1, team2)
                HAVING matches_played >= 3
            ),
            match_details AS (
                SELECT 
                    m.match_id,
                    LEAST(m.team1, m.team2) AS team_a,
                    GREATEST(m.team1, m.team2) AS team_b,
                    m.team1,
                    m.team2,
                    m.match_winner,
                    m.win_margin,
                    m.toss_winner,
                    m.toss_decision,
                    m.venue,
                    m.format
                FROM recent_matches m
                JOIN team_pairs tp 
                    ON LEAST(m.team1, m.team2) = tp.team_a 
                AND GREATEST(m.team1, m.team2) = tp.team_b
            ),
            team_stats AS (
                SELECT
                    team_a,
                    team_b,
                    SUM(CASE WHEN match_winner = team_a THEN 1 ELSE 0 END) AS wins_team_a,
                    SUM(CASE WHEN match_winner = team_b THEN 1 ELSE 0 END) AS wins_team_b,
                    ROUND(AVG(CASE WHEN match_winner = team_a THEN win_margin END), 2) AS avg_margin_team_a,
                    ROUND(AVG(CASE WHEN match_winner = team_b THEN win_margin END), 2) AS avg_margin_team_b
                FROM match_details
                GROUP BY team_a, team_b
            ),
            venue_performance AS (
                SELECT
                    LEAST(team1, team2) AS team_a,
                    GREATEST(team1, team2) AS team_b,
                    venue,
                    toss_decision,
                    SUM(CASE WHEN match_winner = team1 THEN 1 ELSE 0 END) AS wins_team1,
                    SUM(CASE WHEN match_winner = team2 THEN 1 ELSE 0 END) AS wins_team2,
                    COUNT(*) AS total_matches
                FROM recent_matches
                GROUP BY LEAST(team1, team2), GREATEST(team1, team2), venue, toss_decision
            ),
            overall_win_pct AS (
                SELECT
                    team_a,
                    team_b,
                    ROUND(100 * wins_team_a / NULLIF((wins_team_a + wins_team_b),0), 2) AS win_pct_team_a,
                    ROUND(100 * wins_team_b / NULLIF((wins_team_a + wins_team_b),0), 2) AS win_pct_team_b
                FROM team_stats
            )
            SELECT 
                ts.team_a,
                ts.team_b,
                (ts.wins_team_a + ts.wins_team_b) AS total_matches,
                ts.wins_team_a,
                ts.wins_team_b,
                ts.avg_margin_team_a,
                ts.avg_margin_team_b,
                ow.win_pct_team_a,
                ow.win_pct_team_b
            FROM team_stats ts
            JOIN overall_win_pct ow ON ts.team_a = ow.team_a AND ts.team_b = ow.team_b
            ORDER BY total_matches DESC, ts.team_a, ts.team_b;
        """,
    
    "Q23:  Quarterly batting trend & career phase (>=6 quarters)": """
            WITH player_match_order AS (
                SELECT 
                    player_id,
                    player_name,
                    match_id,
                    runs,
                    strike_rate,
                    ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY match_id) AS match_order
                FROM batters_batting_data
            ),
            player_quarters AS (
                SELECT
                    player_id,
                    player_name,
                    CEIL(match_order / 3) AS quarter_number,  -- every 3 matches = 1 quarter
                    COUNT(match_id) AS matches_played,
                    AVG(runs) AS avg_runs,
                    AVG(strike_rate) AS avg_sr
                FROM player_match_order
                GROUP BY player_id, player_name, CEIL(match_order / 3)
                HAVING COUNT(match_id) >= 3
            ),
            player_with_trend AS (
                SELECT
                    player_id,
                    player_name,
                    CONCAT('Q', quarter_number) AS year_quarter,
                    avg_runs,
                    avg_sr,
                    LAG(avg_runs) OVER (PARTITION BY player_id ORDER BY quarter_number) AS prev_avg_runs,
                    LAG(avg_sr) OVER (PARTITION BY player_id ORDER BY quarter_number) AS prev_avg_sr
                FROM player_quarters
            ),
            player_trend_analysis AS (
                SELECT
                    player_id,
                    player_name,
                    year_quarter,
                    avg_runs,
                    avg_sr,
                    CASE
                        WHEN prev_avg_runs IS NULL THEN 'N/A'
                        WHEN avg_runs > prev_avg_runs AND avg_sr > prev_avg_sr THEN 'Improving'
                        WHEN avg_runs < prev_avg_runs AND avg_sr < prev_avg_sr THEN 'Declining'
                        ELSE 'Stable'
                    END AS performance_trend
                FROM player_with_trend
            )
            SELECT 
                player_id,
                player_name,
                COUNT(CASE WHEN performance_trend = 'Improving' THEN 1 END) AS improving_quarters,
                COUNT(CASE WHEN performance_trend = 'Declining' THEN 1 END) AS declining_quarters,
                COUNT(CASE WHEN performance_trend = 'Stable' THEN 1 END) AS stable_quarters,
                CASE
                    WHEN COUNT(CASE WHEN performance_trend = 'Improving' THEN 1 END) >
                        COUNT(CASE WHEN performance_trend = 'Declining' THEN 1 END)
                    THEN 'Career Ascending'
                    WHEN COUNT(CASE WHEN performance_trend = 'Declining' THEN 1 END) >
                        COUNT(CASE WHEN performance_trend = 'Improving' THEN 1 END)
                    THEN 'Career Declining'
                    ELSE 'Career Stable'
                END AS career_phase
            FROM player_trend_analysis
            GROUP BY player_id, player_name;
    """,
        
    "Q24:Best batting partnerships (adjacent, >=5 partnerships)": """
            WITH partnership_stats AS (
                SELECT
                    batter1_name,
                    batter2_name,
                    COUNT(*) AS total_partnerships,
                    ROUND(AVG(runs_partnership), 2) AS avg_runs,
                    SUM(CASE WHEN runs_partnership > 50 THEN 1 ELSE 0 END) AS partnerships_over_50,
                    MAX(runs_partnership) AS highest_partnership,
                    ROUND(
                        CASE 
                            WHEN COUNT(*) = 0 THEN 0
                            ELSE SUM(CASE WHEN runs_partnership > 50 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
                        END, 2
                    ) AS success_rate
                FROM players_partnerships_data
                GROUP BY batter1_name, batter2_name
                HAVING COUNT(*) >= 1
            ),
            ranked_partnerships AS (
                SELECT *,
                    ROW_NUMBER() OVER (ORDER BY success_rate DESC, avg_runs DESC, highest_partnership DESC) AS `ranking`
                FROM partnership_stats
            )
            SELECT *
            FROM ranked_partnerships
            WHERE `ranking` <= 20;
        """,
    "Q25: Quarterly batting trend & career phase (>=6 quarters)": """
            WITH player_match_order AS (
                SELECT 
                    player_id,
                    player_name,
                    match_id,
                    runs,
                    strike_rate,
                    ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY match_id) AS match_order
                FROM batters_batting_data
            ),
            player_quarters AS (
                SELECT
                    player_id,
                    player_name,
                    CEIL(match_order / 3) AS quarter_number,  -- every 3 matches = 1 quarter
                    COUNT(match_id) AS matches_played,
                    AVG(runs) AS avg_runs,
                    AVG(strike_rate) AS avg_sr
                FROM player_match_order
                GROUP BY player_id, player_name, CEIL(match_order / 3)
                HAVING COUNT(match_id) >= 3
            ),
            player_with_trend AS (
                SELECT
                    player_id,
                    player_name,
                    CONCAT('Q', quarter_number) AS year_quarter,
                    avg_runs,
                    avg_sr,
                    LAG(avg_runs) OVER (PARTITION BY player_id ORDER BY quarter_number) AS prev_avg_runs,
                    LAG(avg_sr) OVER (PARTITION BY player_id ORDER BY quarter_number) AS prev_avg_sr
                FROM player_quarters
            ),
            player_trend_analysis AS (
                SELECT
                    player_id,
                    player_name,
                    year_quarter,
                    avg_runs,
                    avg_sr,
                    CASE
                        WHEN prev_avg_runs IS NULL THEN 'N/A'
                        WHEN avg_runs > prev_avg_runs AND avg_sr > prev_avg_sr THEN 'Improving'
                        WHEN avg_runs < prev_avg_runs AND avg_sr < prev_avg_sr THEN 'Declining'
                        ELSE 'Stable'
                    END AS performance_trend
                FROM player_with_trend
            )
            SELECT 
                player_id,
                player_name,
                COUNT(CASE WHEN performance_trend = 'Improving' THEN 1 END) AS improving_quarters,
                COUNT(CASE WHEN performance_trend = 'Declining' THEN 1 END) AS declining_quarters,
                COUNT(CASE WHEN performance_trend = 'Stable' THEN 1 END) AS stable_quarters,
                CASE
                    WHEN COUNT(CASE WHEN performance_trend = 'Improving' THEN 1 END) >
                        COUNT(CASE WHEN performance_trend = 'Declining' THEN 1 END)
                    THEN 'Career Ascending'
                    WHEN COUNT(CASE WHEN performance_trend = 'Declining' THEN 1 END) >
                        COUNT(CASE WHEN performance_trend = 'Improving' THEN 1 END)
                    THEN 'Career Declining'
                    ELSE 'Career Stable'
                END AS career_phase
            FROM player_trend_analysis
            GROUP BY player_id, player_name;
    """
}


# ----------------- Streamlit UI -----------------
def show_sql_queries():
    st.title("🏏 Cricket SQL Analytics (25 Queries)")
    st.markdown("---")

    conn = create_connection()
    if conn is None:
        st.warning("Could not connect to the database. Please check credentials.")
        return

    st.subheader("Choose a Query")
    query_selection = st.selectbox("Select a predefined query:", list(QUERIES.keys()), index=0)
    selected_query_text = QUERIES[query_selection]

    # Editable SQL area
    query_input = st.text_area("Or edit / enter your own SQL:", value=selected_query_text, height=200)

    if st.button("Run Query"):
        if query_input.strip():
            with st.spinner("Running query..."):
                rows = run_query(conn, query_input)

            if rows:
                st.subheader("Results")
                st.dataframe(rows, use_container_width=True)
                st.success("✅ Query executed successfully!")
            else:
                st.warning("⚠️ No results returned.")
        else:
            st.warning("Please enter a SQL query.")

    conn.close()
    st.markdown("---")
    st.subheader("📌 Available Tables")
    st.write("""
    - `players`
    - `recent_matches`
    - `top_odi_runs`
    - `venues`
    - `combined_matches`
    - `batting_data`
    - `series_matches`
    - `players_stats`
    - `players_partnerships_data`
    - `bowlers_bowling_venue_data`
    - `batters_batting_data`
    - `bowling_data`
    - `fielding_data`
    """)


# ----------------- Run App -----------------
if __name__ == "__main__":
    show_sql_queries()
