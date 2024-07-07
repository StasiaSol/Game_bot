import s_taper
from s_taper.consts import *
from telebot.types import Message

def is_new_user(msg:Message):
    res = users.read('userid', msg.chat.id)
    if res != []:
        return False
    return True


user_scheme = {
    "userid": INT + KEY,
    "name": TEXT,
    "power": TEXT,
    "hp": INT,
    "dmg": INT,
    'defend': BLN
    }
users = s_taper.Taper("users", "data.db").create_table(user_scheme)

