# Django Tech Challenge - Accommodation Booking API

Welcome to the Django implementation of Buoy's accommodation booking tech challenge!

This repository contains a **partially implemented accommodations booking REST API**, designed as a work-in-progress prototype for a real-world application.

You must use the provided code sample and its dependencies to solve the problems explained below.

The solution must be a cloud git repository, hosted on any cloud git tool of your choice.

- Its first commit must:
  - Have the message "First commit"
  - Have the exact code sample as it was provided, no changes whatsoever
- From this point on, work on the problems exposed below as you like

NOTE: In case you want to create a private git repository, please grant the user matthew@buoydevelopment.com full access to the repo. If you do so, please make it clear once you reply with your answer.

---

# Current implementation (added by author)

## Summary
- Accommodation types: hotel/apartment; apartments block overlapping bookings, hotels allow overlaps.
- Availability API returns the next available date for apartments; hotels accept overlaps and return the requested date.
- Voice notes: multipart upload saved to local storage, async transcription via Celery + RabbitMQ using OpenAI Whisper; status goes pending → succeeded/failed.
- Dependency Injector wires file storage and transcription service.

## Available endpoints
- Accommodations:
  - `GET/POST /accommodations/`
  - `GET/PUT/PATCH/DELETE /accommodations/<id>/`
  - `GET /accommodations/<id>/availability?date=YYYY-MM-DD`
- Bookings:
  - `GET/POST /bookings/`
  - `GET/PUT/PATCH/DELETE /bookings/<id>/`
- Voice Notes (nested under bookings):
  - `GET /bookings/<booking_id>/voice-notes/`
  - `POST /bookings/<booking_id>/voice-notes/` (multipart `audio_file`) → saves file and enqueues transcription
  - `GET /bookings/<booking_id>/voice-notes/<id>/`
  - `DELETE /bookings/<booking_id>/voice-notes/<id>/`

## Data models
- `Accommodation`: type (hotel/apartment), name, description, price, location.
- `Booking`: FK to accommodation, start_date, end_date, guest_name.
- `VoiceNote`: FK to booking, transcript, status (pending/succeeded/failed), file_name, file_type; storage key derived from booking/id.

## Project structure (top-level)
- `accommodation_booking/` — Django project, settings, DI container, Celery app.
- `accommodations/` — accommodations app (models/serializers/views/tests).
- `bookings/` — bookings + voice notes (models/serializers/views/tests).
- `data/` — local storage path for voice-note audio (mounted via volume).
- `compose.yml`, `Dockerfile`, `requirements*.txt`, `env.example` — infra and dependencies.

## Environment variables (used)
- Core: `DEBUG`, `SECRET_KEY`
- Database: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- Celery: `CELERY_BROKER_URL` (fire-and-forget; no result backend configured)
- OpenAI: `OPENAI_API_KEY`, `OPENAI_MODEL` (default `whisper-1`), `OPENAI_LANGUAGE` (default `en`)
- Storage: `LOCAL_FILE_STORAGE_DIRECTORY` (default `./data`, shared volume for web/worker)
- Transcription: `TRANSCRIPTION_PROVIDER` (default `local`, but can be set to `openai`)

## Local setup (Docker Compose)
1) Copy `env.example` to `.env` and adjust values.  
2) Build and start services (web, worker, RabbitMQ, Postgres):
   ```bash
   docker compose up --build
   ```
3) Apply migrations:
   ```bash
   docker compose run --rm web python manage.py migrate
   ```
4) API: http://localhost:8006  
   RabbitMQ UI: http://localhost:15672 (user/pass: `rabbitmq` / `rabbitmq`)

---

# Problem #1

### Issue to solve

There's an Accommodations entity already in place, however the business model only includes Hotels and Apartments.

### Expected behaviour

- Add these 2 new entities to the project.
- Provide endpoints for their management.

# Problem #2

### Issue to solve

Currently, every Accommodation can contain several overlapping Bookings with the same `start_date` and `end_date`. This makes sense for Hotels, which can have different Rooms booked simultaneously, but it wouldn't work for Apartments.

### Expected behaviour

- Apartments should not allow overlapping bookings during the same period (`start_date` and `end_date`).
- Hotels should allow overlapping bookings during the same period, as these would correspond to bookings for different rooms within the hotel.

