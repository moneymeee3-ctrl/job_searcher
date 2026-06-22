"""EMBEDHUNT AI — Custom Exception Hierarchy"""
from fastapi import HTTPException, status

class EmbedHuntException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message; self.status_code = status_code; super().__init__(message)

class NotFoundError(EmbedHuntException):
    def __init__(self, resource: str, id: str = ""):
        super().__init__(f"{resource}{' ' + id if id else ''} not found", 404)

class ConflictError(EmbedHuntException):
    def __init__(self, message: str): super().__init__(message, 409)

class ValidationError(EmbedHuntException):
    def __init__(self, message: str): super().__init__(message, 422)

class AuthenticationError(EmbedHuntException):
    def __init__(self, message: str = "Authentication failed"): super().__init__(message, 401)

class AuthorizationError(EmbedHuntException):
    def __init__(self, message: str = "Insufficient permissions"): super().__init__(message, 403)

class ParseError(EmbedHuntException):
    def __init__(self, message: str): super().__init__(message, 422)

class StorageError(EmbedHuntException):
    def __init__(self, message: str): super().__init__(message, 500)
