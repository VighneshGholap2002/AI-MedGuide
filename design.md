# Design Document - Clinical Note Summarizer

## 1. Executive Summary

### 1.1 System Overview
The Clinical Note Summarizer is a microservices-based healthcare application that leverages Natural Language Processing (NLP) to automatically analyze clinical notes, detect risk factors, and generate structured summaries for healthcare professionals. The system follows a three-tier architecture with a React frontend, Spring Boot backend, and Python-based NLP service, all backed by MongoDB for data persistence.

### 1.2 Design Goals
- **Modularity**: Loosely coupled services for independent scaling and maintenance
- **Performance**: Sub-2-second response times for clinical note processing
- **Reliability**: Fault-tolerant architecture with graceful error handling
- **Usability**: Intuitive interface requiring minimal training
- **Extensibility**: Easy integration with EHR systems and future enhancements
- **Deployability**: Single-command deployment using Docker Compose

### 1.3 Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | React + TypeScript | 18.2 | User interface |
| Backend | Spring Boot | 3.1.5 | REST API & orchestration |
| NLP Service | FastAPI | 0.104 | Text processing |
| Database | MongoDB | 7.0 | Data persistence |
| Styling | Tailwind CSS | 3.3 | UI styling |
| Containerization | Docker | Latest | Deployment |

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│                    (Web Browser - Port 3000)                     │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Case Form   │  │  Case List   │  │ Case Detail  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                           │
│                  (Spring Boot - Port 8080)                       │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              REST API Controllers                         │  │
│  │  • PatientCaseController                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Service Layer                                │  │
│  │  • SummarizationService                                  │  │
│  │  • Case Management Logic                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Repository Layer                             │  │
│  │  • PatientCaseRepository (MongoDB)                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────┬──────────────────────┘
               │                           │
               │ HTTP/JSON                 │ MongoDB Protocol
               ▼                           ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│    NLP Service Layer     │    │    Data Layer            │
│  (FastAPI - Port 8000)   │    │  (MongoDB - Port 27017)  │
│                          │    │                          │
│  • Text Processing       │    │  • patient_cases         │
│  • Risk Detection        │    │  • summaries             │
│  • ICD Generation        │    │  • metadata              │
│  • Confidence Scoring    │    │                          │
└──────────────────────────┘    └──────────────────────────┘
```


### 2.2 Component Interaction Flow

```
User Action: Create & Summarize Case
│
├─► 1. Frontend (React)
│   ├─ User fills case form
│   ├─ Validates input
│   └─ POST /api/v1/cases
│
├─► 2. Backend (Spring Boot)
│   ├─ Receives request
│   ├─ Validates data
│   ├─ Saves to MongoDB
│   └─ Returns case ID
│
├─► 3. User clicks "Summarize"
│   └─ POST /api/v1/cases/{id}/summarize
│
├─► 4. Backend orchestrates
│   ├─ Retrieves case from MongoDB
│   ├─ Prepares NLP request
│   └─ POST to NLP Service
│
├─► 5. NLP Service (FastAPI)
│   ├─ Receives clinical notes
│   ├─ Extracts chief complaint
│   ├─ Identifies key findings
│   ├─ Detects risk words
│   ├─ Analyzes risk factors
│   ├─ Generates ICD codes
│   ├─ Calculates confidence
│   └─ Returns structured summary
│
├─► 6. Backend processes response
│   ├─ Receives NLP results
│   ├─ Updates case in MongoDB
│   └─ Returns to frontend
│
└─► 7. Frontend displays results
    ├─ Shows summary sections
    ├─ Highlights risk words
    ├─ Displays confidence score
    └─ Lists risk factors & ICD codes
```

### 2.3 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Host                               │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Docker Compose Network                     │ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │ │
│  │  │   Frontend   │  │   Backend    │  │ NLP Service │ │ │
│  │  │  Container   │  │  Container   │  │  Container  │ │ │
│  │  │  (nginx)     │  │  (Java 17)   │  │ (Python)    │ │ │
│  │  │  Port: 3000  │  │  Port: 8080  │  │ Port: 8000  │ │ │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │ │
│  │         │                  │                 │         │ │
│  │         └──────────────────┴─────────────────┘         │ │
│  │                            │                            │ │
│  │                   ┌────────▼────────┐                  │ │
│  │                   │    MongoDB      │                  │ │
│  │                   │    Container    │                  │ │
│  │                   │   Port: 27017   │                  │ │
│  │                   └─────────────────┘                  │ │
│  │                                                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Volumes:                                                     │
│  • mongodb-data (persistent storage)                         │
│  • backend-logs                                              │
│  • nlp-logs                                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Component Design

### 3.1 Frontend Layer (React + TypeScript)

#### 3.1.1 Component Structure

```
src/
├── App.tsx                    # Main application component
├── index.tsx                  # Entry point
├── components/
│   ├── CaseForm.tsx          # Case creation form
│   ├── CaseList.tsx          # List of all cases
│   └── CaseDetail.tsx        # Detailed case view with summary
├── services/
│   └── api.ts                # API client (Axios)
└── styles/
    ├── App.css               # Global styles
    └── index.css             # Tailwind imports
