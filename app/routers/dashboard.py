from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.dependencies.auth import require_roles
from app.models.enums import UserRole
from app.schemas.dashboard import DashboardStatsResponse
from app.services.dashboard import DashboardService


router = APIRouter(
	prefix="/dashboard",
	tags=["Dashboard"],
	dependencies=[
		Depends(
			require_roles(
				UserRole.ADMIN,
				UserRole.OFFICER,
			)
		)
	],
)


@router.get(
	"/stats",
	response_model=DashboardStatsResponse,
)
def get_dashboard_stats(
	db: Session = Depends(get_db),
):
	service = DashboardService(db)

	return service.get_dashboard_stats()