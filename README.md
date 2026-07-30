# Vehicle License Plate Registration, Recognition, and Verification System

A FastAPI backend powering an AI-based Vehicle License Plate Recognition System. It provides secure authentication, vehicle management, OCR processing, and license plate detection.

## Features

- FastAPI app startup with CORS and router registration.
- PostgreSQL access through SQLAlchemy engine/session setup.
- Alembic migrations for `users` and `vehicles`.
- JWT login, current user lookup, inactive-user blocking, Swagger OAuth password-flow login.
- Role-based backend access through `require_roles`.
- Vehicle CRUD: list, create, update, delete, lookup by plate.
- Vehicle search, status filter, vehicle type filter, sorting, pagination.
- Dashboard stats from vehicle counts and recent registrations.
- Image upload recognition endpoint using YOLO, OpenCV preprocessing, EasyOCR, candidate scoring, and debug image output.
- Verification by plate number and verification after image recognition.
- Admin/officer privacy filtering in verification responses.
- React login, protected routes, role routes, dashboard layout, vehicle table/form/dialogs, recognition upload/results/candidates, verification display, toast errors.

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

## Repository Structure

```text
vehicle-plate-api/
  requirements.txt
  README.md
  alembic.ini
  alembic/
    env.py
    versions/
      f46a8393affa_initial_migration.py
      802a7651598e_create_users_table.py
      7fa86e489685_create_vehicles_table.py
  app/
    main.py
    ai/models/license_plate.pt
    config/
      database.py
      security.py
      settings.py
    dependencies/
      auth.py
      pagination.py
      vehicle.py
    exceptions/
      vehicle.py
      verification.py
    models/
      base.py
      enums.py
      mixins.py
      user.py
      vehicle.py
      verification.py
    routers/
      auth.py
      dashboard.py
      recognition.py
      test.py
      vehicle.py
      verification.py
    schemas/
      auth.py
      dashboard.py
      recognition.py
      user.py
      vehicle.py
      verification.py
    services/
      auth.py
      dashboard.py
      detector.py
      image_processing.py
      ocr.py
      recognition.py
      vehicle.py
      verification.py
    static/.gitkeep
    uploads/.gitkeep
    utils/debug.py
```

# Chapter 1 - High-Level System Overview

The application manages registered vehicles and helps officers/admins recognize and verify license plates.

The three core concepts are:

- Registration: storing a vehicle and owner record in PostgreSQL.
- Recognition: reading a plate number from an uploaded image using YOLO, OpenCV, and EasyOCR.
- Verification: checking whether a plate number exists in the registered vehicle database and returning role-aware details.

The backend is responsible for:

- Authentication and authorization.
- Database access.
- Vehicle business rules.
- Recognition and verification pipelines.
- Privacy filtering before data leaves the server.

The frontend is responsible for:

- Login forms and session state.
- Role-based page routing.
- Vehicle table, filters, forms, details, and delete confirmation.
- Image upload, preview, recognition display, OCR candidate selection, manual correction, and verification result display.

Main request architecture:

```text
Browser
  |
  v
React page/component
  |
  v
src/api/client.ts
  |
  v
FastAPI router
  |
  v
Service layer
  |
  v
SQLAlchemy session
  |
  v
PostgreSQL
```

Recognition and verification architecture:

```text
Frontend image upload
  |
  v
POST /recognition/image
  |
  v
RecognitionService
  |
  +--> ImageProcessingService: validate, decode, crop, grayscale, resize, threshold
  +--> PlateDetectionService: YOLO bounding box
  +--> OCRService: EasyOCR, cleanup, candidate scoring
  |
  v
RecognitionResponse
  |
  v
Frontend calls GET /verification/{plate}
  |
  v
VerificationService
  |
  v
VehicleService -> vehicles table
```

Roles:

- Admin: can access admin routes, create/update vehicles, delete vehicles, verify plates, and receive full owner phone/address in verification.
- Officer: can access officer routes, create/update vehicles, verify plates, and receive masked owner details in verification.

# Chapter 2 - Repository and Folder Structure

```text
vehicle-plate-api/  -> FastAPI backend
```

## Backend folders

`app/config`

- Owns settings, database setup, and security helpers.
- Other layers depend on this folder for environment settings, database sessions, password hashing, and JWT utilities.

`app/models`

- Owns SQLAlchemy ORM classes.
- Models describe database tables, columns, constraints, indexes, and relationships.
- Services and migrations depend on these definitions.

`app/schemas`

- Owns Pydantic request and response models.
- Routers use schemas as API contracts.
- Schemas intentionally differ from SQLAlchemy models because API input/output should not expose every persistence detail.

`app/services`

- Owns business logic.
- Routers call services instead of putting all behavior directly inside HTTP handlers.
- Examples: `VehicleService`, `VerificationService`, `RecognitionService`.

