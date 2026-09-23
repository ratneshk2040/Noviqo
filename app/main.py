from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

from app.database import Base, engine, get_db
from app.models import Question, Upload
from app.routers import auth, dashboard, practice, uploads, notes
from app.routers.auth import get_current_active_user
from app.schemas import QuestionOut
from fastapi import Form, File, UploadFile
from sqlalchemy.orm import Session

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Noviqo - Smart Learning Platform", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Robust Base Directory Path
BASE_DIR = Path(__file__).resolve().parent.parent

# Static Files & Templates Setup
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/favicon.ico")
def favicon():
    return FileResponse(BASE_DIR / "static" / "favicon.svg")


# --- 1. MAIN CLEAN PAGE ROUTES ---
@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html")

@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return templates.TemplateResponse(request=request, name="forgot-password.html")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/notes", response_class=HTMLResponse)
def notes_page(request: Request):
    return templates.TemplateResponse(request=request, name="notes.html")

@app.get("/practice", response_class=HTMLResponse)
def practice_page_clean(request: Request):
    return templates.TemplateResponse(request=request, name="practice.html")

@app.get("/upload", response_class=HTMLResponse)
def upload_page_clean(request: Request):
    return templates.TemplateResponse(request=request, name="upload.html")

@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    return templates.TemplateResponse(request=request, name="profile.html")

@app.get("/practice-history", response_class=HTMLResponse)
def practice_history_page(request: Request):
    return templates.TemplateResponse(request=request, name="practice-history.html")


# --- 2. BACKWARD-COMPATIBILITY ROUTES ---
@app.post("/upload", response_model=list[QuestionOut])
def upload_compatibility_route(
    category: str = Form(...),
    subject: str = Form(...),
    year: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return uploads.upload_file(
        category=category,
        subject=subject,
        year=year,
        file=file,
        db=db,
        current_user=current_user,
    )


# --- 3. ROUTERS ---
app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(practice.router)
app.include_router(notes.router)


# --- 3. SAFETY REDIRECT ROUTES ---
@app.get("/index.html")
def redirect_index():
    return RedirectResponse(url="/", status_code=303)

@app.get("/login.html")
def redirect_login():
    return RedirectResponse(url="/login", status_code=303)

@app.get("/signup.html")
def redirect_signup():
    return RedirectResponse(url="/signup", status_code=303)

@app.get("/forgot-password.html")
def redirect_forgot_password():
    return RedirectResponse(url="/forgot-password", status_code=303)

@app.get("/dashboard.html")
def redirect_dashboard():
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/practice.html")
def redirect_practice():
    return RedirectResponse(url="/practice", status_code=303)

@app.get("/upload.html")
def redirect_upload():
    return RedirectResponse(url="/upload", status_code=303)

@app.get("/notes.html")
def redirect_notes():
    return RedirectResponse(url="/notes", status_code=303)

@app.get("/profile.html")
def redirect_profile():
    return RedirectResponse(url="/profile", status_code=303)

@app.get("/practice-history.html")
def redirect_practice_history():
    return RedirectResponse(url="/practice-history", status_code=303)