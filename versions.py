import streamlit as st
import pandas as pd
import os

from database import get_connection


UPLOAD_FOLDER = "uploads"


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
# SAVE VERSION
# ==================================================

def save_version(
    dataset_id,
    version_number,
    changes_description,
    file_name,
    file_path
):

    connection = get_connection()

    cursor = connection.cursor()

    query = """
        INSERT INTO Dataset_Versions
        (
            dataset_id,
            version_number,
            changes_description,
            file_name,
            file_path
        )
        VALUES
        (
            %s, %s, %s, %s, %s
        )
    """

    values = (
        dataset_id,
        version_number,
        changes_description,
        file_name,
        file_path
    )

    cursor.execute(
        query,
        values
    )

    connection.commit()

    cursor.close()
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


    st.divider()

    # ------------------------------------------
    # VERSION INFORMATION
    # ------------------------------------------

    st.subheader(
        "📝 Version Information"
    )

    version_number = st.text_input(
        "Version Number",
        placeholder="Example: 1.0, 1.1, 2.0"
    )

    changes_description = st.text_area(
        "Changes Description",
        placeholder=(
            "Example: Missing values removed, "
            "duplicates handled and new features added."
        )
    )


    # ------------------------------------------
    # UPLOAD VERSION FILE
    # ------------------------------------------

    st.subheader(
        "📤 Upload Version File"
    )

    uploaded_file = st.file_uploader(
        "Choose the updated dataset file",
        type=[
            "csv",
            "xlsx",
            "json"
        ]
    )


    if uploaded_file is not None:

        file_name = uploaded_file.name

        file_extension = os.path.splitext(
            file_name
        )[1].lower()


        # ------------------------------------------
        # READ FILE
        # ------------------------------------------

        try:

            if file_extension == ".csv":

                df = pd.read_csv(
                    uploaded_file
                )

            elif file_extension == ".xlsx":

                df = pd.read_excel(
                    uploaded_file
                )

            elif file_extension == ".json":

                df = pd.read_json(
                    uploaded_file
                )

            else:

                st.error(
                    "Unsupported file format."
                )

                return


        except Exception as e:

            st.error(
                f"Unable to read dataset: {e}"
            )

            return


        # ------------------------------------------
        # VERSION PREVIEW
        # ------------------------------------------

        st.subheader(
            "👀 Version Preview"
        )

        st.dataframe(
            df.head(10),
            use_container_width=True
        )


        # ------------------------------------------
        # VERSION STATISTICS
        # ------------------------------------------

        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Rows",
                df.shape[0]
            )


        with col2:

            st.metric(
                "Columns",
                df.shape[1]
            )


        with col3:

            st.metric(
                "File Size",
                f"{uploaded_file.size / (1024 * 1024):.2f} MB"
            )


        st.write(
            "**Columns:**",
            list(df.columns)
        )


        st.divider()


        # ------------------------------------------
        # SAVE VERSION
        # ------------------------------------------

        if st.button(
            "💾 Save Dataset Version",
            type="primary"
        ):

            if not version_number:

                st.warning(
                    "Please enter a version number."
                )

                return


            if not changes_description:

                st.warning(
                    "Please describe the changes made."
                )

                return


            try:

                if not os.path.exists(
                    UPLOAD_FOLDER
                ):

                    os.makedirs(
                        UPLOAD_FOLDER
                    )


                # Create safe filename
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


                # Save physical file
                with open(
                    file_path,
                    "wb"
                ) as f:

                    f.write(
                        uploaded_file.getbuffer()
                    )


                # Save database information
                save_version(
                    dataset_id,
                    version_number,
                    changes_description,
                    version_file_name,
                    file_path
                )


                st.success(
                    "✅ Dataset version saved successfully!"
                )


            except Exception as e:

                st.error(
                    f"Error saving version: {e}"
                )


# ==================================================
# VERSION HISTORY
# ==================================================

def view_versions():

    st.title(
        "📜 Dataset Version History"
    )

    st.write(
        "View and track all versions of your machine learning datasets."
    )

    st.divider()


    # ------------------------------------------
    # GET DATASETS
    # ------------------------------------------

    datasets = get_datasets()


    if not datasets:

        st.info(
            "No datasets available."
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
        list(dataset_options.keys()),
        key="version_history_dataset"
    )


    dataset_id = dataset_options[
        selected_dataset
    ]


    # ------------------------------------------
    # GET VERSION HISTORY
    # ------------------------------------------

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    query = """
        SELECT
            version_id,
            version_number,
            changes_description,
            file_name,
            file_path,
            upload_date
        FROM Dataset_Versions
        WHERE dataset_id = %s
        ORDER BY upload_date DESC
    """


    cursor.execute(
        query,
        (dataset_id,)
    )


    versions = cursor.fetchall()


    cursor.close()
    connection.close()


    # ------------------------------------------
    # VERSION COUNT
    # ------------------------------------------

    st.divider()


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "🔄 Total Versions",
            len(versions)
        )


    with col2:

        if versions:

            st.metric(
                "🆕 Latest Version",
                versions[0]["version_number"]
            )

        else:

            st.metric(
                "🆕 Latest Version",
                "None"
            )


    # ------------------------------------------
    # DISPLAY VERSION HISTORY
    # ------------------------------------------

    if versions:

        st.subheader(
            "📋 Version Records"
        )


        version_df = pd.DataFrame(
            versions
        )


        display_columns = [
            "version_id",
            "version_number",
            "changes_description",
            "file_name",
            "upload_date"
        ]


        st.dataframe(
            version_df[
                display_columns
            ],
            use_container_width=True,
            hide_index=True
        )


        # --------------------------------------
        # VERSION DETAILS
        # --------------------------------------

        st.divider()

        st.subheader(
            "🔎 Version Details"
        )


        version_numbers = []

        for version in versions:

            version_numbers.append(
                str(version["version_number"])
            )


        selected_version = st.selectbox(
            "Select Version",
            version_numbers
        )


        selected_record = None


        for version in versions:

            if str(
                version["version_number"]
            ) == selected_version:

                selected_record = version

                break


        if selected_record:

            st.write(
                "**Version Number:**",
                selected_record[
                    "version_number"
                ]
            )

            st.write(
                "**Changes:**",
                selected_record[
                    "changes_description"
                ]
            )

            st.write(
                "**File Name:**",
                selected_record[
                    "file_name"
                ]
            )

            st.write(
                "**Upload Date:**",
                selected_record[
                    "upload_date"
                ]
            )

            st.write(
                "**File Path:**",
                selected_record[
                    "file_path"
                ]
            )


    else:

        st.info(
            "No versions available for this dataset."
        )


# ==================================================
# END OF FILE
# ==================================================