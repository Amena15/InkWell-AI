import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "0.1.0"}

def test_templates_endpoints():
    """Test templates CRUD operations"""
    # Create a template
    template_data = {
        "name": "Test Template",
        "description": "A test template",
        "content": "Template content here",
        "type": "srs"
    }
    create_response = client.post("/api/templates/", json=template_data)
    assert create_response.status_code == 201
    template_id = create_response.json()["id"]
    
    # Get the created template
    get_response = client.get(f"/api/templates/{template_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == template_data["name"]
    
    # List all templates
    list_response = client.get("/api/templates/")
    assert list_response.status_code == 200
    assert isinstance(list_response.json(), list)
    
    # Update the template
    update_data = {"name": "Updated Template Name"}
    update_response = client.put(f"/api/templates/{template_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Template Name"
    
    # Delete the template (204 No Content is the correct status for successful deletion)
    delete_response = client.delete(f"/api/templates/{template_id}")
    assert delete_response.status_code == 204

def test_documents_endpoints():
    """Test documents CRUD operations"""
    # Create a document
    doc_data = {
        "title": "Test Document",
        "content": "This is a test document",
        "doc_type": "srs",
        "project_id": "test-project-123",
        "metadata": {}
    }
    create_response = client.post("/api/documents/", json=doc_data)
    assert create_response.status_code == 200
    doc = create_response.json()
    doc_id = doc["id"]
    
    # Verify the created document
    assert doc["title"] == doc_data["title"]
    assert doc["content"] == doc_data["content"]
    assert doc["doc_type"] == doc_data["doc_type"]
    assert doc["project_id"] == doc_data["project_id"]
    
    # Get the created document
    get_response = client.get(f"/api/documents/{doc_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == doc_data["title"]
    
    # Get documents by project
    project_docs = client.get(f"/api/documents/project/test-project-123")
    assert project_docs.status_code == 200
    docs = project_docs.json()
    assert isinstance(docs, list)
    assert len(docs) > 0
    
    # Update the document
    update_data = {
        "title": "Updated Document Title",
        "content": doc_data["content"],
        "doc_type": doc_data["doc_type"],
        "project_id": doc_data["project_id"]
    }
    update_response = client.put(f"/api/documents/{doc_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Document Title"
    
    # Clean up
    delete_response = client.delete(f"/api/documents/{doc_id}")
    assert delete_response.status_code == 204

def test_error_handling():
    """Test error cases"""
    # Non-existent endpoint
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    
    # Invalid document ID format (not a valid UUID)
    response = client.get("/api/documents/123")
    assert response.status_code == 404  # API currently returns 404 for invalid document IDs
    
    # Non-existent document
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/documents/{non_existent_id}")
    assert response.status_code == 404
    
    # Invalid template ID format
    response = client.get("/api/templates/123")
    assert response.status_code == 400  # API currently returns 400 for invalid template IDs
    
    # Invalid HTTP method
    response = client.get("/api/documents/")
    assert response.status_code == 405  # Method Not Allowed for GET /api/documents/
