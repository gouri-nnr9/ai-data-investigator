from fastapi import FastAPI, HTTPException  # type: ignore[import-not-found]
from pydantic import BaseModel

from agent import DataInvestigatorAgent
from models import InvestigationResponse
from fastapi.middleware.cors import CORSMiddleware
from tools import get_schema, run_readonly_sql


app = FastAPI(
    title="AI Data Investigator"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = DataInvestigatorAgent()


class SQLRequest(BaseModel):
    query: str


class InvestigationRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "message": "AI Data Investigator backend is running"
    }


@app.get("/schema")
def schema():
    try:
        return get_schema()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@app.post("/sql")
def execute_sql(request: SQLRequest):
    try:
        return run_readonly_sql(request.query)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@app.post("/investigate",
    response_model=InvestigationResponse,)
def investigate(request: InvestigationRequest):
    try:
        return agent.investigate(
            request.question
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )