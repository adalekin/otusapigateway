import datetime

import connexion

from users import settings
from users.extensions import db
from users.models.user import User, user_schema

from . import utils
from .exception import AuthFailure


def login(login):
    with db.session.begin(subtransactions=True):
        user = db.session.query(User).filter(User.email == login["email"]).one_or_none()

        AuthFailure.require_condition(
            user and user.verify_password(login["password"]),
            "The email or password is incorrect"
        )

        user.last_login = datetime.datetime.utcnow()
        db.session.add(user)

    access_token = utils.access_token_for_user(user)

    user_dump = user_schema.dump(user).data
    user_dump["access_token"] = access_token

    return user_dump, 200


def logout():
    access_token, _ = utils.jwt_read_from_header(request=connexion.request)
    utils.jwt_blacklist_token(access_token)

    return connexion.NoContent, 204
