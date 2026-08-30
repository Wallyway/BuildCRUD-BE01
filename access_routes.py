from fastapi import APIRouter, Header, HTTPException
from typing import Optional

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


@router.get("/protected/profile", tags=["protected"], summary="User profile", description="Requires an Authorization: Bearer <token> header. Returns 401 when the header is missing or malformed.")
def profile(authorization: Optional[str] = Header(default=None)):
    token = extract_token(authorization)
    return {"message": "Token received", "token": token}
