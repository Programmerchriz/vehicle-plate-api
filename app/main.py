from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.routers.auth import router as auth_router
from app.routers.vehicle import router as vehicle_router
from app.routers.dashboard import router as dashboard_router
from app.routers.recognition import router as recognition_router
# from app.routers.test import router as test_router

from app.services.detector import PlateDetectionService
from app.services.ocr import OCRService

@asynccontextmanager
async def lifespan(app: FastAPI):
  # Warm up AI models
  PlateDetectionService()
  OCRService()

  yield

app = FastAPI(
  title=settings.APP_NAME,
  version=settings.APP_VERSION,
  lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://vehicle-license-plate.vercel.app",
        # "http://127.0.0.1:5173",
        # "http://10.129.181.181:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(vehicle_router)
app.include_router(dashboard_router)
app.include_router(recognition_router)
# app.include_router(test_router)


@app.get("/")
def root():
  return {
    "message": "Vehicle Plate Recognition API",
    # "database": "connected",
  }