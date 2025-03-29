# backend/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    resumes = relationship("Resume", back_populates="user")

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    user = relationship("User", back_populates="resumes")
    matches = relationship("Match", back_populates="resume")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String)
    company = Column(String)
    matches = relationship("Match", back_populates="job")

class Match(Base):
    __tablename__ = "matches"
    resume_id = Column(Integer, ForeignKey("resumes.id"), primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), primary_key=True)
    score = Column(Float, nullable=False)
    resume = relationship("Resume", back_populates="matches")
    job = relationship("Job", back_populates="matches")