# Problem #3

### Issue to solve

If frontend needs to, given an accommodation's `id` and a `date`, retrieve the next available date for that accommodation.

### Question

- How would you solve this problem?
- What data or API would you provide to the frontend?

# Problem #4 – Voice Notes (Voice-to-Text Extension)

> **Context**  
> As this API grows, accommodation operators and support agents want to move faster when capturing contextual information about a booking (special requests, incident reports, hand-off notes between shifts, etc.). Typing out these notes is slow and often skipped; they’d prefer to speak into their phone or laptop and have the system store both the original audio and a clean text transcript.

### Business Goal

Enable staff to attach short **voice notes** to a booking so that:

- A staff member can **record a brief audio note** related to a specific booking.
- The system **transcribes that audio to text** using a voice-to-text service.
- Other staff can **view the transcription alongside the original booking**, and (optionally) download or listen to the original audio file.

This section is intentionally open-ended: you may choose any tools, libraries, services, or architecture you believe are appropriate.

---

### Functional Requirements

#### 1. Attach a Voice Note to a Booking

- Given an existing booking, the system must allow a client to submit a short audio clip associated with that booking.
- Audio may be uploaded as a file (e.g., `.wav`, `.mp3`, `.m4a`, etc.).
- You are free to design the endpoint(s), but they should be **REST-ful** and consistent with the project’s existing API style.

#### 2. Transcribe the Audio

- The system must send the audio to a **voice-to-text (VTT) service** of your choice and store the resulting transcription.
- The transcription must be persisted in the database and clearly associated with:
  - the booking  
  - the original audio resource
- You may implement transcription **synchronously** (request blocks until complete) or **asynchronously** (background worker, queue, webhook, etc.).
- Document your choice and the trade-offs.

#### 3. Retrieve a Booking’s Voice Notes

- A client must be able to retrieve a booking and see **all voice notes** associated with it, including at least:
  - an identifier  
  - the transcript text  
  - creation timestamp  
- Optionally expose a way to download or play the original audio file.

---

### Technical & Design Guidelines

You are free to choose:

#### Voice-to-Text Provider

Any API or library is acceptable (cloud-hosted or local), provided that:

- The integration is **cleanly encapsulated** behind an interface or abstraction.
- The README includes instructions for running the transcription step locally (API keys, environment variables, etc.).

#### API Design

You may introduce new resources (e.g., nested routes under `bookings`) or extend existing endpoints.  
The design should be:

- consistent with REST principles  
- discoverable and documented  
- aligned with the project’s conventions  

#### Implementation Details

You choose how to:

- model voice notes in the database  
- structure Django/DRF components (serializers, viewsets, services, storage, etc.)  
- handle background work (if used)

The goal is not to pick the “right” VTT provider, but to demonstrate **how** you structure a clean, testable integration.

---

### What We’ll Be Looking For

#### API & Data Modeling

- Clear, extensible API surface  
- Data model that accommodates multiple notes per booking and future enhancements

#### Integration Design

- VTT provider wrapped in a clean abstraction  
- Ability to swap providers with minimal rewriting

#### Error Handling & Edge Cases

- Handling of failed transcription attempts  
- Validation for unsupported audio formats  
- Clear feedback to API consumers  

#### Testing & Observability

- Meaningful tests (mocking external services is fine)  
- Helpful logging for debugging failures  

#### Documentation & Developer Experience

- Notes describing:
  - chosen VTT provider  
  - local configuration instructions  
  - assumptions and limitations  

---

### Scope & Timeboxing

This extension should not double the scope of the exercise.

- Favor a small, well-designed slice over an exhaustive system.
- Reasonable simplifying assumptions are acceptable (e.g., max audio length, limited file formats).
- If the VTT provider requires paid usage, document how we can still verify your integration using free tiers, test modes, or clear stubs/mocks.

# Problem #5 (For Applied ML Candidates Only) — ML Systems Design Add-On

This section is required only for candidates applying to Applied ML / ML Engineering roles.  
It is intentionally short and should take no more than 30–45 minutes.

