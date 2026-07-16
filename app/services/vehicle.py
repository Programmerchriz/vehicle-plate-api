from sqlalchemy import (
  asc,
  desc,
  Select,
	select,
)
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import (
  VehicleCreate,
	VehicleUpdate,
)
from app.models.enums import (
  VehicleStatus,
  VehicleType,
	)

from app.exceptions.vehicle import (
	VehicleAlreadyExistsError,
	VehicleNotFoundError,
)

SORT_COLUMNS = {
	"plate_number": Vehicle.plate_number,
	"owner_name": Vehicle.owner_name,
	"registration_date": Vehicle.registration_date,
	"created_at": Vehicle.created_at,
}

class VehicleService:
	def __init__(self, db: Session):
		self.db = db

	def create_vehicle(
		self,
		data: VehicleCreate,
		current_user: User,
	) -> Vehicle:
		plate_number = data.plate_number.strip().upper()

		existing_vehicle = self.get_vehicle_by_plate(plate_number)

		if existing_vehicle:
			raise VehicleAlreadyExistsError("Vehicle with this plate number already exists.")

		vehicle = Vehicle(
			plate_number=plate_number,
			owner_name=data.owner_name.strip(),
			owner_phone=data.owner_phone.strip(),
			owner_address=data.owner_address.strip(),
			vehicle_make=data.vehicle_make.strip(),
			vehicle_model=data.vehicle_model.strip(),
			vehicle_color=data.vehicle_color.strip(),
			vehicle_type=data.vehicle_type,
			manufacture_year=data.manufacture_year,
			registration_date=data.registration_date,
			expiry_date=data.expiry_date,
			status=data.status,
			created_by_id=current_user.id,
		)

		self.db.add(vehicle)
		self.db.commit()
		self.db.refresh(vehicle)

		return vehicle

	def update_vehicle(
		self,
		vehicle: Vehicle,
		data: VehicleUpdate,
	) -> Vehicle:
		update_data = data.model_dump(exclude_unset=True)

		if "plate_number" in update_data:
			update_data["plate_number"] = (
				update_data["plate_number"]
				.strip()
				.upper()
			)

			existing = self.get_vehicle_by_plate(update_data["plate_number"])

			if existing and existing.id != vehicle.id:
				raise VehicleAlreadyExistsError(
          "Vehicle with this plate number already exists."
        )

		for field, value in update_data.items():
			if isinstance(value, str):
				value = value.strip()

			setattr(vehicle, field, value)

		self.db.commit()
		self.db.refresh(vehicle)

		return vehicle

	def delete_vehicle(
		self,
		vehicle: Vehicle,
	) -> None:
		self.db.delete(vehicle)
		self.db.commit()

	def get_vehicle(
		self,
		vehicle_id: int,
	) -> Vehicle | None:
		statement = (
			select(Vehicle)
			.where(Vehicle.id == vehicle_id)
		)

		return self.db.scalar(statement)

	def get_vehicle_by_plate(
		self,
		plate_number: str,
	) -> Vehicle | None:
		statement = (
			select(Vehicle)
			.where(
				Vehicle.plate_number == plate_number.strip().upper()
			)
		)

		return self.db.scalar(statement)

	def search(
    self,
    *,
    search: str | None = None,
    status: VehicleStatus | None = None,
    vehicle_type: VehicleType | None = None,
    sort: str | None = None,
  ) -> Select[tuple[Vehicle]]:
		statement = select(Vehicle)

		if search:
			search = f"%{search.strip()}%"

			statement = statement.where(
				Vehicle.plate_number.ilike(search)
				| Vehicle.owner_name.ilike(search)
				| Vehicle.vehicle_make.ilike(search)
				| Vehicle.vehicle_model.ilike(search)
			)

		if status:
			statement = statement.where(
				Vehicle.status == status
			)

		if vehicle_type:
			statement = statement.where(
				Vehicle.vehicle_type == vehicle_type
			)
		
		if sort:
			descending = sort.startswith("-")
			column_name = sort.removeprefix("-")
			column = SORT_COLUMNS.get(column_name)
			
			if column:
				statement = statement.order_by(
          desc(column) if descending else asc(column)
        )

		return statement