"""
Authentication API Router.

Demonstrates FastAPI APIRouter structure and route declaration.
In Express/Node.js, this corresponds to `const router = express.Router(); router.post('/login', handler)`.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post(
    "/login",
    response_model=AuthTokenResponse,
    summary="User Login",
    description="Authenticate user credentials and return a JWT access token."
)
async def login(credentials: LoginRequest):
    """
    Authenticate user endpoint stub.
    In FastAPI, input bodies are validated automatically against Pydantic models.
    Invalid JSON or missing fields automatically trigger HTTP 422 Unprocessable Entity responses.
    """
    if credentials.email == "user@example.com" and credentials.password == "password":
        return AuthTokenResponse(access_token="mock_jwt_token_123456789")
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password credentials."
    )
