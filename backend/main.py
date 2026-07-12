"""AI-First CRM HCP Module — FastAPI Backend Entry Point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from routes import hcps, interactions, products, agent
from seed_data import seed_database

# Create all tables
Base.metadata.create_all(bind=engine)

# Seed data
db = SessionLocal()
try:
    seed_database(db)
finally:
    db.close()

app = FastAPI(
    title="AI-First CRM — HCP Module",
    description="Healthcare Professional interaction management powered by LangGraph AI agents",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(hcps.router)
app.include_router(interactions.router)
app.include_router(products.router)
app.include_router(agent.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "AI-First CRM HCP Module", "version": "1.0.0"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "database": "connected", "agent": "ready"}
