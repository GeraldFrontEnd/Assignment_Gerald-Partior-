import os
import sys
import json
import argparse
import hvac

def get_env(name: str, default: str = None) -> str:
    val = os.getenv(name, default)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val

def get_secret_kv2(mount: str, path: str) -> dict:
    """
    Retrieve a secret from Vault KV v2 using hvac.
    """
    vault_addr = get_env("VAULT_ADDR")
    vault_token = get_env("VAULT_TOKEN")

    client = hvac.Client(url=vault_addr, token=vault_token)
    if not client.is_authenticated():
        raise RuntimeError("Vault authentication failed")

    try:
        secret = client.secrets.kv.v2.read_secret_version(
            mount_point=mount,
            path=path
        )
        return secret["data"]["data"]
    except hvac.exceptions.InvalidPath:
        raise KeyError(f"Secret not found at {mount}/{path}")

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

