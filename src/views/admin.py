from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.admin import AdminController
from src.dependencies import get_admin_controller, get_rbac_session
from src.enums import UserRole


router = APIRouter(prefix="/api", tags=["Admin"])


@router.post("/users")
async def create_user(
    username: str,
    password: str,
    role: UserRole,
    full_name: str,
    controller: AdminController = Depends(get_admin_controller),
    session: AsyncSession = Depends(get_rbac_session),
) -> Response:
    model = await controller.create_user(session, username, password, role, full_name)
    return JSONResponse(
        content={
            "username": model.username,
            "user_id": model.user_id,
            "role": model.role.value,
            "full_name": model.full_name,
        },
        status_code=status.HTTP_201_CREATED,
    )


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    username: str,
    role: UserRole,
    full_name: str,
    controller: AdminController = Depends(get_admin_controller),
    session: AsyncSession = Depends(get_rbac_session),
) -> Response:
    model = await controller.update_user(session, user_id, username, role, full_name)
    return JSONResponse(
        content={
            "username": model.username,
            "user_id": model.user_id,
            "role": model.role.value,
            "full_name": model.full_name,
        },
        status_code=status.HTTP_200_OK,
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    controller: AdminController = Depends(get_admin_controller),
    session: AsyncSession = Depends(get_rbac_session),
) -> Response:
    await controller.delete_user(session, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/softwareTypes")
async def create_software_type(
    name: str,
    controller: AdminController = Depends(get_admin_controller),
    session: AsyncSession = Depends(get_rbac_session),
) -> Response:
    model = await controller.create_sw_type(session, name)
    return JSONResponse(
        content={"name": model.name, "sw_type_id": model.sw_type_id},
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/auditLogs")
async def get_audit_logs(
    limit: int = 50,
    controller: AdminController = Depends(get_admin_controller),
    session: AsyncSession = Depends(get_rbac_session),
) -> Response:
    models = await controller.get_audit_logs(session, limit)
    return JSONResponse(
        content=[
            {
                "log_id": model.log_id,
                "user_id": model.user_id,
                "action": model.action,
                "action_time": model.action_time.isoformat(),
            }
            for model in models
        ],
        status_code=status.HTTP_200_OK,
    )
