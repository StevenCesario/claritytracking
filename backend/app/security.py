from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# We import these to interact with our database and schemas.
from . import database, models, schemas

# --- Configuration ---
# Load secrets from environment variables.
# Using os.environ['KEY'] is a deliberate choice. It will raise a KeyError
# and crash the app on startup if the key is missing, which is a secure
# default behavior.
try:
    SECRET_KEY = os.environ["SECRET_KEY"]
except KeyError:
    raise RuntimeError("SECRET_KEY must be set in the environment variables.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # A token will be valid for 30 minutes.

# --- Password Hashing ---
# This creates a context for hashing and verifying passwords using bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

# --- JWT (Token) Handling ---
# This is the "Locksmith" that creates the JWT.
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # The 'sub' (subject) claim is standard for storing the user's ID.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# This tells FastAPI where to look for the token (in the Authorization header).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# --- The "Bouncer" Dependency ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)) -> models.User:
    """
    Decodes a JWT, validates it, and fetches the corresponding user from the database.
    This function will be a dependency for all protected endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(user_id=int(user_id))
    except (JWTError, ValueError):
        # Catches any decoding errors or if the user_id isn't a valid integer.
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    
    if user is None:
        raise credentials_exception
        
    return user
