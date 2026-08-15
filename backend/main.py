from fastapi import FastAPI, HTTPException  # pyright: ignore[reportMissingImports]
from pydantic import BaseModel

from tools import get_schema, run_readonly_sql


app = FastAPI(
    title="AI Data Investigator"
)


class SQLRequest(BaseModel):
    query: str


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