The purpose is to understand your real-world experience operating ML systems and how you reason about ML architecture, performance, and trade-offs. We are not looking for long essays—short, clear bullet points are preferred.

Where relevant, please reference concrete details from systems you have actually built or operated. We will explore your answers in detail during the live interview.

---

### Part A — Prior Experience (Real-World Applied ML Work)

In 5–10 bullet points, describe a production ML-powered system you have personally built or operated.  
This can be in ASR/VTT, OCR, NLP, RAG, ranking, fraud detection, or any other ML domain.

Please include (at least):

1. What the system did (e.g., OCR pipeline, streaming ASR, retrieval system, fraud detection).  
2. Your exact role and what parts you owned.  
3. Traffic characteristics (throughput, request sizes, concurrency, latency targets, etc.).  
4. Infrastructure / compute details:  
   - CPU vs GPU  
   - instance types  
   - memory/latency constraints  
   - batching strategy (if applicable)  
5. Key bottlenecks or incidents you encountered in production.  
6. Observability:  
   - how you monitored inference  
   - metrics you tracked (latency, drift, error rates, etc.)  
7. What you would do differently with the benefit of hindsight.

---

### Part B — Voice-to-Text System Architecture (Applied to This Project)

Using the voice-notes feature from Problem #4, outline how you would design a production-ready voice-to-text subsystem if the product needed to scale beyond the single-app architecture used in the take-home.

You may answer in bullet points.  
Keep this section to 1–2 pages maximum.

Include:

1. High-level architecture:  
   - where transcription happens (inline vs async vs separate microservice)  
   - data flow from API → storage → transcription → callbacks → persistence  

2. Model/provider selection:  
   - hosted API (OpenAI Whisper, Deepgram, etc.) vs self-hosted models  
   - trade-offs of your choice  
   - how you would switch providers if necessary  

3. Performance considerations:  
   - expected latency and throughput  
   - GPU vs CPU inference choices and rationale  
   - batching, streaming, or chunking strategies  

4. Scalability strategy:  
   - autoscaling approach  
   - concurrency limits  
   - worker vs pod model  
   - queue selection (if used)  

5. Observability:  
   - metrics and logs you would capture  
   - how you would track failures, retries, and slowdowns  
   - how you would detect drift or degradation  

6. Failure handling and degraded modes:  
   - behavior when transcription fails  
   - retry strategy  
   - how to handle corrupted audio or timeouts  
   - fallback behavior to maintain system utility  

7. Security and compliance considerations:  
   - storage approach for audio  
   - retention policy  
   - considerations for PII or sensitive audio content  

---

### Part C — Optional Architecture Sketch

If helpful, include a simple diagram showing your proposed architecture.  
A hand-drawn sketch, Mermaid diagram, or ASCII diagram is acceptable.

---

### Notes

- Do not overthink this section. We are evaluating how you think, not how long you spend writing.  
- Specificity is preferred over polished writing.  
- It is acceptable to note assumptions or unknowns.  


---


## TECH CONTEXT
### Stack

