from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import httpx
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Annotated, AsyncGenerator
from dotenv import load_dotenv
import os
from starlette.responses import FileResponse, StreamingResponse
from auth_utils import get_jti_from_token, create_access_token
from session_store import sessions
import time

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
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

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

async def ollama_stream(history: list[dict]) -> AsyncGenerator[bytes, None]:
    """
    Async generator that yields raw bytes from Ollama as soon as they arrive.
    """
    payload = {
        "model": MODEL_NAME,
        "messages": history,
        "stream": True,
    }

    async with httpx.AsyncClient() as client:
        async with client.stream("POST", OLLAMA_URL, json=payload) as resp:
            resp.raise_for_status()          # raises 4xx/5xx if the request failed
            async for chunk in resp.aiter_bytes():
                if chunk:
                    yield chunk

app = FastAPI()
@app.get("/")
def serve_frontend():
    return FileResponse("./public/index.html")

@app.post("/login", response_model = TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code = 401, detail = "Invalid username or password")
    token = create_access_token(data = {"sub": user["username"]})
    return TokenResponse(accessToken = token)

@app.post("/ask")
async def ask(
    payload: Request,
    token: str = Depends(oauth2_scheme),
):
    jti = get_jti_from_token(token)
    history, expiry = sessions.get(jti, ([], 0.0))

    if expiry < time.time():
        history, expiry = [], 0.0

    history.append({"role": "user", "content": payload.query})

    assistant_chunks = bytearray()

    async def streamer() -> AsyncGenerator[bytes, None]:
        async for chunk in ollama_stream(history):
            # Pass the chunk on to the client *and* keep a copy
            yield chunk
            assistant_chunks.extend(chunk)

        # After the stream ends, append the assistant message to history
        reply_text = assistant_chunks.decode("utf-8").strip()
        history.append({"role": "assistant", "content": reply_text})

        # Persist the new history with a TTL
        sessions[jti] = (history, time.time() + ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    return StreamingResponse(streamer(), media_type="text/plain")
