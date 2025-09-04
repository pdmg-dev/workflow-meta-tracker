# app/config.py
import os


def get_config():
    match os.getenv("FLASK_ENV"):
        case "production":
            return ProductionConfig
        case "testing":
            return TestingConfig
        case "development":
            return DevelopmentConfig


class BaseConfig:
    SECRET_KEY = "secretkey"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"


class ProductionConfig(BaseConfig):
    pass
