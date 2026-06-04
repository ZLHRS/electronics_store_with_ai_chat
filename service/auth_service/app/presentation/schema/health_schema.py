from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    success: bool = Field(default=True)
    body: str = Field(default="Service is working")
