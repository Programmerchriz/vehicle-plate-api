from enum import Enum


class UserRole(str, Enum):
  ADMIN = "admin"
  OFFICER = "officer"


class VehicleStatus(str, Enum):
  ACTIVE = "ACTIVE"
  INACTIVE = "INACTIVE"
  EXPIRED = "EXPIRED"
  SUSPENDED = "SUSPENDED"

class VehicleType(str, Enum):
  CAR = "CAR"
  SUV = "SUV"
  TRUCK = "TRUCK"
  BUS = "BUS"
  MOTORCYCLE = "MOTORCYCLE"
  OTHER = "OTHER"