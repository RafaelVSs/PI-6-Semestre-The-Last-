from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.maintenance_repository import MaintenanceRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.models.maintenance import Maintenance
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate
from app.schemas.enums import MaintenanceStatus
from app.common.exceptions.validation_exceptions import ValidationError
from app.common.exceptions.veiculo_exceptions import VeiculoNotFoundError

# Pub/Sub
from app.integrations.pubsub.client import get_pubsub_client

logger = logging.getLogger(__name__)


class MaintenanceService:
    def __init__(self, db: AsyncSession):
        self.repo = MaintenanceRepository(db)
        self.vehicle_repo = VehicleRepository(db)
        try:
            self.pubsub_client = get_pubsub_client()
            logger.info("✅ PubSubClient inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao obter PubSubClient: {e}", exc_info=True)
            self.pubsub_client = None
    
    async def create_maintenance(self, maintenance_data: MaintenanceCreate) -> Dict[str, Any]:
        """Publica solicitação de manutenção no Pub/Sub para processamento assíncrono"""
        # Validar se o veículo existe
        try:
            vehicle = await self.vehicle_repo.get_by_placa(maintenance_data.placa)
        except:
            raise VeiculoNotFoundError.by_placa(maintenance_data.placa)
        
        # Validar KM atual
        if maintenance_data.km_atual < 0:
            raise ValidationError.invalid_field("km_atual", "Quilometragem não pode ser negativa")
        
        # Validar que pelo menos um item de manutenção foi selecionado
        items = [
            maintenance_data.oleo,
            maintenance_data.filtro_oleo,
            maintenance_data.filtro_combustivel,
            maintenance_data.filtro_ar,
            maintenance_data.engraxamento
        ]
        if not any(items):
            raise ValidationError.invalid_field(
                "manutencoes",
                "Pelo menos um item de manutenção deve ser selecionado"
            )

        logger.info("📢 Publicando solicitação de manutenção no Pub/Sub...")
        
        if self.pubsub_client is None:
            logger.error("⚠️ PubSubClient não está disponível")
            raise ValidationError.invalid_field("pubsub", "Sistema de mensageria indisponível")
        
        try:
            # Gerar ID temporário para tracking
            temp_id = str(uuid4())
            
            logger.info(f"🚀 Publicando manutenção [ID Temp: {temp_id}] no Pub/Sub...")

            payload = {
                "temp_id": temp_id,
                "placa": maintenance_data.placa,
                "km_atual": maintenance_data.km_atual,
                "status": "pendente",
                "manutencoes": {
                    "oleo": maintenance_data.oleo,
                    "filtro_oleo": maintenance_data.filtro_oleo,
                    "filtro_combustivel": maintenance_data.filtro_combustivel,
                    "filtro_ar": maintenance_data.filtro_ar,
                    "engraxamento": maintenance_data.engraxamento
                }
            }
            
            logger.info(f"📦 Payload preparado: {payload}")

            message_id = await self.pubsub_client.publish_message(
                data=payload,
                event_type="maintenance.created",
                placa=maintenance_data.placa
            )
            
            logger.info(f"✅ Mensagem publicada com sucesso! Message ID: {message_id}")

            return {
                "message": "Solicitação de manutenção enviada para processamento",
                "message_id": message_id,
                "temp_id": temp_id,
                "status": "queued"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao publicar manutenção no Pub/Sub: {type(e).__name__}: {e}", exc_info=True)
            raise ValidationError.invalid_field("pubsub", f"Falha ao enviar mensagem: {str(e)}")

    async def get_maintenance_by_id(self, maintenance_id: UUID) -> Maintenance:
        """Busca uma manutenção pelo ID"""
        return await self.repo.get_by_id(maintenance_id)

    async def get_maintenances(
        self,
        skip: int = 0, 
        limit: int = 100,
        placa: Optional[str] = None,
        status: Optional[MaintenanceStatus] = None
    ) -> List[Maintenance]:
        """Lista manutenções com filtros e paginação"""
        return await self.repo.get_all(
            skip=skip,
            limit=limit,
            placa=placa,
            status=status
        )

    async def count_maintenances(
        self,
        placa: Optional[str] = None,
        status: Optional[MaintenanceStatus] = None
    ) -> int:
        """Conta o número total de manutenções"""
        return await self.repo.count(
            placa=placa,
            status=status
        )

    async def update_maintenance(
        self, 
        maintenance_id: UUID, 
        maintenance_data: MaintenanceUpdate
    ) -> Maintenance:
        """Atualiza uma manutenção existente com validações"""
        # Validar KM se fornecido
        if maintenance_data.km_atual is not None and maintenance_data.km_atual < 0:
            raise ValidationError.invalid_field("km_atual", "Quilometragem não pode ser negativa")
        
        return await self.repo.update(maintenance_id, maintenance_data)

    async def delete_maintenance(self, maintenance_id: UUID) -> bool:
        """Remove uma manutenção"""
        return await self.repo.delete(maintenance_id)

    async def update_status(
        self, 
        maintenance_id: UUID, 
        status: MaintenanceStatus
    ) -> Maintenance:
        """Atualiza o status de uma manutenção"""
        return await self.repo.update_status(maintenance_id, status)

    async def get_maintenances_by_placa(self, placa: str) -> List[Maintenance]:
        """Busca manutenções por placa"""
        # Validar se veículo existe
        try:
            await self.vehicle_repo.get_by_placa(placa)
        except:
            raise VeiculoNotFoundError.by_placa(placa)
        
        return await self.repo.get_by_placa(placa)

    async def get_maintenances_by_status(self, status: MaintenanceStatus) -> List[Maintenance]:
        """Busca manutenções por status"""
        return await self.repo.get_by_status(status)
    
    async def concluir_manutencao(self, maintenance_id: UUID) -> Maintenance:
        """Marca manutenção como concluída"""
        return await self.update_status(maintenance_id, MaintenanceStatus.CONCLUIDA)
    
    async def cancelar_manutencao(self, maintenance_id: UUID) -> Maintenance:
        """Marca manutenção como cancelada"""
        return await self.update_status(maintenance_id, MaintenanceStatus.CANCELADA)
