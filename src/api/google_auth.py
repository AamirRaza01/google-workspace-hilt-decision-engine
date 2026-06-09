"""
Google Authentication Engine
Provides a centralized connection manager for Google API services.
Handles token caching and silent auto-refresh streams natively.
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger()

class GoogleAuthManager:
    """Manages explicit token life-cycles and cross-client credential loading."""
    _instance = None

    def __new__(cls):
        """Implement a Singleton pattern to prevent multiple duplicate auth flows."""
        if cls._instance is None:
            cls._instance = super(GoogleAuthManager, cls).__new__(cls)
            cls._instance._creds = None
        return cls._instance

    def get_credentials(self) -> Credentials:
        """
        Retrieves valid authenticated user credentials.
        Loads existing sessions from disk or invokes an interactive OAuth local server flow.
        """
        if self._creds and self._creds.valid:
            return self._creds

        settings = get_settings()
        creds = None

        # Step 1: Attempt to pull cached user authorizations from disk
        if os.path.exists(settings.google_token_path):
            try:
                creds = Credentials.from_authorized_user_file(
                    settings.google_token_path,
                    settings.google_scopes
                )
                logger.info("Successfully loaded cached Google credentials from token.json")
            except Exception as e:
                logger.warning(f"Failed parsing cached token file: {e}. Moving to re-auth.")

        # Step 2: Validate credentials or trigger refreshing mechanics if expired
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Google access token expired. Triggering silent refresh stream...")
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Failed refreshing Google security token: {e}")
                    creds = None

            # Step 3: If no valid credentials exist, prompt explicit browser sign-in flow
            if not creds:
                if not os.path.exists(settings.google_credentials_path):
                    critical_err = (
                        f"CRITICAL: OAuth application client descriptor file not found at '{settings.google_credentials_path}'. "
                        f"Please place your downloaded 'credentials.json' inside the root workspace folder."
                    )
                    logger.critical(critical_err)
                    raise FileNotFoundError(critical_err)

                logger.info("Initiating local server OAuth loop. Please complete sign-in via your web browser...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.google_credentials_path,
                    settings.google_scopes
                )
                # Opens browser locally for explicit user approval
                creds = flow.run_local_server(port=0)

            # Step 4: Write authorized state back to disk for upcoming runs
            try:
                with open(settings.google_token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
                logger.info(f"Successfully cached fresh workspace credentials into {settings.google_token_path}")
            except Exception as e:
                logger.error(f"Could not persist user security session token to disk: {e}")

        self._creds = creds
        return self._creds