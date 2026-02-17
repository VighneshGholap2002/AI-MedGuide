from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.routes import summarization

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Clinical NLP Service",
    description="NLP microservice for clinical note summarization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(summarization.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Clinical NLP Service started")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Clinical NLP Service shut down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
