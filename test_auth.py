""" Verification script to check Google OAuth Browser Streams """
import sys
from src.utils.logger import setup_logger
from src.api.google_auth import GoogleAuthManager
from googleapiclient.discovery import build

def verify_google_auth():
    setup_logger()
    print("=" * 80)
    print("🔒 GOOGLE WORKSPACE OAUTH LOGIN VERIFICATION HARNESS")
    print("=" * 80)
    
    try:
        auth_manager = GoogleAuthManager()
        creds = auth_manager.get_credentials()
        
        # Build a temporary live resource to verify scope authorization
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        
        print("\n🎉 OAUTH AUTHENTICATION FLUIDLY VERIFIED!")
        print(f"Connected to User Account: {profile.get('emailAddress')}")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ Configuration Error Encountered: {e}")
        print("Please ensure credentials.json is placed inside your root directory.")
        print("=" * 80)

if __name__ == "__main__":
    verify_google_auth()