import os
import time
import requests
import pytest

from vault_client import get_secret_kv2

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "root")
MOUNT = "secret"
PATH = "app/config"

def seed_secret():
    url = f"{VAULT_ADDR}/v1/{MOUNT}/data/{PATH}"
    headers = {"X-Vault-Token": VAULT_TOKEN}
    payload = {"data": {"username": "demo", "password": "s3cr3t"}}
    r = requests.post(url, headers=headers, json=payload, timeout=5)
    assert r.status_code in (200, 204), f"Failed to seed secret: {r.status_code} {r.text}"

@pytest.fixture(scope="session", autouse=True)
def ensure_vault_ready():
    health = f"{VAULT_ADDR}/v1/sys/health"
    for _ in range(30):
        try:
            r = requests.get(health, timeout=2)
            if r.status_code in (200, 429, 472, 473):
                break
        except Exception:
            pass
        time.sleep(1)
    seed_secret()

def test_get_secret_kv2_success():
    secret = get_secret_kv2(MOUNT, PATH)
    assert secret["username"] == "demo"
    assert secret["password"] == "s3cr3t"

def test_get_secret_kv2_not_found():
    with pytest.raises(KeyError):
        get_secret_kv2(MOUNT, "nonexistent/path")