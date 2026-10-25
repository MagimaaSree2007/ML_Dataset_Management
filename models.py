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
# SAVE MODEL
# ==================================================

def save_model(
    dataset_id,
    model_name,
    algorithm,
    problem_type,
    hyperparameters
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO Models
        (
            dataset_id,
            model_name,
            algorithm,
            problem_type,
            hyperparameters
        )
        VALUES
        (
            %s, %s, %s, %s, %s
        )
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

    cursor.close()
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

    if st.button(
        "💾 Save Model",
        type="primary"
    ):

        if not model_name:

            st.warning(
                "Please enter a model name."
            )

            return

        try:

            save_model(
                dataset_id,
                model_name,
                algorithm,
                problem_type,
                hyperparameters
            )

            st.success(
                "✅ Model information saved successfully!"
            )

        except Exception as e:

            st.error(
                f"Error saving model: {e}"
            )


# ==================================================
# GET ALL MODELS
# ==================================================

def get_all_models():

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

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
        FROM Models m
        JOIN Datasets d
        ON m.dataset_id = d.dataset_id
        ORDER BY m.training_date DESC
    """

    cursor.execute(query)

    models = cursor.fetchall()

    cursor.close()
    connection.close()

    return models


# ==================================================
# MODEL LIBRARY
# ==================================================

def view_models():

    st.title("📚 Model Library")

    st.write(
        "Search, filter and explore machine learning models stored in the system."
    )

    st.divider()

    # ------------------------------------------
    # GET MODELS
    # ------------------------------------------

    models = get_all_models()

    if not models:

        st.info(
            "No models available."
        )

        return

    df = pd.DataFrame(models)

    # ------------------------------------------
    # SUMMARY
    # ------------------------------------------

    st.subheader("📊 Model Summary")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🤖 Total Models",
            len(df)
        )

    with col2:

        st.metric(
            "📁 Datasets Used",
            df["dataset_id"].nunique()
        )

    with col3:

        st.metric(
            "🧠 Algorithms Used",
            df["algorithm"].nunique()
        )

    st.divider()

    # ------------------------------------------
    # SEARCH & FILTER
    # ------------------------------------------

    st.subheader("🔍 Search & Filter")

    search_model = st.text_input(
        "Search Model Name",
        placeholder="Example: Random Forest"
    )

    col1, col2, col3 = st.columns(3)

    # ------------------------------------------
    # DATASET FILTER
    # ------------------------------------------

    with col1:

        dataset_options = ["All"]

        for dataset in df[
            "dataset_name"
        ].dropna():

            dataset = str(dataset)

            if dataset not in dataset_options:

                dataset_options.append(dataset)

        selected_dataset = st.selectbox(
            "Dataset",
            dataset_options
        )

    # ------------------------------------------
    # ALGORITHM FILTER
    # ------------------------------------------

    with col2:

        algorithm_options = ["All"]

        for algorithm in df[
            "algorithm"
        ].dropna():

            algorithm = str(algorithm)

            if algorithm not in algorithm_options:

                algorithm_options.append(algorithm)

        selected_algorithm = st.selectbox(
            "Algorithm",
            algorithm_options
        )

    # ------------------------------------------
    # PROBLEM TYPE FILTER
    # ------------------------------------------

    with col3:

        problem_options = ["All"]

        for problem in df[
            "problem_type"
        ].dropna():

            problem = str(problem)

            if problem not in problem_options:

                problem_options.append(problem)

        selected_problem = st.selectbox(
            "Problem Type",
            problem_options
        )

    # ------------------------------------------
    # SORTING
    # ------------------------------------------

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
    # COPY DATAFRAME
    # ------------------------------------------

    filtered_df = df.copy()

    # ------------------------------------------
    # SEARCH
    # ------------------------------------------

    if search_model:

        filtered_df = filtered_df[
            filtered_df[
                "model_name"
            ]
            .astype(str)
            .str.contains(
                search_model,
                case=False,
                na=False
            )
        ]

    # ------------------------------------------
    # DATASET FILTER
    # ------------------------------------------

    if selected_dataset != "All":

        filtered_df = filtered_df[
            filtered_df[
                "dataset_name"
            ].astype(str)
            == selected_dataset
        ]

    # ------------------------------------------
    # ALGORITHM FILTER
    # ------------------------------------------

    if selected_algorithm != "All":

        filtered_df = filtered_df[
            filtered_df[
                "algorithm"
            ].astype(str)
            == selected_algorithm
        ]

    # ------------------------------------------
    # PROBLEM TYPE FILTER
    # ------------------------------------------

    if selected_problem != "All":

        filtered_df = filtered_df[
            filtered_df[
                "problem_type"
            ].astype(str)
            == selected_problem
        ]

    # ------------------------------------------
    # SORTING
    # ------------------------------------------

    if sort_option == "Newest First":

        filtered_df = filtered_df.sort_values(
            by="training_date",
            ascending=False
        )

    elif sort_option == "Oldest First":

        filtered_df = filtered_df.sort_values(
            by="training_date",
            ascending=True
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
    # RESULT COUNT
    # ------------------------------------------

    st.divider()

    st.write(
        f"📊 **{len(filtered_df)} model(s) found**"
    )

    # ------------------------------------------
    # DISPLAY MODELS
    # ------------------------------------------

    if not filtered_df.empty:

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
            filtered_df[
                display_columns
            ],
            use_container_width=True,
            hide_index=True
        )

        # --------------------------------------
        # MODEL DETAILS
        # --------------------------------------

        st.divider()

        st.subheader(
            "🔎 Model Details"
        )

        model_ids = []

        for model_id in filtered_df[
            "model_id"
        ]:

            model_ids.append(
                str(model_id)
            )

        selected_model_id = st.selectbox(
            "Select Model",
            model_ids
        )

        selected_model = filtered_df[
            filtered_df["model_id"]
            == int(selected_model_id)
        ].iloc[0]

        st.write(
            "**Dataset:**",
            selected_model[
                "dataset_name"
            ]
        )

        st.write(
            "**Model Name:**",
            selected_model[
                "model_name"
            ]
        )

        st.write(
            "**Algorithm:**",
            selected_model[
                "algorithm"
            ]
        )

        st.write(
            "**Problem Type:**",
            selected_model[
                "problem_type"
            ]
        )

        st.write(
            "**Hyperparameters:**",
            selected_model[
                "hyperparameters"
            ]
        )

        st.write(
            "**Training Date:**",
            selected_model[
                "training_date"
            ]
        )

    else:

        st.warning(
            "No models match the selected filters."
        )


# ==================================================
# END OF FILE
# ==================================================