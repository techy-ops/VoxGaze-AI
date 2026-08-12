# VoxGaze AI

### Your eyes become the controller. Your camera becomes your voice.

VoxGaze AI is an AI-powered accessibility platform designed to explore alternative ways of communicating with and controlling digital devices for people with speech, hearing, and motor impairments.

The platform combines **eye tracking, lip reading, sign language recognition, and AI-driven intent processing** into a modular system built with a React Native frontend and a FastAPI backend.

> **VoxGaze AI explores a simple idea: technology should adapt to the ways people can interact — not force everyone to interact in the same way.**

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

# Architecture

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
              │  Intelligence Layer │
              │                     │
              │  Intent Processing  │
              │  Context Engine     │
              │  Phrase Prediction  │
              │  Command Processing │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │     FastAPI API     │
              └──────────┬──────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        Accessibility Communication Emergency
          Workflows      Services    Workflows