from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import VehicleStatus
from app.models.vehicle import Vehicle


class DashboardService:
	def __init__(self, db: Session):
		self.db = db

	def get_dashboard_stats(self):
		total_vehicles = self.db.scalar(
			select(func.count(Vehicle.id))
		) or 0

		active_vehicles = self.db.scalar(
			select(func.count(Vehicle.id)).where(
				Vehicle.status == VehicleStatus.ACTIVE
			)
		) or 0

		inactive_vehicles = self.db.scalar(
			select(func.count(Vehicle.id)).where(
				Vehicle.status == VehicleStatus.INACTIVE
			)
		) or 0

		expired_vehicles = self.db.scalar(
			select(func.count(Vehicle.id)).where(
				Vehicle.status == VehicleStatus.EXPIRED
			)
		) or 0

		suspended_vehicles = self.db.scalar(
			select(func.count(Vehicle.id)).where(
				Vehicle.status == VehicleStatus.SUSPENDED
			)
		) or 0

		recent_registrations = self.db.scalars(
			select(Vehicle)
			.order_by(Vehicle.created_at.desc())
			.limit(5)
		).all()

		return {
			"total_vehicles": total_vehicles,
			"active_vehicles": active_vehicles,
			"inactive_vehicles": inactive_vehicles,
			"expired_vehicles": expired_vehicles,
			"suspended_vehicles": suspended_vehicles,
			"recent_registrations": recent_registrations,
		}