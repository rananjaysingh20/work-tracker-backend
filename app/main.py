from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import auth, projects, tasks, time_entries, categories, clients, team_members, reports, notifications, time_entry_files
from app.routes import client_files

app = FastAPI(
    title="Work Tracker API",
    description="API for the Work Tracker application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://webgigs-tracker.web.app",  # Default Firebase domain
        "https://webgigs-tracker.firebaseapp.com",  # Default Firebase domain
        "https://webgigs.in"  # Custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Work Tracker API"}

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(time_entries.router, prefix="/api/time-entries", tags=["Time Entries"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(team_members.router, prefix="/api/team-members", tags=["Team Members"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(client_files.router, prefix="/api", tags=["client-files"])
app.include_router(time_entry_files.router, prefix="/api", tags=["time-entry-files"])

# TODO: Add other routers as they are implemented
# app.include_router(team_members.router, prefix="/api/team-members", tags=["Team Members"])
