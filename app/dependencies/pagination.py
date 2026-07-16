from fastapi import Depends, Query


class PaginationParams:
	def __init__(
		self,
		page: int = Query(1, ge=1),
		page_size: int = Query(10, ge=1, le=100),
	):
		self.page = page
		self.page_size = page_size

	@property
	def offset(self) -> int:
		return (self.page - 1) * self.page_size


PaginationDep = Depends(PaginationParams)