```

#### 3.1.2 Component Responsibilities

**App.tsx**
- Main layout with 3-column design
- State management for selected case
- Routing between components
- Error boundary handling

**CaseForm.tsx**
- Input validation
- Form submission
- Success/error notifications
- Reset functionality

**CaseList.tsx**
- Display all cases
- Filter and search (future)
- Click to select case
- Visual status indicators

**CaseDetail.tsx**
- Display case information
- Show summary results
- Risk word highlighting
- Action buttons (Summarize, Edit, Delete)
- Confidence score visualization

#### 3.1.3 State Management

```typescript
// Application State
interface AppState {
  cases: PatientCase[];
  selectedCase: PatientCase | null;
  loading: boolean;
  error: string | null;
}

// Patient Case Model
interface PatientCase {
  id: string;
  caseTitle: string;
  patientAge: number;
  gender: 'Male' | 'Female' | 'Other';
  clinicalNotes: string;
  createdAt: string;
  updatedAt: string;
  summary?: Summary;
}

// Summary Model
interface Summary {
  chiefComplaint: string;
  keyFindings: string;
  assessment: string;
  recommendations: string[];
  icdCodes: string;
  riskWords: RiskWord[];
  riskFactors: string[];
  confidenceScore: number;
  metadata: SummaryMetadata;
}
```

#### 3.1.4 API Integration

```typescript
// API Service (api.ts)
class ApiService {
  private baseURL = 'http://localhost:8080/api/v1';
  
  async createCase(case: CreateCaseRequest): Promise<PatientCase>
  async getCases(): Promise<PatientCase[]>
  async getCase(id: string): Promise<PatientCase>
  async updateCase(id: string, case: UpdateCaseRequest): Promise<PatientCase>
  async summarizeCase(id: string): Promise<PatientCase>
  async deleteCase(id: string): Promise<void>
}
```

#### 3.1.5 UI Design Patterns

**Color Scheme**
- Primary: Blue (#3B82F6)
- Success: Green (#10B981)
- Warning: Orange (#F59E0B)
- Danger: Red (#EF4444)
- Background: Gray (#F9FAFB)

**Typography**
- Headings: Inter font, bold
- Body: Inter font, regular
- Code: Monospace

**Responsive Breakpoints**
- Desktop: 1024px+
- Tablet: 768px - 1023px
- Mobile: < 768px (not primary target)


### 3.2 Backend Layer (Spring Boot)

#### 3.2.1 Package Structure

```
com.clinical.summarizer/
├── ClinicalSummarizerApplication.java    # Main application
├── config/
│   ├── MongoConfig.java                  # MongoDB configuration
│   ├── CorsConfig.java                   # CORS settings
│   └── RestTemplateConfig.java           # HTTP client config
├── controller/
│   └── PatientCaseController.java        # REST endpoints
├── model/
│   ├── PatientCase.java                  # Domain model
│   └── Summary.java                      # Summary model
├── repository/
│   └── PatientCaseRepository.java        # MongoDB repository
├── service/
│   ├── SummarizationService.java         # Business logic
│   ├── SummarizationRequest.java         # NLP request DTO
│   └── SummarizationResponse.java        # NLP response DTO
└── exception/
    ├── CaseNotFoundException.java        # Custom exceptions
    └── GlobalExceptionHandler.java       # Error handling
```

#### 3.2.2 REST API Design

**Base URL**: `/api/v1`

| Method | Endpoint | Request Body | Response | Status Codes |
|--------|----------|--------------|----------|--------------|
| POST | `/cases` | CreateCaseRequest | PatientCase | 201, 400 |
| GET | `/cases` | - | List<PatientCase> | 200 |
| GET | `/cases/{id}` | - | PatientCase | 200, 404 |
| PUT | `/cases/{id}` | UpdateCaseRequest | PatientCase | 200, 404 |
| POST | `/cases/{id}/summarize` | - | PatientCase | 200, 404, 500 |
| DELETE | `/cases/{id}` | - | - | 204, 404 |
| GET | `/cases/health` | - | HealthStatus | 200 |

#### 3.2.3 Data Models

```java
@Document(collection = "patient_cases")
public class PatientCase {
    @Id
    private String id;
    
    @NotBlank
    @Size(max = 200)
    private String caseTitle;
    
    @Min(0) @Max(150)
    private Integer patientAge;
    
    @NotNull
    private Gender gender;
    
    @NotBlank
    @Size(max = 10000)
    private String clinicalNotes;
    
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    @DBRef
    private Summary summary;
}

@Document(collection = "summaries")
public class Summary {
    @Id
    private String id;
    
    private String chiefComplaint;
    private String keyFindings;
    private String assessment;
    private List<String> recommendations;
    private String icdCodes;
    private List<RiskWord> riskWords;
    private List<String> riskFactors;
    
    @Min(0) @Max(95)
    private Integer confidenceScore;
    
    private SummaryMetadata metadata;
}
```

#### 3.2.4 Service Layer Design

```java
@Service
public class SummarizationService {
    
    private final PatientCaseRepository repository;
    private final RestTemplate restTemplate;
    
    @Value("${nlp-service.url}")
    private String nlpServiceUrl;
    
    @Value("${nlp-service.timeout}")
    private int timeout;
    
