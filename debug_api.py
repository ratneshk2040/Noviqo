from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

cases = [
    ("signup", "/api/auth/signup", {"username": "testuser", "email": "test@example.com", "password": "secret123"}),
    ("token", "/api/auth/token", {"username": "testuser", "password": "secret123"}),
]

for name, path, payload in cases:
    print(f'== {name} ==')
    if path.endswith('/token'):
        r = client.post(path, data=payload)
    else:
        r = client.post(path, json=payload)
    print('status=', r.status_code)
    print(r.text[:800])
    print()
