import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Tuple, Optional
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from .config import settings


def hash_password(password: str) -> str:
    """
    Gera hash seguro da senha usando bcrypt
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def generate_salt() -> str:
    """
    Gera um salt aleatório para operações criptográficas
    """
    return secrets.token_hex(32)


def generate_secure_token(length: int = 32) -> str:
    """
    Gera um token seguro para reset de senha, confirmação de email, etc.
    """
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """
    Gera hash SHA-256 de um token para armazenamento seguro
    """
    return hashlib.sha256(token.encode()).hexdigest()


def generate_password_reset_token() -> Tuple[str, str]:
    """
    Gera token para reset de senha e seu hash
    """
    token = generate_secure_token(32)
    token_hash = hash_token(token)
    return token, token_hash


def verify_token(plain_token: str, hashed_token: str) -> bool:
    """
    Verifica se um token corresponde ao seu hash
    """
    return hash_token(plain_token) == hashed_token


class SecurityConfig:
    """Configurações de segurança do sistema"""
    
    # Configurações de senha
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = False
    
    # Configurações de token
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 1
    EMAIL_CONFIRMATION_TOKEN_EXPIRE_HOURS = 24
    
    # Configurações de tentativas de login
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_DURATION_MINUTES = 15


def validate_password_strength(password: str) -> Tuple[bool, list[str]]:
    """
    Valida a força de uma senha baseada nas configurações de segurança
    """
    errors = []
    
    # Verificar comprimento
    if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
        errors.append(f"Senha deve ter pelo menos {SecurityConfig.MIN_PASSWORD_LENGTH} caracteres")
    
    if len(password) > SecurityConfig.MAX_PASSWORD_LENGTH:
        errors.append(f"Senha deve ter no máximo {SecurityConfig.MAX_PASSWORD_LENGTH} caracteres")
    
    # Verificar maiúsculas
    if SecurityConfig.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        errors.append("Senha deve conter pelo menos uma letra maiúscula")
    
    # Verificar minúsculas
    if SecurityConfig.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        errors.append("Senha deve conter pelo menos uma letra minúscula")
    
    # Verificar dígitos
    if SecurityConfig.REQUIRE_DIGITS and not any(c.isdigit() for c in password):
        errors.append("Senha deve conter pelo menos um número")
    
    # Verificar caracteres especiais
    if SecurityConfig.REQUIRE_SPECIAL_CHARS:
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            errors.append("Senha deve conter pelo menos um caractere especial")
    
    return len(errors) == 0, errors


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT de acesso
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica e valida um token JWT
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
