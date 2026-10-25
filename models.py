
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
            SELECT
                dataset_id,
                dataset_name
            FROM datasets
            ORDER BY dataset_name
        """

        cursor.execute(query)
        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# ==================================================
# SAVE MODEL
# ==================================================

def save_model(
    dataset_id,
    model_name,
    algorithm,
    problem_type,
    hyperparameters
):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO models
            (
                dataset_id,
                model_name,
                algorithm,
                problem_type,
                hyperparameters
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            dataset_id,
            model_name,
            algorithm,
            problem_type,
            hyperparameters
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
        if connection and connection.is_connected():
            connection.close()


# ==================================================
# MODEL MANAGEMENT
# ==================================================

def model_management():
    st.title("🤖 Model Management")

    st.write(
        "Manage machine learning models trained using the available datasets."
    )

    st.divider()

    try:
        datasets = get_datasets()
    except Exception as e:
        st.error(f"Unable to load datasets: {e}")
        return

    if not datasets:
        st.warning(
            "No datasets available. Please upload a dataset first."
        )
        return

    dataset_options = {}

    for dataset in datasets:
        label = (
            str(dataset["dataset_name"])
            + " (ID: "
            + str(dataset["dataset_id"])
            + ")"
        )
        dataset_options[label] = dataset["dataset_id"]

    selected_dataset = st.selectbox(
        "Select Dataset",
        list(dataset_options.keys())
    )

    dataset_id = dataset_options[selected_dataset]

    # ------------------------------------------
    # MODEL INFORMATION
    # ------------------------------------------

    st.subheader("📝 Model Information")

    model_name = st.text_input(
        "Model Name",
        placeholder="Example: Diabetes Random Forest Model"
    )

    algorithm = st.selectbox(
        "Machine Learning Algorithm",
        [
            "Linear Regression",
            "Logistic Regression",
            "Decision Tree",
            "Random Forest",
            "Support Vector Machine",
            "K-Nearest Neighbors",
            "Naive Bayes",
            "XGBoost",
            "K-Means",
            "Neural Network",
            "Other"
        ]
    )

    problem_type = st.selectbox(
        "Problem Type",
        [
            "Classification",
            "Regression",
            "Clustering",
            "Other"
        ]
    )

    # ------------------------------------------
    # HYPERPARAMETERS
    # ------------------------------------------

    st.subheader("⚙️ Hyperparameters")

    hyperparameters = st.text_area(
        "Enter Hyperparameters",
        placeholder=(
            "Example: n_estimators=100, "
            "max_depth=10, random_state=42"
        )
    )

    st.divider()

    # ------------------------------------------
    # SAVE MODEL
    # ------------------------------------------

    if st.button("💾 Save Model", type="primary"):
        if not model_name.strip():
            st.warning("Please enter a model name.")
            return

        try:
            save_model(
                dataset_id,
                model_name.strip(),
                algorithm,
                problem_type,
                hyperparameters.strip()
            )

            st.success("✅ Model information saved successfully!")

        except Exception as e:
            st.error(f"Error saving model: {e}")


# ==================================================
# GET ALL MODELS
# ==================================================

def get_all_models():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                m.model_id,
                m.dataset_id,
                d.dataset_name,
                m.model_name,
                m.algorithm,
                m.problem_type,
                m.hyperparameters,
                m.training_date
            FROM models m
            JOIN datasets d
                ON m.dataset_id = d.dataset_id
            ORDER BY m.training_date DESC
        """

        cursor.execute(query)
        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# ==================================================
# MODEL LIBRARY
# ==================================================

