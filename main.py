import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Job, Candidate, Application

app = FastAPI(title="HR Recruit API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "HR Recruit API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# Utilities
class IdResponse(BaseModel):
    id: str


def _oid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


# Jobs Endpoints
@app.post("/api/jobs", response_model=IdResponse)
def create_job(job: Job):
    inserted_id = create_document("job", job)
    return {"id": inserted_id}


@app.get("/api/jobs")
def list_jobs():
    jobs = get_documents("job")
    # Convert ObjectId to string
    for j in jobs:
        j["id"] = str(j.pop("_id"))
    return jobs


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    doc = db["job"].find_one({"_id": _oid(job_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")
    doc["id"] = str(doc.pop("_id"))
    return doc


# Candidates Endpoints
@app.post("/api/candidates", response_model=IdResponse)
def create_candidate(candidate: Candidate):
    inserted_id = create_document("candidate", candidate)
    return {"id": inserted_id}


@app.get("/api/candidates")
def list_candidates():
    items = get_documents("candidate")
    for it in items:
        it["id"] = str(it.pop("_id"))
    return items


# Applications Endpoints
@app.post("/api/applications", response_model=IdResponse)
def submit_application(apply: Application):
    # Ensure referenced job exists
    job = db["job"].find_one({"_id": _oid(apply.job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found for application")

    # If candidate_id provided, ensure it exists
    if apply.candidate_id:
        cand = db["candidate"].find_one({"_id": _oid(apply.candidate_id)})
        if not cand:
            raise HTTPException(status_code=404, detail="Candidate not found")

    inserted_id = create_document("application", apply)
    return {"id": inserted_id}


@app.get("/api/applications")
def list_applications(job_id: Optional[str] = None, status: Optional[str] = None):
    query = {}
    if job_id:
        query["job_id"] = job_id
    if status:
        query["status"] = status
    items = get_documents("application", query)
    for it in items:
        it["id"] = str(it.pop("_id"))
    return items


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
