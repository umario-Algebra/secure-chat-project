from storage import add_user, get_user, load_users


print("Users before:", load_users())

try:
    add_user("mario", "demo-hash-123")
    print("User mario added")
except ValueError as e:
    print("Add user result:", str(e))

print("User mario:", get_user("mario"))
print("Users after:", load_users())