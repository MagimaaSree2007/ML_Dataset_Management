import streamlit as st
import pandas as pd
from database import get_connection


# ==================================================
# GET MODELS
# ==================================================

def get_models():

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            m.model_id,
            m.model_name,
            d.dataset_name,
            m.problem_type
        FROM Models m
        JOIN Datasets d
        ON m.dataset_id = d.dataset_id
        ORDER BY m.model_name
    """

    cursor.execute(query)

    models = cursor.fetchall()

    cursor.close()
    connection.close()

    return models


# ==================================================
# SAVE PERFORMANCE
# ==================================================

def save_performance(
    model_id,
    accuracy,
    precision_score,
    recall_score,
    f1_score,
    rmse,
    mae,
    r2_score
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO Performance
        (
            model_id,
            accuracy,
            precision_score,
            recall_score,
            f1_score,
            rmse,
            mae,
            r2_score
        )
        VALUES
        (
            %s, %s, %s, %s, %s,
            %s, %s, %s
        )
    """

    values = (
        model_id,
        accuracy,
        precision_score,
        recall_score,
        f1_score,
        rmse,
        mae,
        r2_score
    )

    cursor.execute(query, values)

    connection.commit()

    cursor.close()
    connection.close()


# ==================================================
# PERFORMANCE MANAGEMENT
# ==================================================

