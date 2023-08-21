# main.py - Write a program for user registration in fastAPI ( Using postgreSQL )
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# FastAPI app
app = FastAPI()

# SQLAlchemy setup for PostgreSQL database
Base = declarative_base()
postgres_engine = create_engine('postgresql://postgres:2341560@localhost/postgres')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)

# SQLAlchemy models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String, unique=True, index=True)

class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    profile_picture = Column(String)

Base.metadata.create_all(bind=postgres_engine)

# Pydantic model for user registration
class UserRegistration(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str
    profile_picture: str

# FastAPI route for user registration
@app.post("/register_user/")
async def register_user(user_data: UserRegistration):
    db = SessionLocal()
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if phone already exists
    existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    # Register user in PostgreSQL
    new_user = User(full_name=user_data.full_name,
                    email=user_data.email,
                    password=user_data.password,
                    phone=user_data.phone)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db.close()
    return {"message": "User registered successfully"}

# FastAPI route to get user details
@app.get("/user/{user_id}")
async def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.close()
    return {
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
    }
