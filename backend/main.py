from fastapi import FastAPI, HTTPException  # type: ignore[import-not-found]
from pydantic import BaseModel

from agent import DataInvestigatorAgent
from models import InvestigationResponse
from tools import get_schema, run_readonly_sql


app = FastAPI(
    title="AI Data Investigator"
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