from pydantic import BaseModel

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: str
    role: str | None = None