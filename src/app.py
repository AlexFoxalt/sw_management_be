from fastapi import FastAPI, Request, status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from settings import Settings
from src.exceptions import (
    ServiceConflict,
    ServiceException,
    ServiceForbidden,
    ServiceNotFound,
    ServiceUnauthorized,
)
from src.views import admin, login, manager, supervisor


def _add_middlewares(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=settings.allowed_credentials,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )


def _include_routers(app: FastAPI) -> None:
    app.include_router(login.router)
    app.include_router(admin.router)
    app.include_router(manager.router)
    app.include_router(supervisor.router)


def _custom_exception_handler(_: Request, exception: ServiceException) -> JSONResponse:
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if isinstance(exception, ServiceConflict):
        status_code = status.HTTP_409_CONFLICT
    if isinstance(exception, ServiceNotFound):
        status_code = status.HTTP_404_NOT_FOUND
    if isinstance(exception, ServiceForbidden):
        status_code = status.HTTP_403_FORBIDDEN
    if isinstance(exception, ServiceUnauthorized):
        status_code = status.HTTP_401_UNAUTHORIZED
    return JSONResponse(status_code=status_code, content={"message": str(exception)})


def _add_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(ServiceException, _custom_exception_handler)


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title=settings.app_title, swagger_ui_parameters={"operationsSorter": "method"})
    _add_middlewares(app, settings)
    _include_routers(app)
    _add_exception_handler(app)
    return app
