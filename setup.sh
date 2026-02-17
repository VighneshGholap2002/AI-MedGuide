#!/bin/bash

echo "🏥 Clinical Note Summarizer - Complete Setup Guide"
echo "=================================================="
echo ""

# Check requirements
echo "📋 Checking requirements..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi

if ! command -v java &> /dev/null; then
    echo "❌ Java not found. Please install Java 17+"
    exit 1
fi

if ! command -v mvn &> /dev/null; then
    echo "❌ Maven not found. Please install Maven"
    exit 1
fi

echo "✅ All requirements met!"
echo ""

# Build backend
echo "🏗️  Building Backend (Spring Boot)..."
cd backend
mvn clean install -q
cd ..
echo "✅ Backend built successfully!"
echo ""

# Setup NLP service
echo "🔧 Setting up NLP Service (Python)..."
cd nlp-service
if [ ! -d "venv" ]; then
    python -m venv venv
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    pip install -r requirements.txt -q
fi
echo "✅ NLP Service ready!"
echo ""

cd ..

# Setup frontend
echo "📦 Installing Frontend dependencies..."
cd frontend
npm install -q
cd ..
echo "✅ Frontend ready!"
echo ""

echo "🚀 Start the services with:"
echo ""
echo "Option 1 - Docker Compose (Recommended):"
echo "  docker-compose -f docker/docker-compose.yml up -d"
echo ""
echo "Option 2 - Manual (3 terminals):"
echo ""
echo "Terminal 1 - MongoDB (already running via Docker):"
echo "  docker run -d -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password mongo:7.0"
echo ""
echo "Terminal 2 - Backend:"
echo "  cd backend && mvn spring-boot:run"
echo ""
echo "Terminal 3 - NLP Service:"
echo "  cd nlp-service && source venv/bin/activate && python -m uvicorn app.main:app --reload"
echo ""
echo "Terminal 4 - Frontend:"
echo "  cd frontend && npm start"
echo ""
echo "Access the application at: http://localhost:3000"
echo ""
