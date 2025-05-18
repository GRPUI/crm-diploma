from datetime import timedelta, datetime, timezone
from typing import Dict, Any
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException
from jwt import InvalidTokenError
from passlib.handlers.argon2 import argon2
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from starlette.requests import Request

from core.db import DatabaseHandler
from core.db.models import User
from core.request_models.auth import RefreshTokenModel, SignInModel, SignUpModel
from core.responce_models.auth import (
    RefreshTokenResponseModel,
    SignInResponseModel,
    SignUpResponseModel,
)
from deps import SettingsMarker
from settings import Settings


async def sign_token(
    jwt_type: str,
    subject: str,
    jwt_secret: str,
    payload: Dict[str, Any] = {},
    ttl: timedelta = None,
) -> str:
    """
    Функция для создания JWT токена.

    :param jwt_type: Тип токена (например, "access" или "refresh").
    :param subject: Идентификатор субъекта (пользователя), для которого создается токен.
    :param jwt_secret: Секретный ключ, используемый для подписи токена.
    :param payload: Дополнительные данные, которые будут включены в токен.
    :param ttl: Время жизни токена (time-to-live). Если не указано, токен будет бессрочным.
    :return: Сгенерированный JWT токен в виде строки.
    """
    current_timestamp = datetime.now(tz=timezone.utc).timestamp()

    data = dict(
        iss="auth_service@crm",
        sub=subject,
        type=jwt_type,
        jti=str(uuid4()),
        iat=current_timestamp,
        nbf=payload["nbf"] if payload.get("nbf") else current_timestamp,
    )
    data.update(dict(exp=data["nbf"] + int(ttl.total_seconds()))) if ttl else None
    payload.update(data)

    return jwt.encode(payload=payload, key=jwt_secret, algorithm="HS256")


async def encode_password(password: str, jwt_secret: str) -> str:
    """
    Функция для кодирования пароля

    Эта функция кодирует пароль, используя алгоритм хэширования HS-256.

    :param password: Пароль, который необходимо закодировать.
    :param jwt_secret: Секретный ключ, используемый для кодирования пароля.
    :return: Закодированный пароль.
    """
    return jwt.encode({"password": password}, key=jwt_secret, algorithm="HS256")


async def check_access_token(
    request: Request,
    settings: Settings = Depends(SettingsMarker),
) -> int | None:
    """
    Функция для проверки токена

    Эта функция проверяет валидность токена доступа, переданного в заголовке авторизации.

    :param request: Заголовок авторизации, содержащий токен доступа.
    :param settings: Объект настроек, содержащий секретный ключ для декодирования токена.
    :return: Идентификатор пользователя, если токен валиден.
    :raises HTTPException: Если токен отсутствует, имеет неверный формат или недействителен.
    """

    if request.cookies.get("access_token") is None:
        raise HTTPException(status_code=401, detail="Token is required")

    clear_token = request.cookies.get("access_token")

    try:
        payload = jwt.decode(
            jwt=clear_token, key=settings.jwt_secret_key, algorithms=["HS256", "RS256"]
        )
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user_id


async def renew(
    data: RefreshTokenModel, db: DatabaseHandler, jwt_secret: str
) -> RefreshTokenResponseModel:
    """
    Функция для обновления токена

    Эта функция обрабатывает процесс обновления токена. Она проверяет действительность
    токена обновления и генерирует новый токен доступа, если токен обновления действителен.

    :param db: Объект DatabaseHandler для взаимодействия с базой данных.
    :param data: Объект RefreshTokenModel, содержащий токен обновления, предоставленный пользователем.
    :param jwt_secret: Секретный ключ, используемый для кодирования JWT токенов.
    :return: Объект RefreshTokenResponseModel, содержащий новый токен доступа и старый токен обновления.
    :raises HTTPException: Если токен обновления недействителен или пользователь не найден.
    """
    user_id = jwt.decode(
        jwt=data.refresh_token, key=jwt_secret, algorithms=["HS256"]
    ).get("sub")
    async with db.sessionmaker() as session:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        exists = result.scalars().first()

    if not exists:
        raise HTTPException(status_code=401, detail="Invalid token")

    access = await sign_token("access", user_id, jwt_secret, ttl=timedelta(minutes=15))

    return RefreshTokenResponseModel(access_token=access)


async def sign_in(
    data: SignInModel, jwt_secret: str, db: DatabaseHandler
) -> SignInResponseModel:
    """
    Функция для входа

    Эта функция обрабатывает процесс входа пользователя. Она проверяет учетные данные пользователя
    и генерирует токены доступа и обновления, если учетные данные верны.

    :param data: Объект SignInModel, содержащий имя пользователя и пароль, предоставленные пользователем.
    :param jwt_secret: Секретный ключ, используемый для кодирования JWT токенов.
    :param db: Объект DatabaseHandler для взаимодействия с базой данных.
    :return: Объект SignInResponseModel, содержащий токены доступа и обновления.
    :raises HTTPException: Если имя пользователя или пароль неверны.
    """
    async with db.sessionmaker() as session:
        query = select(User).where(User.username == data.username)
        result = await session.execute(query)
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User is not active")
        decoded_password = argon2.verify(data.password, user.password_hash)
        if not decoded_password:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        user_id = user.id
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access = await sign_token("access", user_id, jwt_secret, ttl=timedelta(minutes=15))
    refresh = await sign_token("refresh", user_id, jwt_secret, ttl=timedelta(days=30))

    return SignInResponseModel(access_token=access, refresh_token=refresh)


async def sign_up(data: SignUpModel, jwt_secret: str, db: DatabaseHandler):
    """
    Функция для регистрации

    Эта функция обрабатывает процесс регистрации пользователя. Она создает новую запись
    в базе данных и генерирует токены доступа и обновления для нового пользователя.

    :param data: Объект SignUpModel, содержащий имя пользователя, пароль и адрес электронной почты.
    :param jwt_secret: Секретный ключ, используемый для кодирования JWT токенов.
    :param db: Объект DatabaseHandler для взаимодействия с базой данных.
    :return: Объект SignInResponseModel, содержащий токены доступа и обновления.
    :raises HTTPException: Если пользователь с таким именем пользователя уже существует.
    """
    async with db.sessionmaker() as session:
        query = select(User.id).where(User.username == data.username)
        result = await session.execute(query)
        exists = result.scalars().first()

    if exists:
        raise HTTPException(status_code=409, detail="User already exists")

    async with db.sessionmaker() as session:
        try:
            user = (
                insert(User)
                .values(
                    username=data.username,
                    password=await encode_password(data.password, jwt_secret),
                    email=data.email,
                )
                .returning(User)
            )
            result = await session.execute(user)
            user = result.scalars().first()
            user_id = str(user.uuid)
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        else:
            await session.commit()
    access = await sign_token("access", user_id, jwt_secret, ttl=timedelta(minutes=15))
    refresh = await sign_token("refresh", user_id, jwt_secret, ttl=timedelta(days=30))

    return SignUpResponseModel(access_token=access, refresh_token=refresh)
