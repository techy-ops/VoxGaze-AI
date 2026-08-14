# VoxGaze AI

### Your eyes become the controller. Your camera becomes your voice.

VoxGaze AI is an AI-powered accessibility platform designed to explore alternative ways of communicating with and controlling digital devices for people with speech, hearing, and motor impairments.

The platform combines **eye tracking, lip reading, sign language recognition, and AI-driven intent processing** into a modular system built with React Native and FastAPI.

> Technology should adapt to the ways people can interact — not force everyone to interact in the same way.

---

## Overview

People with speech, hearing, or motor impairments can face challenges when communicating, navigating digital interfaces, or accessing assistance.

VoxGaze AI approaches this problem through multimodal computer vision and AI. Visual inputs such as **gaze, blinks, lip movements, and hand gestures** can be processed and passed through an intelligence layer for interpretation and interaction.

The system is structured into independent modules so that perception, inference, intelligence, accessibility, and communication components can evolve separately.

---

## Key Capabilities

### 👁️ Eye Tracking

Camera-based eye interaction components for:

- Gaze estimation
- Blink detection
- Facial landmark processing
- Head-pose processing
- Eye-based command handling

### 👄 Lip Reading

A dedicated video-processing pipeline for:

- Lip detection
- Video preprocessing
- Lip-reading inference
- API-based interaction

### 🤟 Sign Language Recognition

A recognition pipeline containing:

- Hand detection
- Gesture classification
- Gesture processing

### 🧠 AI Intelligence

An intelligence layer for:

- Intent processing
- Context handling
- Phrase prediction
- Command processing
- Rules-based decisions
- User behavior handling

### 🔊 Communication Services

Backend services supporting:

- GPT-based processing
- Translation
- Text-to-speech
- Firebase integration

### ♿ Accessibility & Emergency

Dedicated API modules for:

- Accessibility workflows
- Emergency workflows
- Eye tracking
- Lip reading
- Sign language
- AI interactions

---

## Architecture

```text
                         USER
                          │
                          ▼
              ┌─────────────────────┐
              │    Visual Inputs     │
              │                     │
              │  Gaze • Blink       │
              │  Lips • Gestures    │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │    AI Perception    │
              │                     │
              │  Eye Tracking       │
              │  Lip Reading        │
              │  Sign Language      │
              │  Video Processing   │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Inference Engine   │
              │                     │
              │  Model Routing      │
              │  Model Management   │
              │  Predictions        │
              │  Benchmarking        │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Intelligence Layer  │
              │                     │
              │ Intent Processing   │
              │ Context Handling    │
              │ Phrase Prediction   │
              │ Command Processing  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │     FastAPI API     │
              └──────────┬──────────┘
                         │
               ┌─────────┼─────────┐
               ▼         ▼         ▼
        Accessibility Communication Emergency
          Workflows      Services    Workflows
```

---

## Tech Stack

### Frontend

- React Native
- TypeScript
- Android Native APIs
- Camera and device interaction APIs

### Backend

- Python
- FastAPI
- Pydantic
- Uvicorn
- REST APIs

### AI & Computer Vision

- OpenCV
- MediaPipe
- PyTorch
- ONNX Runtime
- Lip-reading models
- Sign-language and gesture recognition models
- GPT-based intelligence services

### Data & Cloud

- Firebase
- Firebase Authentication
- Firebase Firestore
- Firebase Cloud Messaging

### Development

- Git & GitHub
- Pytest
- npm
- Android development tooling

---

## Project Structure

