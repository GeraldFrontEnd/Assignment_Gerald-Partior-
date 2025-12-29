import os
import hvac


class VaultClient:
    def __init__(self, addr=None, token=None, verify=None):
        self.addr = addr or os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")
        self.token = token or os.environ.get("VAULT_TOKEN")
        verify_env = os.environ.get("VAULT_VERIFY", "true").lower()
        self.verify = verify if verify is not None else (verify_env == "true")
        self.client = hvac.Client(url=self.addr, token=self.token, verify=self.verify)

    def read_kv2(self, mount_point: str, secret_path: str) -> dict:
        resp = self.client.secrets.kv.v2.read_secret_version(
            path=secret_path,
            mount_point=mount_point
        )
        return resp["data"]["data"]
