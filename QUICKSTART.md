# 🏥 Clinical Note Summarizer - Quick Reference Guide

## 📁 Complete Project Structure

```
clinical-summarizer/
│
├── 📄 README.md                          # Main project documentation
├── 📄 setup.sh                           # Linux/Mac setup script
├── 📄 setup.bat                          # Windows setup script
│
├── 📁 backend/                           # Spring Boot API Layer
│   ├── pom.xml                           # Maven configuration
│   ├── README.md                         # Backend documentation
│   ├── .gitignore
│   └── src/main/
│       ├── java/com/clinical/summarizer/
│       │   ├── ClinicalSummarizerApplication.java      # Main class
│       │   ├── controller/
│       │   │   └── PatientCaseController.java          # REST endpoints
│       │   ├── service/
│       │   │   ├── SummarizationService.java           # Business logic
│       │   │   ├── SummarizationRequest.java
│       │   │   └── SummarizationResponse.java
│       │   ├── model/
│       │   │   ├── PatientCase.java                    # MongoDB entity
│       │   │   └── Summary.java
│       │   ├── repository/
│       │   │   └── PatientCaseRepository.java          # Database access
│       │   └── config/
│       └── resources/
│           └── application.yml                         # Configuration
│
├── 📁 nlp-service/                       # Python FastAPI Microservice
│   ├── requirements.txt                  # Python dependencies
│   ├── README.md                         # NLP service documentation
│   ├── .gitignore
│   └── app/
│       ├── main.py                       # FastAPI app
│       ├── models/
│       │   └── schemas.py                # Pydantic models
│       ├── services/
│       │   └── nlp_processor.py          # NLP logic
│       └── routes/
│           └── summarization.py          # API endpoints
│
├── 📁 frontend/                          # React TypeScript UI
│   ├── package.json                      # NPM configuration
│   ├── tsconfig.json                     # TypeScript configuration
│   ├── README.md                         # Frontend documentation
│   ├── .gitignore
│   ├── public/
│   │   └── index.html                    # HTML template
│   └── src/
│       ├── App.tsx                       # Main component
│       ├── App.css
│       ├── index.tsx                     # React root
│       ├── index.css
│       ├── services/
│       │   └── api.ts                    # API client
│       └── components/
│           ├── CaseForm.tsx              # Create case form
│           ├── CaseList.tsx              # Cases listing
│           └── CaseDetail.tsx            # Case details & results
│
├── 📁 docker/                            # Container Configuration
│   ├── docker-compose.yml                # All services orchestration
│   ├── Dockerfile.backend                # Spring Boot image
│   ├── Dockerfile.nlp                    # FastAPI image
│   └── Dockerfile.frontend               # React image
│
├── 📁 data/                              # Sample Data
│   ├── sample_cases.json                 # MIMIC-III based samples
│   └── import_samples.sh                 # MongoDB import script
```

## 🚀 Quick Start Commands

### Using Docker Compose (Recommended)

```bash
cd clinical-summarizer
docker-compose -f docker/docker-compose.yml up -d
```

### Manual Setup - Linux/Mac

```bash
cd clinical-summarizer
chmod +x setup.sh
./setup.sh
```

### Manual Setup - Windows

```bash
cd clinical-summarizer
setup.bat
```

## 🌐 Service URLs

| Service     | URL                                      | Port  | Purpose        |
| ----------- | ---------------------------------------- | ----- | -------------- |
| Frontend    | http://localhost:3000                    | 3000  | React UI       |
| Backend API | http://localhost:8080/api                | 8080  | REST API       |
| NLP Service | http://localhost:8000                    | 8000  | NLP Processing |
| MongoDB     | mongodb://admin:password@localhost:27017 | 27017 | Database       |

## 📚 Key Technologies

| Layer             | Technology  | Version |
| ----------------- | ----------- | ------- |
| Backend API       | Spring Boot | 3.1.5   |
| Backend Language  | Java        | 17      |
| NLP Service       | FastAPI     | 0.104.1 |
| NLP Language      | Python      | 3.11    |
| Frontend          | React       | 18.2.0  |
| Frontend Language | TypeScript  | 5.3.0   |
| Database          | MongoDB     | 7.0     |
| Container         | Docker      | Latest  |

## 🔌 API Endpoints

### Patient Cases (/api/v1/cases)

| Method | Endpoint                       | Action              |
| ------ | ------------------------------ | ------------------- |
| POST   | `/api/v1/cases`                | Create new case     |
| GET    | `/api/v1/cases`                | List all cases      |
| GET    | `/api/v1/cases/{id}`           | Get case details    |
| PUT    | `/api/v1/cases/{id}`           | Update case         |
| POST   | `/api/v1/cases/{id}/summarize` | Analyze & summarize |
| DELETE | `/api/v1/cases/{id}`           | Delete case         |
| GET    | `/api/v1/cases/health`         | Health check        |

