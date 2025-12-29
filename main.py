import os
from vault_client import VaultClient

def run():
    mount = os.environ.get("VAULT_KV_MOUNT", "secret")
    path = os.environ.get("VAULT_SECRET_PATH", "demo/app-config")
    vc = VaultClient()
    data = vc.read_kv2(mount, path)
    print(f"Retrieved secret: {data}")

if __name__ == "__main__":
    run()
