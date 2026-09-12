from locust import HttpUser, between, task

class EnterpriseUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def health(self):
        self.client.get("/health", name="gateway-health")

    @task(3)
    def products(self):
        self.client.get("/api/v1/products", name="list-products")
