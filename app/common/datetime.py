from datetime import datetime, timezone


def utcnow() -> datetime:
    now = datetime.now(timezone.utc)
    # Trunca os microssegundos mantendo somente milissegundos
    # O mongodb não armazena microssegundos
    return now.replace(microsecond=(now.microsecond // 1000) * 1000)
