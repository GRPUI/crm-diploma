from pydantic import BaseModel


class SignInResponseModel(BaseModel):
    access_token: str
    refresh_token: str


class SignUpResponseModel(SignInResponseModel):
    pass


class RefreshTokenResponseModel(BaseModel):
    access_token: str