`app/routers`

- Owns HTTP routes, path parameters, query parameters, dependencies, and HTTP status codes.
- Routers should be thin: parse request, call service, translate known exceptions to `HTTPException`.

`app/dependencies`

- Owns reusable FastAPI dependencies such as `get_current_user`, `require_roles`, pagination params, and vehicle lookup by ID.

`app/exceptions`

- Owns domain-specific exception classes.
- Currently vehicle exceptions are used; verification exceptions file is empty.

`app/ai/models`

- Stores the YOLO model file: `license_plate.pt`.

`app/utils`

- Contains `debug.py`, which saves intermediate recognition images to a local `debug/` folder.

`alembic`

- Tracks database schema migrations.
- Current migrations create the `users` and `vehicles` tables.

# Chapter 3 - Complete End-to-End Workflow

## Registered vehicle workflow

```text
1. Officer logs in.
   Files:
   - src/pages/auth/Login.tsx
   - src/context/AuthProvider.tsx
   - src/api/auth.ts
   - app/routers/auth.py
   - app/services/auth.py

2. Officer opens recognition page.
   Files:
   - src/App.tsx
   - src/routes/ProtectedRoute.tsx
   - src/routes/RoleRoute.tsx
   - src/pages/officer/Recognition.tsx
   - src/components/recognition/RecognitionPage.tsx

3. Officer uploads image.
   Files:
   - UploadCard.tsx
   - src/schemas/recognition.ts
   - src/api/recognition.ts

4. Backend recognizes image.
   Files:
   - app/routers/recognition.py
   - app/services/recognition.py
   - app/services/detector.py
   - app/services/image_processing.py
   - app/services/ocr.py

5. Frontend verifies best plate.
   Files:
   - RecognitionPage.tsx
   - src/api/verification.ts
   - app/routers/verification.py
   - app/services/verification.py
   - app/services/vehicle.py

6. Backend returns registered vehicle.
   Files:
   - app/schemas/verification.py
   - src/components/verification/VerificationCard.tsx
   - VehicleSummary.tsx
   - OwnerInfo.tsx
```

## Unknown vehicle workflow

```text
1. Recognition returns a plate.
2. Verification returns found=false.
3. VerificationCard shows "Vehicle not registered".
4. User clicks Register vehicle.
5. RecognitionPage opens VehicleForm with initialPlateNumber.
6. VehicleForm submits POST /vehicles.
7. onSuccess calls verifyPlate(selectedPlate).
8. VerificationCard re-renders as registered.
```

Key frontend connection:

Path: `vehicle-plate/src/components/recognition/RecognitionPage.tsx`

```tsx
<VehicleForm
  open={vehicleFormOpen}
  vehicle={null}
  initialPlateNumber={selectedPlate}
  onSuccess={() => {
    void handleRegistrationSuccess();
  }}
/>
```

# Chapter 4 - Error Handling

## Backend error flow

Common mechanisms:

- Pydantic validation errors: automatic FastAPI 422 responses.
- `HTTPException`: explicit status code and message.
- Domain exceptions: converted in routers.
- Recognition `ValueError`: invalid image/no plate/no OCR result.
- Recognition unexpected errors: converted to runtime/500 paths.

Path: `vehicle-plate-api/app/routers/vehicle.py`

```python
except VehicleAlreadyExistsError as exc:
  raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail=str(exc),
  )
```

Path: `vehicle-plate/src/api/client.ts`

```ts
if (!response.ok) {
  let message = "Something went wrong.";
  let details;

  if (typeof error.detail === "string") {
    message = error.detail;
  } else if (Array.isArray(error.detail)) {
    message = "Validation failed.";
    details = error.detail;
  }

  throw new ApiClientError(message, response.status, details);
}
```

What it does:

- Converts backend errors into JavaScript exceptions.
- Preserves validation details for later UI use.

## Error table

| Scenario | Backend status | Backend source | Frontend behavior |
|---|---:|---|---|
| Invalid login | 401 | `routers/auth.py` | Login page toast displays error |
| Inactive user login | 403 | `routers/auth.py` | Login page toast displays error |
| Invalid/missing token | 401 | `dependencies/auth.py` | Auth initialization logs out and navigates to login |
| Wrong role | 403 | `require_roles` or `require_verification_role` | Toast error or unauthorized page if blocked by frontend route |
| Duplicate plate | 409 | `VehicleService` -> `routers/vehicle.py` | Vehicle form toast displays message |
| Invalid vehicle body | 422 | Pydantic/FastAPI | API client message is "Validation failed." |
| Vehicle by ID missing | 404 | `get_vehicle` dependency | Toast error in delete/update flow |
| Vehicle by plate missing | 404 | `routers/vehicle.py` | Lookup API throws; verification endpoint instead returns `found=false` |
| Invalid image type | 400 or 422 | `ImageProcessingService` via recognition/verification router | Recognition page toast displays message |
| No plate detected | 400 or 422 | `RecognitionService` | Recognition page toast displays message |
| OCR returns no candidates | 400 or 422 | `RecognitionService` | Recognition page toast displays message |
| Slow request | client-side error | `AbortController` in `apiClient` | Toast displays timeout message |

