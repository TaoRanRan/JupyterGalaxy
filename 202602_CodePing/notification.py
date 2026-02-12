import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def notify_teams() -> bool:
    """
    Send a Teams notification via workflows webhook.
    
    Returns:
        True if successful, False otherwise.
    """
    webhook_url = os.getenv("TEAMS_WORKFLOW_URL")
    
    if not webhook_url:
        logger.error("TEAMS_WORKFLOW_URL environment variable not set")
        return False
    
    try:
        response = requests.post(webhook_url, timeout=10)
        response.raise_for_status()
        logger.info("Teams notification sent successfully")
        return True
    except requests.exceptions.Timeout:
        logger.error("Request timeout sending Teams notification")
        return False
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {e}")
        return False
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")

        return False
