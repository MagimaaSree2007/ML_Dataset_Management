
import streamlit as st
import pandas as pd
import os

from database import get_connection


UPLOAD_FOLDER = "uploads"


# ==================================================
# GET DATASETS
# ==================================================

def get_datasets():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT dataset_id, dataset_name
            FROM datasets
            ORDER BY dataset_name
        """

        cursor.execute(query)
        return cursor.fetchall()

    except Exception as e:
        st.error(f"Unable to retrieve datasets: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ==================================================
# SAVE VERSION
# ==================================================

def save_version(
    dataset_id,
    version_number,
    changes_description,
    file_name,
    file_path
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO dataset_versions
            (
                dataset_id,
                version_number,
                changes_description,
                file_name,
                file_path
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            dataset_id,
            version_number,
            changes_description,
            file_name,
            file_path
        )

        cursor.execute(query, values)
        connection.commit()

    except Exception:
        if connection:
            connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ==================================================
# ADD DATASET VERSION
# ==================================================

def add_version():
    st.title("🔄 Dataset Version Management")

    st.write(
        "Create and manage different versions of your machine learning datasets."
    )

    st.divider()

    datasets = get_datasets()

    if not datasets:
        st.warning("No datasets available. Please upload a dataset first.")
        return

    dataset_options = {
        f'{dataset["dataset_name"]} (ID: {dataset["dataset_id"]})':
        dataset["dataset_id"]
        for dataset in datasets
    }

    selected_dataset = st.selectbox(
        "Select Dataset",
        list(dataset_options.keys())
    )

    dataset_id = dataset_options[selected_dataset]

    st.divider()
    st.subheader("📝 Version Information")

    version_number = st.text_input(
        "Version Number",
        placeholder="Example: 1.0, 1.1, 2.0"
    ).strip()

    changes_description = st.text_area(
        "Changes Description",
        placeholder=(
            "Example: Missing values removed, duplicates handled "
            "and new features added."
        )
    ).strip()

    st.subheader("📤 Upload Version File")

    uploaded_file = st.file_uploader(
        "Choose the updated dataset file",
        type=["csv", "xlsx", "json"],
        key="dataset_version_upload"
    )

    if uploaded_file is None:
        return

    file_name = os.path.basename(uploaded_file.name)
    file_extension = os.path.splitext(file_name)[1].lower()

    # Read the uploaded dataset
    try:
        if file_extension == ".csv":
            df = pd.read_csv(uploaded_file)
        elif file_extension == ".xlsx":
            df = pd.read_excel(uploaded_file)
        elif file_extension == ".json":
            df = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file format.")
            return

    except Exception as e:
        st.error(f"Unable to read dataset: {e}")
        return

    st.subheader("👀 Version Preview")
    st.dataframe(df.head(10), use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Rows", df.shape[0])

    with col2:
        st.metric("Columns", df.shape[1])

    with col3:
        st.metric(
            "File Size",
            f"{uploaded_file.size / (1024 * 1024):.2f} MB"
        )

    st.write("**Columns:**", list(df.columns))
    st.divider()

    if st.button("💾 Save Dataset Version", type="primary"):
        if not version_number:
            st.warning("Please enter a version number.")
            return

        if not changes_description:
            st.warning("Please describe the changes made.")
            return

        version_file_name = None
        file_path = None

        try:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            safe_version = (
                version_number
                .replace(" ", "_")
                .replace("/", "_")
                .replace("\\", "_")
            )

            version_file_name = (
                f"dataset_{dataset_id}_"
                f"version_{safe_version}_"
                f"{file_name}"
            )

            file_path = os.path.join(
                UPLOAD_FOLDER,
                version_file_name
            )

            # Save the uploaded file
            uploaded_file.seek(0)

            with open(file_path, "wb") as file:
                file.write(uploaded_file.getbuffer())

            # Save version details in MySQL
            save_version(
                dataset_id,
                version_number,
                changes_description,
                version_file_name,
                file_path
            )

            st.success("✅ Dataset version saved successfully!")
            st.rerun()

        except Exception as e:
            # Avoid leaving an orphaned file if database saving fails
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass

            st.error(f"Error saving version: {e}")


# ==================================================
# VERSION HISTORY
# ==================================================

def view_versions():
    st.title("📜 Dataset Version History")

    st.write(
        "View and track all versions of your machine learning datasets."
    )

    st.divider()

    datasets = get_datasets()

    if not datasets:
        st.info("No datasets available.")
        return

    dataset_options = {
        f'{dataset["dataset_name"]} (ID: {dataset["dataset_id"]})':
        dataset["dataset_id"]
        for dataset in datasets
    }

    selected_dataset = st.selectbox(
        "Select Dataset",
        list(dataset_options.keys()),
        key="version_history_dataset"
    )

    dataset_id = dataset_options[selected_dataset]

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                version_id,
                version_number,
                changes_description,
                file_name,
                file_path,
                upload_date
            FROM dataset_versions
            WHERE dataset_id = %s
            ORDER BY upload_date DESC
        """

        cursor.execute(query, (dataset_id,))
        versions = cursor.fetchall()

    except Exception as e:
        st.error(f"Unable to retrieve version history: {e}")
        return

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("🔄 Total Versions", len(versions))

    with col2:
        latest_version = (
            versions[0]["version_number"] if versions else "None"
        )
        st.metric("🆕 Latest Version", latest_version)

    if not versions:
        st.info("No versions available for this dataset.")
        return

    st.subheader("📋 Version Records")

    version_df = pd.DataFrame(versions)

    display_columns = [
        "version_id",
        "version_number",
        "changes_description",
        "file_name",
        "upload_date"
    ]

    st.dataframe(
        version_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("🔎 Version Details")

    # Use the version ID as the unique selection value
    version_lookup = {
        f'Version {v["version_number"]} (ID: {v["version_id"]})':
        v
        for v in versions
    }

    selected_label = st.selectbox(
        "Select Version",
        list(version_lookup.keys()),
        key="version_details_selection"
    )

    selected_record = version_lookup[selected_label]

    st.write("**Version Number:**", selected_record["version_number"])
    st.write("**Changes:**", selected_record["changes_description"])
    st.write("**File Name:**", selected_record["file_name"])
    st.write("**Upload Date:**", selected_record["upload_date"])
    st.write("**File Path:**", selected_record["file_path"])
