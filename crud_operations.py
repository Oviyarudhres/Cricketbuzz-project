# crud_operations_cricket.py
import streamlit as st
import pymysql
import os
from dotenv import load_dotenv

# ----------------- DB Connection -----------------
def create_connection():
    """Connect to MySQL (reuses same style as your queries file)."""
    load_dotenv()
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "Oviya@0108"),
            database=os.getenv("DB_NAME", "cricketss_api"),
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        st.error(f"❌ DB connection error: {e}")
        return None


# ----------------- Extract -----------------
def fetch_table(conn, table, limit=100):
    """Extract table rows."""
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {table} LIMIT {limit}")
            return cur.fetchall()
    except Exception as e:
        st.error(f"Read error: {e}")
        return []


def get_columns(conn, table):
    """Extract column metadata for a table."""
    try:
        with conn.cursor() as cur:
            cur.execute(f"DESCRIBE {table}")
            return cur.fetchall()
    except Exception as e:
        st.error(f"Metadata error: {e}")
        return []


# ----------------- Load (CRUD Ops) -----------------
def insert_row(conn, table, row_dict):
    """Insert a row dynamically."""
    cols = ", ".join(row_dict.keys())
    vals = ", ".join(["%s"] * len(row_dict))
    sql = f"INSERT INTO {table} ({cols}) VALUES ({vals})"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, list(row_dict.values()))
        return True
    except Exception as e:
        st.error(f"Insert error: {e}")
        return False


def update_rows(conn, table, set_clause, where_clause):
    """Update row(s)."""
    sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        return True
    except Exception as e:
        st.error(f"Update error: {e}")
        return False


def delete_rows(conn, table, where_clause):
    """Delete row(s)."""
    sql = f"DELETE FROM {table} WHERE {where_clause}"
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        return True
    except Exception as e:
        st.error(f"Delete error: {e}")
        return False


# ----------------- Streamlit UI -----------------
def show_crud_operations():
    st.title("🛠️ Cricket Database CRUD (ETL Style)")

    conn = create_connection()
    if not conn:
        st.stop()

    # Select table
    st.subheader("📂 Choose Table")
    tables = ["players", "recent_matches", "venues", "batting_data"]
    table = st.selectbox("Table", tables)

    st.divider()

    # READ
    st.subheader("📖 View Table")
    limit = st.slider("Rows to load", 5, 1000, 50)
    rows = fetch_table(conn, table, limit)
    if rows:
        st.dataframe(rows, use_container_width=True)

    st.divider()

    # CREATE
    st.subheader("➕ Insert Row")
    cols = get_columns(conn, table)
    form_inputs = {}
    with st.form("insert_form", clear_on_submit=True):
        for col in cols:
            col_name = col["Field"]
            if col["Extra"] == "auto_increment":
                st.text_input(f"{col_name} (AUTO)", disabled=True)
            else:
                form_inputs[col_name] = st.text_input(f"{col_name} ({col['Type']})")
        submit_insert = st.form_submit_button("Insert Row")
    if submit_insert:
        clean = {k: v for k, v in form_inputs.items() if v.strip() != ""}
        if insert_row(conn, table, clean):
            st.success("✅ Row inserted!")

    st.divider()

    # UPDATE
    st.subheader("📝 Update Rows")
    with st.form("update_form"):
        set_clause = st.text_input("SET clause", placeholder="player_name='New Name'")
        where_clause = st.text_input("WHERE clause", placeholder="player_id=1")
        submit_update = st.form_submit_button("Run Update")
    if submit_update:
        if update_rows(conn, table, set_clause, where_clause):
            st.success("✅ Update successful!")

    st.divider()

    # DELETE
    st.subheader("🗑️ Delete Rows")
    with st.form("delete_form"):
        where_clause = st.text_input("WHERE condition", placeholder="player_id=1")
        submit_delete = st.form_submit_button("Delete")
    if submit_delete:
        if delete_rows(conn, table, where_clause):
            st.success("✅ Row(s) deleted!")


# ----------------- Run App -----------------
if __name__ == "__main__":
    show_crud_operations()