    public PatientCase summarizeCase(String caseId) {
        // 1. Retrieve case from database
        PatientCase patientCase = repository.findById(caseId)
            .orElseThrow(() -> new CaseNotFoundException(caseId));
        
        // 2. Prepare NLP request
        SummarizationRequest request = new SummarizationRequest(
            patientCase.getClinicalNotes(),
            patientCase.getPatientAge(),
            patientCase.getGender()
        );
        
        // 3. Call NLP service with retry logic
        SummarizationResponse response = callNlpService(request);
        
        // 4. Create summary object
        Summary summary = mapToSummary(response);
        
        // 5. Update case with summary
        patientCase.setSummary(summary);
        patientCase.setUpdatedAt(LocalDateTime.now());
        
        // 6. Save and return
        return repository.save(patientCase);
    }
    
    private SummarizationResponse callNlpService(SummarizationRequest request) {
        // Retry logic with exponential backoff
        // Timeout handling
        // Error mapping
    }
}
```

#### 3.2.5 Error Handling Strategy

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(CaseNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleCaseNotFound(CaseNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("CASE_NOT_FOUND", ex.getMessage()));
    }
    
    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ErrorResponse> handleValidation(ValidationException ex) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
            .body(new ErrorResponse("VALIDATION_ERROR", ex.getMessage()));
    }
    
    @ExceptionHandler(NlpServiceException.class)
    public ResponseEntity<ErrorResponse> handleNlpService(NlpServiceException ex) {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("NLP_SERVICE_ERROR", ex.getMessage()));
    }
}
```

#### 3.2.6 Configuration

```yaml
# application.yml
spring:
  application:
    name: clinical-summarizer
  data:
    mongodb:
      uri: mongodb://admin:password@localhost:27017/clinical_summarizer
      authentication-database: admin
      
server:
  port: 8080
  
nlp-service:
  url: http://localhost:8000/api/v1
  timeout: 30000
  retry:
    max-attempts: 3
    backoff-delay: 1000
    
logging:
  level:
    com.clinical.summarizer: INFO
    org.springframework.data.mongodb: DEBUG
```


### 3.3 NLP Service Layer (FastAPI + Python)

#### 3.3.1 Project Structure

```
app/
├── main.py                      # FastAPI application
├── models/
│   └── schemas.py              # Pydantic models
├── routes/
│   └── summarization.py        # API routes
└── services/
    └── nlp_processor.py        # NLP logic
```

#### 3.3.2 API Endpoints

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Clinical NLP Service",
    version="1.0.0",
    description="Natural Language Processing for clinical notes"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/api/v1/summarize")
async def summarize_clinical_notes(request: SummarizationRequest):
    """Process clinical notes and return structured summary"""
    
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "nlp-service"}
```

#### 3.3.3 Data Models (Pydantic)

```python
# models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class SummarizationRequest(BaseModel):
    clinical_notes: str = Field(..., max_length=10000)
    patient_age: int = Field(..., ge=0, le=150)
    gender: Gender

class RiskWord(BaseModel):
    word: str
    level: str  # CRITICAL or HIGH

class SummaryMetadata(BaseModel):
    processed_at: str
    model_version: str = "1.0.0"
    processing_time_ms: int
    status: str

class SummarizationResponse(BaseModel):
    chief_complaint: str
    key_findings: str
    assessment: str
    recommendations: List[str]
    icd_codes: str
    risk_words: List[RiskWord]
    risk_factors: List[str]
    confidence_score: int = Field(..., ge=0, le=95)
    metadata: SummaryMetadata
```

#### 3.3.4 NLP Processing Logic

```python
# services/nlp_processor.py
import re
from datetime import datetime
from typing import List, Tuple

