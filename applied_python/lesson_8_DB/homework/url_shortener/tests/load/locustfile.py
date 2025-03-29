from locust import HttpUser, task, between


class ShortenerUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def create_short_link(self):
        self.client.post("/links/shorten",
                         json={"original_url": "http://example.com"},
                         headers={"Authorization": "Bearer testtoken"}
                         )

    @task(3)
    def redirect_link(self):
        self.client.get("/abc123", allow_redirects=False)

    def on_start(self):
        response = self.client.post("/login",
                                    data={"username": "testuser", "password": "testpass"}
                                    )
        self.token = response.json()["access_token"]
