# ☁️ CloudImage — Cloud Image Processing Service

> A production-style, secure, API-first image processing platform built with **FastAPI, PostgreSQL, AWS S3, JWT authentication, Pillow, SQLAlchemy, and Alembic**.

CloudImage allows authenticated users to upload images, securely store them in private AWS S3 storage, perform image transformations, retrieve transformed files through temporary presigned URLs, and manage their image library through a RESTful API.

---

## 🚀 Features

### 🔐 Authentication & Security

- User registration and login
- JWT-based authentication
- Argon2 password hashing
- Protected image APIs
- User-specific resource authorization
- Generic authentication error messages
- Private AWS S3 bucket
- Temporary S3 presigned URLs
- File size validation
- MIME type validation
- Image integrity validation
- Image dimension limits
- Maximum pixel-count protection
- Environment-based secrets
- Sensitive credentials excluded from Git

### 🖼️ Image Management

- Upload images
- Retrieve image metadata
- List user images
- Pagination
- Search by filename
- Filter by image format
- Sort by:
  - Newest
  - Oldest
  - Largest
  - Smallest
- Generate secure image access URLs
- Delete images
- Delete associated transformations

### 🎨 Image Transformations

Supported transformations include:

- Resize
- Crop
- Rotate
- Flip
- Mirror
- Grayscale
- Sepia
- Watermark
- Format conversion
- Quality control

Supported formats:

- JPEG
- PNG
- WebP
- GIF

### ⚡ Transformation Caching

CloudImage generates a deterministic transformation hash using **SHA3-256**.

If the same transformation is requested again:

```text
User Request
     ↓
Transformation Hash
     ↓
Database Cache Lookup
     ↓
 ┌───────────────┐
 │ Cached Result │──→ Return existing result
 └───────────────┘
          │
          ↓ cache miss
   Process Image
          ↓
      Upload S3
          ↓
       Save DB
```

This avoids unnecessary image processing and duplicate S3 uploads.

### ☁️ AWS S3 Storage

Images are stored in a private AWS S3 bucket.

Storage structure:

```text
users/
├── {user_id}/
│   ├── images/
│   │   ├── <uuid>.jpg
│   │   ├── <uuid>.png
│   │   └── ...
│   │
│   └── transformations/
│       ├── <uuid>.jpg
│       ├── <uuid>.webp
│       └── ...
```

The application does **not** expose the S3 bucket publicly.

Instead, it generates temporary presigned URLs:

```text
Private S3 Object
       ↓
FastAPI
       ↓
Presigned URL
       ↓
Client
```

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │       Client        │
                         │ Swagger / Frontend  │
                         └──────────┬──────────┘
                                    │
                                    │ HTTPS / REST API
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │     API Layer       │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
             ┌────────────┐  ┌────────────┐  ┌──────────────┐
             │   Auth     │  │   Image    │  │Transformation│
             │  Service   │  │  Service   │  │   Service    │
             └─────┬──────┘  └─────┬──────┘  └──────┬───────┘
                   │               │                │
                   │               │                │
                   ▼               ▼                ▼
             ┌─────────────────────────────────────────────┐
             │                  PostgreSQL                  │
             │ Users / Images / Transformations            │
             └──────────────────────┬──────────────────────┘
                                    │
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       AWS S3        │
                         │   Private Objects   │
                         └─────────────────────┘
```

---

# 🧰 Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| API Framework | FastAPI |
| Validation | Pydantic |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database Migration | Alembic |
| Image Processing | Pillow |
| Object Storage | AWS S3 |
| AWS SDK | Boto3 |
| Authentication | JWT |
| Password Hashing | Argon2 |
| Configuration | Pydantic Settings |
| Logging | Python Logging |
| API Documentation | Swagger / OpenAPI |
| Testing | Pytest |
| Version Control | Git / GitHub |

---

# 📁 Project Structure

```text
CloudImage/
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── app/
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── dependencies.py
│   │   ├── health.py
│   │   └── image.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── database.py
│   │   ├── logging.py
│   │   └── security.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── image.py
│   │   └── transformation.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── image.py
│   │   ├── image_query.py
│   │   └── transformation.py
│   │
│   ├── services/
│   │   ├── file_service.py
│   │   ├── image_service.py
│   │   ├── image_validator.py
│   │   └── transformation_service.py
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   └── s3_storage.py
│   │
│   ├── utils/
│   │   ├── cache_utils.py
│   │   ├── file_utils.py
│   │   ├── hash_utils.py
│   │   ├── image_utils.py
│   │   └── storage_key.py
│   │
│   └── main.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

---

# 🔄 Image Processing Pipeline

## Upload Flow

```text
Client
  │
  │ Upload Image
  ▼
FastAPI
  │
  ├── File Size Validation
  │
  ├── MIME Type Validation
  │
  ├── Pillow Image Validation
  │
  ├── Dimension Validation
  │
  ├── Pixel Count Validation
  │
  ▼
Temporary File
  │
  ▼
AWS S3
  │
  ▼
PostgreSQL
  │
  ▼
API Response
```

