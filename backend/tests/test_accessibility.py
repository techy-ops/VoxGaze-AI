def test_get_accessibility_settings(client):
    """Test GET /accessibility/settings endpoint."""
    response = client.get("/accessibility/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["high_contrast"] is True
    assert data["font_size"] == "large"


def test_update_accessibility_settings(client):
    """Test PUT /accessibility/settings endpoint."""
    payload = {
        "high_contrast": False,
        "font_size": "medium",
        "speech_rate": 1.2,
        "gaze_sensitivity": 0.9
    }
    response = client.put("/accessibility/settings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["high_contrast"] is False
    assert data["font_size"] == "medium"
    assert data["speech_rate"] == 1.2
