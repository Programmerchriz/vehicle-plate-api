from fastapi import APIRouter, Depends

from app.dependencies.auth import require_roles
from app.models.enums import UserRole

router = APIRouter(
  prefix="/test",
  tags=["Testing"],
)


@router.get("/admin")
def admin_only(
  _ = Depends(
    require_roles(UserRole.ADMIN),
  ),
):
  return {
    "message": "Welcome Admin!"
  }


@router.get("/officer")
def officer_only(
  _ = Depends(
    require_roles(
      UserRole.ADMIN,
      UserRole.OFFICER,
    ),
  ),
):
  return {
    "message": "Welcome Officer!"
  }