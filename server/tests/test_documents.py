import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
from fastapi import status

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up test environment variables
os.environ["OPENAI_API_KEY"] = "test-api-key"

# Import the app after setting up environment variables
from app.main import app

# Create a test client
client = TestClient(app)

# Mock the OpenAI service
mock_openai_service = MagicMock()
mock_openai_service.generate_document = AsyncMock(
    return_value="Mock generated document content"
)

# Test data
VALID_DOCUMENT_REQUEST = {
    "project_id": "test-project-123",
    "project_description": "A test project for document generation",
    "code_snippets": [
        {
            "language": "python",
            "code": "def hello():\n    print('Hello, World!')",
            "file_path": "test.py"
        }
    ],
    "document_type": "srs",
    "additional_context": "This is a test context"
}

# Fixtures
@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_openai():
    with patch('app.routes.documents.openai_service', mock_openai_service):
        yield mock_openai_service

# Test document generation
@pytest.mark.asyncio
async def test_generate_document_success(client, mock_openai):
    """Test successful document generation"""
    # Setup mock
    mock_openai.generate_document.return_value = "Mock generated document content"
    
    response = client.post("/api/documents/generate", json=VALID_DOCUMENT_REQUEST)
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert "message" in data
    assert "document" in data
    assert data["message"] == "Document generated successfully"
    assert "content" in data["document"]
    assert "metadata" in data["document"]
    
    # Verify the mock was called
    mock_openai.generate_document.assert_called_once()

def test_generate_document_missing_required_fields(client):
    """Test document generation with missing required fields"""
    test_data = {"project_id": "test-project-123"}  # Missing required fields
    response = client.post("/api/documents/generate", json=test_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Verify the response contains validation error details
    error_data = response.json()
    assert "detail" in error_data
    # Check for the specific validation error
    assert any("field required" in str(e).lower() for e in error_data["detail"])

def test_generate_document_invalid_document_type(client):
    """Test document generation with invalid document type"""
    test_data = VALID_DOCUMENT_REQUEST.copy()
    test_data["document_type"] = "invalid_type"
    
    response = client.post("/api/documents/generate", json=test_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Verify the response contains validation error details
    error_data = response.json()
    assert "detail" in error_data
    # Check for validation error about document type
    assert any("document_type" in str(e) for e in error_data["detail"])

@pytest.mark.asyncio
async def test_generate_document_empty_code_snippets(client, mock_openai):
    """Test document generation with empty code snippets"""
    # Setup mock
    mock_openai.generate_document.return_value = "Mock generated document content"
    
    test_data = VALID_DOCUMENT_REQUEST.copy()
    test_data["code_snippets"] = []
    
    response = client.post("/api/documents/generate", json=test_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["message"] == "Document generated successfully"
    
    # Verify the mock was called
    mock_openai.generate_document.assert_called_once()

@pytest.mark.asyncio
async def test_generate_document_large_input(client, mock_openai):
    """Test document generation with large input"""
    # Setup mock
    mock_openai.generate_document.return_value = "Mock generated document content"
    
    large_description = "A" * 10000
    test_data = VALID_DOCUMENT_REQUEST.copy()
    test_data["project_description"] = large_description
    
    response = client.post("/api/documents/generate", json=test_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["message"] == "Document generated successfully"
    
    # Verify the mock was called with the large input
    mock_openai.generate_document.assert_called_once()
    args, _ = mock_openai.generate_document.call_args
    assert len(args[0].project_description) == len(large_description)

@pytest.mark.asyncio
async def test_generate_document_special_characters(client, mock_openai):
    """Test document generation with special characters"""
    # Setup mock
    special_content = "Mock generated document content with special chars"
    mock_openai.generate_document.return_value = special_content
    
    special_chars = "!@#$%^&*()_+{}|:<>?[];',./`~"
    test_data = VALID_DOCUMENT_REQUEST.copy()
    test_data["project_description"] = f"Special chars: {special_chars}"
    
    response = client.post("/api/documents/generate", json=test_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["message"] == "Document generated successfully"
    
    # Verify the mock was called with the special characters
    mock_openai.generate_document.assert_called_once()
    args, _ = mock_openai.generate_document.call_args
    assert special_chars in args[0].project_description

# Test error handling
def test_nonexistent_endpoint(client):
    """Test non-existent API endpoint"""
    response = client.get("/api/nonexistent")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    error_data = response.json()
    assert "detail" in error_data

@pytest.mark.asyncio
async def test_invalid_http_method(client, mock_openai):
    """Test invalid HTTP method for an endpoint"""
    # Setup mock (shouldn't be called for this test)
    mock_openai.generate_document = AsyncMock()
    
    # Test GET on a POST-only endpoint
    response = client.get("/api/documents/generate")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    # Verify the mock was not called
    mock_openai.generate_document.assert_not_called()
    
    # Verify the response includes the allowed methods
    assert "Allow" in response.headers
    assert "POST" in response.headers["Allow"]
