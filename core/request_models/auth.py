from pydantic import BaseModel


class SignInModel(BaseModel):
    username: str
    password: str


class SignUpModel(SignInModel):
    email: str


class RefreshTokenModel(BaseModel):
    refresh_token: str
