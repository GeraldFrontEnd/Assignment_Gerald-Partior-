import os
import time
import pytest
import hvac

from vault_client import get_secret_kv2

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "root")
MOUNT = "secret"
PATH = "app/config"

def seed_secret():
    client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
    client.secrets.kv.v2.create_or_update_secret(
        mount_point=MOUNT,
        path=PATH,
        secret={"username": "demo", "password": "s3cr3t"}
    )

@pytest.fixture(scope="session", autouse=True)
def ensure_vault_ready():
    client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
    for _ in range(30):
        if client.is_authenticated():
            break
        time.sleep(1)
    seed_secret()

def test_get_secret_kv2_success():
    secret = get_secret_kv2(MOUNT, PATH)
    assert secret["username"] == "demo"
    assert secret["password"] == "s3cr3t"

def test_get_secret_kv2_not_found():
    with pytest.raises(KeyError):
        get_secret_kv2(MOUNT, "nonexistent/path")
