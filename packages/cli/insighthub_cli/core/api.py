import httpx

class API:
    def __init__(self, base_url="https://api.insighthub.dev"):
        self.client = httpx.Client(base_url=base_url)

    def get(self, path, **kwargs):
        return self.client.get(path, **kwargs)

    def post(self, path, data=None, **kwargs):
        return self.client.post(path, json=data, **kwargs)