class NLPProcessor:
    
    # Risk word dictionaries
    CRITICAL_RISKS = [
        "chest pain", "acute mi", "myocardial infarction", "stroke",
        "cardiac arrest", "sepsis", "anaphylaxis", "respiratory failure",
        "acute abdomen", "massive hemorrhage", "status epilepticus"
    ]
    
    HIGH_RISKS = [
        "hypertensive crisis", "pulmonary embolism", "acute kidney injury",
        "diabetic ketoacidosis", "severe hypoglycemia", "acute liver failure"
    ]
    
    # ICD code mappings
    ICD_MAPPINGS = {
        "chest pain": "R07.9",
        "hypertension": "I10",
        "diabetes": "E11.9",
        "pneumonia": "J18.9",
        "stroke": "I63.9",
        # ... more mappings
    }
    
    def process_clinical_notes(
        self, 
        notes: str, 
        age: int, 
        gender: str
    ) -> dict:
        """Main processing pipeline"""
        
        start_time = datetime.now()
        
        # 1. Extract chief complaint
        chief_complaint = self._extract_chief_complaint(notes)
        
        # 2. Identify key findings
        key_findings = self._extract_key_findings(notes)
        
        # 3. Generate assessment
        assessment = self._generate_assessment(notes, chief_complaint)
        
        # 4. Detect risk words
        risk_words = self._detect_risk_words(notes)
        
        # 5. Analyze risk factors
        risk_factors = self._analyze_risk_factors(notes, age, gender)
        
        # 6. Generate ICD codes
        icd_codes = self._generate_icd_codes(chief_complaint, assessment)
        
        # 7. Generate recommendations
        recommendations = self._generate_recommendations(
            risk_words, risk_factors
        )
        
        # 8. Calculate confidence score
        confidence = self._calculate_confidence(
            notes, risk_words, risk_factors
        )
        
        # 9. Prepare metadata
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        metadata = {
            "processed_at": datetime.now().isoformat(),
            "model_version": "1.0.0",
            "processing_time_ms": int(processing_time),
            "status": "SUCCESS"
        }
        
        return {
            "chief_complaint": chief_complaint,
            "key_findings": key_findings,
            "assessment": assessment,
            "recommendations": recommendations,
            "icd_codes": icd_codes,
            "risk_words": risk_words,
            "risk_factors": risk_factors,
            "confidence_score": confidence,
            "metadata": metadata
        }
    
    def _extract_chief_complaint(self, notes: str) -> str:
        """Extract chief complaint from notes"""
        # Look for "Chief Complaint:" section
        pattern = r"Chief Complaint:?\s*(.+?)(?:\n\n|\n[A-Z]|$)"
        match = re.search(pattern, notes, re.IGNORECASE | re.DOTALL)
        
        if match:
            complaint = match.group(1).strip()
            return complaint[:200]  # Limit length
        
        # Fallback: use first sentence
        sentences = notes.split('.')
        return sentences[0][:200] if sentences else "Not specified"
    
    def _detect_risk_words(self, notes: str) -> List[dict]:
        """Detect critical and high-risk keywords"""
        notes_lower = notes.lower()
        detected = []
        
        # Check critical risks
        for risk in self.CRITICAL_RISKS:
            if risk in notes_lower:
                detected.append({
                    "word": risk,
                    "level": "CRITICAL"
                })
        
        # Check high risks
        for risk in self.HIGH_RISKS:
            if risk in notes_lower:
                detected.append({
                    "word": risk,
                    "level": "HIGH"
                })
        
        return detected
    
    def _analyze_risk_factors(
        self, 
        notes: str, 
        age: int, 
        gender: str
    ) -> List[str]:
        """Identify patient-specific risk factors"""
        factors = []
        notes_lower = notes.lower()
        
        # Age-based risks
        if age > 65:
            factors.append("Advanced age (>65)")
        elif age < 18:
            factors.append("Pediatric patient")
        
        # Chronic conditions
        conditions = {
            "diabetes": "Diabetes mellitus",
            "hypertension": "Hypertension",
            "heart disease": "Cardiovascular disease",
            "copd": "Chronic obstructive pulmonary disease",
            "kidney disease": "Chronic kidney disease",
            "asthma": "Asthma"
        }
        
        for keyword, factor in conditions.items():
            if keyword in notes_lower:
                factors.append(factor)
        
        # Medication-based risks
        medications = {
            "warfarin": "Anticoagulant therapy",
            "insulin": "Insulin therapy",
            "immunosuppressant": "Immunosuppression"
        }
        
        for med, factor in medications.items():
            if med in notes_lower:
                factors.append(factor)
        
        return factors[:10]  # Limit to 10 factors
    
    def _calculate_confidence(
        self, 
        notes: str, 
        risk_words: List[dict], 
        risk_factors: List[str]
    ) -> int:
        """Calculate confidence score (0-95%)"""
        score = 0
        
        # Note length and structure (0-20 points)
        if len(notes) > 500:
            score += 20
        elif len(notes) > 200:
            score += 10
        
        # Standard sections present (0-25 points)
        sections = [
            "chief complaint", "history", "physical examination",
            "assessment", "plan"
        ]
        sections_found = sum(
            1 for s in sections if s in notes.lower()
        )
        score += min(sections_found * 5, 25)
        
        # Risk factors detected (0-25 points)
        score += min(len(risk_factors) * 5, 25)
        
        # Risk words detected (0-25 points)
        score += min(len(risk_words) * 5, 25)
        
        return min(score, 95)  # Cap at 95%
```

#### 3.3.5 Error Handling

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": "VALIDATION_ERROR",
            "message": str(exc)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An error occurred processing the request"
        }
    )
```


### 3.4 Database Layer (MongoDB)

#### 3.4.1 Database Schema

**Database Name**: `clinical_summarizer`

**Collections**:

1. **patient_cases**
```json
{
  "_id": "ObjectId",
  "caseTitle": "string",
  "patientAge": "number",
  "gender": "string",
  "clinicalNotes": "string",
  "createdAt": "ISODate",
  "updatedAt": "ISODate",
  "summary": {
    "chiefComplaint": "string",
    "keyFindings": "string",
    "assessment": "string",
    "recommendations": ["string"],
    "icdCodes": "string",
    "riskWords": [
      {
        "word": "string",
        "level": "string"
      }
    ],
    "riskFactors": ["string"],
    "confidenceScore": "number",
    "metadata": {
      "processedAt": "ISODate",
      "modelVersion": "string",
      "processingTimeMs": "number",
      "status": "string"
    }
  }
}
```

#### 3.4.2 Indexes

```javascript
// Performance optimization indexes
db.patient_cases.createIndex({ "createdAt": -1 });
db.patient_cases.createIndex({ "caseTitle": "text" });
db.patient_cases.createIndex({ "summary.confidenceScore": -1 });
db.patient_cases.createIndex({ "patientAge": 1 });
```

#### 3.4.3 Data Access Patterns

**Query Patterns**:
1. Get all cases (sorted by creation date)
2. Get case by ID
3. Search cases by title (future)
4. Filter by confidence score (future)
5. Filter by age range (future)

**Write Patterns**:
1. Insert new case
2. Update case with summary
3. Update case fields
4. Delete case

#### 3.4.4 Connection Configuration

