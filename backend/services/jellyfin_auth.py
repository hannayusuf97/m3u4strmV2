from fastapi import HTTPException
import jwt
import os
import requests
import hashlib
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
from typing import Optional
load_dotenv(find_dotenv())

# Configuration
secret_key = os.environ.get('SECRET_TOKEN') 
algorithm = os.environ.get('ALGORITHM', 'H256')
access_token_expire_minutes = 30
refresh_token_expire_days = 7 
server_url = os.environ.get('JELLYFIN_URL')

def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def get_jellyfin_access_token(username: str, password: str) -> dict:
    """Request an access token from the Jellyfin API and return a JWT."""
    combined_string = f"{username}:{server_url}"
    unique_id = hashlib.sha256(combined_string.encode()).hexdigest()
    headers = {
    "X-Emby-Authorization": f'MediaBrowser Client="FastAPI", Device="M3U4STRM", DeviceId="{unique_id}", Version="0.0.1"'
    }
    auth_data = {"Username": username, "Pw": password}

    try:
        response = requests.post(f"{server_url}/Users/AuthenticateByName", headers=headers, json=auth_data)

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        jellyfin_token = response.json().get("AccessToken")
        is_admin = response.json().get("User", {}).get("Policy", {}).get("IsAdministrator", False)

        # Create access and refresh tokens
        access_token = create_jwt_token(
            data={"sub": username, "jellyfin_token": jellyfin_token, "is_admin": is_admin},
            expires_delta=timedelta(minutes=access_token_expire_minutes)
        )
        refresh_token = create_jwt_token(
            data={"sub": username},
            expires_delta=timedelta(days=refresh_token_expire_days)
        )
        
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token, 
            "jellyfin_token": jellyfin_token, 
            "is_admin": is_admin
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to communicate with Jellyfin server: {str(e)}")

class TokenManager:
    """A class to manage Jellyfin tokens and headers."""
    _access_token: Optional[str] = None
    _jellyfin_token: Optional[str] = None
    _token_expiry: Optional[datetime] = None
    _is_admin: Optional[bool] = None

    @classmethod
    def set_access_token(cls, token: str):
        """Store the access token and extract the Jellyfin token."""
        cls._access_token = token
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        cls._jellyfin_token = payload.get("jellyfin_token")
        cls._is_admin = payload.get("is_admin", False)
        cls._token_expiry = datetime.fromtimestamp(payload.get("exp"))

    @classmethod
    def get_jellyfin_token(cls) -> Optional[str]:
        """Return the Jellyfin token if it hasn't expired."""
        if cls._jellyfin_token and cls._token_expiry > datetime.utcnow():
            return cls._jellyfin_token
        return None

    @classmethod
    def get_headers(cls) -> Optional[dict]:
        """Return the headers with the Jellyfin token."""
        jellyfin_token = cls.get_jellyfin_token()
        if jellyfin_token:
            return {
                "X-Emby-Token": jellyfin_token,
                "Content-Type": "application/json"
            }
        return None

    @classmethod
    def is_admin(cls) -> bool:
        """Return whether the current token belongs to an admin user."""
        return cls._is_admin or False

admin_status_cache = {
    "is_admin": None,
    "last_checked": None
}
CACHE_DURATION = timedelta(minutes=10)  # Cache for 10 minutes

def getisAdmin(username: str) -> bool:
    """Check if the user is an admin, updating the cache if the username has changed."""
    global admin_status_cache

    # If the username has changed, reset the cache
    if admin_status_cache.get("username") != username:
        admin_status_cache = {
            "is_admin": None,
            "last_checked": None,
            "username": username
        }

    # Use cached admin status if it's still valid
    if admin_status_cache["is_admin"] is not None:
        if admin_status_cache["last_checked"] and datetime.utcnow() - admin_status_cache["last_checked"] < CACHE_DURATION:
            return admin_status_cache["is_admin"]

    # Check the admin status from the Jellyfin server
    headers = TokenManager.get_headers()
    if not headers:
        raise HTTPException(status_code=401, detail="Unauthorized: No valid token")

    try:
        response = requests.get(f"{server_url}/Users/Me", headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            is_admin = user_data.get("Policy", {}).get("IsAdministrator", False)
            
            # Update the cache with the new admin status and username
            admin_status_cache["is_admin"] = is_admin
            admin_status_cache["last_checked"] = datetime.utcnow()
            admin_status_cache["username"] = username
            
            return is_admin
        elif response.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid or expired Jellyfin token")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Jellyfin API error: {response.text}")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to communicate with Jellyfin server: {str(e)}")

def scanLibrary():
    """Scan the library for new series and videos."""
    headers = TokenManager.get_headers()
    
    if not headers:
        raise HTTPException(status_code=401, detail="Unauthorized: No valid token")
    response = requests.post(f"{server_url}/Library/Refresh", headers=headers, timeout=10)
    
    if response.status_code != 204:
        raise HTTPException(status_code=response.status_code, detail=f"Jellyfin API error: {response.text}")