"""OfficeHub API: local-first freelancer records and AI service status."""
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone
from decimal import Decimal
from os import environ
from typing import Annotated, Literal

import httpx
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

DATABASE_URL = environ.get("DATABASE_URL", "sqlite:///./officehub.db")
OLLAMA_URL = environ.get("OLLAMA_URL", "http://ollama:11434")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), default="")
    company: Mapped[str] = mapped_column(String(200), default="")


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="active")
    client: Mapped[Client | None] = relationship()


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250))
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="todo")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(80), unique=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(40), default="draft")
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ClientIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(default="", max_length=320)
    company: str = Field(default="", max_length=200)


class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    client_id: int | None = None
    status: Literal["active", "paused", "done"] = "active"


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=250)
    project_id: int | None = None
    status: Literal["todo", "doing", "done"] = "todo"
    due_date: date | None = None


class InvoiceIn(BaseModel):
    number: str = Field(min_length=1, max_length=80)
    client_id: int
    amount: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    status: Literal["draft", "sent", "paid"] = "draft"


MODELS = {"clients": Client, "projects": Project, "tasks": Task, "invoices": Invoice}
INPUTS = {"clients": ClientIn, "projects": ProjectIn, "tasks": TaskIn, "invoices": InvoiceIn}


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # Starter only: use Alembic migrations before production.
    yield


app = FastAPI(title="OfficeHub API", version="0.1.0", lifespan=lifespan)


def get_db():
    with SessionLocal() as db:
        yield db


DB = Annotated[Session, Depends(get_db)]


def serialize(obj):
    return {
        col.name: (str(value) if isinstance(value, Decimal) else value)
        for col in obj.__table__.columns
        if (value := getattr(obj, col.name)) is not None
    }


@app.get("/health")
def health(db: DB):
    db.scalar(select(func.count()).select_from(Client))
    return {"status": "ok"}


@app.get("/api/dashboard")
async def dashboard(db: DB):
    counts = {name: db.scalar(select(func.count()).select_from(model)) for name, model in MODELS.items()}
    outstanding = db.scalar(select(func.coalesce(func.sum(Invoice.amount), 0)).where(Invoice.status != "paid"))
    ai_online = False
    models = []
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            response.raise_for_status()
            models = [item["name"] for item in response.json().get("models", [])]
            ai_online = True
    except (httpx.HTTPError, ValueError, KeyError):
        pass
    return {
        "counts": counts,
        "outstanding": str(outstanding),
        "recent_tasks": [serialize(row) for row in db.scalars(select(Task).order_by(Task.id.desc()).limit(5))],
        "ai": {"online": ai_online, "models": models},
    }


@app.get("/api/{resource}")
def list_records(resource: str, db: DB):
    model = MODELS.get(resource)
    if model is None:
        raise HTTPException(404, "Unknown resource")
    return [serialize(row) for row in db.scalars(select(model).order_by(model.id.desc()).limit(200))]


@app.post("/api/{resource}", status_code=201)
def create_record(resource: str, payload: dict, db: DB):
    model, schema = MODELS.get(resource), INPUTS.get(resource)
    if model is None or schema is None:
        raise HTTPException(404, "Unknown resource")
    try:
        data = schema.model_validate(payload).model_dump()
    except ValidationError as exc:
        raise HTTPException(422, exc.errors(include_url=False, include_context=False)) from exc
    if resource in {"projects", "invoices"} and data.get("client_id") is not None:
        if db.get(Client, data["client_id"]) is None:
            raise HTTPException(422, "Client not found")
    if resource == "tasks" and data.get("project_id") is not None:
        if db.get(Project, data["project_id"]) is None:
            raise HTTPException(422, "Project not found")
    if resource == "invoices" and db.scalar(select(Invoice).where(Invoice.number == data["number"])):
        raise HTTPException(409, "Invoice number already exists")
    row = model(**data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize(row)


@app.delete("/api/{resource}/{record_id}", status_code=204)
def delete_record(resource: str, record_id: int, db: DB):
    model = MODELS.get(resource)
    if model is None:
        raise HTTPException(404, "Unknown resource")
    row = db.get(model, record_id)
    if row is None:
        raise HTTPException(404, "Record not found")
    # Remove dependent records first, or add explicit cascade policies, before deleting clients/projects.
    if resource == "clients" and (
        db.scalar(select(Project.id).where(Project.client_id == record_id).limit(1)) is not None
        or db.scalar(select(Invoice.id).where(Invoice.client_id == record_id).limit(1)) is not None
    ):
        raise HTTPException(409, "Client still has projects or invoices")
    if resource == "projects" and db.scalar(select(Task.id).where(Task.project_id == record_id).limit(1)) is not None:
        raise HTTPException(409, "Project still has tasks")
    db.delete(row)
    db.commit()
