from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional



class AlertCreate(BaseModel):
    id_veiculo: UUID
    id_abastecimento: UUID
    severity: str
    message: str


class AlertResponse(AlertCreate):
    id: UUID
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertResolveUpdate(BaseModel):
    resolved: bool = True
