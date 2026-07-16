from math import ceil

from fastapi import (
	APIRouter,
	Depends,
	HTTPException,
	Query,
	status,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies.auth import (
	get_current_user,
	require_roles,
)
from app.dependencies.pagination import PaginationParams
from app.dependencies.vehicle import get_vehicle
from app.exceptions.vehicle import (
	VehicleAlreadyExistsError,
)
from app.models.enums import (
	UserRole,
	VehicleStatus,
	VehicleType,
)
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import (
	VehicleCreate,
	VehicleListResponse,
	VehicleResponse,
	VehicleUpdate,
)
from app.services.vehicle import VehicleService


router = APIRouter(
	prefix="/vehicles",
	tags=["Vehicles"],
	dependencies=[
		Depends(get_current_user),
	],
)


@router.get(
	"/",
	response_model=VehicleListResponse,
)
def get_vehicles(
	pagination: PaginationParams = Depends(),
	search: str | None = Query(None),
	status_filter: VehicleStatus | None = Query(
		None,
		alias="status",
	),
	vehicle_type: VehicleType | None = Query(None),
	sort: str | None = Query(None),
	db: Session = Depends(get_db),
):
	service = VehicleService(db)

	statement = service.search(
		search=search,
		status=status_filter,
		vehicle_type=vehicle_type,
		sort=sort,
	)

	total = db.scalar(
		select(func.count()).select_from(
			statement.subquery()
		)
	) or 0

	items = db.scalars(
		statement
		.offset(pagination.offset)
		.limit(pagination.page_size)
	).all()

	return VehicleListResponse(
		items=items,
		total=total,
		page=pagination.page,
		page_size=pagination.page_size,
		total_pages=ceil(total / pagination.page_size)
		if total
		else 0,
	)


@router.get(
	"/by-plate/{plate_number}",
	response_model=VehicleResponse,
)
def get_vehicle_by_plate(
	plate_number: str,
	db: Session = Depends(get_db),
):
	service = VehicleService(db)

	vehicle = service.get_vehicle_by_plate(
		plate_number,
	)

	if vehicle is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Vehicle not found.",
		)

	return vehicle


@router.get(
	"/{vehicle_id}",
	response_model=VehicleResponse,
)
def get_vehicle_by_id(
	vehicle: Vehicle = Depends(get_vehicle),
):
	return vehicle


@router.post(
	"/",
	response_model=VehicleResponse,
	status_code=status.HTTP_201_CREATED,
)
def create_vehicle(
	data: VehicleCreate,
	db: Session = Depends(get_db),
	current_user: User = Depends(
		require_roles(
			UserRole.ADMIN,
			UserRole.OFFICER,
		),
	),
):
	service = VehicleService(db)

	try:
		return service.create_vehicle(
			data,
			current_user,
		)

	except VehicleAlreadyExistsError as exc:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail=str(exc),
		)


@router.patch(
	"/{vehicle_id}",
	response_model=VehicleResponse,
)
def update_vehicle(
	data: VehicleUpdate,
	vehicle: Vehicle = Depends(get_vehicle),
	db: Session = Depends(get_db),
	_: User = Depends(
		require_roles(
			UserRole.ADMIN,
			UserRole.OFFICER,
		),
	),
):
	service = VehicleService(db)

	try:
		return service.update_vehicle(
			vehicle,
			data,
		)

	except VehicleAlreadyExistsError as exc:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail=str(exc),
		)


@router.delete(
	"/{vehicle_id}",
	status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vehicle(
	vehicle: Vehicle = Depends(get_vehicle),
	db: Session = Depends(get_db),
	_: User = Depends(
		require_roles(
			UserRole.ADMIN,
		),
	),
):
	service = VehicleService(db)

	service.delete_vehicle(vehicle)

