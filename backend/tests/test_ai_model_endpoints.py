import pytest


def test_list_ai_models_endpoint(client):
    """Test GET /ai/models endpoint."""
    response = client.get("/ai/models")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "registered_models_count" in data
    assert "loaded_models_count" in data
    assert "registered_models" in data
    assert "loaded_models" in data
    assert data["registered_models_count"] >= 4


def test_get_ai_models_health_endpoint(client):
    """Test GET /ai/models/health endpoint."""
    response = client.get("/ai/models/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "loaded_models_count" in data
    assert "max_capacity" in data
    assert "hardware" in data
    assert "memory" in data
    assert "loaded_models" in data


def test_reload_ai_model_endpoint_success(client):
    """Test POST /ai/models/reload endpoint with valid model name."""
    payload = {"model_name": "mock_classifier", "version": "1.0.0", "device": "cpu"}
    response = client.post("/ai/models/reload", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "mock_classifier" in data["message"]
    assert "health" in data
    assert data["health"]["is_loaded"] is True


def test_reload_ai_model_endpoint_not_found(client):
    """Test POST /ai/models/reload endpoint with invalid model name."""
    payload = {"model_name": "unknown_invalid_model_123"}
    response = client.post("/ai/models/reload", json=payload)
    assert response.status_code == 404
