# Secure FastAPI User Management Application with Calculation Model

A comprehensive FastAPI application implementing secure user authentication, password hashing, database integration with SQLAlchemy and PostgreSQL, and a calculation model with factory pattern. This project includes complete testing (unit and integration tests), Docker containerization, and CI/CD pipeline with GitHub Actions.

## Features

- **Secure User Authentication**: Password hashing using bcrypt with configurable cost factors
- **Calculation Model**: SQLAlchemy model for storing arithmetic operations (Add, Subtract, Multiply, Divide)
- **Factory Pattern**: Design pattern implementation for creating calculation operations dynamically
- **SQLAlchemy ORM**: Database models with UUID primary keys, foreign keys, and unique constraints
- **Pydantic Validation**: Request/response schemas with comprehensive validation including division by zero checks
- **RESTful API**: Full CRUD operations for user management
- **Comprehensive Testing**: Unit tests for calculations and factory pattern, integration tests with real PostgreSQL database
- **Docker Support**: Multi-stage Dockerfile and Docker Compose for local development
- **CI/CD Pipeline**: GitHub Actions workflow for automated testing and Docker Hub deployment
- **FastAPI Documentation**: Automatic OpenAPI/Swagger documentation

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and endpoints
│   ├── models.py            # SQLAlchemy models (User, Calculation)
│   ├── schemas.py           # Pydantic validation schemas
│   ├── factory.py           # Factory pattern for calculations
│   ├── database.py          # Database configuration
│   └── security.py          # Password hashing utilities
├── tests/
│   ├── __init__.py
│   ├── test_security.py     # Unit tests for password hashing
│   ├── test_schemas.py      # Unit tests for schema validation
│   ├── test_calculations.py # Unit tests for calculations and factory
│   └── test_integration.py  # Integration tests with PostgreSQL
├── .github/workflows/
│   └── ci-cd.yml            # GitHub Actions CI/CD workflow
├── Dockerfile               # Multi-stage Docker image
├── docker-compose.yml       # Local development setup
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project configuration
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Docker Hub Repository

The Docker image for this application is automatically built and pushed to Docker Hub via GitHub Actions on every push to the main branch.

**Docker Hub Repository**: `https://hub.docker.com/r/YOUR_USERNAME/secure-fastapi-app`

> **Note**: Replace `YOUR_USERNAME` with your Docker Hub username after creating the repository.

To pull and run the latest image:
```bash
docker pull YOUR_USERNAME/secure-fastapi-app:latest
docker run -p 8000:8000 YOUR_USERNAME/secure-fastapi-app:latest
```

## Prerequisites

- Python 3.9+
- PostgreSQL 12+ (or Docker)
- Docker & Docker Compose (optional, for containerized setup)
- Git

## Installation

### Option 1: Local Development (Without Docker)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd IS601_Module11
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Create PostgreSQL database**
   ```bash
   # Make sure PostgreSQL is running
   createdb secure_app
   createdb secure_app_test
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

### Option 2: Docker Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd IS601_Module11
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

   The application will start on `http://localhost:8000`
   - Database will be available at `localhost:5432`

## Running Tests

### Unit Tests

The project includes comprehensive unit tests for calculations, factory pattern, schemas, and security:

```bash
# All unit tests
pytest tests/test_security.py tests/test_schemas.py tests/test_calculations.py -v

# Calculation tests (factory pattern and operations)
pytest tests/test_calculations.py -v

# Schema validation tests
pytest tests/test_schemas.py -v

# Security/password hashing tests
pytest tests/test_security.py -v

# Specific test class
pytest tests/test_calculations.py::TestCalculationFactory -v

# Specific test
pytest tests/test_calculations.py::TestDivideOperation::test_divide_by_zero_raises_error -v
```

### Integration Tests

Integration tests require a PostgreSQL database connection. Set the `TEST_DATABASE_URL` environment variable:

```bash
# Local PostgreSQL
export TEST_DATABASE_URL=postgresql://user:password@localhost:5433/secure_app_test
pytest tests/test_integration.py -v

# With Docker Compose (test profile)
docker-compose --profile test up -d test_db
export TEST_DATABASE_URL=postgresql://user:password@localhost:5433/secure_app_test
pytest tests/test_integration.py -v
```

### Run All Tests with Coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

Coverage report will be generated in `htmlcov/index.html`

### Test Summary

**Module 11 Calculation Tests:**
- **test_calculations.py** (42 tests): 
  - OperationType enum validation (2 tests)
  - CalculationCreate schema validation including division by zero (12 tests)
  - CalculationRead schema structure (1 test)
  - Individual operation tests (16 tests): Add, Subtract, Multiply, Divide
  - Factory pattern creation and error handling (11 tests)
  
**Module 10 User Tests (Maintained):**
- **test_schemas.py** (32 tests): User schema validation
- **test_security.py** (32 tests): Password hashing and verification

**Integration Tests:**
- **test_integration.py** (50+ tests): 
  - User CRUD operations with PostgreSQL (34 tests)
  - Calculation model database operations (16 tests)
  - Foreign key relationships and constraints
  - Query filtering by type and user

**Total: 106+ unit tests + 50+ integration tests**

## Calculation Model & Factory Pattern

### Calculation Model

The application includes a calculation model for storing arithmetic operations:

```python
class Calculation(Base):
    __tablename__ = "calculations"
    
    id: UUID (Primary Key)
    a: Float - First operand
    b: Float - Second operand
    type: String(20) - Operation type (Add, Subtract, Multiply, Divide)
    result: Float - Computed result
    user_id: UUID (Foreign Key to User) - Optional
    created_at: DateTime - Auto-populated
```

### Factory Pattern Implementation

The factory pattern is used to create calculation operations dynamically:

```python
from app.factory import CalculationFactory

# Create an operation
operation = CalculationFactory.create_operation("Add")
result = operation.calculate(10.5, 5.5)  # Returns 16.0

# Convenience method
result = CalculationFactory.calculate("Multiply", 3.0, 4.0)  # Returns 12.0

# Get supported operations
operations = CalculationFactory.get_supported_operations()
# Returns: ["Add", "Subtract", "Multiply", "Divide"]
```

### Supported Operations

- **Add**: Addition of two numbers
- **Subtract**: Subtraction of two numbers
- **Multiply**: Multiplication of two numbers
- **Divide**: Division with zero divisor validation

### Validation

The `CalculationCreate` schema includes validation:
- Division by zero is prevented
- Operation type must be one of: Add, Subtract, Multiply, Divide
- Both operands (a, b) are required

## API Endpoints

### Health Check
- `GET /health` - Application health status

### User Management
- `POST /users` - Create a new user
  ```json
  {
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123"
  }
  ```

- `GET /users` - List all users (with pagination)
  - Parameters: `skip` (default: 0), `limit` (default: 10)

- `GET /users/{user_id}` - Get a specific user

- `PUT /users/{user_id}` - Update user information
  ```json
  {
    "username": "newusername",
    "email": "newemail@example.com"
  }
  ```

- `DELETE /users/{user_id}` - Delete a user

### Security
- `POST /verify-password` - Verify user password
  - Parameters: `username`, `password`

**Note**: Calculation endpoints (BREAD operations) will be implemented in Module 12. Currently, the Calculation model and factory pattern are available for direct database operations and testing.

## Authentication & Security

### Password Hashing

Passwords are hashed using bcrypt with the following configuration:
- **Algorithm**: bcrypt
- **Cost Factor**: 12 (configurable in `app/security.py`)
- **Salt**: Randomly generated for each password

```python
from app.security import hash_password, verify_password

# Hash a password
hashed = hash_password("mypassword")

# Verify a password
is_valid = verify_password("mypassword", hashed)
```

### Database Security

- **Unique Constraints**: Username and email are enforced as unique at the database level
- **Password Storage**: Only password hashes are stored, never plain-text passwords
- **UUID Primary Keys**: Uses UUID instead of auto-incrementing integers
- **Foreign Keys**: Calculation model properly references User model with optional relationship
- **Timestamps**: Automatic creation timestamps on all records

