import streamlit as st
import pandas as pd
import mysql.connector

# --- Database connection ---
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='Ramya@123',
    database='sys'
)
cursor = conn.cursor(dictionary=True)

def run_query(sql, params=None):
    cursor.execute(sql, params or ())
    return pd.DataFrame(cursor.fetchall())

# --- Expanded SQL queries dictionary ---
queries = {
    "1. Count how many times each asteroid approached Earth":
        "SELECT neo_reference_id, COUNT(*) AS approach_count FROM close_approach GROUP BY neo_reference_id",

    "2. Average velocity of each asteroid over multiple approaches":
        "SELECT neo_reference_id, AVG(relative_velocity_kmph) AS avg_velocity FROM close_approach GROUP BY neo_reference_id",

    "3. Top 10 fastest asteroids":
        "SELECT neo_reference_id, MAX(relative_velocity_kmph) AS max_velocity FROM close_approach GROUP BY neo_reference_id ORDER BY max_velocity DESC LIMIT 10",

    "4. Hazardous asteroids with > 3 approaches":
        "SELECT A.name, COUNT(*) AS approaches FROM Asteroids A JOIN close_approach C ON A.id = C.neo_reference_id WHERE A.is_potentially_hazardous_asteroid = 1 GROUP BY A.id HAVING approaches > 3",

    "5. Month with the most asteroid approaches":
        "SELECT DATE_FORMAT(close_approach_date, '%Y-%m') AS month, COUNT(*) AS count FROM close_approach GROUP BY month ORDER BY count DESC LIMIT 1",

    "6. Asteroid with the fastest approach speed":
        "SELECT A.name, C.relative_velocity_kmph FROM close_approach C JOIN Asteroids A ON A.id = C.neo_reference_id ORDER BY C.relative_velocity_kmph DESC LIMIT 1",

    "7. Asteroids sorted by max estimated diameter":
        "SELECT name, estimated_diameter_max_km FROM Asteroids ORDER BY estimated_diameter_max_km DESC",

    "8. Asteroids getting closer over time (miss distance vs date)":
        "SELECT neo_reference_id, close_approach_date, miss_distance_km FROM close_approach ORDER BY neo_reference_id, close_approach_date",

    "9. Closest approach date & distance per asteroid":
        "SELECT A.name, MIN(C.close_approach_date) AS closest_date, MIN(C.miss_distance_km) AS closest_distance FROM close_approach C JOIN Asteroids A ON A.id = C.neo_reference_id GROUP BY A.id",

    "10. Asteroids with velocity > 50,000 km/h":
        "SELECT A.name, C.relative_velocity_kmph FROM close_approach C JOIN Asteroids A ON A.id = C.neo_reference_id WHERE C.relative_velocity_kmph > 50000",

    "11. Count approaches per month":
        "SELECT DATE_FORMAT(close_approach_date, '%Y-%m') AS month, COUNT(*) AS count FROM close_approach GROUP BY month",

    "12. Brightest asteroid (lowest absolute magnitude)":
        "SELECT name, absolute_magnitude_h FROM Asteroids ORDER BY absolute_magnitude_h ASC LIMIT 1",

    "13. Count hazardous vs non-hazardous asteroids":
        "SELECT is_potentially_hazardous_asteroid, COUNT(*) AS count FROM Asteroids GROUP BY is_potentially_hazardous_asteroid",

    "14. Asteroids that passed closer than the Moon (< 1 LD)":
        "SELECT A.name, C.close_approach_date, C.miss_distance_lunar FROM close_approach C JOIN Asteroids A ON A.id = C.neo_reference_id WHERE C.miss_distance_lunar < 1",

    "15. Asteroids within 0.05 AU":
        "SELECT A.name, C.close_approach_date, C.astronomical FROM close_approach C JOIN Asteroids A ON A.id = C.neo_reference_id WHERE C.astronomical < 0.05",

    # New advanced queries:

    "16. Largest asteroid ever recorded":
        "SELECT name, estimated_diameter_max_km FROM Asteroids ORDER BY estimated_diameter_max_km DESC LIMIT 1",

    "17. Smallest asteroid ever recorded":
        "SELECT name, estimated_diameter_min_km FROM Asteroids ORDER BY estimated_diameter_min_km ASC LIMIT 1",

    "18. Average miss distance (km) by asteroid":
        "SELECT neo_reference_id, AVG(miss_distance_km) AS avg_miss_km FROM close_approach GROUP BY neo_reference_id",

    "19. Asteroids orbiting Mars":
        "SELECT A.name, C.orbiting_body FROM close_approach C JOIN Asteroids A ON A.id = C.neo_reference_id WHERE C.orbiting_body = 'Mars'",

    "20. Most frequent orbiting body other than Earth":
        "SELECT orbiting_body, COUNT(*) AS count FROM close_approach WHERE orbiting_body != 'Earth' GROUP BY orbiting_body ORDER BY count DESC LIMIT 1",

    "21. Median velocity of all approaches":
        "SELECT AVG(relative_velocity_kmph) AS median_velocity FROM (SELECT relative_velocity_kmph FROM close_approach ORDER BY relative_velocity_kmph LIMIT 2 - (SELECT COUNT(*) FROM close_approach) % 2 OFFSET (SELECT (COUNT(*) - 1) / 2 FROM close_approach)) AS median_subquery",

    "22. Asteroids with increasing velocity trend (over multiple approaches)":
        """
        SELECT neo_reference_id
        FROM close_approach
        GROUP BY neo_reference_id
        HAVING MAX(relative_velocity_kmph) > MIN(relative_velocity_kmph)
        """,

    "23. Count of unique asteroids observed":
        "SELECT COUNT(DISTINCT neo_reference_id) AS unique_asteroids FROM close_approach",

    "24. Average estimated diameter of hazardous asteroids":
        "SELECT AVG(estimated_diameter_max_km) AS avg_max_diameter FROM Asteroids WHERE is_potentially_hazardous_asteroid = 1",

    "25. Asteroids with close approaches in last 5 years":
        "SELECT A.name, C.close_approach_date FROM close_approach C JOIN Asteroids A ON A.id = C.neo_reference_id WHERE C.close_approach_date >= DATE_SUB(CURDATE(), INTERVAL 5 YEAR)"
}

