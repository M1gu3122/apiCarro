from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    rutas_alertas,
    rutas_asociaciones_seguimiento,
    rutas_camaras,
    rutas_eventos_vehiculo,
    rutas_modulo_x_rol,
    rutas_modulo,
    rutas_ocupacion_zona,
    rutas_roles,
    rutas_seguimientos,
    rutas_tipos_vehiculo,
    rutas_usuarios,
    rutas_vehiculos,
    rutas_visitas,
    rutas_zonas,
)
from app.api.rutas_auth import router as auth_router  # Importar el router en sí

app = FastAPI(
    title="API de Monitoreo y Control Vehicular",
    description="Sistema completo para control de ingreso, salida y seguimiento de vehículos en concesionaria",
    version="1.0.0",
)

# Configurar CORS para permitir comunicaciones con frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, reemplazar con dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir todos los routers de la API
app.include_router(rutas_alertas.router)
app.include_router(rutas_asociaciones_seguimiento.router)
app.include_router(rutas_camaras.router)
app.include_router(rutas_eventos_vehiculo.router)
app.include_router(rutas_modulo_x_rol.router)
app.include_router(rutas_modulo.router)
app.include_router(rutas_ocupacion_zona.router)
app.include_router(rutas_roles.router)
app.include_router(rutas_seguimientos.router)
app.include_router(rutas_tipos_vehiculo.router)
app.include_router(rutas_usuarios.router)
app.include_router(rutas_vehiculos.router)
app.include_router(rutas_visitas.router)
app.include_router(rutas_zonas.router)
app.include_router(auth_router) 