```javascript
// mongo-init.js (initialization script)
db = db.getSiblingDB('clinical_summarizer');

db.createUser({
  user: 'clinical_app',
  pwd: 'secure_password',
  roles: [
    {
      role: 'readWrite',
      db: 'clinical_summarizer'
    }
  ]
});

// Create collections
db.createCollection('patient_cases');

// Create indexes
db.patient_cases.createIndex({ "createdAt": -1 });
db.patient_cases.createIndex({ "caseTitle": "text" });
```

---

## 4. Security Design

### 4.1 Current Security Posture (Demo/Educational)

**Implemented**:
- Input validation (length limits, type checking)
- CORS configuration (development mode)
- MongoDB authentication
- Error message sanitization

**NOT Implemented** (Required for Production):
- User authentication
- Authorization/RBAC
- Data encryption at rest
- TLS/HTTPS
- API rate limiting
- Audit logging
- Session management
- CSRF protection

### 4.2 Future Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client (Browser)                      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS (TLS 1.3)
                     ▼
┌─────────────────────────────────────────────────────────┐
│              API Gateway / Load Balancer                 │
│  • SSL Termination                                       │
│  • Rate Limiting                                         │
│  • DDoS Protection                                       │
└────────────────────┬────────────────────────────────────┘
                     │ JWT Token
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Authentication Service                      │
│  • JWT Validation                                        │
│  • Role-Based Access Control                            │
│  • Session Management                                    │
└────────────────────┬────────────────────────────────────┘
                     │ Authenticated Request
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend Services                        │
│  • Input Validation                                      │
│  • Authorization Checks                                  │
│  • Audit Logging                                         │
└────────────────────┬────────────────────────────────────┘
                     │ Encrypted Connection
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Database (Encrypted at Rest)                │
│  • Field-Level Encryption (PHI)                         │
│  • Access Logs                                           │
│  • Backup Encryption                                     │
└─────────────────────────────────────────────────────────┘
```

### 4.3 Data Protection Strategy

**Sensitive Data Classification**:
- **PHI (Protected Health Information)**: Clinical notes, patient demographics
- **PII (Personally Identifiable Information)**: Patient identifiers
- **Metadata**: Timestamps, system information

**Protection Measures** (Future):
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Field-level encryption for PHI
- Data anonymization for analytics
- Secure key management (AWS KMS, Azure Key Vault)

---

## 5. Performance Design

### 5.1 Performance Requirements

| Operation | Target | Acceptable | Maximum |
|-----------|--------|------------|---------|
| Create Case | 50ms | 100ms | 200ms |
| Get Case | 25ms | 50ms | 100ms |
| List Cases | 50ms | 100ms | 200ms |
| Summarize | 1000ms | 2000ms | 5000ms |
| Update Case | 50ms | 100ms | 200ms |

### 5.2 Optimization Strategies

#### 5.2.1 Backend Optimizations
- Connection pooling (MongoDB: 10-50 connections)
- HTTP client connection pooling
- Async processing for NLP calls
- Caching frequently accessed cases (future)
- Database query optimization with indexes

#### 5.2.2 NLP Service Optimizations
- Async request handling (FastAPI)
- Text processing optimization
- Compiled regex patterns
- Response caching for identical notes (future)
- Batch processing capability (future)

#### 5.2.3 Frontend Optimizations
- Lazy loading of case details
- Debounced search inputs
- Virtual scrolling for large lists (future)
- Code splitting
- Asset optimization (minification, compression)

#### 5.2.4 Database Optimizations
- Appropriate indexes on query fields
- Connection pooling
- Query result limiting
- Projection to fetch only needed fields
- Aggregation pipeline optimization

### 5.3 Scalability Design

```
Horizontal Scaling Strategy:

┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                         │
└────────┬────────────────┬────────────────┬──────────────┘
         │                │                │
         ▼                ▼                ▼
    ┌────────┐      ┌────────┐      ┌────────┐
    │Backend │      │Backend │      │Backend │
    │   1    │      │   2    │      │   3    │
    └────┬───┘      └────┬───┘      └────┬───┘
         │                │                │
         └────────────────┴────────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │   MongoDB     │
                  │  Replica Set  │
                  └───────────────┘
```

**Scaling Capabilities**:
- Stateless backend services (easy horizontal scaling)
- MongoDB replica sets for read scaling
- NLP service can be scaled independently
- Container orchestration ready (Kubernetes)

---

## 6. Error Handling & Resilience

### 6.1 Error Categories

| Category | Examples | Handling Strategy |
|----------|----------|-------------------|
| Validation | Invalid input, missing fields | Return 400 with details |
| Not Found | Case doesn't exist | Return 404 with message |
| Service Unavailable | NLP service down | Return 503, retry logic |
| Timeout | NLP processing timeout | Return 504, cancel operation |
| Internal | Unexpected errors | Return 500, log details |

### 6.2 Retry Logic

```java
// Backend retry configuration
@Retryable(
    value = {NlpServiceException.class},
    maxAttempts = 3,
    backoff = @Backoff(delay = 1000, multiplier = 2)
)
public SummarizationResponse callNlpService(SummarizationRequest request) {
    // Call NLP service
}
```

### 6.3 Circuit Breaker Pattern (Future)

```
Normal State → Failure Threshold Reached → Circuit Open
     ↑                                           │
     │                                           ▼
     └──────── Success Threshold ←──── Half-Open State
