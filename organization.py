

import streamlit as st
from database import get_connection


def create_organization(name, description=""):
    """Create a company workspace for the logged-in user."""

    user_id = st.session_state.user["user_id"]
    name = name.strip()

    if not name:
        return False, "Enter an organization name."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO organizations
                (organization_name, created_by)
            VALUES (%s, %s)
            """,
            (name, user_id)
        )

        organization_id = cursor.lastrowid

        # Add the creator as organization admin
        cursor.execute(
            """
            INSERT INTO organization_members
                (organization_id, user_id, organization_role)
            VALUES (%s, %s, 'Org Admin')
            """,
            (organization_id, user_id)
        )

        conn.commit()
        return True, f"Workspace '{name}' created successfully."

    except Exception as e:
        conn.rollback()
        return False, f"Could not create workspace: {e}"

    finally:
        cursor.close()
        conn.close()


def get_user_organizations(user_id):
    """Return the organizations the user belongs to."""

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                o.organization_id,
                o.organization_name,
                om.organization_role
            FROM organizations o
            JOIN organization_members om
                ON o.organization_id = om.organization_id
            WHERE om.user_id = %s
            ORDER BY o.organization_name
            """,
            (user_id,)
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def add_existing_member(organization_id, email, role):
    """Add an existing registered user to an organization."""

    current_user_id = st.session_state.user["user_id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verify that the current user is an organization admin
        cursor.execute(
            """
            SELECT organization_role
            FROM organization_members
            WHERE organization_id = %s AND user_id = %s
            """,
            (organization_id, current_user_id)
        )

        membership = cursor.fetchone()

        if not membership or membership["organization_role"] != "Org Admin":
            return False, "Only an organization admin can add members."

        # Find the registered user
        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s",
            (email.strip(),)
        )
        member = cursor.fetchone()

        if not member:
            return False, "This user must register before being added."

        # Prevent duplicate membership
        cursor.execute(
            """
            SELECT member_id
            FROM organization_members
            WHERE organization_id = %s AND user_id = %s
            """,
            (organization_id, member["user_id"])
        )

        if cursor.fetchone():
            return False, "This user is already a member of this workspace."

        cursor.execute(
            """
            INSERT INTO organization_members
                (organization_id, user_id, organization_role)
            VALUES (%s, %s, %s)
            """,
            (organization_id, member["user_id"], role)
        )

        conn.commit()
        return True, "Member added successfully."

    except Exception as e:
        conn.rollback()
        return False, f"Could not add member: {e}"

    finally:
        cursor.close()
        conn.close()


def get_organization_members(organization_id):
    """Fetch all members of an organization."""

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT
                u.name,
                u.email,
                om.organization_role,
                om.joined_at
            FROM organization_members om
            JOIN users u ON u.user_id = om.user_id
            WHERE om.organization_id = %s
            ORDER BY om.joined_at, u.name
            """,
            (organization_id,)
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def organization_page():
    """Streamlit page for organization and team management."""

    st.title("🏢 Company Workspace")
    st.write(
        "Create an organization, view your team workspaces, "
        "and manage existing registered members."
    )

    user_id = st.session_state.user["user_id"]

    with st.expander("Create a company workspace"):
        with st.form("create_org_form"):
            org_name = st.text_input(
                "Company or organization name",
                placeholder="Example: ABC Analytics"
            )

            submitted = st.form_submit_button("Create Workspace")

            if submitted:
                success, message = create_organization(org_name)

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    organizations = get_user_organizations(user_id)

    st.subheader("Your Organizations")

    if not organizations:
        st.info("You have not joined any organization yet.")
        return

    for org in organizations:
        with st.container(border=True):
            st.subheader(org["organization_name"])
            st.caption(f"Your role: {org['organization_role']}")

            # Admin can add registered members
            if org["organization_role"] == "Org Admin":
                with st.expander("Add a registered team member"):
                    with st.form(f"add_member_{org['organization_id']}"):
                        email = st.text_input("Member's registered email")

                        role = st.selectbox(
                            "Assign role",
                            ["Data Analyst", "ML Engineer", "Viewer"]
                        )

                        add = st.form_submit_button("Add Member")

                        if add:
                            success, message = add_existing_member(
                                org["organization_id"],
                                email,
                                role
                            )

                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

            # Display current members
            st.markdown("### Current Members")

            members = get_organization_members(
                org["organization_id"]
            )

            if members:
                st.dataframe(
                    members,
                    use_container_width=True,
                    hide_index=True
                )

                st.caption(f"Total members: {len(members)}")
            else:
                st.info("No members found in this workspace.")
