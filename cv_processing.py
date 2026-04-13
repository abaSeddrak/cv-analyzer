from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import CV
from pydantic import BaseModel

# لو ما عملتش create tables قبل كده
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# نموذج Pydantic للـ POST
class CVCreate(BaseModel):
    name: str
    email: str
    phone: str
    city:str

# GET all CVs
@app.get("/cvs")
def read_cvs(db: Session = Depends(get_db)):
    cvs = db.query(CV).all()
    return [{"id": cv.id, "name": cv.name, "email": cv.email, "phone": cv.phone, "city":cv.city} for cv in cvs]

# POST new CV
@app.post("/cvs")
def create_cv(cv: CVCreate, db: Session = Depends(get_db)):
    new_cv = CV(name=cv.name, email=cv.email, phone=cv.phone, city=cv.city)
    db.add(new_cv)
    db.commit()
    db.refresh(new_cv)
    return {"id": new_cv.id, "name": new_cv.name, "email": new_cv.email, "phone": new_cv.phone,"city":cv.city}