from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.login import LoginController
from src.dependencies import get_login_controller, get_root_session


router = APIRouter(prefix="/api", tags=["Login"])


@router.get("/login")
async def login(
    username: str,
    password: str,
    ctrl: Annotated[LoginController, Depends(get_login_controller)],
    session: Annotated[AsyncSession, Depends(get_root_session)],
) -> JSONResponse:
    jwt = await ctrl.login(session, username, password)
    return JSONResponse(content=jwt, status_code=status.HTTP_200_OK)
