# Backend README

## Spring Boot Clinical Summarizer API

REST API backend for clinical note summarization using Spring Boot and MongoDB.

### Requirements

- Java 17+
- Maven 3.8+
- MongoDB 7.0+

### Setup

1. **Configure application.yml**
   - Update MongoDB URI if not using default localhost
   - Adjust NLP service URL if running on different port

2. **Build**

   ```bash
   mvn clean install
   ```

3. **Run**
   ```bash
   mvn spring-boot:run
   ```

The API will be available at `http://localhost:8080/api`

### Application Configuration

File: `src/main/resources/application.yml`

Key properties:

- `spring.data.mongodb.uri` - MongoDB connection string
- `nlp-service.url` - URL of the NLP microservice
- `nlp-service.timeout` - Request timeout in milliseconds

### Project Structure

```
backend/
├── src/main/java/com/clinical/summarizer/
│   ├── ClinicalSummarizerApplication.java    # Main entry point
│   ├── config/                                # Configuration classes
│   ├── controller/                            # REST controllers
│   ├── service/                               # Business logic
│   ├── model/                                 # Data models
│   └── repository/                            # MongoDB repositories
└── src/main/resources/
    └── application.yml                        # Application properties
```

### API Endpoints

#### Create Case

```http
POST /api/v1/cases
Content-Type: application/json

{
  "caseTitle": "Chest Pain Case",
  "patientAge": "65",
  "gender": "Male",
  "clinicalNotes": "Patient presents with..."
}
```

#### Get All Cases

```http
GET /api/v1/cases
```

#### Get Case by ID

```http
GET /api/v1/cases/{id}
```

#### Update Case

```http
PUT /api/v1/cases/{id}
Content-Type: application/json
```

#### Summarize Case

```http
POST /api/v1/cases/{id}/summarize
```

#### Delete Case

```http
DELETE /api/v1/cases/{id}
```

#### Health Check

```http
GET /api/v1/cases/health
```

### Database Schema

**patient_cases collection:**

```json
{
  "_id": ObjectId,
  "caseTitle": String,
  "patientAge": String,
  "gender": String,
  "clinicalNotes": String,
  "summary": {
    "chiefComplaint": String,
    "keyFindings": String,
    "assessment": String,
    "recommendations": [String],
    "icdCodes": String
  },
  "riskFactors": [String],
  "riskWords": [String],
  "confidenceScore": Integer,
  "metadata": Map,
  "createdAt": Date,
  "updatedAt": Date
}
```

### Exception Handling

The API returns standard HTTP status codes:

- `200 OK` - Successful GET, PUT
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation errors
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server errors

### Logging

Logging is configured in `application.yml`:

- Root level: INFO
- Application level: DEBUG

Logs are output to console with timestamp and message format.

### Performance

- Async processing for summarization using WebFlux
- Connection pooling for MongoDB
- Configurable timeouts for external service calls
- CORS enabled for frontend integration