Frontend components often reset loading in `finally`, for example `VehicleForm`, `LoginPage`, `RecognitionPage`, and `DashboardPage`.

# Chapter 5 - Architectural Decisions

| Decision | Benefit | Trade-off | Alternative | Why reasonable for this |
|---|---|---|---|---|
| Routers for HTTP concerns | Keeps request/response code localized | Some simple routes still contain logic | Put everything in services | Current split is readable |
| Services for business logic | Reusable from multiple routers | Needs discipline to avoid thin wrappers | Fat routers | Verification reuses VehicleService cleanly |
| Schemas for API contracts | Separates API shape from DB shape | Duplicate field names | Return ORM objects directly | Safer and clearer |
| Models for persistence | One ORM source of table truth | ORM learning curve | Raw SQL | SQLAlchemy is suitable for CRUD-heavy app |
| Dependencies for auth and DB | Reusable request lifecycle | FastAPI-specific pattern | Manual calls in each route | Reduces repetition |
| Shared frontend API client | Consistent headers/errors/timeouts | Central bug affects all calls | Raw fetch everywhere | Best fit for small frontend |
| Shared dashboard layout | Consistent admin/officer shell | Some role-specific nuance is hidden | Separate layouts | Current roles are similar |
| Singleton AI services | Avoid repeated model loading | Startup memory/time cost | Load per request | Necessary for YOLO/EasyOCR performance |
| Separate recognition and verification | Supports correction and re-verification | More endpoints/concepts | Single monolithic scan endpoint | Better mental model and reuse |
| Normalized plate numbers | Reliable lookup and duplicate checks | Loses formatting | Store raw and normalized separately | MVP benefits from one canonical key |
| Role-aware backend response | Privacy enforced at source | More response-building code | Hide fields in frontend | Backend is the security boundary |
| Unique plate constraint | Protects data integrity | Database insert may still fail in races | Service-only duplicate check | Correct final guard |
| Sync SQLAlchemy sessions | Simple and common | Blocks worker while DB call runs | Async SQLAlchemy | Fine for MVP scale |
| Do not store images in vehicle table | Vehicle records stay small | No historical image audit | Store image metadata/history | Recognition is separate from registration |
| Plate number as lookup key | Matches business workflow | Plates can change in real life | Internal vehicle identifier or VIN | Plate verification is central use case |

# Chapter 6 - Testing Guide

## Manual backend tests

1. Start backend with `uvicorn app.main:app --reload` from `vehicle-plate-api`.
2. Open `/docs`.
3. Test `/auth/swagger-login` through Swagger Authorize.
4. Call `GET /auth/me` after authorizing.
5. Create a vehicle through `POST /vehicles`.
6. Create the same plate again and confirm 409.
7. Update a vehicle through `PATCH /vehicles/{vehicle_id}`.
8. Delete as admin and confirm 204.
9. Try delete as officer and confirm 403.
10. Test `GET /vehicles?search=Toyota&status=ACTIVE&vehicle_type=SUV&sort=-registration_date`.
11. Test pagination with `page` and `page_size`.
12. Test `GET /verification/{plate}` as admin and officer; compare owner fields.
13. Test an unknown plate and confirm `found=false`.
14. Create an expired registration and confirm verification returns `EXPIRED`.
15. Upload invalid file type to recognition and confirm an error.
16. Upload a valid vehicle image and inspect recognition response fields.

# Glossary

- API contract: The agreed request or response shape between frontend and backend.
- Bearer token: A token sent in the `Authorization` header as proof of authentication.
- Bounding box: Coordinates around a detected object in an image.
- CORS: Browser security rules controlling cross-origin HTTP calls.
- Dependency: In FastAPI, a reusable function that provides request-time values or checks.
- Effective status: Status calculated at response time, such as marking a past-expiry vehicle as expired.
- FormData: Browser object used for multipart file uploads.
- JWT: Signed token that stores claims like user ID and expiration.
- Migration: Versioned database schema change.
- Model: SQLAlchemy class that maps to a database table.
- OCR: Optical character recognition, used here to read plate text from an image.
- ORM: Object relational mapper, a library that maps Python classes to database rows.
- Pydantic schema: Python validation model used for API input/output.
- Router: FastAPI object that groups related endpoints.
- Service layer: Code that holds business rules independent of HTTP details.
- Stored status: The status saved directly in the database row.
- Zod schema: TypeScript validation schema used by frontend forms.