```

### 6.4 Graceful Degradation

**Fallback Strategies**:
1. NLP service unavailable → Return partial summary with lower confidence
2. Database slow → Return cached results (if available)
3. Timeout → Return processing status, allow retry

---

## 7. Monitoring & Observability

### 7.1 Logging Strategy

**Log Levels**:
- **ERROR**: System errors, exceptions
- **WARN**: Degraded performance, retries
- **INFO**: Request/response, business events
- **DEBUG**: Detailed execution flow

**Log Format** (JSON):
```json
{
  "timestamp": "2026-02-14T10:30:00Z",
  "level": "INFO",
  "service": "backend",
  "traceId": "abc123",
  "message": "Case summarized successfully",
  "caseId": "xyz789",
  "processingTime": 1250
}
```

### 7.2 Metrics to Track

**Application Metrics**:
- Request count by endpoint
- Response time percentiles (p50, p95, p99)
- Error rate by type
- NLP service call duration
- Database query duration

**Business Metrics**:
- Cases created per hour
- Summarization success rate
- Average confidence score
- Risk words detected frequency

**System Metrics**:
- CPU usage
- Memory usage
- Disk I/O
- Network throughput

### 7.3 Health Checks

```
GET /api/v1/cases/health
Response:
{
  "status": "UP",
  "components": {
    "database": "UP",
    "nlpService": "UP",
    "diskSpace": "UP"
  },
  "timestamp": "2026-02-14T10:30:00Z"
}
```


---

## 8. Deployment Design

### 8.1 Docker Configuration

#### 8.1.1 Backend Dockerfile

```dockerfile
# Dockerfile.backend
FROM maven:3.8-openjdk-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM openjdk:17-jdk-slim
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

#### 8.1.2 NLP Service Dockerfile

```dockerfile
# Dockerfile.nlp
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 8.1.3 Frontend Dockerfile

```dockerfile
# Dockerfile.frontend
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

### 8.2 Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: clinical-mongodb
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
      MONGO_INITDB_DATABASE: clinical_summarizer
    volumes:
      - mongodb-data:/data/db
      - ./docker/mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js
    networks:
      - clinical-network
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: ../docker/Dockerfile.backend
    container_name: clinical-backend
    ports:
      - "8080:8080"
    environment:
      SPRING_DATA_MONGODB_URI: mongodb://admin:password@mongodb:27017/clinical_summarizer?authSource=admin
      NLP_SERVICE_URL: http://nlp-service:8000/api/v1
    depends_on:
      mongodb:
        condition: service_healthy
      nlp-service:
        condition: service_started
    networks:
      - clinical-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/v1/cases/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nlp-service:
    build:
      context: ./nlp-service
      dockerfile: ../docker/Dockerfile.nlp
    container_name: clinical-nlp
    ports:
      - "8000:8000"
    networks:
      - clinical-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/Dockerfile.frontend
    container_name: clinical-frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - clinical-network

networks:
  clinical-network:
    driver: bridge

volumes:
  mongodb-data:
    driver: local
```

### 8.3 Environment Configuration

#### Development
```properties
# Backend
SPRING_PROFILES_ACTIVE=dev
SPRING_DATA_MONGODB_URI=mongodb://localhost:27017/clinical_summarizer
NLP_SERVICE_URL=http://localhost:8000/api/v1
LOGGING_LEVEL_ROOT=INFO

# Frontend
REACT_APP_API_URL=http://localhost:8080/api/v1
REACT_APP_ENV=development

# NLP Service
LOG_LEVEL=INFO
WORKERS=1
```

#### Production (Future)
```properties
# Backend
SPRING_PROFILES_ACTIVE=prod
SPRING_DATA_MONGODB_URI=${MONGODB_URI}
NLP_SERVICE_URL=${NLP_SERVICE_URL}
LOGGING_LEVEL_ROOT=WARN
SERVER_SSL_ENABLED=true

# Frontend
REACT_APP_API_URL=${API_URL}
REACT_APP_ENV=production

# NLP Service
LOG_LEVEL=WARN
WORKERS=4
```

### 8.4 Deployment Steps

**Single Command Deployment**:
```bash
docker-compose -f docker/docker-compose.yml up -d
```

**Manual Deployment**:
1. Start MongoDB
2. Build and start NLP service
3. Build and start Backend
4. Build and start Frontend
5. Verify health checks
6. Import sample data (optional)

### 8.5 Rollback Strategy

```bash
# Stop current version
docker-compose down

# Restore previous version
docker-compose -f docker-compose.yml.backup up -d

# Verify services
curl http://localhost:8080/api/v1/cases/health
```

---

## 9. Testing Strategy

### 9.1 Testing Pyramid

```
                    ┌─────────────┐
                    │   E2E Tests │  (10%)
                    │   Selenium  │
                    └─────────────┘
                  ┌─────────────────┐
                  │ Integration Tests│  (30%)
                  │  API Testing     │
                  └─────────────────┘
              ┌───────────────────────────┐
              │      Unit Tests           │  (60%)
              │  JUnit, pytest, Jest      │
              └───────────────────────────┘
```

### 9.2 Unit Testing

**Backend (JUnit 5)**:
```java
@SpringBootTest
class SummarizationServiceTest {
    
    @Mock
    private PatientCaseRepository repository;
    
    @Mock
    private RestTemplate restTemplate;
    
    @InjectMocks
    private SummarizationService service;
    