### NLP Service (/api/v1)

| Method | Endpoint            | Purpose                |
| ------ | ------------------- | ---------------------- |
| POST   | `/api/v1/summarize` | Process clinical notes |
| GET    | `/api/v1/health`    | Service status         |

## 📝 Request/Response Example

### Create Case

```bash
curl -X POST http://localhost:8080/api/v1/cases \
  -H "Content-Type: application/json" \
  -d '{
    "caseTitle": "Acute Chest Pain",
    "patientAge": "65",
    "gender": "Male",
    "clinicalNotes": "Chief Complaint: Chest pain..."
  }'
```

### Summarize Case

```bash
curl -X POST http://localhost:8080/api/v1/cases/{id}/summarize
```

### Response

```json
{
  "id": "...",
  "summary": {
    "chiefComplaint": "Chest pain",
    "keyFindings": "...",
    "assessment": "...",
    "recommendations": ["..."],
    "icdCodes": "R07.9, I21.9"
  },
  "riskWords": ["chest pain", "shortness of breath"],
  "riskFactors": ["Advanced age (>65)", "Hypertension"],
  "confidenceScore": 87
}
```

## 🏥 Features & Capabilities

### Core Features

✅ Clinical note summarization
✅ Risk word detection (CRITICAL/HIGH)
✅ Risk factor analysis
✅ ICD code generation
✅ Confidence scoring
✅ Case management (CRUD)

### Advanced Features

✅ Structured JSON output for EHR
✅ Patient demographic consideration
✅ Medical history analysis
✅ Real-time processing
✅ Web-based UI
✅ RESTful API
✅ Docker deployment

## ⚠️ Important Limitations

- **NOT for clinical diagnosis** - Use only as decision support
- Uses synthetic/public data (MIMIC-III subset)
- May miss rare conditions
- Requires healthcare professional review
- Not HIPAA-certified in current form
- No authentication implemented

## 🔧 Troubleshooting

### MongoDB Connection Failed

```bash
# Check if MongoDB is running
docker ps | grep mongo

# Start MongoDB if not running
docker run -d -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo:7.0
```

### NLP Service Timeout

- Check if FastAPI service is running (`http://localhost:8000/api/v1/health`)
- Increase timeout in `backend/src/main/resources/application.yml`
- Check Python service logs

### Frontend Not Connecting to API

- Ensure backend is running on port 8080
- Check CORS settings in `backend/src/main/resources/application.yml`
- Clear browser cache and reload

### Build Failed

```bash
# Clean and rebuild
cd backend && mvn clean install
cd ../nlp-service && rm -rf venv && python -m venv venv
cd ../frontend && rm -rf node_modules && npm install
```

## 📊 Sample Test Cases

Located in `data/sample_cases.json`:

1. **Acute Myocardial Infarction** (68M)
2. **Community-Acquired Pneumonia** (54F)
3. **Diabetic Ketoacidosis** (19M)
4. **Sepsis from UTI** (76F)
5. **Acute Ischemic Stroke** (72M)

Import samples:

```bash
mongoimport --uri="mongodb://admin:password@localhost:27017/clinical_summarizer" \
  --collection=patient_cases \
  --file=data/sample_cases.json \
  --jsonArray \
  --username=admin \
  --password=password \
  --authenticationDatabase=admin
```

## 🔐 Security Notes

### Current Implementation

- No authentication (for demo purposes)
- No encryption
- Minimal validation

### Production Recommendations

- Add JWT authentication
- Encrypt sensitive data
- Implement rate limiting
- Add comprehensive logging
- Use HTTPS/SSL
- Implement HIPAA compliance
- Add audit trails
- Use secrets management

## 📚 Development Resources

- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Docker Documentation](https://docs.docker.com/)

## 🤝 Extension Ideas

1. **Real MIMIC-III Dataset** - Integrate actual anonymized data
2. **Advanced NLP** - Use BERT or GPT models for better summarization
3. **Multi-language Support** - Add language translation
4. **User Authentication** - Add account management
5. **Export Features** - Generate PDF/Word reports
6. **Analytics Dashboard** - Case statistics and trends
7. **Batch Processing** - Handle multiple cases at once
8. **Model Training** - Custom model for specific hospital workflows
9. **Mobile App** - React Native mobile version
10. **Voice Input** - Speech-to-text for case creation

## 📞 Support

For questions, issues, or contributions:

1. Check existing documentation
2. Review sample cases
3. Check service logs
4. Verify all services are running
5. Test with simple cases first

---

**Built for healthcare professionals | Demo purposes only | Not for clinical diagnosis**
