"""App configuration. Use env vars for access control."""
import os

# When set, document upload and settings require this key (form field: access_key)
UPLOAD_ACCESS_KEY = os.getenv("UPLOAD_ACCESS_KEY", "").strip()

def require_access_key() -> bool:
    return bool(UPLOAD_ACCESS_KEY)
