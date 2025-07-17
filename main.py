from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import httpx
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Annotated
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

class Request(BaseModel):
    query: str

class Response(BaseModel):
    response: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

fake_users_db = {
    USERNAME: {
        "username": USERNAME,
        "hashed_password": pwd_context.hash(PASSWORD),
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

app = FastAPI()

@app.post("/login", response_model = TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(data={"sub": user["username"]})
    return TokenResponse(accessToken = token)

@app.post("/ask")
async def ask(
        request: Request,
        token: str = Depends(oauth2_scheme)
) -> Response:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401)

        payload = {
            "model": MODEL_NAME,
            "prompt": request.query,
            "stream": False
        }

        timeout = httpx.Timeout(30.0, connect = 5.0)
        async with httpx.AsyncClient(timeout = timeout) as client:
            response = await client.post(OLLAMA_URL, json = payload)
            response.raise_for_status()
            result = response.json()
            return Response(response = result["response"])
    except JWTError:
        raise HTTPException(status_code=401)
    except httpx.RequestError as e:
        raise HTTPException(status_code = 500, detail=f"Request failed: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code = response.status_code, detail = str(e))
