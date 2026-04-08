import json

from cryptography.fernet import Fernet

from app.core.config import settings


fernet = Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt_note_payload(payload: dict[str, str]) -> bytes:
    serialized = json.dumps(payload).encode()
    return fernet.encrypt(serialized)


def decrypt_note_payload(encrypted: bytes) -> dict[str, str]:
    decrypted = fernet.decrypt(encrypted)
    return json.loads(decrypted.decode())
