# Pydantic schemas for user registration/auth
from pydantic import BaseModel, EmailStr, constr
from pydantic import validator

class RegisterUser(BaseModel): 
    username: constr(
        strip_whitespace=True,
        to_lower=True,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_-]+$"
    )
    email: EmailStr
    password: constr(min_length=8, max_length=128)
    
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "@$!%*?&" for c in value):
            raise ValueError("Password must contain at least one special character (@$!%*?&)")
        return value

    # Pydantic validator

    @validator("password")
    def password_strength(cls, v):
        return cls.validate_password(v)

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserData(BaseModel):
    username: str
    email: str | None = None