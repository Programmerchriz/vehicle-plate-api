from pydantic import BaseModel

from app.schemas.vehicle import VehicleResponse


class DashboardStatsResponse(BaseModel):
	total_vehicles: int
	active_vehicles: int
	inactive_vehicles: int
	expired_vehicles: int
	suspended_vehicles: int

	recent_registrations: list[VehicleResponse]

	model_config = {
		"from_attributes": True,
	}