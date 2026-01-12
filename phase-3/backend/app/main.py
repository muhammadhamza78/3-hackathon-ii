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

DEFAULT_ORIGINS = [
    # "http://localhost:3000",
    # "http://127.0.0.1:3000",
    # "http://localhost:3001",
    # "http://127.0.0.1:3001",
    "https://3-hackathon-ii-v63o.vercel.app",
]

# Parse env CORS
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
        # CSV format
        return [v.strip() for v in env_value.split(",")]
    return []

# Load origins from env
ENV_ORIGINS = parse_cors(settings.CORS_ORIGINS)

# Production allowlist (Vercel preview + prod)
PRODUCTION_ORIGINS = [
    "https://3-hackathon-ii-v63o.vercel.app",
]


ALLOWED_ORIGINS = list(set(DEFAULT_ORIGINS + ENV_ORIGINS + PRODUCTION_ORIGINS))

print("\n" + "=" * 60)
print("🌐 CORS CONFIGURATION ACTIVE")
print("=" * 60)
print("Allowed Origins:")
for o in ALLOWED_ORIGINS:
    print("  -", o)
print("=" * 60 + "\n")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
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

    # Return CORS headers in errors for frontend compatibility
    for allowed in ALLOWED_ORIGINS:
        if allowed.startswith("https://*.") and origin.endswith(allowed[10:]):
            headers = {"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Credentials": "true"}
            break
        if origin == allowed:
            headers = {"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Credentials": "true"}
            break

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
print("   - Auth: /api/auth")
print("   - Tasks: /api/tasks")
print("   - Profile: /api/v1/profile")
print("   - Chat: /api/v1/chat\n")


# -------------------------------------------------
# 🚀 Startup Hook
# -------------------------------------------------
@app.on_event("startup")
async def startup_event():
    print("🚀 FastAPI Starting...")
    if settings.DEBUG:
        print("🔧 Debug ON → Initializing DB")
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
        "docs": "/docs",
        "api": {
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
        return {"status": "ok", "db": "connected", "cors": "enabled"}
    except Exception as e:
        return {"status": "error", "db": "disconnected", "error": str(e)}
