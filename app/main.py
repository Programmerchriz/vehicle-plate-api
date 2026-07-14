from fastapi import FastAPI

from app.config.settings import settings
from app.routers.auth import router as auth_router
from app.routers.test import router as test_router

app = FastAPI(
  title=settings.APP_NAME,
  version=settings.APP_VERSION,
)

app.include_router(auth_router)
app.include_router(test_router)


@app.get("/")
def root():
  return {
    "message": "Vehicle Plate Recognition API",
    "database": "connected",
  }