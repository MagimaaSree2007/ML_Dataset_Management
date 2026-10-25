import streamlit as st
import pandas as pd

from database import get_connection


# ==================================================
# GET DATASETS
# ==================================================

def get_datasets():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            dataset_id,
            dataset_name
        FROM Datasets
        ORDER BY dataset_name
    """

    cursor.execute(query)

    datasets = cursor.fetchall()

    cursor.close()
    connection.close()

    return datasets


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

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO Preprocessing
        (
            dataset_id,
            missing_value_method,
            duplicate_handling,
            encoding_method,
            scaling_method,
            feature_selection,
            other_steps
        )
        VALUES
        (
            %s, %s, %s, %s, %s, %s, %s
        )
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

    cursor.close()
    connection.close()


# ==================================================
# PREPROCESSING MANAGEMENT
# ==================================================

def preprocessing_page():

    st.title("⚙️ Preprocessing Management")

    st.write(
        "Record and manage preprocessing techniques applied to machine learning datasets."
    )

    st.divider()

    # ------------------------------------------
    # GET DATASETS
    # ------------------------------------------

    datasets = get_datasets()

    if not datasets:

        st.warning(
            "No datasets available. Please upload a dataset first."
        )

        return

    dataset_options = {}

    for dataset in datasets:

        dataset_options[
            dataset["dataset_name"]
            + " (ID: "
            + str(dataset["dataset_id"])
            + ")"
        ] = dataset["dataset_id"]

    selected_dataset = st.selectbox(
        "Select Dataset",
        list(dataset_options.keys())
    )

    dataset_id = dataset_options[
        selected_dataset
    ]

    # ------------------------------------------
    # DATA CLEANING
    # ------------------------------------------

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

    # ------------------------------------------
    # DATA TRANSFORMATION
    # ------------------------------------------

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

    # ------------------------------------------
    # FEATURE SELECTION
    # ------------------------------------------

    st.subheader("🎯 Feature Selection")

    feature_selection = st.text_input(
        "Feature Selection Method",
        placeholder="Example: Correlation-based feature selection"
    )

    # ------------------------------------------
    # OTHER STEPS
    # ------------------------------------------

    st.subheader("📝 Other Preprocessing Steps")

    other_steps = st.text_area(
        "Other Steps",
        placeholder="Example: Outlier removal, data type conversion, etc."
    )

    st.divider()

    # ------------------------------------------
    # SAVE
    # ------------------------------------------

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
                feature_selection,
                other_steps
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
        FROM Preprocessing p
        JOIN Datasets d
        ON p.dataset_id = d.dataset_id
        ORDER BY p.preprocessing_date DESC
    """

    cursor.execute(query)

    records = cursor.fetchall()

    cursor.close()
    connection.close()

    return records


# ==================================================
# PREPROCESSING HISTORY
# ==================================================

def view_preprocessing():

    st.title("📋 Preprocessing History")

    st.write(
        "View, search and analyze preprocessing operations applied to datasets."
    )

    st.divider()

    # ------------------------------------------
    # GET RECORDS
    # ------------------------------------------

    records = get_preprocessing_history()

    if not records:

        st.info(
            "No preprocessing records available."
        )

        return

    df = pd.DataFrame(records)

    # ------------------------------------------
    # SUMMARY
    # ------------------------------------------

    st.subheader("📊 Preprocessing Summary")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Records",
            len(df)
        )

    with col2:

        st.metric(
            "Datasets Processed",
            df["dataset_id"].nunique()
        )

    with col3:

        st.metric(
            "Latest Record",
            str(df.iloc[0]["preprocessing_date"])
        )

    st.divider()

    # ------------------------------------------
    # SEARCH & FILTER
    # ------------------------------------------

    st.subheader("🔍 Search & Filter")

    col1, col2, col3 = st.columns(3)

    # Dataset search
    with col1:

        search_dataset = st.text_input(
            "Search Dataset",
            placeholder="Example: Diabetes"
        )

    # Missing value filter
    with col2:

        missing_options = ["All"]

        for value in df[
            "missing_value_method"
        ].dropna():

            value = str(value)

            if value not in missing_options:

                missing_options.append(value)

        selected_missing = st.selectbox(
            "Missing Value Method",
            missing_options
        )

    # Scaling filter
    with col3:

        scaling_options = ["All"]

        for value in df[
            "scaling_method"
        ].dropna():

            value = str(value)

            if value not in scaling_options:

                scaling_options.append(value)

        selected_scaling = st.selectbox(
            "Scaling Method",
            scaling_options
        )

    # ------------------------------------------
    # APPLY SEARCH
    # ------------------------------------------

    filtered_df = df.copy()

    if search_dataset:

        filtered_df = filtered_df[
            filtered_df["dataset_name"]
            .astype(str)
            .str.contains(
                search_dataset,
                case=False,
                na=False
            )
        ]

    # ------------------------------------------
    # APPLY MISSING VALUE FILTER
    # ------------------------------------------

    if selected_missing != "All":

        filtered_df = filtered_df[
            filtered_df[
                "missing_value_method"
            ].astype(str)
            == selected_missing
        ]

    # ------------------------------------------
    # APPLY SCALING FILTER
    # ------------------------------------------

    if selected_scaling != "All":

        filtered_df = filtered_df[
            filtered_df[
                "scaling_method"
            ].astype(str)
            == selected_scaling
        ]

    # ------------------------------------------
    # RESULT COUNT
    # ------------------------------------------

    st.divider()

    st.write(
        f"📊 **{len(filtered_df)} preprocessing record(s) found**"
    )

    # ------------------------------------------
    # DISPLAY TABLE
    # ------------------------------------------

    if not filtered_df.empty:

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

        # --------------------------------------
        # DETAILS
        # --------------------------------------

        st.divider()

        st.subheader("🔎 Preprocessing Details")

        record_ids = []

        for record_id in filtered_df[
            "preprocessing_id"
        ]:

            record_ids.append(
                str(record_id)
            )

        selected_record_id = st.selectbox(
            "Select Record",
            record_ids
        )

        selected_record = filtered_df[
            filtered_df["preprocessing_id"]
            == int(selected_record_id)
        ].iloc[0]

        st.write(
            "**Dataset:**",
            selected_record["dataset_name"]
        )

        st.write(
            "**Missing Value Handling:**",
            selected_record[
                "missing_value_method"
            ]
        )

        st.write(
            "**Duplicate Handling:**",
            selected_record[
                "duplicate_handling"
            ]
        )

        st.write(
            "**Encoding Method:**",
            selected_record[
                "encoding_method"
            ]
        )

        st.write(
            "**Scaling Method:**",
            selected_record[
                "scaling_method"
            ]
        )

        st.write(
            "**Feature Selection:**",
            selected_record[
                "feature_selection"
            ]
        )

        st.write(
            "**Other Steps:**",
            selected_record[
                "other_steps"
            ]
        )

        st.write(
            "**Preprocessing Date:**",
            selected_record[
                "preprocessing_date"
            ]
        )

    else:

        st.warning(
            "No preprocessing records match the selected filters."
        )


# ==================================================
# END OF FILE
# ==================================================