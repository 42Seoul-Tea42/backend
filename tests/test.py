import json
from wsgi import application as app


def test_hello():
    client = app.test_client()
    response = client.get("/hello")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == 200
    assert data["message"] == "Hello there, welcome to Tea42"