    @Test
    void testSummarizeCase_Success() {
        // Given
        PatientCase case = createTestCase();
        when(repository.findById(anyString())).thenReturn(Optional.of(case));
        
        // When
        PatientCase result = service.summarizeCase("test-id");
        
        // Then
        assertNotNull(result.getSummary());
        verify(repository, times(1)).save(any());
    }
}
```

**NLP Service (pytest)**:
```python
def test_extract_chief_complaint():
    processor = NLPProcessor()
    notes = "Chief Complaint: Chest pain\n\nHistory: ..."
    
    result = processor._extract_chief_complaint(notes)
    
    assert result == "Chest pain"

def test_detect_risk_words():
    processor = NLPProcessor()
    notes = "Patient has chest pain and shortness of breath"
    
    risks = processor._detect_risk_words(notes)
    
    assert len(risks) > 0
    assert any(r["word"] == "chest pain" for r in risks)
```

**Frontend (Jest + React Testing Library)**:
```typescript
describe('CaseForm', () => {
  test('validates required fields', async () => {
    render(<CaseForm onSubmit={jest.fn()} />);
    
    const submitButton = screen.getByText('Create Case');
    fireEvent.click(submitButton);
    
    expect(await screen.findByText('Case title is required')).toBeInTheDocument();
  });
  
  test('submits form with valid data', async () => {
    const onSubmit = jest.fn();
    render(<CaseForm onSubmit={onSubmit} />);
    
    fireEvent.change(screen.getByLabelText('Case Title'), {
      target: { value: 'Test Case' }
    });
    // ... fill other fields
    
    fireEvent.click(screen.getByText('Create Case'));
    
    await waitFor(() => expect(onSubmit).toHaveBeenCalled());
  });
});
```

### 9.3 Integration Testing

**API Testing (REST Assured)**:
```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class PatientCaseControllerIntegrationTest {
    
    @LocalServerPort
    private int port;
    
    @Test
    void testCreateAndRetrieveCase() {
        // Create case
        CreateCaseRequest request = new CreateCaseRequest(
            "Test Case", 65, "Male", "Test notes"
        );
        
        String caseId = given()
            .port(port)
            .contentType(ContentType.JSON)
            .body(request)
        .when()
            .post("/api/v1/cases")
        .then()
            .statusCode(201)
            .extract().path("id");
        
        // Retrieve case
        given()
            .port(port)
        .when()
            .get("/api/v1/cases/" + caseId)
        .then()
            .statusCode(200)
            .body("caseTitle", equalTo("Test Case"));
    }
}
```

### 9.4 End-to-End Testing

**Selenium/Cypress**:
```javascript
describe('Clinical Summarizer E2E', () => {
  it('creates and summarizes a case', () => {
    cy.visit('http://localhost:3000');
    
    // Fill form
    cy.get('[name="caseTitle"]').type('E2E Test Case');
    cy.get('[name="patientAge"]').type('65');
    cy.get('[name="gender"]').select('Male');
    cy.get('[name="clinicalNotes"]').type('Test clinical notes');
    
    // Submit
    cy.get('button[type="submit"]').click();
    
    // Verify case appears in list
    cy.contains('E2E Test Case').should('be.visible');
    
    // Click to view details
    cy.contains('E2E Test Case').click();
    
    // Summarize
    cy.contains('Summarize Case').click();
    
    // Verify summary appears
    cy.contains('Chief Complaint').should('be.visible');
    cy.get('[data-testid="confidence-score"]').should('exist');
  });
});
```

### 9.5 Performance Testing

**JMeter Test Plan**:
- 50 concurrent users
- Ramp-up: 10 seconds
- Duration: 5 minutes
- Operations: Create case (40%), Get case (40%), Summarize (20%)

**Expected Results**:
- Average response time < 500ms
- 95th percentile < 2000ms
- Error rate < 1%
- Throughput > 100 requests/second

---

## 10. Data Flow Diagrams

### 10.1 Case Creation Flow

```
User → Frontend → Backend → MongoDB
  │        │         │          │
  │ Fill   │ POST    │ Insert   │ Store
  │ Form   │ /cases  │ Document │ Data
  │        │         │          │
  │        │ ◄───────┴──────────┘
  │        │   201 Created
  │ ◄──────┘
  │  Display Success
```

### 10.2 Summarization Flow

```
User → Frontend → Backend → NLP Service
  │        │         │            │
  │ Click  │ POST    │ Retrieve   │
  │Summarize│/summarize│ Case      │
  │        │         │            │
  │        │         │ POST       │ Process
  │        │         │ /summarize │ Notes
  │        │         │            │
  │        │         │ ◄──────────┘
  │        │         │   Summary
  │        │         │
  │        │         │ Update MongoDB
  │        │         │
  │        │ ◄───────┘
  │        │   200 OK + Summary
  │ ◄──────┘
  │  Display Results
```

### 10.3 Risk Detection Flow

```
Clinical Notes
      │
      ▼
┌─────────────────┐
│ Text Processing │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│Critical│ │   High   │
│ Risks  │ │  Risks   │
└────┬───┘ └────┬─────┘
     │          │
     └────┬─────┘
          │
          ▼
    ┌──────────┐
    │ Risk List│
    │ + Levels │
    └──────────┘
