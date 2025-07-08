import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI Customer Support Agent Backend is running."}

def test_query_agent():
    response = client.post("/api/query", json={"query": "How do I reset my password?"})
    assert response.status_code == 200
    assert "answer" in response.json()
    assert isinstance(response.json()["answer"], str)
