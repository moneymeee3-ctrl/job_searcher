"""EMBEDHUNT AI — Auth Dependencies"""
from app.auth.permissions import get_current_user_id, get_current_user_role, require_role, require_min_role, UserRole
__all__ = ["get_current_user_id","get_current_user_role","require_role","require_min_role","UserRole"]