def performance_management():

    st.title("📈 Performance Management")

    st.write(
        "Record and manage machine learning model evaluation metrics."
    )

    st.divider()

    models = get_models()

    if not models:

        st.warning(
            "No models available. Please add a model first."
        )

        return

    model_options = {}

    for model in models:

        label = (
            model["model_name"]
            + " - "
            + model["dataset_name"]
            + " (ID: "
            + str(model["model_id"])
            + ")"
        )

        model_options[label] = model["model_id"]

    selected_model = st.selectbox(
        "Select Model",
        list(model_options.keys())
    )

    model_id = model_options[selected_model]

    selected_model_data = next(
        model for model in models
        if model["model_id"] == model_id
    )

    problem_type = selected_model_data["problem_type"]

    st.info(
        f"Problem Type: **{problem_type}**"
    )

    # ------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------

    if problem_type == "Classification":

        st.subheader(
            "📊 Classification Metrics"
        )

        col1, col2 = st.columns(2)

        with col1:

            accuracy = st.number_input(
                "Accuracy",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.001
            )

            precision_score = st.number_input(
                "Precision",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.001
            )

        with col2:

            recall_score = st.number_input(
                "Recall",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.001
            )

            f1_score = st.number_input(
                "F1 Score",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.001
            )

        rmse = None
        mae = None
        r2_score = None

    # ------------------------------------------
    # REGRESSION
    # ------------------------------------------

    elif problem_type == "Regression":

        st.subheader(
            "📊 Regression Metrics"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            rmse = st.number_input(
                "RMSE",
                min_value=0.0,
                value=0.0,
                step=0.001
            )

        with col2:

            mae = st.number_input(
                "MAE",
                min_value=0.0,
                value=0.0,
                step=0.001
            )

        with col3:

            r2_score = st.number_input(
                "R² Score",
                min_value=-1.0,
                max_value=1.0,
                value=0.0,
                step=0.001
            )

        accuracy = None
        precision_score = None
        recall_score = None
        f1_score = None

    # ------------------------------------------
    # CLUSTERING
    # ------------------------------------------

    elif problem_type == "Clustering":

        st.subheader(
            "📊 Clustering Performance"
        )

        st.info(
            "Clustering models generally use metrics such as "
            "Silhouette Score or Davies-Bouldin Index. "
            "These are not included in the current database schema."
        )

        accuracy = None
        precision_score = None
        recall_score = None
        f1_score = None
        rmse = None
        mae = None
        r2_score = None

    # ------------------------------------------
    # OTHER
    # ------------------------------------------

    else:

        st.subheader(
            "📊 Model Performance"
        )

        accuracy = st.number_input(
            "Accuracy",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.001
        )

        precision_score = st.number_input(
            "Precision",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.001
        )

        recall_score = st.number_input(
            "Recall",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.001
        )

        f1_score = st.number_input(
            "F1 Score",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.001
        )

        rmse = None
        mae = None
        r2_score = None

    st.divider()

    if st.button(
        "💾 Save Performance",
        type="primary"
    ):

        try:

            save_performance(
                model_id,
                accuracy,
                precision_score,
                recall_score,
                f1_score,
                rmse,
                mae,
                r2_score
            )

            st.success(
                "✅ Performance metrics saved successfully!"
            )

        except Exception as e:

            st.error(
                f"Error saving performance: {e}"
            )


# ==================================================
# GET PERFORMANCE RECORDS
# ==================================================

def get_all_performance():

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    query = """
        SELECT
            p.performance_id,
            p.model_id,
            d.dataset_name,
            m.model_name,
            m.algorithm,
            m.problem_type,
            p.accuracy,
            p.precision_score,
            p.recall_score,
            p.f1_score,
            p.rmse,
            p.mae,
            p.r2_score,
            p.evaluation_date

        FROM Performance p

        JOIN Models m
        ON p.model_id = m.model_id

        JOIN Datasets d
        ON m.dataset_id = d.dataset_id

        ORDER BY p.evaluation_date DESC
    """

    cursor.execute(query)

    performance_records = cursor.fetchall()

    cursor.close()
    connection.close()

    return performance_records


# ==================================================
# PERFORMANCE LIBRARY
# ==================================================

def view_performance():

    st.title("📋 Performance Library")

    st.write(
        "Search, filter and compare machine learning model performance."
    )

    st.divider()

    performance_records = get_all_performance()

    if not performance_records:

        st.info(
            "No performance records available."
        )

        return

    df = pd.DataFrame(
        performance_records
    )

    # ==========================================
    # SUMMARY
    # ==========================================

    st.subheader(
        "📊 Performance Summary"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "📈 Total Records",
            len(df)
        )

    with col2:

        st.metric(
            "🤖 Models Evaluated",
            df["model_id"].nunique()
        )

    with col3:

        st.metric(
            "📁 Datasets",
            df["dataset_name"].nunique()
        )

    with col4:

        classification_count = len(
            df[
                df["problem_type"]
                == "Classification"
            ]
        )

        st.metric(
            "🎯 Classification",
            classification_count
        )

    st.divider()

    # ==========================================
    # SEARCH
    # ==========================================

    st.subheader(
        "🔍 Search & Filter"
    )

    search_model = st.text_input(
        "Search Model Name",
        placeholder="Example: Random Forest"
    )

    col1, col2, col3 = st.columns(3)

    # ==========================================
    # DATASET FILTER
    # ==========================================

    with col1:

        dataset_options = ["All"]

        for dataset in df[
            "dataset_name"
        ].dropna():

            dataset = str(dataset)

            if dataset not in dataset_options:

                dataset_options.append(
                    dataset
                )

        selected_dataset = st.selectbox(
            "Dataset",
            dataset_options
        )

    # ==========================================
    # ALGORITHM FILTER
    # ==========================================

    with col2:

        algorithm_options = ["All"]

        for algorithm in df[
            "algorithm"
        ].dropna():

            algorithm = str(algorithm)

            if algorithm not in algorithm_options:

                algorithm_options.append(
                    algorithm
                )

        selected_algorithm = st.selectbox(
            "Algorithm",
            algorithm_options
        )

    # ==========================================
    # PROBLEM TYPE
    # ==========================================

    with col3:

        problem_options = ["All"]

        for problem in df[
            "problem_type"
        ].dropna():

            problem = str(problem)

            if problem not in problem_options:

                problem_options.append(
                    problem
                )

        selected_problem = st.selectbox(
            "Problem Type",
            problem_options
        )

    # ==========================================
    # SORTING
    # ==========================================

    sort_option = st.selectbox(
        "Sort By",
        [
            "Newest First",
            "Oldest First",
            "Highest Accuracy",
            "Highest F1 Score",
            "Highest R² Score"
        ]
    )

    filtered_df = df.copy()

    # ==========================================
    # SEARCH FILTER
    # ==========================================

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

    # ==========================================
    # DATASET FILTER
    # ==========================================

    if selected_dataset != "All":

        filtered_df = filtered_df[
            filtered_df[
                "dataset_name"
            ].astype(str)
            == selected_dataset
        ]

    # ==========================================
    # ALGORITHM FILTER
    # ==========================================

    if selected_algorithm != "All":

        filtered_df = filtered_df[
            filtered_df[
                "algorithm"
            ].astype(str)
            == selected_algorithm
        ]

    # ==========================================
    # PROBLEM TYPE FILTER
    # ==========================================

    if selected_problem != "All":

        filtered_df = filtered_df[
            filtered_df[
                "problem_type"
            ].astype(str)
            == selected_problem
        ]

    # ==========================================
    # SORTING
    # ==========================================

    if sort_option == "Newest First":

        filtered_df = filtered_df.sort_values(
            by="evaluation_date",
            ascending=False
        )

    elif sort_option == "Oldest First":

        filtered_df = filtered_df.sort_values(
            by="evaluation_date",
            ascending=True
        )

    elif sort_option == "Highest Accuracy":

        filtered_df = filtered_df.sort_values(
            by="accuracy",
            ascending=False,
            na_position="last"
        )

    elif sort_option == "Highest F1 Score":

        filtered_df = filtered_df.sort_values(
            by="f1_score",
            ascending=False,
            na_position="last"
        )

    elif sort_option == "Highest R² Score":

        filtered_df = filtered_df.sort_values(
            by="r2_score",
            ascending=False,
            na_position="last"
        )

    st.divider()

    st.write(
        f"📊 **{len(filtered_df)} performance record(s) found**"
    )

    # ==========================================
    # DISPLAY TABLE
    # ==========================================

    if not filtered_df.empty:

        display_columns = [
            "performance_id",
            "dataset_name",
            "model_name",
            "algorithm",
            "problem_type",
            "accuracy",
            "precision_score",
            "recall_score",
            "f1_score",
            "rmse",
            "mae",
            "r2_score",
            "evaluation_date"
        ]

        st.dataframe(
            filtered_df[
                display_columns
            ],
            use_container_width=True,
            hide_index=True
        )

        # ======================================
        # BEST MODEL
        # ======================================

        classification_df = filtered_df[
            filtered_df[
                "problem_type"
            ] == "Classification"
        ]

        if not classification_df.empty:

            best_model = classification_df.loc[
                classification_df[
                    "accuracy"
                ].idxmax()
            ]

            st.success(
                "🏆 Best Classification Model: "
                + str(best_model["model_name"])
                + " | Accuracy: "
                + str(best_model["accuracy"])
            )

        regression_df = filtered_df[
            filtered_df[
                "problem_type"
            ] == "Regression"
        ]

        if not regression_df.empty:

            valid_r2 = regression_df[
                regression_df[
                    "r2_score"
                ].notna()
            ]

            if not valid_r2.empty:

                best_regression = valid_r2.loc[
                    valid_r2[
                        "r2_score"
                    ].idxmax()
                ]

                st.info(
                    "🏆 Best Regression Model: "
                    + str(
                        best_regression[
                            "model_name"
                        ]
                    )
                    + " | R²: "
                    + str(
                        best_regression[
                            "r2_score"
                        ]
                    )
                )

        # ======================================
        # DETAILS
        # ======================================

        st.divider()

        st.subheader(
            "🔎 Performance Details"
        )

        performance_ids = [
            str(x)
            for x in filtered_df[
                "performance_id"
            ]
        ]

        selected_id = st.selectbox(
            "Select Performance Record",
            performance_ids
        )

        selected_record = filtered_df[
            filtered_df[
                "performance_id"
            ] == int(selected_id)
        ].iloc[0]

        st.write(
            "**Dataset:**",
            selected_record[
                "dataset_name"
            ]
        )

        st.write(
            "**Model:**",
            selected_record[
                "model_name"
            ]
        )

        st.write(
            "**Algorithm:**",
            selected_record[
                "algorithm"
            ]
        )

        st.write(
            "**Problem Type:**",
            selected_record[
                "problem_type"
            ]
        )

        if selected_record[
            "problem_type"
        ] == "Classification":

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Accuracy",
                    selected_record[
                        "accuracy"
                    ]
                )

            with col2:
                st.metric(
                    "Precision",
                    selected_record[
                        "precision_score"
                    ]
                )

            with col3:
                st.metric(
                    "Recall",
                    selected_record[
                        "recall_score"
                    ]
                )

            with col4:
                st.metric(
                    "F1 Score",
                    selected_record[
                        "f1_score"
                    ]
                )

        elif selected_record[
            "problem_type"
        ] == "Regression":

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "RMSE",
                    selected_record[
                        "rmse"
                    ]
                )

            with col2:
                st.metric(
                    "MAE",
                    selected_record[
                        "mae"
                    ]
                )

            with col3:
                st.metric(
                    "R² Score",
                    selected_record[
                        "r2_score"
                    ]
                )

        st.write(
            "**Evaluation Date:**",
            selected_record[
                "evaluation_date"
            ]
        )

    else:

        st.warning(
            "No performance records match the selected filters."
        )