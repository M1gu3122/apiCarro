import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from passlib.context import CryptContext

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Directorio base del proyecto (subir dos niveles desde app/core)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

# Cargar las variables del archivo .env si existe
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY no configurada en el archivo .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Configuración de bcrypt para hashing de contraseñas
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Funciones de hashing de contraseñas
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que una contraseña coincida con el hash guardado"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera un hash seguro de la contraseña"""
    return pwd_context.hash(password)