The main libraries are:
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django ORM](https://docs.djangoproject.com/en/5.0/topics/db/)

### Docker Setup
To set up the project using Docker Compose, follow these steps:

1. Ensure you have Docker and Docker Compose installed on your machine.
2. Build and start the Docker containers:

  ```bash
  docker compose up --build
  ```

3. The application should now be running and accessible at `http://localhost:8006`.

### Swagger Documentation

The interactive API documentation is available at:
```
http://localhost:8006/documentation/
```

### Migrations

Migrations are automatically applied when the Docker containers start via the `entrypoint.sh` script.

For manual migration management during development:

#### Migration creation
1. Stop the web container: `docker compose stop web`
2. Run the migration creation command: 
   ```bash
   docker compose run --rm web python manage.py makemigrations
   ```
3. Restart containers: `docker compose up`

#### Manual Migration Up
```bash
docker compose run --rm web python manage.py migrate
```

#### Manual Migration Down
```bash
docker compose run --rm web python manage.py migrate <app_name> <migration_number>
```

## 🚀 Current Implementation

### Available Endpoints

#### Accommodations
- `GET /accommodations/` - List all accommodations
- `POST /accommodations/` - Create accommodation
- `GET /accommodations/{id}/` - Get accommodation by ID
- `PUT /accommodations/{id}/` - Update accommodation
- `DELETE /accommodations/{id}/` - Delete accommodation

#### Bookings
- `GET /bookings/` - List all bookings
- `POST /bookings/` - Create booking
- `GET /bookings/{id}/` - Get booking by ID
- `PUT /bookings/{id}/` - Update booking
- `DELETE /bookings/{id}/` - Delete booking

### Current Data Models

#### Accommodation (Base Model)
```json
{
    "id": 1,
    "name": "Luxury Hotel Downtown",
    "description": "A beautiful hotel in the city center",
    "price": "150.00",
    "location": "Downtown"
}
```

#### Booking
```json
{
    "id": 1,
    "accommodation": 1,
    "start_date": "2024-02-01",
    "end_date": "2024-02-05",
    "guest_name": "John Doe"
}
```

## 🔧 Development Setup

### Docker Development (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd tech-challenge-python
   ```

2. **Start with Docker Compose**:
   ```bash
   docker compose up --build
   ```

3. **Access the application**:
   - API: `http://localhost:8006`
   - Documentation: `http://localhost:8006/documentation/`
   - Admin: `http://localhost:8006/admin/`

### Local Development (without Docker)

1. **Prerequisites**:
   - Python 3.11+
   - PostgreSQL 15+

2. **Install PostgreSQL** (if not already installed):
   ```bash
   # macOS with Homebrew
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install postgresql postgresql-contrib
   sudo systemctl start postgresql
   
   # Windows - Download from https://www.postgresql.org/download/windows/
   ```

3. **Create database**:
   ```bash
   # Connect to PostgreSQL as superuser
   sudo -u postgres psql
   
   # Or on macOS/Windows where postgres user might be your username:
   psql postgres
   
   # Create database and user
   CREATE DATABASE accommodation_booking;
   CREATE USER postgres WITH ENCRYPTED PASSWORD 'postgres';
   GRANT ALL PRIVILEGES ON DATABASE accommodation_booking TO postgres;
   \q
   ```

4. **Setup Python environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env file with your database settings if different from defaults
   ```

7. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

8. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

9. **Start development server**:
   ```bash
   python manage.py runserver 8006
   ```

10. **Access the application**:
    - API: `http://localhost:8006`
    - Documentation: `http://localhost:8006/documentation/`
    - Admin: `http://localhost:8006/admin/` (if superuser created)

## 📁 Project Structure

```
tech-challenge-python/
├── accommodation_booking/     # Django project settings
│   ├── __init__.py
│   ├── settings.py           # Configuration with PostgreSQL
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py              # WSGI application
│   └── asgi.py              # ASGI application
├── accommodations/           # Accommodations app
│   ├── migrations/          # Database migrations
│   ├── models.py            # Accommodation model
│   ├── serializers.py       # DRF serializers with validation
│   ├── views.py            # Accommodation views
│   ├── urls.py             # URL routing
│   ├── admin.py            # Admin configuration
│   └── apps.py             # App configuration
├── bookings/                # Bookings app
│   ├── migrations/          # Database migrations
│   ├── models.py           # Booking model
│   ├── serializers.py      # Booking serializers
│   ├── views.py           # Booking CRUD operations
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   └── apps.py            # App configuration
├── requirements.txt        # Python dependencies
├── docker compose.yml     # Docker services configuration
├── Dockerfile            # Docker image definition
├── entrypoint.sh         # Docker entrypoint script
├── env.example          # Environment variables template
├── manage.py           # Django management commands
└── README.md          # This documentation
```

Additional structure (Clean Architecture Inspired):
- `accommodation_booking/application/` — application layer
  - `protocols/` — interfaces (e.g., `file_storage`, `transcription_service`, `voice_note_repository`)
  - `commands/` — orchestrations for background work (e.g., `transcribe_voice_note.py`)
  - `usecases/` — use-case services (e.g., `create_voice_note.py`)
- `accommodation_booking/infrastructure/` — implementations of application protocols
  - `local/file_storage.py` — local storage backend (uses `LOCAL_FILE_STORAGE_DIRECTORY`)
  - `openai/transcription_service.py` — Whisper-based transcription via OpenAI API
- `accommodation_booking/container.py` — dependency injection wiring (providers for storage, transcription, use cases)

## 🌐 Environment Variables

Create a `.env` file based on `env.example`:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CELERY_BROKER_URL` | Celery broker (RabbitMQ) | `amqp://rabbitmq:rabbitmq@rabbitmq:5672//` | No |
| `DB_HOST` | Database host | `localhost` | No |
| `DB_NAME` | Database name | `accommodation_booking` | No |
| `DB_PASSWORD` | Database password | `postgres` | No |
| `DB_PORT` | Database port | `5432` | No |
| `DB_USER` | Database user | `postgres` | No |
| `DEBUG` | Enable debug mode | `True` | No |
| `LOCAL_FILE_STORAGE_DIRECTORY` | Path for voice-note audio storage | `./data` | No |
| `OPENAI_API_KEY` | API key for transcription | _none_ | Yes (to transcribe if `openai` provider selected) |
| `OPENAI_LANGUAGE` | Default transcription language | `en` | No |
| `OPENAI_MODEL` | Whisper model | `whisper-1` | No |
| `SECRET_KEY` | Django secret key | `django-insecure-your-secret-key-here` | Yes (change in production) |
| `TRANSCRIPTION_PROVIDER` | Select between `local` and `openai` transcription provider | `local` | No |

## 📡 Available Endpoints (implemented)
- Accommodations:
  - `GET/POST /accommodations/`
  - `GET/PUT/PATCH/DELETE /accommodations/<id>/`
  - `GET /accommodations/<id>/availability?date=YYYY-MM-DD`
- Bookings:
  - `GET/POST /bookings/`
  - `GET/PUT/PATCH/DELETE /bookings/<id>/`
- Voice Notes (nested under bookings):
  - `GET /bookings/<booking_id>/voice-notes/`
  - `POST /bookings/<booking_id>/voice-notes/` (multipart `audio_file`)
  - `GET /bookings/<booking_id>/voice-notes/<id>/`
  - `DELETE /bookings/<booking_id>/voice-notes/<id>/`

## 🗂️ Data Models (implemented)
- `Accommodation`: type (hotel/apartment), name, description, price, location.
- `Booking`: FK accommodation, start_date, end_date, guest_name; apartments block overlaps.
- `VoiceNote`: FK booking, transcript, status (pending/succeeded/failed), file_name, file_type; storage key derived from booking/id.

## 🧪 Testing the API

You can test the API using the interactive documentation at `http://localhost:8006/documentation/` or use curl:

```bash
# List accommodations
curl http://localhost:8006/accommodations/

# Create an accommodation
curl -X POST http://localhost:8006/accommodations/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Hotel",
    "description": "A test hotel",
    "price": "100.00",
    "location": "Test City"
  }'

# List bookings
curl http://localhost:8006/bookings/

# Create a booking (replace {accommodation_id} with actual ID)
curl -X POST http://localhost:8006/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "accommodation": 1,
    "start_date": "2024-03-01",
    "end_date": "2024-03-05",
    "guest_name": "John Doe"
  }'
```

---

## 🚨 Current Dependencies

The project uses the following key dependencies (see `requirements.txt` for versions):

- `Django==5.0.0` - Web framework
- `djangorestframework==3.14.0` - REST API framework
- `psycopg2-binary==2.9.9` - PostgreSQL adapter
- `drf-spectacular==0.27.0` - API documentation
- `django-cors-headers==4.3.1` - CORS handling
- `python-dotenv==1.0.0` - Environment variable management 
- `dependency-injector==4.48.2` - Dependency injection containers for Python
- `requests==2.32.5` - Synchronous HTTP requests
- `celery==5.5.3` - Command queue
- `faster-whisper==1.2.1` - Local transcription provider

---

## 🔧 Current Development Dependencies

- `django-stubs==5.2.7` - Django annotatted types
- `black==25.11.0` - Code formatting
- `isort==7.0.0` - Organize imports

---

# Solution overview (added by author)

## Current implementation
- Accommodation types: hotel/apartment; apartments block overlapping bookings; hotels allow overlaps.
- Availability endpoint returns the next available date for apartments, immediate date for hotels.
- Voice notes: multipart upload saved to local storage, async transcription via Celery + RabbitMQ using OpenAI Whisper; status transitions pending → succeeded/failed.
- DI (dependency-injector) wires file storage and transcription service.

## Stack
- Django + DRF, Postgres, RabbitMQ, Celery (fire-and-forget), OpenAI Whisper for transcription.
- Voice notes: upload stored on a shared local volume (`data/`); Celery worker reads the file and transcribes asynchronously.
- Dependency Injector wires `file_storage` (local) and `transcription_service` (OpenAI).

## Environment variables
- `DEBUG`  
- `SECRET_KEY`  
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`  
- `CELERY_BROKER_URL` (e.g. `amqp://rabbitmq:rabbitmq@rabbitmq:5672//`)  
- `OPENAI_API_KEY`, `OPENAI_MODEL` (default `whisper-1`), `OPENAI_LANGUAGE` (default `en`)  
- `LOCAL_FILE_STORAGE_DIRECTORY` (default `./data`, shared volume path)

## Run locally (Docker Compose)
1) Copy `env.example` to `.env` and adjust values.  
2) Build and start services (web, worker, RabbitMQ, Postgres):
   ```bash
   docker compose up --build
   ```
