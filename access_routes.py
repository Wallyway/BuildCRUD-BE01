from fastapi import APIRouter, Depends
from supabase_auth import User

from auth_dependency import require_user

router = APIRouter()


@router.get("/public/info", tags=["public"], summary="Public info", description="Open to anyone. No token needed.")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@router.get("/protected/profile", tags=["protected"], summary="User profile", description="Returns the account behind the token. 401 when the header is missing, 401 when Supabase rejects the token.")
def profile(user: User = Depends(require_user)):
    return {"id": user.id, "email": user.email, "created_at": user.created_at}


@router.get("/protected/dashboard", tags=["protected"], summary="User dashboard", description="Second protected route, guarded by the same dependency and holding no token logic of its own.")
def dashboard(user: User = Depends(require_user)):
    return {"message": f"Welcome back, {user.email}", "user_id": user.id}
