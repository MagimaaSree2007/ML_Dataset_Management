import streamlit as st
import pandas as pd
import plotly.express as px

from database import get_connection


# --------------------------------------------------
# GET COUNT
# --------------------------------------------------

def get_count(table_name):

    connection = get_connection()

    cursor = connection.cursor()

    query = f"SELECT COUNT(*) FROM {table_name}"

    cursor.execute(query)

    count = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return count


# --------------------------------------------------
# DATASETS BY DOMAIN
# --------------------------------------------------

def get_datasets_by_domain():

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            domain,
            COUNT(*) AS total_datasets
        FROM Datasets
        GROUP BY domain
        ORDER BY total_datasets DESC
    """

    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


# --------------------------------------------------
# MODELS BY ALGORITHM
# --------------------------------------------------

def get_models_by_algorithm():

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            algorithm,
            COUNT(*) AS total_models
        FROM Models
        GROUP BY algorithm
        ORDER BY total_models DESC
    """

    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


# --------------------------------------------------
# MODEL PERFORMANCE
# --------------------------------------------------

def get_model_performance():

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            m.model_name,
            m.algorithm,
            m.problem_type,
            d.dataset_name,
            p.accuracy,
            p.precision_score,
            p.recall_score,
            p.f1_score,
            p.rmse,
            p.mae,
            p.r2_score
        FROM Performance p
        JOIN Models m
        ON p.model_id = m.model_id
        JOIN Datasets d
        ON m.dataset_id = d.dataset_id
        ORDER BY p.evaluation_date DESC
    """

    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


# --------------------------------------------------
# RECENT DATASETS
# --------------------------------------------------

def get_recent_datasets():

    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            d.dataset_name,
            d.domain,
            d.file_type,
            d.row_count,
            d.column_count,
            d.target_column,
            u.name AS uploaded_by,
            d.upload_date
        FROM Datasets d
        JOIN Users u
        ON d.user_id = u.user_id
        ORDER BY d.upload_date DESC
        LIMIT 5
    """

    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

def show_dashboard():

    st.title("📊 MLDMS Dashboard")

    st.write(
        "Machine Learning Dataset Management System"
    )

    st.divider()


    # --------------------------------------------------
    # SUMMARY METRICS
    # --------------------------------------------------

    total_users = get_count("Users")

    total_datasets = get_count("Datasets")

    total_versions = get_count("Dataset_Versions")

    total_preprocessing = get_count("Preprocessing")

    total_models = get_count("Models")

    total_performance = get_count("Performance")


    # First row

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "👥 Total Users",
            total_users
        )

    with col2:

        st.metric(
            "📁 Total Datasets",
            total_datasets
        )

    with col3:

        st.metric(
            "🔄 Dataset Versions",
            total_versions
        )


    # Second row

    col4, col5, col6 = st.columns(3)

    with col4:

        st.metric(
            "⚙️ Preprocessing Records",
            total_preprocessing
        )

    with col5:

        st.metric(
            "🤖 Total Models",
            total_models
        )

    with col6:

        st.metric(
            "📈 Performance Records",
            total_performance
        )


    st.divider()


    # --------------------------------------------------
    # DATASET ANALYTICS
    # --------------------------------------------------

    st.subheader("📁 Dataset Analytics")

    domain_data = get_datasets_by_domain()

    if domain_data:

        domain_df = pd.DataFrame(domain_data)

        col1, col2 = st.columns(2)


        # Pie chart

        with col1:

            fig = px.pie(
                domain_df,
                names="domain",
                values="total_datasets",
                title="Datasets by Domain",
                hole=0.35
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        # Bar chart

        with col2:

            fig = px.bar(
                domain_df,
                x="domain",
                y="total_datasets",
                title="Dataset Count by Domain",
                text="total_datasets"
            )

            fig.update_traces(
                textposition="outside"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:

        st.info(
            "No dataset information available."
        )


    st.divider()


    # --------------------------------------------------
    # MODEL ANALYTICS
    # --------------------------------------------------

    st.subheader("🤖 Model Analytics")

    algorithm_data = get_models_by_algorithm()

    if algorithm_data:

        algorithm_df = pd.DataFrame(
            algorithm_data
        )

        fig = px.bar(
            algorithm_df,
            x="algorithm",
            y="total_models",
            title="Models by Algorithm",
            text="total_models"
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Algorithm",
            yaxis_title="Number of Models"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No model information available."
        )


    st.divider()


    # --------------------------------------------------
    # MODEL PERFORMANCE
    # --------------------------------------------------

    st.subheader("🏆 Model Performance")

    performance_data = get_model_performance()

    if performance_data:

        performance_df = pd.DataFrame(
            performance_data
        )


        # Classification models

        classification_df = performance_df[
            performance_df["problem_type"]
            == "Classification"
        ].copy()


        if not classification_df.empty:

            st.write(
                "**Classification Model Performance**"
            )

            display_df = classification_df[
                [
                    "model_name",
                    "algorithm",
                    "dataset_name",
                    "accuracy",
                    "precision_score",
                    "recall_score",
                    "f1_score"
                ]
            ]

            st.dataframe(
                display_df,
                use_container_width=True
            )


            # Accuracy chart

            fig = px.bar(
                classification_df,
                x="model_name",
                y="accuracy",
                title="Classification Model Accuracy",
                text="accuracy"
            )

            fig.update_traces(
                texttemplate="%{text:.3f}",
                textposition="outside"
            )

            fig.update_yaxes(
                range=[0, 1]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        # Regression models

        regression_df = performance_df[
            performance_df["problem_type"]
            == "Regression"
        ].copy()


        if not regression_df.empty:

            st.write(
                "**Regression Model Performance**"
            )

            display_df = regression_df[
                [
                    "model_name",
                    "algorithm",
                    "dataset_name",
                    "rmse",
                    "mae",
                    "r2_score"
                ]
            ]

            st.dataframe(
                display_df,
                use_container_width=True
            )


    else:

        st.info(
            "No performance records available. "
            "Add performance metrics to see analytics."
        )


    st.divider()


    # --------------------------------------------------
    # RECENT DATASETS
    # --------------------------------------------------

    st.subheader("🕐 Recent Datasets")

    recent_data = get_recent_datasets()

    if recent_data:

        recent_df = pd.DataFrame(
            recent_data
        )

        st.dataframe(
            recent_df,
            use_container_width=True
        )

    else:

        st.info(
            "No datasets available."
        )