3) Apply migrations:
   ```bash
   docker compose run --rm web python manage.py migrate
   ```
4) API: http://localhost:8006  
   RabbitMQ UI: http://localhost:15672 (user/pass: `rabbitmq` / `rabbitmq`)

## Available endpoints
- Accommodations:  
  - `GET/POST /accommodations/`  
  - `GET/PUT/PATCH/DELETE /accommodations/<id>/`  
  - `GET /accommodations/<id>/availability?date=YYYY-MM-DD`
- Bookings:  
  - `GET/POST /bookings/`  
  - `GET/PUT/PATCH/DELETE /bookings/<id>/` (apartments block overlapping dates)
- Voice Notes (nested):  
  - `GET /bookings/<booking_id>/voice-notes/`  
  - `POST /bookings/<booking_id>/voice-notes/` (multipart `audio_file`) → saves file locally and enqueues transcription  
  - `GET /bookings/<booking_id>/voice-notes/<id>/`  
  - `DELETE /bookings/<booking_id>/voice-notes/<id>/`

## Current data models
- `Accommodation`: type (hotel/apartment), name, description, price, location.
- `Booking`: FK to accommodation, start_date, end_date, guest_name (ordering by id).
- `VoiceNote`: FK to booking, transcript, status (pending/succeeded/failed), file_name, file_type; storage key derived from booking/id.

