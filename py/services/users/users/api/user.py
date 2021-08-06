import datetime

import connexion

from sqlalchemy import or_

from werkzeug.security import generate_password_hash

from users import settings
from users.models.user import User, user_schema
from users.extensions import db

from . import utils
from .exception import AccessDenied, AlreadyExists, NoSuchUser


def create(user):
    with db.session.begin(subtransactions=True):
        phone = user.get("phone")

        if phone:
            user_already_exists_condition = or_(User.email == user["email"], User.phone == phone)
        else:
            user_already_exists_condition = User.email == user["email"]

        user_already_exists = db.session.query(User.query.filter(user_already_exists_condition).exists()).scalar()

        AlreadyExists.require_condition(
            not user_already_exists, "A user already exists with the specified email address or phone number"
        )

        if user["password"]:
            user["password"] = generate_password_hash(user["password"])

        user_ = User(**user)
        db.session.add(user_)

    access_token = utils.access_token_for_user(user=user_)

    user_dump = user_schema.dump(user_).data
    user_dump["access_token"] = access_token

    return user_dump, 201


def get(user_id):
    _, payload = utils.jwt_read_from_header()

    AccessDenied.require_condition(payload and str(user_id) in (str(payload["user_id"]), "current"), "Access denied")

    user_ = utils.get_user_by_id(user_id)

    return user_schema.dump(user_).data


def update(user_id, user1):
    _, payload = utils.jwt_read_from_header()

    AccessDenied.require_condition(payload and str(user_id) in (str(payload["user_id"]), "current"), "Access denied")

    with db.session.begin(subtransactions=True):
        user_ = utils.get_user_by_id(user_id)

        for k, v in user1.items():
            setattr(user_, k, v)

        db.session.add(user_)

    return user_schema.dump(user_).data