# --- Streamlit UI ---

st.set_page_config(page_title="🚀 Asteroid Data Explorer", layout="wide")

st.title("🚀 Asteroid Data Explorer")

st.markdown(
    """
    Welcome to the Asteroid Data Explorer!  
    Use the sidebar to select from predefined queries or apply custom filters to explore the asteroid dataset.
    """
)

# Sidebar: Query selection
st.sidebar.header("Predefined SQL Queries")
selected_query = st.sidebar.selectbox("Select a query to run", list(queries.keys()))

if st.sidebar.button("Run Query"):
    st.subheader(f"Results: {selected_query}")
    df = run_query(queries[selected_query])
    st.dataframe(df, use_container_width=True)

# Sidebar: Filters
st.sidebar.markdown("---")
st.sidebar.header("Custom Search Filters")

with st.sidebar.expander("Date Range Filter"):
    min_date = st.date_input("From date", value=pd.to_datetime("1990-01-01"))
    max_date = st.date_input("To date", value=pd.to_datetime("2025-12-31"))

with st.sidebar.expander("Numeric Filters"):
    max_au = st.slider("Max Astronomical Units", 0.0, 1.0, 0.3)
    max_lunar = st.slider("Max Lunar Distance", 0.0, 100.0, 50.0)
    min_velocity = st.slider("Min Relative Velocity (km/h)", 0.0, 100000.0, 25000.0)
    min_diam_min = st.slider("Min Estimated Diameter Min (km)", 0.0, 10.0, 0.0)
    max_diam_max = st.slider("Max Estimated Diameter Max (km)", 0.0, 20.0, 10.0)

hazard_choice = st.sidebar.selectbox("Is Hazardous?", ["All", "Yes", "No"])

# Filter Query
filter_query = """
SELECT A.name, C.close_approach_date, C.relative_velocity_kmph, 
       C.astronomical, C.miss_distance_lunar, C.miss_distance_km,
       A.estimated_diameter_min_km, A.estimated_diameter_max_km, 
       A.is_potentially_hazardous_asteroid
FROM close_approach C
JOIN Asteroids A ON A.id = C.neo_reference_id
WHERE C.close_approach_date BETWEEN %s AND %s
  AND C.astronomical <= %s
  AND C.miss_distance_lunar <= %s
  AND C.relative_velocity_kmph >= %s
  AND A.estimated_diameter_min_km >= %s
  AND A.estimated_diameter_max_km <= %s
"""

params = [min_date, max_date, max_au, max_lunar, min_velocity, min_diam_min, max_diam_max]

if hazard_choice == "Yes":
    filter_query += " AND A.is_potentially_hazardous_asteroid = 1"
elif hazard_choice == "No":
    filter_query += " AND A.is_potentially_hazardous_asteroid = 0"

if st.sidebar.button("Run Filtered Search"):
    st.subheader("Filtered Asteroid Approaches")
    filtered_df = run_query(filter_query, params)
    if filtered_df.empty:
        st.warning("No results found for your filter criteria.")
    else:
        st.dataframe(filtered_df, use_container_width=True)