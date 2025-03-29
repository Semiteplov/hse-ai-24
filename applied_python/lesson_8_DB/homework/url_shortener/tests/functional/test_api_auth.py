def test_register(client):
    response = client.post("/register", json={
        "username": "newuser",
        "password": "newpass"
    })
    assert response.status_code == 200
    assert "message" in response.json()