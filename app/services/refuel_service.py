from typing import Optional, List
from datetime import date
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.refuel_repository import RefuelRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.models.refuel import Refuel
from app.schemas.refuel import RefuelCreate, RefuelUpdate
from app.common.exceptions.validation_exceptions import ValidationError
from app.common.exceptions.veiculo_exceptions import VeiculoNotFoundError


class RefuelService:
    """Service para lógica de negócio de abastecimento"""
    
    def __init__(self, db: AsyncSession):
        self.repository = RefuelRepository(db)
        self.vehicle_repository = VehicleRepository(db)
    
    async def create_refuel(self, refuel_data: RefuelCreate) -> Refuel:
        """Criar novo abastecimento"""
        # Validações de negócio
        if refuel_data.litros <= 0:
            raise ValidationError("Quantidade de litros deve ser maior que zero")
        
        if refuel_data.valor_litro <= 0:
            raise ValidationError("Valor por litro deve ser maior que zero")
        
        if refuel_data.km <= 0:
            raise ValidationError("Quilometragem deve ser maior que zero")
        
        # Validar média apenas se tanque cheio
        if refuel_data.media is not None and not refuel_data.tanque_cheio:
            raise ValidationError("Média só pode ser calculada quando o tanque está cheio")
        
        # Buscar veículo pela placa
        try:
            vehicle = await self.vehicle_repository.get_by_placa(refuel_data.placa)
        except VeiculoNotFoundError:
            raise ValidationError(f"Veículo com placa {refuel_data.placa} não encontrado")
        
        # Validar que KM do abastecimento >= KM atual do veículo
        if refuel_data.km < vehicle.km_atual:
            raise ValidationError(
                f"KM do abastecimento ({refuel_data.km}) não pode ser menor que o KM atual do veículo ({vehicle.km_atual})"
            )
        
        # Validar que não pode abastecer mais que a capacidade do tanque
        if refuel_data.litros > vehicle.capacidade_tanque:
            raise ValidationError(
                f"Quantidade de litros ({refuel_data.litros}L) excede a capacidade do tanque ({vehicle.capacidade_tanque}L)"
            )
        
        # Criar o abastecimento
        refuel = await self.repository.create(refuel_data)
        
        # Atualizar informações do veículo
        vehicle.km_atual = refuel_data.km
        vehicle.km_ultimo_abastecimento = refuel_data.km
        
        # Verificar se precisa atualizar manutenção vencida
        if vehicle.km_prox_manutencao is not None and vehicle.km_atual >= vehicle.km_prox_manutencao:
            vehicle.manutencao_vencida = True
        
        await self.vehicle_repository.db.commit()
        
        return refuel
    
    async def get_refuel_by_id(self, refuel_id: int) -> Refuel:
        """Buscar abastecimento por ID"""
        return await self.repository.get_by_id(refuel_id)
    
    async def get_refuels(
        self,
        skip: int = 0,
        limit: int = 100,
        placa: Optional[str] = None,
        id_usuario: Optional[UUID] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> List[Refuel]:
        """Listar abastecimentos com filtros"""
        return await self.repository.get_all(
            skip=skip,
            limit=limit,
            placa=placa,
            id_usuario=str(id_usuario) if id_usuario else None,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
    
    async def count_refuels(
        self,
        placa: Optional[str] = None,
        id_usuario: Optional[UUID] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None
    ) -> int:
        """Contar abastecimentos com filtros"""
        return await self.repository.count(
            placa=placa,
            id_usuario=str(id_usuario) if id_usuario else None,
            data_inicio=data_inicio,
            data_fim=data_fim
        )
    
    async def update_refuel(
        self,
        refuel_id: int,
        refuel_data: RefuelUpdate
    ) -> Refuel:
        """Atualizar abastecimento"""
        # Validações se campos forem fornecidos
        if refuel_data.litros is not None and refuel_data.litros <= 0:
            raise ValidationError("Quantidade de litros deve ser maior que zero")
        
        if refuel_data.valor_litro is not None and refuel_data.valor_litro <= 0:
            raise ValidationError("Valor por litro deve ser maior que zero")
        
        if refuel_data.km is not None and refuel_data.km <= 0:
            raise ValidationError("Quilometragem deve ser maior que zero")
        
        return await self.repository.update(refuel_id, refuel_data)
    
    async def delete_refuel(self, refuel_id: int) -> None:
        """Deletar abastecimento"""
        await self.repository.delete(refuel_id)
