from typing import Any

from pydantic import BaseModel, Field


class Finding(BaseModel):
    title: str
    description: str
    severity: str = "info"


class Evidence(BaseModel):
    finding: str
    value: str
    source: str


class InvestigationResponse(BaseModel):
    question: str
    status: str
    summary: str = ""
    findings: list[Finding] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    queries: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)