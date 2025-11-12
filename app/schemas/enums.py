from enum import Enum


class UserStatus(str, Enum):
    """Enum para status do usuário"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    PENDENTE = "pendente"


class UserType(str, Enum):
    """Enum para tipo do usuário"""
    ADM = "adm"
    MOTORISTA = "motorista"
    MECANICO = "mecanico"
    ESCRITORIO = "escritorio"
    
class TelephoneNumberStatus(str, Enum):
    """Enum para status do número de telefone"""
    ATIVO = "ativo"
    INATIVO = "inativo"


class VehicleType(str, Enum):
    """Enum para tipo de veículo"""
    CARRO = "carro"
    CAMINHAO = "caminhao"
    VAN = "van"


class MaintenanceStatus(str, Enum):
    """Enum para status da manutenção"""
    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"