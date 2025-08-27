import os
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

from __schemas__ import CurrentUser

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


password_hasher = PasswordHasher(
    time_cost=2,        # Number of iterations
    memory_cost=102400, # RAM usage in KiB (e.g., 100MB)
    parallelism=8,      # Threads
    hash_len=32,        # Length of the hash
    salt_len=16         # Salt length
)

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using Argon2.
    """
    return password_hasher.hash(password)

def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    Verifies a plain-text password against its hashed version.
    Returns True if matched, False otherwise.
    """
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency function to extract and validate the current user from a JWT token.

    This function is used in FastAPI routes to authorize users based on a JWT token
    provided in the Authorization header (using the OAuth2 Bearer token scheme).

    It decodes the token using the secret key and returns a CurrentUser object if
    the token is valid. If the token is missing, expired, invalid, or if the
    secret key is not configured, it raises appropriate HTTP exceptions.

    Args:
        token (str): The JWT token provided via FastAPI's OAuth2PasswordBearer dependency.

    Returns:
        CurrentUser: An instance containing the decoded token data.

    Raises:
        HTTPException: If the token is missing, expired, or invalid.
        RuntimeError: If the SECRET_KEY is not set in environment variables.
    """
    if not token:
        raise HTTPException(status_code=401, detail="auth token not provided")
    try:
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            raise RuntimeError("SECRET_KEY not set in environment")
        decoded_token = jwt.decode(token, key=secret_key, algorithms=["HS256"])
        return CurrentUser(**decoded_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="auth token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="auth token is invalid")