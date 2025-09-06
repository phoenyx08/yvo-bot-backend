import uuid
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    print("Creating access token")
    """Return a signed JWT that contains a unique `jti`."""
    to_encode = data.copy()

    # ---- expiry ---------------------------------------------------------
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    # ---- jti -------------------------------------------------------------
    # This is the piece missing from your earlier version.
    to_encode["jti"] = str(uuid.uuid4())

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)




def get_jti_from_token(token: str) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload["jti"]
