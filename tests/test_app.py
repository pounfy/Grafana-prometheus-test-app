from app.app import app


def test_home_is_healthy():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert response.json["message"] == "Hello from the monitored app!"


def test_work_reports_duration():
    client = app.test_client()
    response = client.get("/work?seconds=0")

    assert response.status_code == 200
    assert response.json["duration_seconds"] == 0


def test_work_rejects_non_numeric_duration():
    client = app.test_client()
    response = client.get("/work?seconds=invalid")

    assert response.status_code == 400


def test_failure_endpoint_returns_500():
    client = app.test_client()
    response = client.get("/fail")

    assert response.status_code == 500
