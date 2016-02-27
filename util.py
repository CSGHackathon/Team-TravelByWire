import requests

class MockFailure:
    status_code = 500

def get(url, timeout=60):
    try:
        return requests.get(url, timeout=timeout)
    except Exception:
        return MockFailure()

