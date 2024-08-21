from typing import List
from pydantic import BaseModel
from passlib.handlers.sha2_crypt import sha512_crypt as crypto


class User(BaseModel):
    username: str
    hashed_password: str


class DataBase(BaseModel):
    user: List[User]


DB = DataBase(
    user=[
        # highlight-start
        User(username="admin", hashed_password=crypto.hash("12345")),
        User(username="tester", hashed_password=crypto.hash("12345")),
        # highlight-end
    ]
)


def get_user(username: str) -> User:
    user = [user for user in DB.user if user.username == username]
    # pdb.set_trace()
    if user:
        return user[0]
    return None
