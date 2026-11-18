from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.security import MODULOS_POR_RECURSO, requerir_modulo

from app.api import (
    rutas_dashboard,
    rutas_reportes,
    rutas_monitoreo,
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
    rutas_zonas,
    rutas_usuarios,
    rutas_visitas,
    rutas_vehiculos,
    auth_routes
    
)

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
app.include_router(rutas_alertas.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["alertas"]))])
app.include_router(rutas_asociaciones_seguimiento.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["asociaciones_seguimiento"]))])
app.include_router(rutas_camaras.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["camaras"]))])
app.include_router(rutas_eventos_vehiculo.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["eventos_vehiculo"]))])
app.include_router(rutas_modulo_x_rol.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["modulo_x_rol"]))])
app.include_router(rutas_modulo.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["modulo"]))])
app.include_router(rutas_ocupacion_zona.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["ocupacion_zona"]))])
app.include_router(rutas_roles.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["roles"]))])
app.include_router(rutas_seguimientos.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["seguimientos"]))])
app.include_router(rutas_tipos_vehiculo.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["tipos_vehiculo"]))])
app.include_router(rutas_zonas.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["zonas"]))])
app.include_router(rutas_usuarios.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["usuarios"]))])
app.include_router(auth_routes.router)
app.include_router(rutas_visitas.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["visitas"]))])
app.include_router(rutas_vehiculos.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["vehiculos"]))])
app.include_router(rutas_dashboard.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["dashboard"]))])
app.include_router(rutas_reportes.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["reportes"]))])
app.include_router(rutas_monitoreo.router, dependencies=[Depends(requerir_modulo(MODULOS_POR_RECURSO["monitoreo"]))])
