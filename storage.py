import json
from pathlib import Path


DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"


def ensure_data_file():
    DATA_DIR.mkdir(exist_ok=True)

    if not USERS_FILE.exists():
        USERS_FILE.write_text("{}", encoding="utf-8")


def load_users() -> dict:
    ensure_data_file()
    content = USERS_FILE.read_text(encoding="utf-8").strip()

    if not content:
        return {}

    return json.loads(content)


def save_users(users: dict):
    ensure_data_file()
    USERS_FILE.write_text(
        json.dumps(users, indent=2),
        encoding="utf-8"
    )


def get_user(username: str):
    users = load_users()
    return users.get(username)


def add_user(username: str, password_hash: str):
    users = load_users()

    if username in users:
        raise ValueError("User already exists")

    users[username] = {
        "password_hash": password_hash
    }

    save_users(users)