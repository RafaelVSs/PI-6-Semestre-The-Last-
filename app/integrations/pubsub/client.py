"""
Cliente Google Cloud Pub/Sub para publicação de mensagens
"""
import json
import logging
import os
from typing import Any, Dict
from google.cloud import pubsub_v1
from google.api_core import retry

from app.core.config import settings

logger = logging.getLogger(__name__)


class PubSubClient:
    """Cliente para publicação de mensagens no Google Cloud Pub/Sub"""
    
    def __init__(self):
        """Inicializa o publisher client"""
        # Define o caminho das credenciais se fornecido
        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
        
        # Usa o caminho padrão se não estiver configurado
        default_credentials_path = "app/integrations/pubsub/credential/serjava-demo-key.json"
        if not settings.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(default_credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = default_credentials_path
        
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = f"projects/{settings.GCP_PROJECT_ID}/topics/{settings.PUBSUB_TOPIC}"
        logger.info(f"PubSubClient inicializado para tópico: {self.topic_path}")
    
    async def publish_message(self, data: Dict[str, Any], **attributes) -> str:
        """
        Publica uma mensagem no tópico Pub/Sub
        
        Args:
            data: Dicionário com os dados a serem publicados (será convertido para JSON)
            **attributes: Atributos adicionais da mensagem (metadata)
        
        Returns:
            message_id: ID da mensagem publicada
        """
        try:
            # Converter dados para JSON bytes
            message_json = json.dumps(data, default=str)
            message_bytes = message_json.encode('utf-8')
            
            # Publicar mensagem (com retry automático)
            future = self.publisher.publish(
                self.topic_path,
                message_bytes,
                **attributes
            )
            
            # Aguardar confirmação
            message_id = future.result(timeout=30)
            
            logger.info(f"Mensagem publicada com sucesso. ID: {message_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Erro ao publicar mensagem no Pub/Sub: {e}")
            raise
    
    def __del__(self):
        """Cleanup ao destruir o cliente"""
        try:
            # Aguardar publicações pendentes
            self.publisher.stop()
        except Exception:
            pass


# Singleton instance
_pubsub_client: PubSubClient = None


def get_pubsub_client() -> PubSubClient:
    """Retorna instância singleton do PubSubClient"""
    global _pubsub_client
    if _pubsub_client is None:
        _pubsub_client = PubSubClient()
    return _pubsub_client
