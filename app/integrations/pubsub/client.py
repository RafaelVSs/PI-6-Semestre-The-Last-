"""
Cliente Google Cloud Pub/Sub para publicação de mensagens
"""
import json
import logging
import os
import tempfile
from typing import Any, Dict, Optional
from google.cloud import pubsub_v1
from google.oauth2 import service_account
from google.api_core import retry

from app.core.config import settings

logger = logging.getLogger(__name__)


class PubSubClient:
    """Cliente para publicação de mensagens no Google Cloud Pub/Sub"""
    
    def __init__(self):
        """Inicializa o publisher client"""
        logger.info("🔧 Inicializando PubSubClient...")
        
        credentials = self._get_credentials()
        
        if credentials:
            logger.info("📝 Criando PublisherClient com credenciais customizadas")
            self.publisher = pubsub_v1.PublisherClient(credentials=credentials)
        else:
            # Fallback para credenciais padrão do ambiente
            logger.info("📝 Criando PublisherClient com credenciais padrão do ambiente")
            self.publisher = pubsub_v1.PublisherClient()
        
        self.topic_path = f"projects/{settings.GCP_PROJECT_ID}/topics/{settings.PUBSUB_TOPIC}"
        logger.info(f"✅ PubSubClient inicializado para tópico: {self.topic_path}")
    
    def _get_credentials(self) -> Optional[service_account.Credentials]:
        """
        Obtém credenciais do Google Cloud de diferentes fontes (prioridade):
        1. Arquivo via caminho em variável de ambiente (GOOGLE_APPLICATION_CREDENTIALS)
        2. Arquivo padrão no projeto (dev only)
        """
        # Opção 1: Arquivo via variável de ambiente
        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            if os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
                logger.info(f"Usando credenciais Pub/Sub do arquivo: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
                return None  # Deixa o Google Auth usar o arquivo
            else:
                logger.warning(f"Arquivo de credenciais não encontrado: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
        
        # Opção 2: Arquivo padrão (apenas desenvolvimento)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        default_credentials_path = os.path.join(project_root, "app", "integrations", "pubsub", "credential", "serjava-demo-key.json")
        
        if os.path.exists(default_credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = default_credentials_path
            logger.info(f"Usando credenciais Pub/Sub padrão: {default_credentials_path}")
            return None  # Deixa o Google Auth usar o arquivo
        
        logger.warning("Nenhuma credencial Pub/Sub configurada. Tentando usar credenciais padrão do ambiente.")
        return None
    
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
