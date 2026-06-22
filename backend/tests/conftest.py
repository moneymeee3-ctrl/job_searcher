"""EMBEDHUNT AI — Test Configuration"""
import os
os.environ["SECRET_KEY"] = "test-secret-key-minimum-32-chars-embedhunt!!"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test"
os.environ["APP_ENV"] = "test"
os.environ["LOG_FORMAT"] = "text"
os.environ["LOG_LEVEL"] = "WARNING"
