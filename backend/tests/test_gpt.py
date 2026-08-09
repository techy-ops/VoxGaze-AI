def test_gpt_assist_endpoint(client):
    """Test POST /gpt/assist endpoint."""
    payload = {"prompt": "Help me activate eye tracking mode"}
    response = client.post("/gpt/assist", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "response" in data
    assert "tokens_used" in data
