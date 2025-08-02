# RAG Document Retrieval API

## Features
- Upload up to 20 documents (max 1000 pages each)
- Document chunking and embedding storage in a vector DB
- Retrieval-Augmented Generation (RAG) pipeline
- REST API (Flask): upload, query, and view document metadata
- Metadata stored in PostgreSQL
- Docker Compose for deployment
- Unit and integration tests

## Setup
1. Clone the repo and navigate to the project folder.
2. Build and start services:
   ```
docker-compose up --build
   ```
3. The API will be available at `http://localhost:5000`

## API Endpoints
- `POST /upload` — Upload documents
- `POST /query` — Query the system
- `GET /documents` — View processed document metadata

## Testing
To run tests:
```
pytest
```

## Configuration
- Environment variables are set in `.env`

---

For more details, see code comments and docstrings.
