"""
Database Schemas for HR Recruit App

Each Pydantic model represents a collection in MongoDB. The collection name
is the lowercase of the class name.

- Job -> "job"
- Candidate -> "candidate"
- Application -> "application"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class Job(BaseModel):
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Full role description")
    location: str = Field(..., description="City / Remote / Hybrid")
    department: str = Field(..., description="Department e.g. Engineering, Sales")
    employment_type: str = Field(..., description="Full-time, Part-time, Contract, Intern")
    salary_min: Optional[float] = Field(None, ge=0, description="Minimum yearly salary")
    salary_max: Optional[float] = Field(None, ge=0, description="Maximum yearly salary")
    skills: List[str] = Field(default_factory=list, description="Required skills")
    is_active: bool = Field(True, description="Whether the job is open for applications")


class Candidate(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    resume_url: Optional[str] = Field(None, description="Link to resume/CV")
    experience_years: Optional[float] = Field(None, ge=0, le=80, description="Years of experience")
    skills: List[str] = Field(default_factory=list, description="Candidate skills")


class Application(BaseModel):
    job_id: str = Field(..., description="ID of the job posting")
    candidate_id: Optional[str] = Field(None, description="Existing candidate ID if available")
    candidate_name: str = Field(..., description="Applicant name")
    candidate_email: EmailStr = Field(..., description="Applicant email")
    resume_url: Optional[str] = Field(None, description="Link to resume/CV")
    cover_letter: Optional[str] = Field(None, description="Cover letter text")
    status: str = Field("submitted", description="Application status: submitted, reviewing, interview, rejected, hired")