## Database Models

### User Model

```python
class User(Base):
    __tablename__ = "users"
    
    id: UUID (Primary Key)
    username: String(50) - Unique, indexed
    email: String(100) - Unique, indexed
    password_hash: String(255) - Bcrypt hash
    created_at: DateTime - Auto-populated
```

### Calculation Model

```python
class Calculation(Base):
    __tablename__ = "calculations"
    
    id: UUID (Primary Key)
    a: Float - First operand
    b: Float - Second operand
    type: String(20) - Operation type
    result: Float - Calculated result
    user_id: UUID (Foreign Key, Optional) - Links to User
    created_at: DateTime - Auto-populated
```

## CI/CD Pipeline

### GitHub Actions Workflow

The project includes an automated CI/CD pipeline (`.github/workflows/ci-cd.yml`) that:

1. **Tests on Push**: Runs on every push to `main` or `develop` branches
2. **Unit Tests**: Tests password hashing, schema validation, calculations, and factory pattern
3. **Integration Tests**: Tests with real PostgreSQL database for both User and Calculation models
4. **Coverage Report**: Generates test coverage reports
5. **Docker Build**: Builds Docker image on successful tests
6. **Docker Hub Push**: Pushes image to Docker Hub (requires secrets configuration)

### GitHub Secrets Configuration

To enable Docker Hub deployment, add the following secrets to your GitHub repository:

- `DOCKER_HUB_USERNAME`: Your Docker Hub username
- `DOCKER_HUB_PASSWORD`: Your Docker Hub password or token

**Steps to add secrets:**
1. Go to repository Settings
2. Navigate to Secrets and variables → Actions
3. Click "New repository secret"
4. Add `DOCKER_HUB_USERNAME` and `DOCKER_HUB_PASSWORD`

### Docker Hub Repository

Once configured, Docker images are automatically pushed to:
- **Repository**: `docker.io/{DOCKER_HUB_USERNAME}/secure-fastapi-app`
- **Tags**: 
  - `latest` (for main branch)
  - `branch-{branch-name}`
  - `main-{commit-sha}`

## Docker Hub Integration

### Pull Image from Docker Hub

```bash
docker pull <your-docker-hub-username>/secure-fastapi-app:latest
```

### Run Container

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@host:5432/secure_app \
  <your-docker-hub-username>/secure-fastapi-app:latest
```

### Docker Hub Links

- Docker Hub Repository: `https://hub.docker.com/r/YOUR_USERNAME/secure-fastapi-app`
- Pull Image: `docker pull YOUR_USERNAME/secure-fastapi-app:latest`

**Note**: Replace `YOUR_USERNAME` with your actual Docker Hub username.

### Module 11 Assignment Submission

This repository fulfills Module 11 requirements:
- ✅ Calculation model with SQLAlchemy (no raw SQL)
- ✅ Pydantic schemas with validation (CalculationCreate, CalculationRead)
- ✅ Factory pattern for calculation operations
- ✅ 42 unit tests for calculations and factory
- ✅ 16 integration tests with PostgreSQL
- ✅ CI/CD pipeline updated and passing
- ✅ Docker image builds and pushes to Docker Hub
- ✅ Complete documentation (README + REFLECTION)

## Development Workflow

### Making Changes

1. Create a feature branch
   ```bash
   git checkout -b feature/your-feature
   ```

2. Make changes and run tests locally
   ```bash
   pytest -v
   ```

3. Commit changes
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

4. Push to repository
   ```bash
   git push origin feature/your-feature
   ```

5. Create Pull Request on GitHub

### Debugging

**Enable verbose logging in the application**:
```bash
# In .env
LOG_LEVEL=DEBUG
```

**View Docker logs**:
```bash
docker-compose logs -f app
docker-compose logs -f db
```

**Connect to database**:
```bash
psql postgresql://user:password@localhost:5432/secure_app
```

## Configuration

### Environment Variables

