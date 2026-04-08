from fastapi import FastAPI
app = FastAPI()

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import CV  # تأكد إن عندك CV معرف في models.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import CV

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_cvs(db: Session = Depends(get_db)):
    cvs = db.query(CV).all()
    return [{"id": cv.id, "name": cv.name, "email": cv.email, "phone": cv.phone} for cv in cvs]