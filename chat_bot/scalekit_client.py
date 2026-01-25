"""
Shared ScaleKit client configuration module.
Provides a centralized ScaleKit client instance for use across all integrations.
"""
import os
import scalekit.client
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate required environment variables
_client_id = os.getenv("SCALEKIT_CLIENT_ID")
_client_secret = os.getenv("SCALEKIT_CLIENT_SECRET")
_env_url = os.getenv("SCALEKIT_ENV_URL")

if not _client_id:
    raise ValueError("SCALEKIT_CLIENT_ID is required in .env file")
if not _client_secret:
    raise ValueError("SCALEKIT_CLIENT_SECRET is required in .env file")
if not _env_url:
    raise ValueError("SCALEKIT_ENV_URL is required in .env file")

# Initialize shared ScaleKit client (singleton pattern)
_scalekit_client = None

def get_scalekit_client():
    """
    Get or create the shared ScaleKit client instance.
    
    Returns:
        scalekit.client.ScalekitClient: The shared ScaleKit client instance
    """
    global _scalekit_client
    
    if _scalekit_client is None:
        _scalekit_client = scalekit.client.ScalekitClient(
            client_id=_client_id,
            client_secret=_client_secret,
            env_url=_env_url,
        )
        logger.info("Initialized shared ScaleKit client")
    
    return _scalekit_client

# Convenience accessor for the connect interface
def get_connect():
    """
    Get the ScaleKit connect interface from the shared client.
    
    Returns:
        The connect interface for executing tools and managing connections
    """
    return get_scalekit_client().connect
