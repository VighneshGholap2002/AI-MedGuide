from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SummarizationRequest(BaseModel):
    caseId: str
    clinicalNotes: str
    patientAge: str
    gender: str

class Summary(BaseModel):
    chiefComplaint: str
    keyFindings: str
    assessment: str
    recommendations: List[str]
    icdCodes: str

class SummarizationResponse(BaseModel):
    caseId: str
    summary: Summary
    riskFactors: List[str]
    riskWords: List[str]
    confidenceScore: int
    metadata: Dict[str, Any]

class HealthCheck(BaseModel):
    status: str
    version: str
