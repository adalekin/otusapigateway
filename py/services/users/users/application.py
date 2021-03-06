import importlib
import logging
import sys

import connexion

import connexion_buzz

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from sqlalchemy.exc import ProgrammingError

from . import settings
from .api import exception
from .extensions import db, ma, migrate
from .models.user import User

__all__ = ["create_app"]

logging.basicConfig(level=logging.INFO)


def create_app(settings_override=None):
    app = connexion.App(__name__, specification_dir="./spec/", options={"swagger_ui": False}, debug=settings.DEBUG)
    app.add_api("openapi.yaml", arguments={"title": "AFFO User Service API"}, validate_responses=True)

    application = app.app
    application.config.from_object(settings)

    if settings_override:
        application.config.update(settings_override)

    app.add_error_handler(connexion_buzz.ConnexionBuzz, connexion_buzz.ConnexionBuzz.build_error_handler())

    # Import DB models. Flask-SQLAlchemy doesn't do this automatically.
    with application.app_context():
        for module in application.config.get("SQLALCHEMY_MODEL_IMPORTS", list()):
            importlib.import_module(module)

    # Initialize extensions/add-ons/plugins.

    # Flask-SQLAlchemy must be initialized before Flask-Marshmallow.
    db.init_app(application)
    ma.init_app(application)
    migrate.init_app(application, db)

    sentry_sdk.init(integrations=[FlaskIntegration()], **application.config.get("SENTRY_CONFIG", {}))

    return application
