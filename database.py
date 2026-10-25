
import os
import streamlit as st
import mysql.connector


def get_connection():
    """Use Render environment variables or Streamlit secrets for cloud,
    and local MySQL for local development."""

    # Option 1: Render environment variables
    if os.getenv("MYSQL_HOST"):
        host = os.getenv("MYSQL_HOST")
        port = int(os.getenv("MYSQL_PORT", "3306"))
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")
        database = os.getenv("MYSQL_DATABASE")

    # Option 2: Streamlit Cloud secrets
    else:
        try:
            db = st.secrets["mysql"]
            host = db["host"]
            port = int(db["port"])
            user = db["user"]
            password = db["password"]
            database = db["database"]

        # Option 3: Local MySQL
        except (KeyError, FileNotFoundError):
            host = "localhost"
            port = 3306
            user = os.getenv("LOCAL_MYSQL_USER", "root")
            password = os.getenv("LOCAL_MYSQL_PASSWORD", "")
            database = "ml_dataset_management"

    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        ssl_disabled=(host == "localhost" or host == "127.0.0.1"),
        connection_timeout=15
    )
