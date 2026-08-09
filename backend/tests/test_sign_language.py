def test_sign_language_endpoint(client):
    """Test POST /sign-language/process endpoint."""
    response = client.post("/sign-language/process", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["translated_text"] == "Thank you"
    assert data["confidence"] == 0.92