---

# 🎨 Transformation Pipeline

```text
Original Image
      │
      ▼
TransformationRequest
      │
      ▼
Generate SHA3-256 Hash
      │
      ▼
Check Database Cache
      │
 ┌────┴─────┐
 │          │
Hit        Miss
 │          │
 ▼          ▼
Return    Download
Existing    from S3
Result       │
             ▼
      Apply Transformations
             │
             ▼
       Encode Output
             │
             ▼
        Upload to S3
             │
             ▼
       Save Metadata
             │
             ▼
       Return Result
```

---

# 🗄️ Database Design

## Users

```text
users
├── id
├── username
├── email
├── password_hash
└── created_at
```

## Images

```text
images
├── id
├── user_id
├── original_filename
├── storage_key
├── mime_type
├── format
├── width
├── height
├── file_size
├── created_at
└── updated_at
```

## Image Transformations

```text
image_transformations
├── id
├── image_id
├── user_id
├── transformation_hash
├── storage_key
├── format
├── mime_type
├── width
├── height
├── file_size
└── created_at
```

Relationship:

```text
User
 │
 └──< Images
        │
        └──< Transformations
```

---

# 🔐 AWS S3 Security

The S3 bucket is configured as **private**.

The application's IAM user requires only object-level permissions:

```text
s3:PutObject
s3:GetObject
s3:DeleteObject
```

Object access:

```text
arn:aws:s3:::YOUR_BUCKET/*
```

`ListBucket` permission is not required because image listing is handled through PostgreSQL.

### Security principle

```text
Public S3 Bucket
      ❌

Private S3 Bucket
      ✅
          │
          ▼
FastAPI generates temporary
presigned URL
          │
          ▼
Client accesses object
```

---

# 🔑 Authentication

CloudImage uses JWT Bearer authentication.

```text
Register
   ↓
Argon2 Password Hash
   ↓
PostgreSQL
```

Login:

```text
Username + Password
       ↓
Verify Argon2 Hash
       ↓
Generate JWT
       ↓
Client
```

Protected request:

```http
Authorization: Bearer <access_token>
```

JWT expiration is configurable through environment variables.

---

# 🛡️ Image Validation

Before an image is stored, CloudImage validates:

### File size

Default maximum:

```text
10 MB
```

### MIME type

Allowed:

```text
image/jpeg
image/png
image/webp
image/gif
```

### Image integrity

Pillow verifies that the file is a valid image.

### Dimensions

Maximum:

```text
10000 × 10000
```

### Pixel count

Maximum:

```text
50,000,000 pixels
```

This provides multiple layers of protection rather than trusting only the uploaded filename or MIME type.

---

# 🌐 API Endpoints

Base URL:

```text
/api/v1
```

## Health

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Application health |
| GET | `/health/db` | Database health |

## Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Login |
| GET | `/auth/me` | Current user |

## Images

| Method | Endpoint | Description |
|---|---|---|
| POST | `/images` | Upload image |
| GET | `/images` | List images |
| GET | `/images/{image_id}` | Get image metadata |
| GET | `/images/{image_id}/file` | Generate original file URL |
| GET | `/images/{image_id}/download` | Generate download URL |
| POST | `/images/{image_id}/transform` | Transform image |
| DELETE | `/images/{image_id}` | Delete image |

## Transformations

| Method | Endpoint | Description |
|---|---|---|
| GET | `/images/transformations/{transformation_id}/file` | Generate transformed image URL |

---

# 📚 API Documentation

When running locally:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

# ⚙️ Local Setup

## 1. Clone repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd CloudImage
```

## 2. Create virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔧 Environment Configuration

Create:

```text
.env
```

Use `.env.example` as the template.

Example:

```env
APP_NAME=Cloud Image Processing Service
APP_VERSION=1.0.0
DEBUG=True

DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/image_service

JWT_SECRET_KEY=YOUR_SECRET_KEY
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

MAX_FILE_SIZE_MB=10

AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY
AWS_REGION=ap-south-1
AWS_S3_BUCKET_NAME=YOUR_BUCKET_NAME
```

> **Never commit `.env` or AWS credentials to GitHub.**

---

# 🗃️ Database Setup

Create the PostgreSQL database:

```text
image_service
```

Run migrations:

```bash
alembic upgrade head
```

Check migration status:

```bash
alembic current
```

Check for schema differences:

```bash
alembic check
```

Expected:

```text
No new upgrade operations detected.
```

---

# ▶️ Run Application

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Application:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 🧪 Testing

The API was regression-tested across the complete application flow.

Test coverage includes:

### Health

- Application health
- Database health

### Authentication

- User registration
- Duplicate registration
- Login
- Current user
- Invalid credentials
- Invalid JWT

### Image Upload

- JPEG
- PNG
- WebP
- File size validation
- MIME validation
- Corrupted images
- Invalid uploads

### Image Management

- Get image
- List images
- Pagination
- Search
- Format filtering
- Sorting
- File URL generation
- Download URL generation
- Delete

### Transformations

- Resize
- Crop
- Rotate
- Flip
- Mirror
- Grayscale
- Sepia
- Watermark
- Format conversion
- Quality settings

### Transformation Cache

- Cache miss
- Transformation processing
- Cache hit
- Existing transformation reuse

### Authorization

Cross-user access was tested to ensure users cannot access another user's:

- Image metadata
- Original image
- Transformations
- Files
- Delete operations

### Storage

- S3 upload
- S3 download
- S3 deletion
- Presigned URL generation
- Database/S3 cleanup behavior

---

# 📊 API Response Strategy

File endpoints return JSON instead of redirecting directly to S3.

Example:

```json
{
  "url": "temporary-presigned-url",
  "mime_type": "image/png",
  "expires_in": 3600
}
```

This keeps the API behavior predictable for clients and Swagger/OpenAPI testing.

---

# 📝 Logging

Application logging is implemented using Python's standard logging framework.

Log format:

```text
timestamp | logger | filename | level | message
```

Example:

```text
2026-09-04 12:30:20 | app | image_service.py | INFO | Image upload started
```

Logs are written to:

```text
app/logs/
```

Log files are excluded from Git through `.gitignore`.

Sensitive information such as:

- Passwords
- JWT tokens
- AWS secret keys
- Presigned URLs

is not intentionally logged.

---

# 🔄 Database Migrations

Alembic is used instead of directly calling SQLAlchemy `create_all()`.

Create migration:

```bash
alembic revision --autogenerate -m "description"
```

Apply:

```bash
alembic upgrade head
```

Rollback:

```bash
alembic downgrade -1
```

Check:

```bash
alembic check
```

---

# 🔒 Security Design

CloudImage follows several security principles:

```text
                Security Layers

                     │
        ┌────────────┴────────────┐
        ▼                         ▼
 Authentication              Authorization
        │                         │
        ▼                         ▼
       JWT                 User ownership checks
        │                         │
        └────────────┬────────────┘
                     ▼
              Input Validation
                     │
                     ▼
             Image Validation
                     │
                     ▼
              Private S3
                     │
                     ▼
          Temporary Presigned URLs
```

Additional controls:

- Environment-based configuration
- Password hashing with Argon2
- Private S3 bucket
- Least-privilege IAM policy
- File size limits
- Image dimension limits
- Pixel-count limits
- Ownership validation
- Database transactions
- S3 cleanup on database failure

---

# 🧠 Engineering Highlights

This project demonstrates practical backend and cloud engineering concepts:

### API Architecture

```text
Router
  ↓
Service
  ↓
Model / Storage
```

Business logic is kept outside the API router wherever possible.

### Separation of Concerns

```text
API
 ↓
Services
 ↓
Storage / Database
```

### Cloud Storage

Uses AWS S3 rather than storing uploaded files directly on the application server.

### Database-backed Metadata

S3 stores binary objects while PostgreSQL stores searchable metadata.

### Deterministic Caching

Transformation requests are converted into a stable hash so identical operations can reuse previous results.

### Failure Cleanup

If an S3 upload succeeds but the database transaction fails, the uploaded S3 object is removed to avoid orphaned objects.

---

# 📈 Version History

The project is developed using semantic versioning.

```text
v0.1.0
Project foundation

v0.2.0
Authentication and user management

v0.3.0
Image upload and validation

v0.4.0
AWS S3 storage integration

v0.5.0
Image transformation pipeline

v0.6.0
Image management and transformation caching

v0.7.0
API regression and security validation

v1.0.0
Production-ready backend
```

---

# 🛣️ Roadmap

Future development:

- [ ] Automated pytest test suite
- [ ] Docker containerization
- [ ] Docker Compose development environment
- [ ] GitHub Actions CI/CD
- [ ] API rate limiting
- [ ] Global exception handling
- [ ] Redis caching
- [ ] Background image processing
- [ ] Celery task queue
- [ ] Image optimization pipeline
- [ ] React frontend
- [ ] Image gallery dashboard
- [ ] Before/after transformation preview
- [ ] AWS cloud deployment
- [ ] Monitoring and metrics
- [ ] Production observability
- [ ] Custom domain and HTTPS

---

# 🎯 Project Goals

CloudImage was designed to demonstrate how a real-world image processing backend can be built using:

```text
Python
+
FastAPI
+
PostgreSQL
+
AWS S3
+
JWT
+
Pillow
+
SQLAlchemy
+
Alembic
```

The focus is not only on image manipulation, but also on:

- API architecture
- Cloud storage
- Authentication
- Authorization
- Database design
- Caching
- Security
- Error handling
- Logging
- Testing
- Production readiness

---

# 👨‍💻 Author

**Vidyanshu Kushawaha**

B.Tech CSE — Data Science

Interested in:

- Machine Learning Engineering
- Backend Engineering
- Data Science
- Cloud Engineering
- MLOps

---

# ⭐ If You Find This Project Useful

Consider giving the repository a ⭐ on GitHub.

---

## 📄 License

This project is intended for educational, portfolio, and development purposes.