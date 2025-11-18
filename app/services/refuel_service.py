from typing import Optional, List
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.refuel_repository import RefuelRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.models.refuel import Refuel
from app.schemas.refuel import RefuelCreate, RefuelUpdate
from app.common.exceptions.validation_exceptions import ValidationError
from app.common.exceptions.veiculo_exceptions import VeiculoNotFoundError

# 🔥 IA
from app.services.ai_training_service import train_online_append
from app.services.ai_service import detect_anomaly
from app.services.alert_service import AlertService


class RefuelService:
    """Service para lógica de negócio de abastecimento"""
    
    def __init__(self, db: AsyncSession):
        self.repository = RefuelRepository(db)
        self.vehicle_repository = VehicleRepository(db)
        self.alert_service = AlertService(db)

    async def create_refuel(self, refuel_data: RefuelCreate) -> Refuel:
        """Criar novo abastecimento"""

        # ---------- Validações ----------
        if refuel_data.litros <= 0:
            raise ValidationError("Quantidade de litros deve ser maior que zero")
        
        if refuel_data.valor_litro <= 0:
            raise ValidationError("Valor por litro deve ser maior que zero")
        
        if refuel_data.km <= 0:
            raise ValidationError("Quilometragem deve ser maior que zero")

        try:
            vehicle = await self.vehicle_repository.get_by_placa(refuel_data.placa)
        except VeiculoNotFoundError:
            raise ValidationError(f"Veículo com placa {refuel_data.placa} não encontrado")

        if refuel_data.km < vehicle.km_atual:
            raise ValidationError(
                f"KM do abastecimento ({refuel_data.km}) não pode ser menor que o KM atual do veículo ({vehicle.km_atual})"
            )

        if refuel_data.litros > vehicle.capacidade_tanque:
            raise ValidationError(
                f"Quantidade de litros ({refuel_data.litros}L) excede a capacidade do tanque ({vehicle.capacidade_tanque}L)"
            )
        
        # ---------- Cálculo de média ----------
        media_calculada: Optional[Decimal] = None
        
        if refuel_data.tanque_cheio:
            ultimo_tanque_cheio = await self.repository.get_last_refuel_by_placa(
                placa=refuel_data.placa,
                tanque_cheio=True,
                before_km=refuel_data.km
            )
            
            if ultimo_tanque_cheio:
                distancia = refuel_data.km - ultimo_tanque_cheio.km
                
                if distancia > 0:
                    litros_intermediarios = await self.repository.get_sum_litros_between_km(
                        placa=refuel_data.placa,
                        km_start=ultimo_tanque_cheio.km,
                        km_end=refuel_data.km
                    )
                    
                    litros_totais = litros_intermediarios + refuel_data.litros
                    
                    if litros_totais > 0:
                        media_calculada = Decimal(distancia) / Decimal(litros_totais)
                        media_calculada = media_calculada.quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )

        # Média só existe se tanque_cheio=True
        refuel_data.media = media_calculada if refuel_data.tanque_cheio else None

        # ---------- IA: adicionar ao histórico + treinar ----------
        if media_calculada is not None:
            train_online_append(refuel_data.placa, float(media_calculada))

        # ---------- Criar abastecimento no banco ----------
        refuel = await self.repository.create(refuel_data)

        # IA: atualizar dados do veículo
        if media_calculada is not None:
            vehicle.modelo_ia_treinado = True
            vehicle.data_ultimo_treinamento = datetime.utcnow()

        # ------------ IA: detectar ANOMALIA ------------
        if media_calculada is not None:
            result = detect_anomaly(refuel_data.placa, float(media_calculada))

            if result["anomalia"] is True:
                # determinar severidade
                limite_inf = result["limite_inferior"]
                m = float(media_calculada)

                if m < limite_inf * 0.8:
                    severity = "HIGH"
                else:
                    severity = "MEDIUM"

                await self.alert_service.create_alert(
                    id_veiculo=vehicle.id,
                    id_abastecimento=refuel.id,
                    severity=severity,
                    message=f"Consumo anormal detectado! Média {media_calculada} km/L"
                )

        # ---------- Atualizar veículo ----------
        vehicle.km_atual = refuel_data.km
        vehicle.km_ultimo_abastecimento = refuel_data.km
        
        if vehicle.km_prox_manutencao is not None and vehicle.km_atual >= vehicle.km_prox_manutencao:
            vehicle.manutencao_vencida = True
        
        await self.vehicle_repository.db.commit()
        
        return refuel
    
    async def get_refuel_by_id(self, refuel_id: int) -> Refuel:
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
        if refuel_data.litros is not None and refuel_data.litros <= 0:
            raise ValidationError("Quantidade de litros deve ser maior que zero")
        
        if refuel_data.valor_litro is not None and refuel_data.valor_litro <= 0:
            raise ValidationError("Valor por litro deve ser maior que zero")
        
        if refuel_data.km is not None and refuel_data.km <= 0:
            raise ValidationError("Quilometragem deve ser maior que zero")
        
        return await self.repository.update(refuel_id, refuel_data)
    
    async def delete_refuel(self, refuel_id: int) -> None:
        await self.repository.delete(refuel_id)
