
import bcrypt
from database import get_connection


def register_user(name, email, password, role="User"):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        print("Registration DB:", connection.server_host, connection.server_port)
        cursor = connection.cursor()

        # Check whether this email already exists
        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s",
            (email.strip(),)
        )

        if cursor.fetchone():
            return False, "Email already registered."

        # Hash the password before storing it
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # Create a normal User account
        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
            """,
            (name.strip(), email.strip(), password_hash, "User")
        )

        connection.commit()
        return True, "Registration successful."

    except Exception as e:
        if connection:
            connection.rollback()
        return False, f"Registration failed: {e}"

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def login_user(email, password):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        print("Login DB:", connection.server_host, connection.server_port)
        cursor = connection.cursor(dictionary=True)

        # Use lowercase users to match the Aiven table name
        cursor.execute(
            """
            SELECT user_id, name, email, password_hash, role
            FROM users
            WHERE email = %s
            """,
            (email.strip(),)
        )

        user = cursor.fetchone()

        if user is None:
            return None

        # Verify the entered password against the stored hash
        stored_hash = user["password_hash"]

        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")

        if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            user.pop("password_hash", None)
            return user

        return None

    except Exception as e:
        print("Login error:", e)
        return None

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

