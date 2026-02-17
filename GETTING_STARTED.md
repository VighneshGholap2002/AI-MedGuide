# Getting Started with Clinical Note Summarizer

Welcome! This guide will get you up and running quickly.

## ⏱️ 5-Minute Quick Start (Docker)

### Prerequisites

- Docker Desktop installed
- 4GB RAM available

### Steps

1. Navigate to project directory:

   ```bash
   cd clinical-summarizer
   ```

2. Start all services:

   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

3. Wait 30 seconds for services to initialize

4. Open browser: **http://localhost:3000**

5. Try the demo:
   - Copy sample clinical notes from `data/sample_cases.json`
   - Click "Create Case"
   - Fill in the form
   - Click "Summarize Case"
   - View results!

## 🛠️ 15-Minute Manual Setup (Windows)

### Step 1: Start MongoDB

```bash
docker run -d -p 27017:27017 ^
  -e MONGO_INITDB_ROOT_USERNAME=admin ^
  -e MONGO_INITDB_ROOT_PASSWORD=password ^
  mongo:7.0
```

### Step 2: Build and Run Backend (Terminal 1)

```bash
cd backend
mvn clean install
mvn spring-boot:run
```

✅ Backend ready at http://localhost:8080/api

### Step 3: Run NLP Service (Terminal 2)

```bash
cd nlp-service
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

✅ NLP Service ready at http://localhost:8000

### Step 4: Start Frontend (Terminal 3)

```bash
cd frontend
npm install
npm start
```

✅ Frontend ready at http://localhost:3000

## 🧪 Testing the Application

### Option 1: Upload Clinical Notes

1. Go to "Create New Case" form
2. Fill in patient info:
   - Case Title: "Chest Pain Case"
   - Age: 65
   - Gender: Male
3. Paste clinical notes (from samples)
4. Click "Create Case"
5. Select case from list
6. Click "Summarize Case"
7. View results with:
   - ⚠️ Risk words highlighting
   - 📋 Structured summary
   - 📊 Confidence score
   - 🏥 ICD codes

### Option 2: Use Sample Data

```bash
# Import pre-made sample cases
mongoimport --uri="mongodb://admin:password@localhost:27017/clinical_summarizer" \
  --collection=patient_cases \
  --file=data/sample_cases.json \
  --jsonArray \
  --username=admin \
  --password=password \
  --authenticationDatabase=admin
```

Then refresh frontend to see 5 sample cases.

## 🔍 Understanding the Flow

```
┌─────────────────────────────────────────┐
│  You upload clinical notes via UI       │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Frontend sends to Backend (Spring Boot)│
│  POST /api/v1/cases                     │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Backend stores in MongoDB              │
│  Then calls NLP Service                 │
│  POST /api/v1/cases/{id}/summarize      │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  NLP Service (FastAPI) processes notes: │
│  ✓ Extract chief complaint              │
│  ✓ Find key findings                    │
│  ✓ Detect risk words (CRITICAL/HIGH)    │
│  ✓ Identify risk factors                │
│  ✓ Generate ICD codes                   │
│  ✓ Calculate confidence score           │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Results sent back to Backend           │
│  Backend updates MongoDB                │
│  Response sent to Frontend              │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Frontend displays beautiful results    │
│  with risk highlighting and details     │
└─────────────────────────────────────────┘
```

## 📊 Sample Clinical Note

Try this sample in the form:

```
Chief Complaint: Chest pain

History of Present Illness:
65-year-old male presenting with acute onset crushing substernal chest pain
radiating to left arm lasting 30 minutes. Associated with diaphoresis and
shortness of breath. Patient has history of hypertension and diabetes.

Physical Examination:
BP 155/95, HR 105, RR 22, O2 sat 94%
Anxious, diaphoretic
Cardiac: Tachycardia
Lungs: Bilateral crackles

