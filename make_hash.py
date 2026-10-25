
import bcrypt
from getpass import getpass

password = input("Enter a new admin password: ")

password_hash = bcrypt.hashpw(
    password.encode("utf-8"),
    bcrypt.gensalt()
).decode("utf-8")

print("\nGenerated bcrypt hash:")
print(password_hash)

