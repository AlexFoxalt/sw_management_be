from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi import status as st
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.supervisor import SupervisorController
from src.dependencies import get_rbac_session, get_supervisor_controller


router = APIRouter(prefix="/api", tags=["Supervisor"])


@router.get("/departments/installedSoftware/{dept_id}")
async def get_department_installed_software(
    dept_id: int,
    controller: SupervisorController = Depends(get_supervisor_controller),
    session: AsyncSession = Depends(get_rbac_session),
) -> Response:
    models = await controller.get_dept_installed_sw(session, dept_id)
    return JSONResponse(
        content=[
            {
                "software_id": model.software_id,
                "sw_type_id": model.sw_type_id,
                "sw_type_name": model.sw_type.name,
                "code": model.code,
                "name": model.name,
                "short_name": model.short_name,
                "manufacturer": model.manufacturer,
            }
            for model in models
        ],
        status_code=st.HTTP_200_OK,
    )


@router.get("/departments/assignedComputers/{dept_id}")
async def get_department_assigned_computers(
    dept_id: int,
    controller: SupervisorController = Depends(get_supervisor_controller),
    session: AsyncSession = Depends(get_rbac_session),
) -> Response:
    models = await controller.get_dept_computer_assignments(session, dept_id)
    return JSONResponse(
        content=[
            {
                "computer_id": model.computer_id,
                "inventory_number": model.inventory_number,
                "computer_type": model.computer_type.value,
                "purchase_date": model.purchase_date.isoformat(),
                "status": model.status,
            }
            for model in models
        ],
        status_code=st.HTTP_200_OK,
    )


@router.get("/licenses/expiring")
async def get_expiring_licenses(
    start_date: datetime,
    end_date: datetime,
    controller: SupervisorController = Depends(get_supervisor_controller),
    session: AsyncSession = Depends(get_rbac_session),
) -> Response:
    models = await controller.get_expiring_licenses(session, start_date, end_date)
    return JSONResponse(
        content=[
            {
                "license_id": model.license_id,
                "software_id": model.software_id,
                "software_name": model.software.name,
                "vendor_id": model.vendor_id,
                "vendor_name": model.vendor.name,
                "start_date": model.start_date.isoformat(),
                "end_date": model.end_date.isoformat(),
                "price_per_unit": model.price_per_unit,
            }
            for model in models
        ],
        status_code=st.HTTP_200_OK,
    )
