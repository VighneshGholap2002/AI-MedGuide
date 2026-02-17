from fastapi import APIRouter, HTTPException
from app.models.schemas import SummarizationRequest, SummarizationResponse, Summary, HealthCheck
from app.services.nlp_processor import ClinicalNoteProcessor
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["summarization"])

@router.post("/summarize", response_model=SummarizationResponse)
async def summarize_case(request: SummarizationRequest):
    """Summarize clinical notes and extract key information"""
    try:
        logger.info(f"Processing case: {request.caseId}")
        
        processor = ClinicalNoteProcessor()
        
        # Extract components
        chief_complaint = processor.extract_chief_complaint(request.clinicalNotes)
        key_findings = processor.extract_key_findings(request.clinicalNotes)
        risk_words = processor.detect_risk_words(request.clinicalNotes)
        risk_factors = processor.identify_risk_factors(
            request.clinicalNotes,
            request.patientAge,
            request.gender
        )
        icd_codes = processor.generate_icd_codes(request.clinicalNotes)
        confidence_score = processor.calculate_confidence_score(request.clinicalNotes, risk_words)
        
        # Generate assessment and recommendations
        assessment = f"Patient presents with {chief_complaint.lower()}. Key findings include: {key_findings}."
        recommendations = [
            "Continue monitoring vital signs",
            "Follow-up in 24-48 hours",
            "Consider specialist consultation if symptoms persist"
        ]
        
        if risk_words:
            recommendations.insert(0, f"HIGH PRIORITY: Risk factors detected: {', '.join(risk_words)}")
        
        summary = Summary(
            chiefComplaint=chief_complaint,
            keyFindings=key_findings,
            assessment=assessment,
            recommendations=recommendations,
            icdCodes=icd_codes
        )
        
        response = SummarizationResponse(
            caseId=request.caseId,
            summary=summary,
            riskFactors=risk_factors,
            riskWords=risk_words,
            confidenceScore=confidence_score,
            metadata={
                "processedAt": "2026-02-12T12:00:00Z",
                "modelVersion": "1.0.0",
                "status": "SUCCESS"
            }
        )
        
        logger.info(f"Case {request.caseId} processed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error processing case {request.caseId}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to summarize case: {str(e)}")

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(status="UP", version="1.0.0")
