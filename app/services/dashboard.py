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
		
		status_counts = {
      status: count
      for status, count in self.db.execute(
        select(
          Vehicle.status,
          func.count(Vehicle.id),
        )
        .group_by(Vehicle.status)
      ).all()
    }

		recent_registrations = self.db.scalars(
			select(Vehicle)
			.order_by(Vehicle.created_at.desc())
			.limit(5)
		).all()

		return {
      "total_vehicles": total_vehicles,
      "active_vehicles": status_counts.get(
        VehicleStatus.ACTIVE,
        0,
      ),
      "inactive_vehicles": status_counts.get(
        VehicleStatus.INACTIVE,
        0,
      ),
      "expired_vehicles": status_counts.get(
        VehicleStatus.EXPIRED,
        0,
      ),
      "suspended_vehicles": status_counts.get(
        VehicleStatus.SUSPENDED,
        0,
      ),
      "recent_registrations": recent_registrations,
    }