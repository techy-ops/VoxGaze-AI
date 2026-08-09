def test_root_endpoint(client):
    """Test GET / response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["documentation"] == "/docs"


def test_health_check_endpoint(client):
    """Test GET /health response."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
