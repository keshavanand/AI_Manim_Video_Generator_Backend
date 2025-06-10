# Pydantic schemas for user registration/auth
from pydantic import BaseModel, EmailStr, constr
class Register_user(BaseModel):
    email: EmailStr  # already includes email pattern validation
    username: constr(
        strip_whitespace=True,
        to_lower=True,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_-]+$"
    )
    password: constr(min_length=8)

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User_Data(BaseModel):
    username: str
    email: str | None = None