## Project structure (top-level)
- `accommodation_booking/` — Django project, settings, DI container, Celery app.
- `accommodations/` — app for accommodations (models, serializers, views, tests).
- `bookings/` — app for bookings and voice notes (models, serializers, views, tests).
- `data/` — local storage path for voice-note audio (mounted via volume).
- `compose.yml`, `Dockerfile`, `requirements*.txt`, `env.example` — infra and dependencies.

## Voice notes flow
- Upload `multipart/form-data` with `audio_file`.  
- Accepted audio MIME types: `audio/mpeg`, `audio/mp3`, `audio/mpga`, `audio/mpeg3`, `audio/mp4`, `audio/aac`, `audio/x-aac`, `audio/wav`, `audio/x-wav`, `audio/flac`, `audio/x-flac`, `audio/ogg`, `audio/opus`, `audio/webm`.  
- Video MIME types remapped: `video/mp4`, `video/mpeg`, `video/webm`.  
- Status lifecycle: `pending` → `succeeded` or `failed`. Files stored as `booking########-voicenote########` under `data/`.

## Design notes
- Problem #3: availability endpoint returns `{accommodation_id, next_available_date}`; apartments scan bookings for the first gap, hotels allow overlaps and return the requested date.  
- Problem #4: async chosen to avoid blocking web workers on long transcribes; sync would be simpler but ties up threads/processes for full audio duration.

## Tests
```bash
docker compose run --rm web python manage.py test
```


## Known caveats / TODOs
- Celery runs fire-and-forget (no result backend). If you need task result tracking, enable a backend (Redis/RPC) and adjust settings.

---

