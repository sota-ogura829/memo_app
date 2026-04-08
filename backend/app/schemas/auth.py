from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenUser(BaseModel):
    id: int
    username: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: TokenUser
