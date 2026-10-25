
import streamlit as st
import pandas as pd
from database import get_connection


# --------------------------------------------------
# FUNCTION 1: Get the count of records in a table
# --------------------------------------------------
def get_count(table_name):
    """
    Returns the total number of records in a table.
    Uses lowercase table names to match the Aiven database.
    """

    # Allow only known table names for safety
    allowed_tables = {
        "users",
        "datasets",
        "dataset_versions",
        "preprocessing",
        "models",
        "performance",
    }

    if table_name not in allowed_tables:
        raise ValueError(f"Invalid table name: {table_name}")

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = f"SELECT COUNT(*) FROM `{table_name}`"
        cursor.execute(query)

        result = cursor.fetchone()
        return result[0] if result else 0

    except Exception as e:
        st.error(f"Unable to count records in {table_name}: {e}")
        return 0

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# --------------------------------------------------
# FUNCTION 2: Display the dashboard
# --------------------------------------------------
def show_dashboard():
    """Displays the main dashboard and project statistics."""

    st.title("ML Dataset Management System")
    st.markdown(
        "Monitor datasets, preprocessing activities, "
        "machine learning models, and performance."
    )

    st.divider()

    # Fetch counts using lowercase database table names
    total_users = get_count("users")
    total_datasets = get_count("datasets")
    total_versions = get_count("dataset_versions")
    total_preprocessing = get_count("preprocessing")
    total_models = get_count("models")
    total_performance = get_count("performance")

    # ----------------------------------------------
    # Display summary metrics
    # ----------------------------------------------
    st.subheader("System Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Users", total_users)

    with col2:
        st.metric("Total Datasets", total_datasets)

    with col3:
        st.metric("Dataset Versions", total_versions)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("Preprocessing Records", total_preprocessing)

    with col5:
        st.metric("ML Models", total_models)

    with col6:
        st.metric("Performance Records", total_performance)

    st.divider()

    # ----------------------------------------------
    # Display recent datasets
    # ----------------------------------------------
    st.subheader("Recent Datasets")

    connection = None
    cursor = None

    try:
        connection = get_connection()

        query = """
            SELECT
                d.dataset_id,
                d.dataset_name,
                d.domain,
                u.name AS uploaded_by
            FROM datasets AS d
            LEFT JOIN users AS u
                ON d.user_id = u.user_id
            ORDER BY d.dataset_id DESC
            LIMIT 10
        """

        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)

        datasets = cursor.fetchall()

        if datasets:
            df = pd.DataFrame(datasets)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No datasets have been added yet.")

    except Exception as e:
        st.error(f"Unable to load recent datasets: {e}")

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

    st.divider()

    # ----------------------------------------------
    # Dashboard information
    # ----------------------------------------------
    st.subheader("Available Modules")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            **Dataset Management**
            - Upload and organize datasets
            - Manage dataset versions
            - Track preprocessing activities
            """
        )

    with col2:
        st.markdown(
            """
            **Machine Learning Management**
            - Manage machine learning models
            - Record model performance
            - Review evaluation results
            """
        )