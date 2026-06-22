"""EMBEDHUNT AI — Auth domain models (reexport from app models)"""
from app.models.user import User
from app.auth.permissions import UserRole
__all__ = ["User", "UserRole"]