def view_models():
    st.title("📚 Model Library")

    st.write(
        "Search, filter and explore machine learning models stored in the system."
    )

    st.divider()

    try:
        models = get_all_models()
    except Exception as e:
        st.error(f"Unable to load models: {e}")
        return

    if not models:
        st.info("No models available.")
        return

    df = pd.DataFrame(models)

    # ------------------------------------------
    # SUMMARY
    # ------------------------------------------

    st.subheader("📊 Model Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🤖 Total Models", len(df))

    with col2:
        st.metric("📁 Datasets Used", df["dataset_id"].nunique())

    with col3:
        st.metric("🧠 Algorithms Used", df["algorithm"].nunique())

    st.divider()

    # ------------------------------------------
    # SEARCH AND FILTERS
    # ------------------------------------------

    st.subheader("🔍 Search & Filter")

    search_model = st.text_input(
        "Search Model Name",
        placeholder="Example: Random Forest"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        dataset_options = ["All"] + sorted(
            df["dataset_name"].dropna().astype(str).unique().tolist()
        )

        selected_dataset = st.selectbox(
            "Dataset",
            dataset_options
        )

    with col2:
        algorithm_options = ["All"] + sorted(
            df["algorithm"].dropna().astype(str).unique().tolist()
        )

        selected_algorithm = st.selectbox(
            "Algorithm",
            algorithm_options
        )

    with col3:
        problem_options = ["All"] + sorted(
            df["problem_type"].dropna().astype(str).unique().tolist()
        )

        selected_problem = st.selectbox(
            "Problem Type",
            problem_options
        )

    sort_option = st.selectbox(
        "Sort By",
        [
            "Newest First",
            "Oldest First",
            "Model Name",
            "Algorithm"
        ]
    )

    # ------------------------------------------
    # APPLY FILTERS
    # ------------------------------------------

    filtered_df = df.copy()

    if search_model:
        filtered_df = filtered_df[
            filtered_df["model_name"]
            .astype(str)
            .str.contains(search_model, case=False, na=False)
        ]

    if selected_dataset != "All":
        filtered_df = filtered_df[
            filtered_df["dataset_name"].astype(str) == selected_dataset
        ]

    if selected_algorithm != "All":
        filtered_df = filtered_df[
            filtered_df["algorithm"].astype(str) == selected_algorithm
        ]

    if selected_problem != "All":
        filtered_df = filtered_df[
            filtered_df["problem_type"].astype(str) == selected_problem
        ]

    # ------------------------------------------
    # SORTING
    # ------------------------------------------

    if sort_option == "Newest First":
        filtered_df = filtered_df.sort_values(
            by="training_date",
            ascending=False,
            na_position="last"
        )

    elif sort_option == "Oldest First":
        filtered_df = filtered_df.sort_values(
            by="training_date",
            ascending=True,
            na_position="last"
        )

    elif sort_option == "Model Name":
        filtered_df = filtered_df.sort_values(
            by="model_name",
            ascending=True
        )

    elif sort_option == "Algorithm":
        filtered_df = filtered_df.sort_values(
            by="algorithm",
            ascending=True
        )

    # ------------------------------------------
    # DISPLAY RESULTS
    # ------------------------------------------

    st.divider()

    st.write(f"📊 **{len(filtered_df)} model(s) found**")

    if filtered_df.empty:
        st.warning("No models match the selected filters.")
        return

    display_columns = [
        "model_id",
        "dataset_name",
        "model_name",
        "algorithm",
        "problem_type",
        "hyperparameters",
        "training_date"
    ]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    # ------------------------------------------
    # MODEL DETAILS
    # ------------------------------------------

    st.divider()
    st.subheader("🔎 Model Details")

    model_ids = filtered_df["model_id"].tolist()

    selected_model_id = st.selectbox(
        "Select Model",
        model_ids,
        format_func=lambda x: str(x)
    )

    selected_model = filtered_df[
        filtered_df["model_id"] == selected_model_id
    ].iloc[0]

    st.write("**Dataset:**", selected_model["dataset_name"])
    st.write("**Model Name:**", selected_model["model_name"])
    st.write("**Algorithm:**", selected_model["algorithm"])
    st.write("**Problem Type:**", selected_model["problem_type"])
    st.write("**Hyperparameters:**", selected_model["hyperparameters"])
    st.write("**Training Date:**", selected_model["training_date"])


