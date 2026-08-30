from fastapi import APIRouter, Depends, Header, HTTPException
from typing import Optional

from auth_dependency import get_auth
from auth_service import AuthService

router = APIRouter()


def extract_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Access token required")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        raise HTTPException(status_code=401, detail="Access token required")
    return parts[1]


@router.get("/public/info", tags=["public"], summary="Public info", description="Open to anyone. No token needed.")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@router.get("/protected/profile", tags=["protected"], summary="User profile", description="Requires an Authorization: Bearer <token> header. 401 when the header is missing, and 401 when Supabase rejects the token.")
def profile(authorization: Optional[str] = Header(default=None), auth: AuthService = Depends(get_auth)):
    token = extract_token(authorization)
    user = auth.get_user(token)
    return {"id": user.id, "email": user.email, "created_at": user.created_at}
