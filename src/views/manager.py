from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi import status as st
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.manager import ManagerController
from src.dependencies import get_manager_controller, get_rbac_session, read_token
from src.enums import ComputerType


router = APIRouter(prefix="/api", tags=["Manager"])


@router.get("/computers")
async def get_computers(
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    models = await controller.get_all_computers(session, token)
    return JSONResponse(
        content=[
            {
                "computer_id": model.computer_id,
                "inventory_number": model.inventory_number,
                "computer_type": model.computer_type.value,
                "purchase_date": model.purchase_date.isoformat(),
                "status": model.status,
                "assigned_dept": {
                    "dept_id": model.assignment.department.dept_id,
                    "dept_name": model.assignment.department.dept_name,
                    "dept_code": model.assignment.department.dept_code,
                    "dept_short_name": model.assignment.department.dept_short_name,
                }
                if model.assignment
                else None,
            }
            for model in models
        ],
        status_code=st.HTTP_200_OK,
    )


@router.get("/softwareTypes")
async def get_software_types(
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    models = await controller.get_all_sw_types(session, token)
    return JSONResponse(
        content=[{"name": model.name, "sw_type_id": model.sw_type_id} for model in models],
        status_code=st.HTTP_200_OK,
    )


@router.get("/software")
async def get_software(
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    models = await controller.get_all_software(session, token)
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


@router.get("/vendors")
async def get_vendors(
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    models = await controller.get_all_vendors(session, token)
    return JSONResponse(
        content=[
            {
                "vendor_id": model.vendor_id,
                "name": model.name,
                "address": model.address,
                "phone": model.phone,
                "website": model.website,
            }
            for model in models
        ],
        status_code=st.HTTP_200_OK,
    )


@router.get("/licenses")
async def get_licenses(
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    models = await controller.get_all_licenses(session, token)
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


@router.get("/installations")
async def get_installations(
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    models = await controller.get_all_installations(session, token)
    return JSONResponse(
        content=[
            {
                "installation_id": model.installation_id,
                "license_id": model.license_id,
                "computer_id": model.computer_id,
                "install_date": model.install_date.isoformat(),
                "license": {
                    "license_id": model.license.license_id,
                    "software_id": model.license.software_id,
                    "software_name": model.license.software.name,
                    "vendor_id": model.license.vendor_id,
                    "vendor_name": model.license.vendor.name,
                    "start_date": model.license.start_date.isoformat(),
                    "end_date": model.license.end_date.isoformat(),
                    "price_per_unit": model.license.price_per_unit,
                }
                if model.license
                else None,
                "computer": {
                    "computer_id": model.computer_id,
                    "inventory_number": model.computer.inventory_number,
                    "computer_type": model.computer.computer_type.value,
                    "purchase_date": model.computer.purchase_date.isoformat(),
                    "status": model.computer.status,
                }
                if model.computer
                else None,
            }
            for model in models
        ],
        status_code=st.HTTP_200_OK,
    )


@router.post("/computers")
async def create_computer(
    inventory_number: str,
    computer_type: ComputerType,
    purchase_date: datetime,
    status: str,
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    model = await controller.create_computer(
        session, token, inventory_number, computer_type, purchase_date, status
    )
    return JSONResponse(
        content={
            "computer_id": model.computer_id,
            "inventory_number": model.inventory_number,
            "computer_type": model.computer_type.value,
            "purchase_date": model.purchase_date.isoformat(),
            "status": model.status,
        },
        status_code=st.HTTP_201_CREATED,
    )


@router.post("/computerAssignments")
async def create_computer_assignment(
    computer_id: int,
    dept_id: int,
    doc_number: str,
    doc_date: datetime,
    doc_type: str,
    start_date: datetime,
    end_date: datetime | None = None,
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    model = await controller.create_computer_assignment(
        session, token, computer_id, dept_id, start_date, end_date, doc_number, doc_date, doc_type
    )
    return JSONResponse(
        content={
            "assignment_id": model.assignment_id,
            "computer_id": model.computer_id,
            "dept_id": model.dept_id,
            "start_date": model.start_date.isoformat(),
            "end_date": model.end_date.isoformat() if model.end_date is not None else None,
            "doc_number": model.doc_number,
            "doc_date": model.doc_date.isoformat(),
            "doc_type": model.doc_type,
        },
        status_code=st.HTTP_201_CREATED,
    )


@router.delete("/computers/{computer_id}")
async def delete_computer(
    computer_id: int,
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    await controller.delete_computer(session, token, computer_id)
    return Response(status_code=st.HTTP_204_NO_CONTENT)


@router.post("/software")
async def create_software(
    sw_type_id: int,
    code: str,
    name: str,
    short_name: str | None,
    manufacturer: str,
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    model = await controller.create_software(
        session, token, sw_type_id, code, name, short_name, manufacturer
    )
    return JSONResponse(
        content={
            "software_id": model.software_id,
            "sw_type_id": model.sw_type_id,
            "sw_type_name": model.sw_type.name,
            "code": model.code,
            "name": model.name,
            "short_name": model.short_name,
            "manufacturer": model.manufacturer,
        },
        status_code=st.HTTP_201_CREATED,
    )


@router.post("/licenses")
async def create_license(
    software_id: int,
    vendor_id: int,
    start_date: datetime,
    end_date: datetime,
    price_per_unit: float,
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    model = await controller.create_license(
        session, token, software_id, vendor_id, start_date, end_date, price_per_unit
    )
    return JSONResponse(
        content={
            "license_id": model.license_id,
            "software_id": model.software_id,
            "software_name": model.software.name,
            "vendor_id": model.vendor_id,
            "vendor_name": model.vendor.name,
            "start_date": model.start_date.isoformat(),
            "end_date": model.end_date.isoformat(),
            "price_per_unit": model.price_per_unit,
        },
        status_code=st.HTTP_201_CREATED,
    )


@router.post("/installations")
async def create_installation(
    license_id: int,
    computer_id: int,
    install_date: datetime,
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    model = await controller.create_installation(
        session, token, license_id, computer_id, install_date
    )
    return JSONResponse(
        content={
            "installation_id": model.installation_id,
            "license_id": model.license_id,
            "computer_id": model.computer_id,
            "install_date": model.install_date.isoformat(),
            "license": {
                "license_id": model.license.license_id,
                "software_id": model.license.software_id,
                "software_name": model.license.software.name,
                "vendor_id": model.license.vendor_id,
                "vendor_name": model.license.vendor.name,
                "start_date": model.license.start_date.isoformat(),
                "end_date": model.license.end_date.isoformat(),
                "price_per_unit": model.license.price_per_unit,
            }
            if model.license
            else None,
            "computer": {
                "computer_id": model.computer_id,
                "inventory_number": model.computer.inventory_number,
                "computer_type": model.computer.computer_type.value,
                "purchase_date": model.computer.purchase_date.isoformat(),
                "status": model.computer.status,
            }
            if model.computer
            else None,
        },
        status_code=st.HTTP_201_CREATED,
    )


@router.get("/computers/installedSoftware/{computer_id}")
async def get_computer_installed_software(
    computer_id: int,
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    models = await controller.get_computer_software(session, token, computer_id)
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


@router.post("/vendors")
async def create_vendor(
    name: str,
    address: str,
    phone: str,
    website: str | None = None,
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    model = await controller.create_vendor(session, token, name, address, phone, website)
    return JSONResponse(
        content={
            "vendor_id": model.vendor_id,
            "name": model.name,
            "address": model.address,
            "phone": model.phone,
            "website": model.website,
        },
        status_code=st.HTTP_201_CREATED,
    )


@router.get("/reports/installedSoftware")
async def generate_report_with_installed_software(
    date: datetime,
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    data = await controller.gen_installed_sw_report(session, token, date)
    return JSONResponse(content=data, status_code=st.HTTP_200_OK)


@router.get("/reports/countSoftwareLicenses")
async def generate_report_with_counted_software_licenses(
    date: datetime,
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    data = await controller.gen_counted_sw_licenses_report(session, token, date)
    return JSONResponse(content=data, status_code=st.HTTP_200_OK)


@router.get("/reports/countDepartmentsComputers")
async def generate_report_with_counted_department_computers(
    date: datetime,
    controller: ManagerController = Depends(get_manager_controller),
    session: AsyncSession = Depends(get_rbac_session),
    token: dict = Depends(read_token),
) -> Response:
    data = await controller.gen_counted_depts_comps_report(session, token, date)
    return JSONResponse(content=data, status_code=st.HTTP_200_OK)
