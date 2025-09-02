import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import Base, get_db
from app.main import app
from app.core.config import settings

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override the get_db dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the get_db dependency in the app
app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

# Test data
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
}

def test_create_user():
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
            "full_name": TEST_USER["full_name"]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == TEST_USER["email"]
    assert "id" in data
    TEST_USER["id"] = data["id"]

def test_login():
    """Test user login and token generation."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    TEST_USER["token"] = data["access_token"]
    TEST_USER["headers"] = {"Authorization": f"Bearer {TEST_USER['token']}"}

def test_create_project():
    """Test project creation."""
    project_data = {
        "name": "Test Project",
        "description": "A test project"
    }
    response = client.post(
        "/api/v1/projects/",
        json=project_data,
        headers=TEST_USER["headers"]
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == project_data["name"]
    assert "id" in data
    TEST_USER["project_id"] = data["id"]

def test_generate_srs_document():
    """Test SRS document generation."""
    # First, create a test code file
    test_code = """
    def hello_world():
        """Prints 'Hello, World!' to the console."""
        print("Hello, World!")
    """
    
    # Save test code to a temporary file
    with open("test_code.py", "w") as f:
        f.write(test_code)
    
    # Test document generation
    with open("test_code.py", "rb") as f:
        response = client.post(
            "/api/v1/ai/generate-document",
            params={
                "document_type": "srs",
                "project_id": TEST_USER["project_id"],
                "project_description": "A test project for documentation generation"
            },
            files={"code_files": ("test_code.py", f, "text/x-python")},
            headers=TEST_USER["headers"]
        )
    
    # Clean up
    if os.path.exists("test_code.py"):
        os.remove("test_code.py")
    
    assert response.status_code == 200
    data = response.json()
    assert "document" in data
    assert "analysis" in data
    assert "suggestions" in data
    
    # Save document ID for later tests
    TEST_USER["document_id"] = data["document"]["id"]

def test_analyze_code_documentation():
    """Test code documentation analysis."""
    test_code = """
    def add(a, b):
        return a + b
    """
    test_docs = """
    This is a function that adds two numbers.
    """
    
    response = client.post(
        "/api/v1/ai/analyze-code-docs",
        json={
            "code": test_code,
            "documentation": test_docs
        },
        headers=TEST_USER["headers"]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "consistency_score" in data
    assert "elements_analyzed" in data
    assert "issues_found" in data

def test_cleanup():
    """Clean up test data."""
    # Delete test document
    if "document_id" in TEST_USER:
        response = client.delete(
            f"/api/v1/documents/{TEST_USER['document_id']}",
            headers=TEST_USER["headers"]
        )
        assert response.status_code in [200, 404]
    
    # Delete test project
    if "project_id" in TEST_USER:
        response = client.delete(
            f"/api/v1/projects/{TEST_USER['project_id']}",
            headers=TEST_USER["headers"]
        )
        assert response.status_code in [200, 404]
    
    # Delete test user
    if "id" in TEST_USER:
        # Note: In a real application, you'd need to implement user deletion
        # or use a test database that gets cleaned up after tests
        pass

# Run the tests
if __name__ == "__main__":
    pytest.main(["-v", "test_api.py"])

# Add the test functions to a test suite
TEST_FUNCTIONS = [
    test_create_user,
    test_login,
    test_create_project,
    test_generate_srs_document,
    test_analyze_code_documentation,
    test_cleanup
]

def run_tests():
    """Run all test functions and print results."""
    results = {}
    for test_func in TEST_FUNCTIONS:
        try:
            test_func()
            results[test_func.__name__] = "PASSED"
        except AssertionError as e:
            results[test_func.__name__] = f"FAILED: {str(e)}"
        except Exception as e:
            results[test_func.__name__] = f"ERROR: {str(e)}"
    
    # Print test results
    print("\nTest Results:")
    print("-" * 50)
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    # Return True if all tests passed
    return all("PASSED" in result for result in results.values())

if __name__ == "__main__":
    run_tests()