```

---

## 11. Future Enhancements

### 11.1 Phase 2 Architecture

**Advanced NLP Integration**:
```
┌─────────────────────────────────────────┐
│         NLP Service (Enhanced)          │
│                                         │
│  ┌──────────────┐  ┌────────────────┐ │
│  │ Rule-Based   │  │  ML Models     │ │
│  │  Processor   │  │  (BERT/GPT)    │ │
│  └──────────────┘  └────────────────┘ │
│         │                  │           │
│         └────────┬─────────┘           │
│                  │                     │
│         ┌────────▼────────┐           │
│         │  Model Router   │           │
│         │  (Ensemble)     │           │
│         └─────────────────┘           │
└─────────────────────────────────────────┘
```

### 11.2 Microservices Evolution

```
Current: Monolithic Backend
Future: Microservices

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Case       │  │Summarization │  │   Analytics  │
│   Service    │  │   Service    │  │   Service    │
└──────────────┘  └──────────────┘  └──────────────┘
       │                 │                  │
       └─────────────────┴──────────────────┘
                         │
                  ┌──────▼──────┐
                  │ API Gateway │
                  └─────────────┘
```

### 11.3 Advanced Features Roadmap

**Q1 2026**:
- User authentication (JWT)
- Role-based access control
- Audit logging
- PDF export

**Q2 2026**:
- Real MIMIC-III integration
- Advanced ML models
- Batch processing
- Analytics dashboard

**Q3 2026**:
- Mobile application
- Voice input
- Multi-language support
- Real-time collaboration

**Q4 2026**:
- HIPAA compliance
- HL7/FHIR integration
- Custom model training
- Production deployment

---

## 12. Appendices

### 12.1 Technology Justification

| Technology | Justification |
|------------|---------------|
| Spring Boot | Industry standard for Java microservices, excellent ecosystem |
| FastAPI | High performance Python framework, async support, auto-documentation |
| React | Popular, component-based, large community, TypeScript support |
| MongoDB | Flexible schema for evolving medical data, JSON-native |
| Docker | Consistent deployment, easy scaling, industry standard |
| Tailwind CSS | Utility-first, rapid development, consistent design |

### 12.2 Design Patterns Used

1. **Repository Pattern**: Data access abstraction (Backend)
2. **Service Layer Pattern**: Business logic separation (Backend)
3. **DTO Pattern**: Data transfer objects for API (Backend)
4. **Component Pattern**: Reusable UI components (Frontend)
5. **Singleton Pattern**: Service instances (Backend)
6. **Factory Pattern**: Object creation (NLP Service)
7. **Strategy Pattern**: Risk detection algorithms (NLP Service)

### 12.3 API Response Examples

**Successful Case Creation**:
```json
{
  "id": "65d1234567890abcdef12345",
  "caseTitle": "Acute Chest Pain",
  "patientAge": 65,
  "gender": "Male",
  "clinicalNotes": "Chief Complaint: Chest pain...",
  "createdAt": "2026-02-14T10:30:00Z",
  "updatedAt": "2026-02-14T10:30:00Z",
  "summary": null
}
```

**Successful Summarization**:
```json
{
  "id": "65d1234567890abcdef12345",
  "caseTitle": "Acute Chest Pain",
  "patientAge": 65,
  "gender": "Male",
  "clinicalNotes": "Chief Complaint: Chest pain...",
  "createdAt": "2026-02-14T10:30:00Z",
  "updatedAt": "2026-02-14T10:35:00Z",
  "summary": {
    "chiefComplaint": "Chest pain",
    "keyFindings": "Elevated troponin, ST elevation on EKG",
    "assessment": "Acute myocardial infarction",
    "recommendations": [
      "Immediate cardiology consultation",
      "Administer aspirin and anticoagulation",
      "Prepare for cardiac catheterization"
    ],
    "icdCodes": "I21.9, R07.9",
    "riskWords": [
      {"word": "chest pain", "level": "CRITICAL"},
      {"word": "acute mi", "level": "CRITICAL"}
    ],
    "riskFactors": [
      "Advanced age (>65)",
      "Hypertension",
      "Diabetes mellitus"
    ],
    "confidenceScore": 87,
    "metadata": {
      "processedAt": "2026-02-14T10:35:00Z",
      "modelVersion": "1.0.0",
      "processingTimeMs": 1250,
      "status": "SUCCESS"
    }
  }
}
```

### 12.4 Glossary

| Term | Definition |
|------|------------|
| **Microservices** | Architectural style with loosely coupled services |
| **REST** | Representational State Transfer API architecture |
| **DTO** | Data Transfer Object for API communication |
| **CORS** | Cross-Origin Resource Sharing for web security |
| **JWT** | JSON Web Token for authentication |
| **PHI** | Protected Health Information under HIPAA |
| **ICD** | International Classification of Diseases codes |
| **NLP** | Natural Language Processing |
| **EHR** | Electronic Health Record system |
| **FHIR** | Fast Healthcare Interoperability Resources |

---

## 13. Document Control

### 13.1 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-14 | Development Team | Initial design document |

### 13.2 Review and Approval

**Technical Review**: Completed
**Architecture Review**: Completed
**Security Review**: Pending (for production)
**Compliance Review**: Not applicable (educational use)

### 13.3 Related Documents

- `requirements.md` - Functional and non-functional requirements
- `README.md` - Project overview and quick start
- `GETTING_STARTED.md` - Setup and deployment guide
- `PROJECT_SUMMARY.md` - Project status and features

---

**Document Classification**: Educational/Demonstration Project
**Confidentiality**: Public (Open Source)
**Distribution**: Unlimited
**Last Updated**: February 14, 2026
