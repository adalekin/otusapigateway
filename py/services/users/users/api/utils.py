import base64
import json

import connexion

import requests

from users import settings
from users.extensions import db
from users.models.user import User

from .exception import NoSuchUser


AUTH_SESSION = requests.Session()


def _auth_api(path):
    return settings.AUTH_URL + path


def jwt_encode_token(payload):
    response = AUTH_SESSION.post(_auth_api("/jwt/encode/"), json={"iss": "affo", "payload": payload})
    response.raise_for_status()

    return response.json()["access_token"]


def jwt_blacklist_token(access_token):
    response = AUTH_SESSION.post(_auth_api("/jwt/blacklist/"), json={"access_token": access_token})
    response.raise_for_status()


def jwt_read_from_header():
    token = None
    payload = None

    payload_string = connexion.request.headers.get("X-JWT-Payload")

    if payload_string:
        payload = json.loads(base64.b64decode(payload_string))

    token_string = connexion.request.headers.get("X-JWT-Token")

    if token_string:
        bearer, _, token = header.partition(" ")

    return token, payload


def access_token_for_user(user):
    return jwt_encode_token(payload={"user_id": user.id})


def get_user_by_id(user_id):
    if user_id == "current":
        _, payload = jwt_read_from_header()
        user_id = payload["user_id"]

    user = db.session.query(User).filter(User.id == user_id).one_or_none()

    NoSuchUser.require_condition(user, "The user with {user_id} identifier does not exist", user_id=user_id)

    return user
