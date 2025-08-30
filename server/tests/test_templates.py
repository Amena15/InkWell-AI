import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_templates():
    response = client.get("/api/templates/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_template():
    test_template = {
        "name": "Test Template",
        "description": "A test template",
        "content": "Template content here",
        "type": "srs"
    }
    response = client.post("/api/templates/", json=test_template)
    assert response.status_code == 201  # 201 Created is the correct status code for resource creation
    data = response.json()
    assert data["name"] == test_template["name"]
    assert "id" in data

def test_get_template():
    # First create a template
    test_template = {
        "name": "Test Get Template",
        "description": "Test getting a template",
        "content": "Test content",
        "type": "srs"
    }
    create_response = client.post("/api/templates/", json=test_template)
    template_id = create_response.json()["id"]
    
    # Now try to get it
    response = client.get(f"/api/templates/{template_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_template["name"]
    assert data["id"] == template_id

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "version": "0.1.0"}
