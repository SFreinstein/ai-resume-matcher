from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import models
from db import SessionLocal, engine
from llm import compute_similarity
from config import SECRET_KEY

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency: database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Security settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# Register
@app.post("/register")
def register(name: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(password)
    new_user = models.User(name=name, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered successfully"}

# Login
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Upload resume
@app.post("/upload_resume")
async def upload_resume(user: models.User = Depends(get_current_user), file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    resume_text = content.decode("utf-8", errors="ignore")
    new_resume = models.Resume(user_id=user.id, content=resume_text)
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    return {"msg": "Resume uploaded successfully", "resume_id": new_resume.id}

# Get all jobs
@app.get("/jobs")
def get_jobs(db: Session = Depends(get_db)):
    return db.query(models.Job).all()

# Get job by ID
@app.get("/job/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# MatchRequest Pydantic model
class MatchRequest(BaseModel):
    resume_id: int

# Match jobs
@app.post("/match_jobs")
def match_jobs(request: MatchRequest, db: Session = Depends(get_db)):
    resume = db.query(models.Resume).filter(models.Resume.id == request.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    jobs = db.query(models.Job).all()
    match_results = []

    for job in jobs:
        score = compute_similarity(resume.content, job.description)
        print(f"📊 Matching Resume ID {resume.id} with Job '{job.title}' — Score: {score}")
        match_results.append({
            "job_id": job.id,
            "title": job.title,
            "score": score
        })
        db.merge(models.Match(resume_id=resume.id, job_id=job.id, score=score))

    db.commit()
    top_matches = sorted(match_results, key=lambda x: x["score"], reverse=True)[:5]
    return {"matches": top_matches}

# Job seeding logic
def seed_jobs(db: Session):
    if db.query(models.Job).count() == 0:
        print("🌱 Seeding sample job listings...")
        sample_jobs = [
            models.Job(title="Software Engineer", description="Develop backend services using Python and FastAPI."),
            models.Job(title="Data Scientist", description="Analyze datasets and build machine learning models using Python."),
            models.Job(title="Frontend Developer", description="Build responsive user interfaces using React and JavaScript."),
            models.Job(title="DevOps Engineer", description="Manage CI/CD pipelines, Docker containers, and cloud infrastructure."),
            models.Job(title="AI Researcher", description="Research and implement AI models in natural language processing."),
        ]
        db.add_all(sample_jobs)
        db.commit()
        print("✅ Seeding complete.")
    else:
        print("ℹ️ Jobs already exist in the database — skipping seeding.")

# Automatically seed jobs on startup
@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    seed_jobs(db)
    db.close()
