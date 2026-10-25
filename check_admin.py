
import bcrypt
from database import get_connection

email = "admin@gmail.com"
password = input("Enter the admin password you are trying: ")

connection = get_connection()
cursor = connection.cursor(dictionary=True)

cursor.execute(
    "SELECT password_hash FROM users WHERE email = %s",
    (email,)
)

user = cursor.fetchone()

if user:
    stored_hash = user["password_hash"]

    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        print("Password verification successful!")
    else:
        print("Password does not match the stored hash.")
else:
    print("Admin account not found.")

cursor.close()
connection.close()
