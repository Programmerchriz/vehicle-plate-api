# Vehicle Plate Recognition System — Backend

A FastAPI backend powering an AI-based Vehicle License Plate Recognition System. It provides secure authentication, vehicle management, OCR processing, license plate detection, search history, and audit logging.

## Features

- JWT Authentication
- Role-Based Authorization
- Vehicle CRUD
- Vehicle Search
- License Plate Detection (YOLOv8)
- OCR Recognition (EasyOCR)
- OCR Cleaning
- Vehicle Verification
- Search History
- Audit Logs
- PostgreSQL Database
- Docker Support

## Tech Stack

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic
- Passlib
- Python-JOSE
- OpenCV
- Ultralytics YOLOv8
- EasyOCR

## Project Structure

```
app/
├── config/
├── dependencies/
├── models/
├── routers/
├── schemas/
├── services/
├── utils/
└── main.py
```

## Getting Started

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it and install dependencies:

```bash
pip install -r requirements.txt
```

Run the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```
http://localhost:8000
```

Interactive API documentation:

```
http://localhost:8000/docs
```

## Frontend Repository

The backend exposes REST APIs consumed by the React frontend.