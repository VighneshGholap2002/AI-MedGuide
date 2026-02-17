# NLP Service

Fast API-based microservice for clinical note processing and summarization.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /api/v1/summarize` - Summarize clinical notes
- `GET /api/v1/health` - Health check