Initial Labs:
EKG: ST elevation in leads II, III, aVF
Troponin I: 2.8 ng/mL (elevated)
```

### Expected Results:

- ✅ Risk words: "chest pain", "shortness of breath"
- ⚠️ Risk factors: Advanced age, Hypertension, Diabetes
- 🏥 ICD codes: R07.9, I10, E11.9
- 📈 Confidence: 85-90%

## 📚 Project Structure

Each component is independent:

**Backend** (`/backend`)

- Handles REST APIs
- Manages database
- Coordinates with NLP service
- Returns structured responses

**NLP Service** (`/nlp-service`)

- Processes clinical notes
- Extracts information
- Detects risks
- Generates codes

**Frontend** (`/frontend`)

- React UI
- Case management
- Results display
- Real-time updates

**Database** (`MongoDB`)

- Stores patient cases
- Stores summaries
- Persistent storage

## 🔧 Configuration

### Backend Settings

File: `backend/src/main/resources/application.yml`

Key settings:

```yaml
spring.data.mongodb.uri: mongodb://localhost:27017/clinical_summarizer
nlp-service.url: http://localhost:8000
nlp-service.timeout: 30000
```

### Frontend Settings

File: `frontend/src/services/api.ts`

```typescript
const API_BASE_URL = "http://localhost:8080/api";
```

## ❓ Common Issues & Fixes

### Issue: Backend won't start

```bash
# Solution: Clean build
cd backend
mvn clean install
mvn spring-boot:run
```

### Issue: NLP service timeout

```bash
# Check if running
curl http://localhost:8000/api/v1/health

# If not running
cd nlp-service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Issue: Frontend can't connect

```bash
# Check backend health
curl http://localhost:8080/api/v1/cases/health

# If needed, clear browser cache
# Open http://localhost:3000 in incognito mode
```

### Issue: MongoDB errors

```bash
# Check if running
docker ps | grep mongo

# Restart MongoDB
docker stop clinical-mongodb
docker rm clinical-mongodb
docker run -d -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo:7.0
```

## 🎓 Learning Resources

### Understanding the Stack

1. **Spring Boot** - Backend Framework
   - Handles HTTP requests
   - Manages CRUD operations
   - Coordinates between services

2. **FastAPI** - NLP Service Framework
   - Fast Python framework
   - Processes text
   - Returns JSON

3. **React** - Frontend Framework
   - User interface
   - Real-time updates
   - Component-based

4. **MongoDB** - NoSQL Database
   - Stores documents
   - Flexible schema
   - JSON-like storage

5. **Docker** - Containerization
   - Packages services
   - Ensures consistency
   - Simplifies deployment

## 🚀 Next Steps

1. ✅ Try basic functionality with sample data
2. ✅ Create own test case
3. ✅ Explore API endpoints with Postman
4. ✅ Review code structure
5. ✅ Experiment with modifying risk keywords
6. ✅ Consider adding authentication
7. ✅ Plan extensions (PDF export, etc.)

## 📞 Need Help?

### Check Documentation

- Main README: `README.md`
- Quick Reference: `QUICKSTART.md`
- Backend Docs: `backend/README.md`
- Frontend Docs: `frontend/README.md`
- NLP Service Docs: `nlp-service/README.md`

### Check Logs

```bash
# Backend logs - visible in terminal where mvn runs
# NLP Service logs - visible in terminal where uvicorn runs
# Frontend logs - check browser console (F12)
# MongoDB logs - check docker logs
```

### Use Sample Data

```json
5 pre-built cases ready in: data/sample_cases.json
- Myocardial Infarction
- Pneumonia
- Diabetic Ketoacidosis
- Sepsis
- Stroke
```

## ✅ Checklist

Before diving in, ensure:

- [ ] Docker is installed and running
- [ ] Java 17+ installed
- [ ] Maven installed
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] 4GB+ RAM available
- [ ] Ports 3000, 8000, 8080, 27017 are free

## 🎉 You're Ready!

```bash
# One-command start (if using Docker):
docker-compose -f docker/docker-compose.yml up -d

# Then visit: http://localhost:3000

# Happy coding! 🚀
```

---

**Questions?** Check the main README or service-specific documentation in each folder.
