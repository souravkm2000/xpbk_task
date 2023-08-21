# main1.py - Write a program for user registration in FastAPI ( Using two database PostgreSQL and MobgoDB )
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from pymongo import MongoClient
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# FastAPI app
app = FastAPI()

# SQLAlchemy setup for PostgreSQL database
Base = declarative_base()
postgres_engine = create_engine('postgresql://postgres:2341560@localhost/postgres')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)

# MongoDB setup
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['profile']

# SQLAlchemy models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
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
    profile_picture: Optional[str] = None

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

    # Store profile picture in MongoDB
    if user_data.profile_picture:
        profile_data = {"user_id": new_user.id, "profile_picture": user_data.profile_picture}
        mongo_db.profiles.insert_one(profile_data)

    db.close()
    return {"message": "User registered successfully"}

# FastAPI route to get user details
@app.get("/user/{user_id}")
async def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user's profile picture from MongoDB
    profile_data = mongo_db.profiles.find_one({"user_id": user_id})
    profile_picture = profile_data["profile_picture"] if profile_data else None

    db.close()
    return {
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "profile_picture": profile_picture
    }
