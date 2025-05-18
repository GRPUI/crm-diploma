from fastapi import APIRouter
from fastapi.params import Depends
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.v1.services import auth
from core.db import DatabaseHandler
from core.request_models.auth import SignInModel, RefreshTokenModel, SignUpModel
from core.responce_models.defaults import DefaultResponseModel
from deps import SettingsMarker, DatabaseMarker
from settings import Settings

router = APIRouter(tags=["Auth"])


@router.post(
    "/login",
    responses={
        200: {
            "description": "Success",
            "content": {"application/json": {"example": {"message": "Success"}}},
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid username or password"}
                }
            },
        },
    },
    response_model=DefaultResponseModel,
)
async def login(
    data: SignInModel,
    settings: Settings = Depends(SettingsMarker),
    db: DatabaseHandler = Depends(DatabaseMarker),
) -> JSONResponse:
    result = await auth.sign_in(data, settings.jwt_secret_key, db)
    response = JSONResponse(
        {"status": "ok", "detail": "Successfully logged in"},
        status_code=200,
    )
    response.set_cookie(
        key="access_token",
        value=result.access_token,
        httponly=True,
        secure=settings.is_prod,
        samesite="strict",
    )
    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=settings.is_prod,
        samesite="none",
    )
    return response


@router.post("/signup")
async def signup(
    data: SignUpModel,
    settings: Settings = Depends(SettingsMarker),
    db: DatabaseHandler = Depends(DatabaseMarker),
) -> JSONResponse:
    result = await auth.sign_up(data, settings.jwt_secret_key, db)
    response = JSONResponse(
        {"status": "ok", "detail": "Successfully signed up"}, status_code=200
    )
    response.set_cookie(
        key="access_token",
        value=result.access_token,
        httponly=True,
        secure=settings.is_prod,
        samesite="strict",
    )
    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=settings.is_prod,
        samesite="none",
    )
    return response


@router.post(
    "/refresh",
    responses={
        200: {
            "description": "Success",
            "content": {"application/json": {"example": {"message": "Success"}}},
        },
        401: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "Invalid token"}}},
        },
    },
)
async def refresh(
    request: Request,
    settings: Settings = Depends(SettingsMarker),
    db: DatabaseHandler = Depends(DatabaseMarker),
) -> JSONResponse:
    data = RefreshTokenModel(
        refresh_token=request.headers.get("Authorization").split(" ")[1],
    )
    result = await auth.renew(data, db, settings.jwt_secret_key)
    response = JSONResponse({"status": "ok", "detail": "success"}, status_code=200)
    response.set_cookie(
        key="access_token",
        value=result.access_token,
        httponly=True,
        secure=settings.is_prod,
        samesite="strict",
    )
    return response


@router.post("/logout")
async def logout() -> JSONResponse:
    response = JSONResponse(
        {"status": "ok", "detail": "Successfully logged out"}, status_code=200
    )
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return response
