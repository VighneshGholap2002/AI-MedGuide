@echo off
REM Clinical Note Summarizer - Complete Setup Guide for Windows

echo 🏥 Clinical Note Summarizer - Windows Setup Guide
echo ==================================================
echo.

REM Check requirements
echo 📋 Checking requirements...

where docker >nul 2>nul
if ERRORLEVEL 1 (
    echo ❌ Docker not found. Please install Docker Desktop for Windows.
    exit /b 1
)

where java >nul 2>nul
if ERRORLEVEL 1 (
    echo ❌ Java not found. Please install Java 17+
    exit /b 1
)

where mvn >nul 2>nul
if ERRORLEVEL 1 (
    echo ❌ Maven not found. Please install Maven
    exit /b 1
)

echo ✅ All requirements met!
echo.

REM Build backend
echo 🏗️ Building Backend (Spring Boot)...
cd backend
call mvn clean install -q
cd ..
echo ✅ Backend built successfully!
echo.

REM Setup NLP service
echo 🔧 Setting up NLP Service (Python)...
cd nlp-service
if not exist "venv" (
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt -q
)
echo ✅ NLP Service ready!
echo.
cd ..

REM Setup frontend
echo 📦 Installing Frontend dependencies...
cd frontend
call npm install -q
cd ..
echo ✅ Frontend ready!
echo.

echo 🚀 Start the services with:
echo.
echo Option 1 - Docker Compose (Recommended):
echo   docker-compose -f docker/docker-compose.yml up -d
echo.
echo Option 2 - Manual (4 terminals):
echo.
echo Terminal 1 - MongoDB:
echo   docker run -d -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password mongo:7.0
echo.
echo Terminal 2 - Backend:
echo   cd backend ^&^& mvn spring-boot:run
echo.
echo Terminal 3 - NLP Service:
echo   cd nlp-service ^&^& venv\Scripts\activate.bat ^&^& python -m uvicorn app.main:app --reload
echo.
echo Terminal 4 - Frontend:
echo   cd frontend ^&^& npm start
echo.
echo Access the application at: http://localhost:3000
