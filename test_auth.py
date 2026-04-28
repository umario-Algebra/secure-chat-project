from auth import hash_password, verify_password


password = "SecretPassword123!"
stored_hash = hash_password(password)

print("Stored hash:", stored_hash)
print("Correct password:", verify_password("SecretPassword123!", stored_hash))
print("Wrong password:", verify_password("WrongPassword!", stored_hash))