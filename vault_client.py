import os
import sys
import json
import argparse
import requests

def get_env(name: str, default: str = None) -> str:
    val = os.getenv(name, default)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val

def get_secret_kv2(mount: str, path: str) -> dict:
    """
    Retrieve a secret from Vault KV v2.
    Assumes KV v2 at mount (e.g., 'secret') and dev token via env.
    """
    vault_addr = get_env("VAULT_ADDR")
    vault_token = get_env("VAULT_TOKEN")
    url = f"{vault_addr}/v1/{mount}/data/{path}"
    headers = {"X-Vault-Token": vault_token}

    resp = requests.get(url, headers=headers, timeout=5)
    if resp.status_code == 200:
        payload = resp.json()
        return payload.get("data", {}).get("data", {})
    elif resp.status_code == 404:
        raise KeyError(f"Secret not found at {mount}/{path}")
    else:
        try:
            err = resp.json()
        except ValueError:
            err = {"message": resp.text}
        raise RuntimeError(f"Vault error {resp.status_code}: {err}")

def main():
    parser = argparse.ArgumentParser(description="Retrieve secrets from Vault KV v2")
    parser.add_argument("--mount", required=True, help="KV mount path (e.g., secret)")
    parser.add_argument("--path", required=True, help="Secret path (e.g., app/config)")
    args = parser.parse_args()

    try:
        secret = get_secret_kv2(args.mount, args.path)
        print(json.dumps({"mount": args.mount, "path": args.path, "secret": secret}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
d