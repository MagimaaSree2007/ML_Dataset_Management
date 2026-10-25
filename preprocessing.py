
import streamlit as st
import pandas as pd

from database import get_connection


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
# SAVE PREPROCESSING DETAILS
# ==================================================

def save_preprocessing(
    dataset_id,
    missing_value_method,
    duplicate_handling,
    encoding_method,
    scaling_method,
    feature_selection,
    other_steps
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO preprocessing
            (
                dataset_id,
                missing_value_method,
                duplicate_handling,
                encoding_method,
                scaling_method,
                feature_selection,
                other_steps
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            dataset_id,
            missing_value_method,
            duplicate_handling,
            encoding_method,
            scaling_method,
            feature_selection,
            other_steps
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
# PREPROCESSING MANAGEMENT
# ==================================================

def preprocessing_page():
    st.title("⚙️ Preprocessing Management")

    st.write(
        "Record and manage preprocessing techniques applied "
        "to machine learning datasets."
    )

    st.divider()

    datasets = get_datasets()

    if not datasets:
        st.warning(
            "No datasets available. Please upload a dataset first."
        )
        return

    dataset_options = {
        f'{dataset["dataset_name"]} (ID: {dataset["dataset_id"]})':
        dataset["dataset_id"]
        for dataset in datasets
    }

    selected_dataset = st.selectbox(
        "Select Dataset",
        list(dataset_options.keys()),
        key="preprocessing_dataset"
    )

    dataset_id = dataset_options[selected_dataset]

    # DATA CLEANING
    st.subheader("🧹 Data Cleaning")

    missing_value_method = st.selectbox(
        "Missing Value Handling",
        [
            "None",
            "Mean Imputation",
            "Median Imputation",
            "Mode Imputation",
            "Forward Fill",
            "Backward Fill",
            "Rows Removed",
            "Other"
        ]
    )

    duplicate_handling = st.selectbox(
        "Duplicate Handling",
        [
            "None",
            "Duplicates Removed",
            "Duplicates Retained"
        ]
    )

    # DATA TRANSFORMATION
    st.subheader("🔄 Data Transformation")

    encoding_method = st.selectbox(
        "Encoding Method",
        [
            "None",
            "Label Encoding",
            "One-Hot Encoding",
            "Ordinal Encoding",
            "Target Encoding",
            "Other"
        ]
    )

    scaling_method = st.selectbox(
        "Scaling Method",
        [
            "None",
            "StandardScaler",
            "MinMaxScaler",
            "RobustScaler",
            "Normalization",
            "Other"
        ]
    )

    # FEATURE SELECTION
    st.subheader("🎯 Feature Selection")

    feature_selection = st.text_input(
        "Feature Selection Method",
        placeholder="Example: Correlation-based feature selection"
    )

    # OTHER STEPS
    st.subheader("📝 Other Preprocessing Steps")

    other_steps = st.text_area(
        "Other Steps",
        placeholder=(
            "Example: Outlier removal, data type conversion, etc."
        )
    )

    st.divider()

    if st.button(
        "💾 Save Preprocessing Details",
        type="primary"
    ):
        try:
            save_preprocessing(
                dataset_id,
                missing_value_method,
                duplicate_handling,
                encoding_method,
                scaling_method,
                feature_selection.strip(),
                other_steps.strip()
            )

            st.success(
                "✅ Preprocessing details saved successfully!"
            )

        except Exception as e:
            st.error(
                f"Error saving preprocessing details: {e}"
            )


# ==================================================
# GET PREPROCESSING HISTORY
# ==================================================

def get_preprocessing_history():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                p.preprocessing_id,
                p.dataset_id,
                d.dataset_name,
                p.missing_value_method,
                p.duplicate_handling,
                p.encoding_method,
                p.scaling_method,
                p.feature_selection,
                p.other_steps,
                p.preprocessing_date
            FROM preprocessing p
            JOIN datasets d
                ON p.dataset_id = d.dataset_id
            ORDER BY p.preprocessing_date DESC
        """

        cursor.execute(query)
        return cursor.fetchall()

    except Exception as e:
        st.error(f"Unable to retrieve preprocessing history: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ==================================================
# PREPROCESSING HISTORY
# ==================================================

def view_preprocessing():
    st.title("📋 Preprocessing History")

    st.write(
        "View, search and analyze preprocessing operations "
        "applied to datasets."
    )

    st.divider()

    records = get_preprocessing_history()

    if not records:
        st.info("No preprocessing records available.")
        return

    df = pd.DataFrame(records)

    # SUMMARY
    st.subheader("📊 Preprocessing Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Records", len(df))

    with col2:
        st.metric("Datasets Processed", df["dataset_id"].nunique())

    with col3:
        latest_date = df.iloc[0]["preprocessing_date"]
        st.metric("Latest Record", str(latest_date))

    st.divider()

    # SEARCH AND FILTER
    st.subheader("🔍 Search & Filter")

    col1, col2, col3 = st.columns(3)

    with col1:
        search_dataset = st.text_input(
            "Search Dataset",
            placeholder="Example: Diabetes",
            key="preprocessing_search"
        )

    missing_options = ["All"] + sorted(
        df["missing_value_method"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    scaling_options = ["All"] + sorted(
        df["scaling_method"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    with col2:
        selected_missing = st.selectbox(
            "Missing Value Method",
            missing_options,
            key="preprocessing_missing_filter"
        )

    with col3:
        selected_scaling = st.selectbox(
            "Scaling Method",
            scaling_options,
            key="preprocessing_scaling_filter"
        )

    # APPLY FILTERS
    filtered_df = df.copy()

    if search_dataset:
        filtered_df = filtered_df[
            filtered_df["dataset_name"]
            .astype(str)
            .str.contains(
                search_dataset,
                case=False,
                na=False,
                regex=False
            )
        ]

    if selected_missing != "All":
        filtered_df = filtered_df[
            filtered_df["missing_value_method"].astype(str)
            == selected_missing
        ]

    if selected_scaling != "All":
        filtered_df = filtered_df[
            filtered_df["scaling_method"].astype(str)
            == selected_scaling
        ]

    st.divider()

    st.write(
        f"📊 **{len(filtered_df)} preprocessing record(s) found**"
    )

    if filtered_df.empty:
        st.warning(
            "No preprocessing records match the selected filters."
        )
        return

    # DISPLAY TABLE
    display_columns = [
        "preprocessing_id",
        "dataset_name",
        "missing_value_method",
        "duplicate_handling",
        "encoding_method",
        "scaling_method",
        "feature_selection",
        "preprocessing_date"
    ]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    # RECORD DETAILS
    st.divider()
    st.subheader("🔎 Preprocessing Details")

    record_options = {
        (
            f'Record {record["preprocessing_id"]} — '
            f'{record["dataset_name"]}'
        ): record["preprocessing_id"]
        for record in filtered_df.to_dict("records")
    }

    selected_label = st.selectbox(
        "Select Record",
        list(record_options.keys()),
        key="preprocessing_record_details"
    )

    selected_record_id = record_options[selected_label]

    selected_record = filtered_df[
        filtered_df["preprocessing_id"] == selected_record_id
    ].iloc[0]

    st.write("**Dataset:**", selected_record["dataset_name"])
    st.write(
        "**Missing Value Handling:**",
        selected_record["missing_value_method"]
    )
    st.write(
        "**Duplicate Handling:**",
        selected_record["duplicate_handling"]
    )
    st.write(
        "**Encoding Method:**",
        selected_record["encoding_method"]
    )
    st.write(
        "**Scaling Method:**",
        selected_record["scaling_method"]
    )
    st.write(
        "**Feature Selection:**",
        selected_record["feature_selection"]
    )
    st.write(
        "**Other Steps:**",
        selected_record["other_steps"]
    )
    st.write(
        "**Preprocessing Date:**",
        selected_record["preprocessing_date"]
    )


# ==================================================
# END OF FILE
# ==================================================
