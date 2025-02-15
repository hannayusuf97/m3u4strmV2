from fastapi import APIRouter, HTTPException, Depends, Form
from pydantic import BaseModel
from services.jellyfin_auth import get_jellyfin_access_token, create_jwt_token, getisAdmin
from fastapi.security import OAuth2PasswordBearer
import jwt
import os
from datetime import timedelta
from jwt import PyJWTError
from services.jellyfin_auth import TokenManager
from datetime import datetime

router = APIRouter()
login_router = APIRouter()
# In-memory token blacklist (for demonstration purposes)
token_blacklist = set()

server_url = os.environ.get('JELLYFIN_URL')
secret_key = os.environ.get('SECRET_TOKEN') 
algorithm = os.environ.get('ALGORITHM', 'H256')
access_token_expire_minutes = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def verify_jwt_token(token: str = Depends(oauth2_scheme)):
    """Verify and decode a JWT token to extract the username."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

class LoginRequest(BaseModel):
    username: str
    password: str

@login_router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Authenticate user and return access and refresh tokens."""
    try:
        tokens = get_jellyfin_access_token(username, password)
        access_token = tokens["access_token"]
        TokenManager.set_access_token(access_token)
        is_admin = tokens["is_admin"]

        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "jellyfin_token": tokens["jellyfin_token"],
            "token_type": "bearer",
            "is_admin": is_admin,
            "exp": datetime.utcnow() + timedelta(minutes=access_token_expire_minutes)
        }
        
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

class TokenRefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
async def refresh_token(request: TokenRefreshRequest):
    """Refresh access token using a valid refresh token."""
    try:
        payload = jwt.decode(request.refresh_token, secret_key, algorithms=[algorithm])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Create a new access token
        new_access_token = create_jwt_token(
            data={"sub": username},
            expires_delta=timedelta(minutes=access_token_expire_minutes)
        )

        return {"access_token": new_access_token, "token_type": "bearer"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Invalidate the current access token."""
    if token in token_blacklist:
        raise HTTPException(status_code=400, detail="Token already invalidated")
    
    # Add the token to the blacklist
    token_blacklist.add(token)
    return {"message": "Successfully logged out"}

@router.get("/check_admin")
async def check_admin(username: str = Depends(verify_jwt_token)):
    """Check if the currently logged-in user is an admin."""
    try:
        is_admin = getisAdmin(username)  # Pass the username to update the cached status if needed
        return {"is_admin": is_admin}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token format")


