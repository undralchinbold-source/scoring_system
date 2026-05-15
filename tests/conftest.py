"""
Pytest тохиргоо — Flask app-г тест горимд эхлүүлнэ.
"""
import os
import sys

import pytest

# Төслийн root-г Python path-д нэмнэ
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Тестийн орчны тохиргоо — .env файл байхгүй ч ажиллана
os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test_scoring_db")
os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "postgres")


@pytest.fixture(scope="session")
def app():
    from app import create_app
    application = create_app("development")
    application.config["TESTING"] = True
    return application


@pytest.fixture(scope="session")
def app_context(app):
    with app.app_context():
        yield app
