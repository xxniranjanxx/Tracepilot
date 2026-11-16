
def sample_incident():
    return {
        "incident_id": "SYN-TEST-001",
        "short_description": "SAP processing failure",
        "description": "Bot failed during SAP invoice processing",
        "resolution_notes": "Restarted SAP session and retried transaction",
        "priority": "High",
        "resolution_category": "Configuration",
        "resolution_time_hours": 1.5,
        "sla_breached": False
    }


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_incident(client):
    response = client.post(
        "/incidents",
        json=sample_incident()
    )

    assert response.status_code == 201
    assert response.json()["incident"]["incident_id"] == "SYN-TEST-001"


def test_retrieve_incidents(client):
    client.post("/incidents", json=sample_incident())

    response = client.get("/incidents")

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_duplicate_incident(client):
    payload = sample_incident()

    client.post("/incidents", json=payload)
    response = client.post("/incidents", json=payload)

    assert response.status_code == 409


def test_invalid_priority(client):
    payload = sample_incident()
    payload["priority"] = "Urgent"

    response = client.post("/incidents", json=payload)

    assert response.status_code == 422


def test_update_incident(client):
    payload = sample_incident()

    client.post("/incidents", json=payload)

    response = client.patch(
        "/incidents/SYN-TEST-001",
        json={"priority": "Medium"}
    )

    assert response.status_code == 200
    assert response.json()["incident"]["priority"] == "Medium"
    assert (
        response.json()["incident"]["description"]
        == payload["description"]
    )


def test_update_nonexistent_incident(client):
    response = client.patch(
        "/incidents/UNKNOWN-001",
        json={"priority": "Medium"}
    )

    assert response.status_code == 404


def test_update_invalid_priority(client):
    client.post("/incidents", json=sample_incident())

    response = client.patch(
        "/incidents/SYN-TEST-001",
        json={"priority": "Urgent"}
    )

    assert response.status_code == 422


def test_delete_incident(client):
    payload = sample_incident()

    client.post("/incidents", json=payload)

    response = client.delete("/incidents/SYN-TEST-001")

    assert response.status_code == 204

    retrieve_response = client.get("/incidents")
    assert retrieve_response.status_code == 200
    assert retrieve_response.json()["total"] == 0
    assert retrieve_response.json()["incidents"] == []


def test_delete_nonexistent_incident(client):
    response = client.delete("/incidents/UNKNOWN-001")

    assert response.status_code == 404
