"""
Test script to validate backend API endpoints.
Run with: python -m pytest tests/test_api_endpoints.py -v
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data

def test_websocket_connection():
    """Test WebSocket connection"""
    with client.websocket_connect("/ws/test-doc-123?user_id=test-user") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "document_state"
        assert "document_id" in data
        assert "content" in data

# Add more test cases for other endpoints
# TODO: Add tests for document creation, retrieval, updates, etc.
