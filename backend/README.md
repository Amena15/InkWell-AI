# InkWell AI Backend

This is the backend service for InkWell AI, providing APIs for document generation, analysis, and management.

## Features

- User authentication and authorization (JWT)
- Project and document management
- AI-powered document generation (SRS/SDS)
- Code documentation analysis
- Document quality assessment
- RESTful API with OpenAPI documentation

## Prerequisites

- Python 3.8+
- PostgreSQL / SQLite
- OpenAI API key
- Node.js & npm (for frontend)

## Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.example` and update the values:
   ```bash
   cp .env.example .env
   ```
5. Initialize the database:
   ```bash
   alembic upgrade head
   ```

## Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- OpenAPI documentation: `http://localhost:8000/docs`
- Alternative documentation: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── api/                  # API routes
│   │   └── api_v1/           # API version 1
│   │       ├── endpoints/    # Route handlers
│   │       └── api.py        # API router
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Configuration
│   │   ├── security.py       # Authentication & authorization
│   │   └── exceptions.py     # Exception handlers
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic models
│   ├── services/             # Business logic
│   └── database.py           # Database connection
├── migrations/               # Database migrations
├── tests/                    # Test files
├── .env.example              # Example environment variables
├── .gitignore
├── alembic.ini               # Alembic configuration
├── main.py                   # Application entry point
└── requirements.txt          # Dependencies
```

## Testing

Run the test suite:
```bash
pytest
```

## Deployment

For production deployment, consider using:
- Gunicorn with Uvicorn workers
- Nginx as a reverse proxy
- PostgreSQL as the production database
- Environment variables for configuration

## License

This project is licensed under the MIT License - see the LICENSE file for details.
