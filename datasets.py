
import streamlit as st
import pandas as pd
import os

from database import get_connection


# ==================================================
# UPLOAD FOLDER
# ==================================================

UPLOAD_FOLDER = "uploads"


# ==================================================
# SAVE DATASET METADATA
# ==================================================

def save_dataset_metadata(
    dataset_name,
    description,
    domain,
    file_name,
    file_path,
    file_type,
    file_size_mb,
    row_count,
    column_count,
    column_names,
    target_column,
    user_id
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO datasets
            (
                dataset_name,
                description,
                domain,
                file_name,
                file_path,
                file_type,
                file_size_mb,
                row_count,
                column_count,
                column_names,
                target_column,
                user_id
            )
            VALUES (%s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s)
        """

        values = (
            dataset_name,
            description,
            domain,
            file_name,
            file_path,
            file_type,
            file_size_mb,
            row_count,
            column_count,
            column_names,
            target_column,
            user_id
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
# UPLOAD DATASET PAGE
# ==================================================

def upload_dataset(user_id):
    st.title("📁 Dataset Management")

    st.write("Upload and manage machine learning datasets.")
    st.divider()

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    st.subheader("📤 Upload Dataset")

    dataset_name = st.text_input("Dataset Name")
    description = st.text_area("Description")

    domain = st.selectbox(
        "Domain",
        [
            "Healthcare",
            "Finance",
            "Agriculture",
            "Education",
            "Business",
            "Environment",
            "Other"
        ]
    )

    uploaded_file = st.file_uploader(
        "Choose a dataset",
        type=["csv", "xlsx", "json"],
        key="dataset_upload_file"
    )

    if uploaded_file is None:
        return

    file_name = os.path.basename(uploaded_file.name)
    file_extension = os.path.splitext(file_name)[1].lower()

    # READ DATASET
    try:
        if file_extension == ".csv":
            df = pd.read_csv(uploaded_file)
            file_type = "CSV"

        elif file_extension == ".xlsx":
            df = pd.read_excel(uploaded_file)
            file_type = "Excel"

        elif file_extension == ".json":
            df = pd.read_json(uploaded_file)
            file_type = "JSON"

        else:
            st.error("Unsupported file format.")
            return

    except Exception as e:
        st.error(f"Unable to read dataset: {e}")
        return

    # DATASET INFORMATION
    row_count = df.shape[0]
    column_count = df.shape[1]
    column_names = ",".join(df.columns.astype(str))
    file_size_mb = uploaded_file.size / (1024 * 1024)

    # TARGET COLUMN
    target_options = ["None"] + [
        str(column) for column in df.columns
    ]

    selected_target = st.selectbox(
        "Select Target Column",
        target_options,
        key="dataset_target_column"
    )

    target_column = (
        None if selected_target == "None"
        else selected_target
    )

    # DATASET PREVIEW
    st.subheader("👀 Dataset Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )

    # DATASET INFORMATION
    st.subheader("📊 Dataset Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Rows", row_count)

    with col2:
        st.metric("Columns", column_count)

    with col3:
        st.metric("File Size", f"{file_size_mb:.2f} MB")

    st.write("**Columns:**", list(df.columns))

    # SAVE DATASET
    if st.button("💾 Save Dataset", type="primary"):
        if not dataset_name.strip():
            st.warning("Please enter a dataset name.")
            return

        file_path = None

        try:
            # Use a unique filename to avoid overwriting
            # an existing dataset with the same filename.
            import uuid

            stored_file_name = (
                f"{uuid.uuid4().hex}_{file_name}"
            )

            file_path = os.path.join(
                UPLOAD_FOLDER,
                stored_file_name
            )

            uploaded_file.seek(0)

            with open(file_path, "wb") as file:
                file.write(uploaded_file.getbuffer())

            save_dataset_metadata(
                dataset_name.strip(),
                description.strip(),
                domain,
                stored_file_name,
                file_path,
                file_type,
                file_size_mb,
                row_count,
                column_count,
                column_names,
                target_column,
                user_id
            )

            st.success("✅ Dataset uploaded successfully!")

        except Exception as e:
            # Remove the file if its metadata was not saved.
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass

            st.error(f"Error saving dataset: {e}")


# ==================================================
# GET ALL DATASETS
# ==================================================

def get_all_datasets():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                d.dataset_id,
                d.dataset_name,
                d.description,
                d.domain,
                d.file_name,
                d.file_type,
                d.file_size_mb,
                d.row_count,
                d.column_count,
                d.target_column,
                d.upload_date,
                u.name AS uploaded_by
            FROM datasets d
            JOIN users u
                ON d.user_id = u.user_id
            ORDER BY d.upload_date DESC
        """

        cursor.execute(query)
        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ==================================================
# DATASET LIBRARY
# ==================================================

def view_datasets():
    st.title("📚 Dataset Library")

    st.write(
        "Search, filter and explore available machine learning datasets."
    )

    st.divider()

    try:
        datasets = get_all_datasets()
    except Exception as e:
        st.error(f"Unable to load dataset library: {e}")
        return

    if not datasets:
        st.info("No datasets available.")
        return

    df = pd.DataFrame(datasets)

    # SEARCH
    st.subheader("🔍 Search & Filter")

    search_text = st.text_input(
        "Search Dataset Name",
        placeholder="Example: Diabetes",
        key="dataset_library_search"
    )

    col1, col2, col3 = st.columns(3)

    # DOMAIN FILTER
    domain_options = ["All"] + sorted(
        df["domain"].dropna().astype(str).unique().tolist()
    )

    with col1:
        selected_domain = st.selectbox(
            "Domain",
            domain_options,
            key="dataset_domain_filter"
        )

    # FILE TYPE FILTER
    file_type_options = ["All"] + sorted(
        df["file_type"].dropna().astype(str).unique().tolist()
    )

    with col2:
        selected_file_type = st.selectbox(
            "File Type",
            file_type_options,
            key="dataset_file_type_filter"
        )

    # TARGET COLUMN FILTER
    target_options = ["All"] + sorted(
        df["target_column"].dropna().astype(str).unique().tolist()
    )

    with col3:
        selected_target = st.selectbox(
            "Target Column",
            target_options,
            key="dataset_target_filter"
        )

    # SORTING
    sort_option = st.selectbox(
        "Sort By",
        [
            "Newest First",
            "Oldest First",
            "Dataset Name",
            "Most Rows",
            "Most Columns"
        ],
        key="dataset_sort_option"
    )

    filtered_df = df.copy()

    # SEARCH DATASET NAME
    if search_text:
        filtered_df = filtered_df[
            filtered_df["dataset_name"]
            .astype(str)
            .str.contains(
                search_text,
                case=False,
                na=False,
                regex=False
            )
        ]

    # DOMAIN FILTER
    if selected_domain != "All":
        filtered_df = filtered_df[
            filtered_df["domain"].astype(str)
            == selected_domain
        ]

    # FILE TYPE FILTER
    if selected_file_type != "All":
        filtered_df = filtered_df[
            filtered_df["file_type"].astype(str)
            == selected_file_type
        ]

    # TARGET COLUMN FILTER
    if selected_target != "All":
        filtered_df = filtered_df[
            filtered_df["target_column"].astype(str)
            == selected_target
        ]

    # SORTING
    if sort_option == "Newest First":
        filtered_df = filtered_df.sort_values(
            by="upload_date",
            ascending=False
        )

    elif sort_option == "Oldest First":
        filtered_df = filtered_df.sort_values(
            by="upload_date",
            ascending=True
        )

    elif sort_option == "Dataset Name":
        filtered_df = filtered_df.sort_values(
            by="dataset_name",
            ascending=True
        )

    elif sort_option == "Most Rows":
        filtered_df = filtered_df.sort_values(
            by="row_count",
            ascending=False
        )

    elif sort_option == "Most Columns":
        filtered_df = filtered_df.sort_values(
            by="column_count",
            ascending=False
        )

    # RESULTS
    st.divider()

    st.write(
        f"📊 **{len(filtered_df)} dataset(s) found**"
    )

    if not filtered_df.empty:
        display_columns = [
            "dataset_id",
            "dataset_name",
            "domain",
            "file_type",
            "row_count",
            "column_count",
            "target_column",
            "uploaded_by",
            "upload_date"
        ]

        st.dataframe(
            filtered_df[display_columns],
            use_container_width=True,
            hide_index=True
        )

    else:
        st.warning(
            "No datasets match the selected filters."
        )


# ==================================================
# END OF FILE
# ==================================================