```text
VoxGaze-AI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── accessibility.py
│   │   │   ├── ai.py
│   │   │   ├── auth.py
│   │   │   ├── emergency.py
│   │   │   ├── eye_tracking.py
│   │   │   ├── gpt.py
│   │   │   ├── intelligence.py
│   │   │   ├── lip_reading.py
│   │   │   └── sign_language.py
│   │   │
│   │   ├── ai/
│   │   │   └── inference/
│   │   │       ├── base_model.py
│   │   │       ├── benchmark.py
│   │   │       ├── inference_engine.py
│   │   │       ├── model_manager.py
│   │   │       ├── model_registry.py
│   │   │       └── prediction.py
│   │   │
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── main.py
│   │
│   ├── tests/
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── android/
│   ├── ios/
│   ├── src/
│   ├── App.tsx
│   ├── package.json
│   └── README.md
│
├── .gitignore
└── README.md
```

---

## Prerequisites

Make sure the following are installed before setting up the project:

- Python 3.10+
- Node.js 18+
- npm
- Git
- Android Studio and Android SDK
- A configured Android emulator or physical Android device

For backend development, create a Python virtual environment before installing dependencies.

---

## Getting Started

Clone the repository:

```bash
git clone https://github.com/techy-ops/VoxGaze-AI.git
cd VoxGaze-AI
```

The project contains two main components:

```text
backend/   → FastAPI backend and AI services
frontend/  → React Native mobile application
```

---

## Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create and activate a virtual environment.

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your local environment file.

### Windows

```bash
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Configure the required environment variables in `.env`.

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

## Frontend Setup

Open a new terminal and navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start Metro:

```bash
npm start
```

In another terminal, run the Android application:

```bash
npm run android
```

Make sure an Android emulator is running or an Android device is connected and configured for debugging.

---

## Testing

Backend tests use **Pytest**.

From the `backend` directory:

```bash
pytest
```

Run the inference engine tests:

```bash
pytest tests/test_inference_engine.py
```

Run the model manager tests:

```bash
pytest tests/test_model_manager.py
```

Run both:

```bash
pytest tests/test_inference_engine.py tests/test_model_manager.py
```

The test suite currently covers:

- API health endpoints
- Inference pipeline execution
- Batch inference
- Model benchmarking
- Model loading and unloading
- LRU model eviction
- Hardware and device fallback
- Model manager health telemetry

---

## Development Roadmap

### Phase 1 — Core Platform

- [x] FastAPI backend foundation
- [x] React Native frontend foundation
- [x] API routing structure
- [x] Model registry
- [x] Model manager
- [x] Inference engine
- [x] Basic backend test coverage

### Phase 2 — AI Perception

- [ ] Real-time eye tracking
- [ ] Blink detection
- [ ] Lip-reading pipeline
- [ ] Sign language recognition
- [ ] Model optimization and benchmarking

### Phase 3 — Intelligence & Accessibility

- [ ] Context-aware intent processing
- [ ] Phrase prediction
- [ ] Text-to-speech interaction
- [ ] Translation workflows
- [ ] Accessibility-focused device controls

### Phase 4 — Emergency & Integration

- [ ] Emergency assistance workflows
- [ ] SOS interaction
- [ ] Location sharing
- [ ] Notification integration
- [ ] End-to-end frontend and backend integration

### Phase 5 — Optimization

- [ ] Real-time performance optimization
- [ ] Model quantization
- [ ] Improved offline capabilities
- [ ] Accessibility testing
- [ ] Production deployment

---

## Development Principles

VoxGaze AI is being developed around a few core principles:

- **Accessibility first** — interaction should adapt to different abilities.
- **Modular architecture** — perception, inference, intelligence, and services remain independently extensible.
- **Testable components** — core backend functionality is covered by automated tests.
- **Responsible AI** — AI-assisted interactions should remain predictable, transparent, and user-controlled.
- **Performance-aware design** — inference latency and resource usage are considered as the platform evolves.

---

## Contributing

Contributions, ideas, and improvements are welcome.

Create a feature branch:

```bash
git checkout -b feature/your-feature
```

Make your changes and run the relevant tests.

Stage and commit your changes:

```bash
git add .
git commit -m "feat: describe your change"
```

Push your branch:

```bash
git push origin feature/your-feature
```

Then open a pull request.

---

## License

This project is currently under active development. Licensing information will be added as the project approaches its first public release.