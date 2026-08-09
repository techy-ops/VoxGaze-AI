def test_trigger_emergency_alert(client):
    """Test POST /emergency/alert endpoint."""
    payload = {"user_id": "usr_voxgaze_1001", "trigger_source": "blink_sequence"}
    response = client.post("/emergency/alert", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "triggered"
    assert data["alert_id"] == "emg_12345"


def test_get_emergency_status(client):
    """Test GET /emergency/status endpoint."""
    response = client.get("/emergency/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
