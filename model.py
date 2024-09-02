from typing import List
from pydantic import BaseModel
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
import os
from dotenv import load_dotenv

load_dotenv()
USERNAME1 = os.getenv("USERNAME1")
PASSWORD1 = os.getenv("PASSWORD1")


class User(BaseModel):
    username: str
    hashed_password: str
    balance: str


class DataBase(BaseModel):
    user: List[User]


DB = DataBase(
    user=[
        User(
            username=USERNAME1,
            hashed_password=crypto.hash(PASSWORD1),
            balance="10,293.05",
        )
        # add more users here
    ]
)


def get_user(username: str) -> User:
    user = [user for user in DB.user if user.username == username]
    # pdb.set_trace()
    if user:
        return user[0]
    return None
