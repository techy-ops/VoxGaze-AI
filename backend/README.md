# VoxGaze AI Backend

VoxGaze AI is a production-grade AI accessibility platform backend built with Python and FastAPI, following clean architecture, modular design, and dependency injection patterns.

## Project Structure

```
backend/
├── app/
│   ├── api/          # API Route Controllers (Auth, Eye Tracking, Lip Reading, Sign Language, GPT, Emergency, Accessibility)
│   ├── services/     # Core Business Service abstractions (Firebase, GPT, TTS, Translation)
│   ├── models/       # Domain Entities & Models
│   ├── schemas/      # Pydantic Schemas for Input/Output validation
│   ├── utils/        # Logger and operational utilities
│   ├── middleware/   # Custom FastAPI middleware (Logging, Performance execution timing)
│   ├── config.py     # Environment settings using python-dotenv & pydantic-settings
│   ├── database.py   # Database engine and session lifecycle manager
│   ├── dependencies.py # Dependency injection providers for FastAPI routes
│   └── main.py       # FastAPI application entrypoint with CORS & middleware setup
├── tests/            # Pytest suite covering all API endpoints
├── .env.example      # Example environment variables
├── requirements.txt  # Project Python dependencies
└── README.md
```

## Running the Application

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Start Development Server
```bash
uvicorn app.main:app --reload
```

The API server will run at `http://127.0.0.1:8000`.

### 4. Interactive API Documentation
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## Automated Testing

Run unit & integration tests using `pytest`:
```bash
pytest tests/
```
