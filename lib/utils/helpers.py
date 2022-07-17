import disnake
import config
import random
import string
from lib.db import db

def custom_id(view: str, id: int) -> str:
    return f"{config.BOT_NAME}:{view}:{id}"


def get_random_string(amount):
    key_list = []
    for _ in range(amount):
        key_list.append(''.join(random.choice(string.ascii_letters) for i in range(10)))
    for key in key_list:
        db.execute("INSERT INTO access_keys (access_key) VALUES (?)", key)
        db.commit()

def key_check(key: str) -> str:
    keys = []
    keys.append(db.column("SELECT * FROM access_keys"))
    if key in keys:
            return True
    return False
    

