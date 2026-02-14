# 🏥 Clinical Note Summarizer

An AI-powered clinical note summarization system for healthcare professionals that automatically analyzes and summarizes patient cases, highlights risk factors, and generates structured clinical outputs.

## 🎯 Features

- **Automated Clinical Note Summarization**: Extract chief complaints, key findings, and assessments from clinical notes
- **Risk Detection**: Identify critical medical conditions and risk words in real-time
- **Risk Factor Analysis**: Determine patient-specific risk factors based on age, gender, medical history, and medications
- **ICD Code Generation**: Suggest relevant ICD-style codes
- **Confidence Scoring**: Provide confidence scores for summarization accuracy
- **Web UI**: Intuitive React-based interface for case management
- **REST API**: Comprehensive API for integration with EHR systems
- **Docker Support**: Easy deployment with Docker Compose

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (React)                    │
│                    (Port 3000)                           │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              Backend (Spring Boot)                       │
│              (Port 8080)                                 │
│  ├─ REST Controllers                                    │
│  ├─ Service Layer                                       │
│  └─ MongoDB Integration                                 │
└─────────────────────────────────────────────────────────┘
           ↓                              ↓
┌──────────────────────┐      ┌──────────────────────┐
│  NLP Service         │      │  MongoDB             │
│  (FastAPI)           │      │  (Port 27017)        │
│  (Port 8000)         │      │                      │
│  ├─ Note Processing  │      │  - Patient Cases     │
│  ├─ Risk Detection   │      │  - Summaries         │
│  └─ ICD Generation   │      │  - Metadata          │
└──────────────────────┘      └──────────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Spring Boot 3.1.5 (Java 17)
- **NLP Service**: FastAPI (Python 3.11)
- **Database**: MongoDB 7.0
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **API Clients**: Axios
- **Container**: Docker & Docker Compose

## 📋 Prerequisites

- Java 17+
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Maven
- MongoDB (local or via Docker)

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
cd clinical-summarizer
docker-compose -f docker/docker-compose.yml up -d
```

Services will be available at:

- Frontend: http://localhost:3000
- Backend: http://localhost:8080/api
- NLP Service: http://localhost:8000
- MongoDB: mongodb://admin:password@localhost:27017

### Option 2: Manual Setup

#### Start MongoDB

```bash
docker run -d -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo:7.0
```

#### Build and Run Backend

```bash
cd backend
mvn clean install
mvn spring-boot:run
```

#### Setup and Run NLP Service

```bash
cd nlp-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Setup and Run Frontend

```bash
cd frontend
npm install
npm start
```

## 📖 API Endpoints

### Patient Cases

- `POST /api/v1/cases` - Create a new case
- `GET /api/v1/cases` - Get all cases
- `GET /api/v1/cases/{id}` - Get case by ID
- `PUT /api/v1/cases/{id}` - Update case
- `POST /api/v1/cases/{id}/summarize` - Summarize and analyze case
- `DELETE /api/v1/cases/{id}` - Delete case

### NLP Service

- `POST /api/v1/summarize` - Process and summarize clinical notes
- `GET /api/v1/health` - Health check

## 📊 Sample Data

Import sample cases:

```bash
mongoimport --uri="mongodb://admin:password@localhost:27017/clinical_summarizer" \
  --collection=patient_cases \
  --file=data/sample_cases.json \
  --jsonArray \
  --username=admin \
  --password=password \
  --authenticationDatabase=admin
```

## 🔍 Key Features Explained

### Risk Detection

The system identifies critical medical keywords and flags them:

- **CRITICAL**: Chest pain, acute MI, stroke, sepsis, cardiac arrest
- **HIGH**: Hypertensive crisis, pulmonary embolism, acute kidney injury

### Risk Factors

Analyzes patient demographics and medical history:

- Advanced age (>65)
- Chronic conditions (diabetes, hypertension, heart disease)
- Current medications (anticoagulants, insulin)

### Confidence Scoring

Provides 0-95% confidence based on:

- Clinical note length and structure
- Presence of standard medical sections
- Number of detectable risk factors

## ⚠️ Limitations & Disclaimer

- **NOT for diagnosis** - Use only as a clinical decision support tool
- Uses synthetic and public datasets only (MIMIC-III subset)
- May miss rare or complex conditions
- Requires healthcare professional review before clinical use
- Not HIPAA-certified in current form

## 🧪 Testing

### Test Case: Chest Pain

```json
{
  "caseTitle": "Acute Chest Pain",
  "patientAge": "65",
  "gender": "Male",
  "clinicalNotes": "Chief Complaint: Chest pain. 65-year-old male with history of hypertension and diabetes presenting with acute onset substernal chest pain radiating to left arm. Associated with diaphoresis and shortness of breath."
}
```

Expected output will include:

- Risk words detection: ["chest pain", "shortness of breath"]
- Risk factors: ["Advanced age (>65)", "Hypertension", "Diabetes mellitus"]
- ICD codes: ["R07.9", "I10", "E11.9"]
- High confidence score (80+)

## 📁 Project Structure

```
clinical-summarizer/
├── backend/                    # Spring Boot application
│   ├── src/main/java/
│   ├── src/main/resources/
│   └── pom.xml
├── nlp-service/               # Python FastAPI service
│   ├── app/
│   ├── requirements.txt
│   └── README.md
├── frontend/                  # React application
│   ├── src/
│   ├── public/
│   └── package.json
├── docker/                    # Docker configuration
│   ├── Dockerfile.backend
│   ├── Dockerfile.nlp
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── data/                      # Sample data
│   └── sample_cases.json
└── README.md
```

## 🔄 Workflow

1. **Create Case**: Fill in patient information and clinical notes
2. **Upload**: System stores case in MongoDB
3. **Summarize**: Click "Summarize" to trigger NLP processing
4. **NLP Processing**: FastAPI service analyzes the notes
5. **Risk Detection**: Identifies critical keywords and risk factors
6. **Generate Output**: Creates structured summary with ICD codes
7. **Review**: Display results with confidence scores

## 💡 Advanced Features

### Highlight Risk Words

Risk keywords are highlighted in red with risk level:

- 🔴 CRITICAL - Requires immediate attention
- 🟠 HIGH - Significant concern

### Structured JSON Output

All responses include structured data for EHR integration:

```json
{
  "caseId": "...",
  "summary": {
    "chiefComplaint": "...",
    "keyFindings": "...",
    "assessment": "...",
    "recommendations": [...],
    "icdCodes": "..."
  },
  "riskWords": [...],
  "riskFactors": [...],
  "confidenceScore": 85
}
```

## 🤝 Contributing

This is a demonstration project for hackathon/educational purposes. Feel free to extend with:

- Integration with actual MIMIC-III dataset
- Advanced NLP models (BERT, GPT-4)
- HIPAA compliance measures
- More detailed ICD code mapping
- Multi-language support

## 📝 License

MIT License - Use for educational and research purposes

## 🏥 Healthcare Notice

This tool is provided for educational and demonstration purposes only. It is NOT suitable for production clinical use without proper regulatory approval, clinical validation, and compliance with healthcare standards and regulations.

## 📞 Support

For issues or questions, please create an issue in the repository.

---

**Built with ❤️ for healthcare professionals**
