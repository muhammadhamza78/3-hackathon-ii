from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback

from app.api.v1 import auth, tasks, profile, chat
from app.db.session import init_db, engine
from app.config import settings
from sqlmodel import text


# -------------------------------------------------
# Create FastAPI App
# -------------------------------------------------
app = FastAPI(
    title="Task Management API",
    version="1.0.0",
    description="API for managing tasks, users, and chat",
    docs_url="/docs",
    redoc_url="/redoc",
)


# -------------------------------------------------
# 🔐 CORS Configuration
# -------------------------------------------------

# Allowed frontend origins (production + development)
ALLOWED_ORIGINS = [
    # Production Vercel URLs
    "https://3-hackathon-ii.vercel.app",
    "https://3-hackathon-ii-v63o.vercel.app",
    # Local development
    "http://localhost:3000",
    "http://localhost:3001",
]

# Add any additional origins from environment variables
def parse_cors(env_value: str | list | None):
    if not env_value:
        return []
    if isinstance(env_value, list):
        return env_value
    if isinstance(env_value, str):
        env_value = env_value.strip()
        if env_value.startswith("["):
            # JSON list format
            import json
            try:
                return json.loads(env_value)
            except:
                pass
        # Comma-separated format
        return [v.strip() for v in env_value.split(",") if v.strip()]
    return []

# Merge environment origins with hardcoded ones
ENV_ORIGINS = parse_cors(getattr(settings, 'CORS_ORIGINS', None))
ALLOWED_ORIGINS = list(set(ALLOWED_ORIGINS + ENV_ORIGINS))

print("\n" + "=" * 60)
print("🌐 CORS CONFIGURATION ACTIVE")
print("Allowed Origins:")
for origin in ALLOWED_ORIGINS:
    print(f"  ✓ {origin}")
print("=" * 60 + "\n")

# Apply CORS middleware BEFORE including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# 🛑 Global Exception Handler
# -------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"\n❌ GLOBAL EXCEPTION: {type(exc).__name__}: {exc}")
    traceback.print_exc()

    origin = request.headers.get("origin", "")
    headers = {}

    # Add CORS headers to error responses
    if origin in ALLOWED_ORIGINS:
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true"
        }

    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
        headers=headers
    )


# -------------------------------------------------
# 📦 Include Routers
# -------------------------------------------------
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(profile.router, prefix="/api/v1", tags=["Profile"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])

print("✅ Routers Registered:")
print("   → Auth: /api/auth")
print("   → Tasks: /api/tasks")
print("   → Profile: /api/v1/profile")
print("   → Chat: /api/v1/chat\n")


# -------------------------------------------------
# 🚀 Startup Hook
# -------------------------------------------------
@app.on_event("startup")
async def startup_event():
    print("🚀 FastAPI Application Starting...")
    if getattr(settings, 'DEBUG', False):
        print("🔧 Debug Mode: ON → Initializing Database")
        init_db()
    print("✨ Startup Complete\n")


# -------------------------------------------------
# 🌐 Root Endpoint
# -------------------------------------------------
@app.get("/")
async def root():
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "status": "running",
        "backend_url": "https://3-hackathon-ii-production.up.railway.app",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": "/api/auth",
            "tasks": "/api/tasks",
            "profile": "/api/v1/profile",
            "chat": "/api/v1/chat",
        }
    }


# -------------------------------------------------
# 🩺 Health Check
# -------------------------------------------------
@app.get("/health")
async def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "cors": "enabled",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