See `.env.example` for all available options:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@localhost/secure_app` |
| `TEST_DATABASE_URL` | Test database URL | `postgresql://user:password@localhost/secure_app_test` |
| `ENVIRONMENT` | Application environment | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Database URL Format

```
postgresql://[user]:[password]@[host]:[port]/[database]
```

Examples:
- Local: `postgresql://user:password@localhost:5432/secure_app`
- Docker: `postgresql://user:password@db:5432/secure_app`
- Production: `postgresql://user:password@prod-host.rds.amazonaws.com:5432/secure_app`

## Deployment

### Deploy to Production

1. **Build and test locally**
   ```bash
   docker-compose up --build
   pytest
   ```

2. **Create GitHub release**
   - Tag version: `git tag v1.0.0`
   - Push tag: `git push origin v1.0.0`
   - Image will be built and pushed automatically

3. **Deploy with Docker**
   ```bash
   docker pull <your-hub>/secure-fastapi-app:latest
   docker run -e DATABASE_URL=... <your-hub>/secure-fastapi-app
   ```

### Production Best Practices

- Use environment variables for sensitive data
- Keep Docker images small (use multi-stage builds)
- Run containers as non-root user (already configured)
- Use health checks (already configured)
- Implement rate limiting on production
- Use HTTPS/TLS in production
- Regularly update dependencies

## Troubleshooting

### Connection Refused: Database
```
Error: psycopg2.OperationalError: could not connect to server
```
**Solution**: Ensure PostgreSQL is running and `DATABASE_URL` is correct.

### Port Already in Use
```
Error: Address already in use
```
**Solution**: Change port or kill existing process
```bash
lsof -i :8000  # Find process
kill -9 <PID>
```

### Docker Build Fails
```
Error: docker: command not found
```
**Solution**: Install Docker Desktop or Docker Engine.

### Tests Fail with Timeout
```
FAILED tests/test_integration.py - psycopg2.OperationalError
```
**Solution**: Ensure test database is running and accessible.

## Learning Outcomes

This project demonstrates implementation of:

- **CLO3**: Automated testing with pytest and FastAPI test client
- **CLO4**: CI/CD pipeline with GitHub Actions and Docker Hub integration
- **CLO9**: Containerization with Docker and Docker Compose
- **CLO11**: SQL database integration with SQLAlchemy ORM
- **CLO12**: JSON serialization and validation with Pydantic
- **CLO13**: Security best practices including password hashing with bcrypt

## Technologies Used

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0.23
- **Validation**: Pydantic 2.5.0
- **Security**: bcrypt 4.1.1
- **Testing**: pytest 7.4.3
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Web Server**: Uvicorn 0.24.0

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions:
1. Check existing GitHub Issues
2. Review API documentation at `/docs`
3. Check logs: `docker-compose logs -f`
4. Consult FastAPI documentation: https://fastapi.tiangolo.com/

## Reflection Document

### Development Experience

**What Went Well:**
- FastAPI's automatic documentation and validation made development efficient
- Pydantic schemas provided excellent type safety and validation
- bcrypt library simplified secure password hashing
- Docker and Docker Compose made local development consistent
- GitHub Actions workflow automation reduces manual deployment steps

**Challenges Faced:**
- Setting up PostgreSQL test database required careful configuration
- Managing database migrations and schema changes
- Configuring GitHub Actions with Docker Hub secrets
- Ensuring unique constraints were properly enforced at database level

**Key Learnings:**
- Importance of comprehensive testing (unit, integration, end-to-end)
- Security best practices for password storage and authentication
- CI/CD pipeline benefits for automated testing and deployment
- Containerization advantages for consistent development and production environments
- Database design considerations (UUID vs auto-increment, indexing, constraints)

**Future Improvements:**
- Implement JWT token-based authentication
- Add role-based access control (RBAC)
- Implement email verification flow
- Add rate limiting and request throttling
- Implement database migrations with Alembic
- Add monitoring and logging with ELK stack
- Performance optimization and caching strategies
- Implement GraphQL API alongside REST



