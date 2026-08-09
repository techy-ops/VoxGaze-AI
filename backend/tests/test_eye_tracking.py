def test_eye_tracking_endpoint(client):
    """Test POST /eye-track endpoint return contract."""
    response = client.post("/eye-track", json={})
    assert response.status_code == 200
    expected = {
        "status": "success",
        "direction": "left",
        "blink": False
    }
    assert response.json() == expected
