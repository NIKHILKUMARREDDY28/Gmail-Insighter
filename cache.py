import json

from cryptography.fernet import Fernet

from settings import settings
import traceback

import redis

from logger.app_logger import log_message
from settings import settings


try:
    redis_client = redis.from_url(settings.REDIS_HOST,decode_responses=True)
except Exception as e:
    log_message(f"Error connecting to Redis: {traceback.format_exc()}")
    redis_client = None


GLOBAL_USER_DATA_CACHE_PREFIX = "gmail_summariser"

FERNET_KEY = settings.FERNET_KEY  # Should be a 32 url-safe base64-encoded bytes

fernet = Fernet(FERNET_KEY)


def save_encrypted_cache(session_id: str, data: dict, expire_in: int| None = None):
    json_data = json.dumps(data)
    encrypted_data = fernet.encrypt(json_data.encode())

    redis_key = f"{GLOBAL_USER_DATA_CACHE_PREFIX}_{session_id}"
    redis_client.set(redis_key, encrypted_data, ex=expire_in)


def get_session_details_from_cache(session_id: str):
    """
    Retrieves session details from the cache using the session ID.
    """

    redis_key = f"{GLOBAL_USER_DATA_CACHE_PREFIX}_{session_id}"

    encrypted_data = redis_client.get(redis_key)

    if encrypted_data:
        decrypted_data = fernet.decrypt(encrypted_data).decode()
        data_loaded = json.loads(decrypted_data)
        print(f"[{session_id}]: Loaded the data {data_loaded}")
        return data_loaded

    else:
        log_message(message=f"Session details not found for session_id: {session_id}", level="warning")
        return {}
