"""Aplicación FastAPI y rutas REST de AQUASAVE."""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Dispositivo, Medicion
from .schemas import DispositivoCrear, DispositivoSalida, MedicionCrear, MedicionSalida, NivelAgua
from .telegram_service import enviar_alerta_alto

ROOT_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="AQUASAVE API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.post("/api/dispositivos", response_model=DispositivoSalida, status_code=201)
def crear_dispositivo(datos: DispositivoCrear, db: Session = Depends(get_db)):
    if db.get(Dispositivo, datos.id):
        raise HTTPException(409, "Ya existe un dispositivo con ese ID")
    dispositivo = Dispositivo(**datos.model_dump())
    db.add(dispositivo)
    db.commit()
    db.refresh(dispositivo)
    return dispositivo


@app.get("/api/dispositivos", response_model=list[DispositivoSalida])
def listar_dispositivos(db: Session = Depends(get_db)):
    dispositivos = db.scalars(select(Dispositivo).order_by(Dispositivo.nombre)).all()
    salida = []
    for dispositivo in dispositivos:
        ultima = db.scalars(select(Medicion).where(Medicion.dispositivo_id == dispositivo.id).order_by(Medicion.fecha_hora.desc()).limit(1)).first()
        salida.append(DispositivoSalida(**DispositivoCrear.model_validate(dispositivo, from_attributes=True).model_dump(), ultima_medicion=ultima))
    return salida


@app.post("/api/mediciones", response_model=MedicionSalida, status_code=201)
async def crear_medicion(datos: MedicionCrear, db: Session = Depends(get_db)):
    dispositivo = db.get(Dispositivo, datos.dispositivo_id)
    if not dispositivo:
        raise HTTPException(404, "Dispositivo no registrado")
    if not dispositivo.activo:
        raise HTTPException(403, "Dispositivo inactivo")
    medicion = Medicion(**datos.model_dump())
    db.add(medicion)
    db.commit()  # Persistir antes de cualquier comunicación externa.
    db.refresh(medicion)
    if datos.nivel == NivelAgua.ALTO:
        await enviar_alerta_alto(dispositivo.nombre, medicion.distancia, medicion.fecha_hora)
    return medicion


@app.get("/api/mediciones", response_model=list[MedicionSalida])
def historial(dispositivo_id: str | None = None, limit: int = Query(200, ge=1, le=1000), db: Session = Depends(get_db)):
    consulta = select(Medicion).order_by(Medicion.fecha_hora.desc()).limit(limit)
    if dispositivo_id:
        consulta = consulta.where(Medicion.dispositivo_id == dispositivo_id)
    return db.scalars(consulta).all()


@app.get("/api/dispositivos/{dispositivo_id}/mediciones", response_model=list[MedicionSalida])
def mediciones_por_dispositivo(dispositivo_id: str, limit: int = Query(200, ge=1, le=1000), db: Session = Depends(get_db)):
    if not db.get(Dispositivo, dispositivo_id):
        raise HTTPException(404, "Dispositivo no encontrado")
    return db.scalars(select(Medicion).where(Medicion.dispositivo_id == dispositivo_id).order_by(Medicion.fecha_hora.desc()).limit(limit)).all()


# El dashboard se sirve desde la misma aplicación para evitar CORS en producción local.
app.mount("/", StaticFiles(directory=ROOT_DIR / "frontend", html=True), name="frontend")
