from fastapi import Request

from auth_service import AuthService


def get_auth(request: Request) -> AuthService:
    return request.app.state.auth
