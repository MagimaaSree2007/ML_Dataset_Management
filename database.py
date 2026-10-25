
import os
import mysql.connector
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    """Use Aiven on Streamlit Cloud and local MySQL on your PC."""

    try:
        # Try to read cloud credentials if Streamlit secrets exist.
        try:
            db = st.secrets["mysql"]
        except (KeyError, FileNotFoundError):
            db = None
        except Exception as e:
            # No secrets.toml file is normal for local development.
            if "No secrets found" in str(e):
                db = None
            else:
                raise

        if db is not None:
            # Cloud database: Aiven MySQL
            connection = mysql.connector.connect(
                host=db["host"],
                port=int(db["port"]),
                user=db["user"],
                password=db["password"],
                database=db["database"],
                ssl_disabled=False,
                connection_timeout=10
            )
        else:
            # Local database: your computer
            connection = mysql.connector.connect(
                host="127.0.0.1",
                port=3306,
                user="root",
                password=os.getenv("LOCAL_MYSQL_PASSWORD", ""),
                database="ml_dataset_management",
                connection_timeout=10
            )

        return connection

    except mysql.connector.Error as e:
        st.error(f"Database connection failed: {e}")
        raise


