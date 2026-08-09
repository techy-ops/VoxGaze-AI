def test_lip_reading_endpoint(client):
    """Test POST /lip-reading/process endpoint."""
    response = client.post("/lip-reading/process", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["transcript"] == "Hello world"
    assert data["confidence"] == 0.95
