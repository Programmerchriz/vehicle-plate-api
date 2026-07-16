class VehicleError(Exception):
	"""Base exception for all vehicle-related errors."""
	pass


class VehicleNotFoundError(VehicleError):
	"""Raised when a vehicle cannot be found."""
	pass


class VehicleAlreadyExistsError(VehicleError):
	"""Raised when attempting to register a duplicate plate number."""
	pass