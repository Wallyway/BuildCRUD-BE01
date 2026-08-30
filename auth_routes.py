from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from auth_dependency import get_auth, get_token, require_user
from auth_service import AuthService
from supabase_auth import User

router = APIRouter(prefix="/auth", tags=["auth"])


class Credentials(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


@router.post("/signup", status_code=201, summary="Sign up", description="Registers a new account in Supabase. Rejects a missing email or password with 400.")
def signup(credentials: Credentials, auth: AuthService = Depends(get_auth)):
    return auth.sign_up(credentials.email, credentials.password)


@router.post("/login", summary="Log in", description="Exchanges email and password for an access token. 400 if a field is missing, 401 if the credentials are wrong.")
def login(credentials: Credentials, auth: AuthService = Depends(get_auth)):
    return auth.sign_in(credentials.email, credentials.password)


@router.post("/logout", status_code=204, summary="Log out", description="Ends the Supabase session behind the token. Protected: 401 without a valid token.")
def logout(token: str = Depends(get_token), user: User = Depends(require_user), auth: AuthService = Depends(get_auth)):
    auth.sign_out(token)
