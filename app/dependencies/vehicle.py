from fastapi import (
  Depends,
	HTTPException,
  status,
)

from sqlalchemy.orm import Session

from app.config.database import get_db
from app.exceptions.vehicle import VehicleNotFoundError
from app.models.vehicle import Vehicle
from app.services.vehicle import VehicleService


def get_vehicle(
	vehicle_id: int,
	db: Session = Depends(get_db),
) -> Vehicle:
	service = VehicleService(db)

	vehicle = service.get_vehicle(vehicle_id)

	if vehicle is None:
		raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Vehicle not found.",
    )

	return vehicle