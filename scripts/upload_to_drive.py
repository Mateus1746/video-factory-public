import os
import sys
import json
import glob
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes required
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_credentials():
    # 1. Try Environment Variable (GitHub Actions / Secure)
    creds_json = os.environ.get('GDRIVE_CREDENTIALS_JSON')
    
    if creds_json:
        print("🔑 Loading credentials from Environment Variable...")
        info = json.loads(creds_json)
        
        # Detect credential type
        if info.get('type') == 'service_account':
            print("🤖 Authenticating as Service Account...")
            return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        elif info.get('type') == 'authorized_user':
            print("👤 Authenticating as User (OAuth)...")
            return Credentials.from_authorized_user_info(info, scopes=SCOPES)
        else:
            print(f"⚠️ Unknown credential type: {info.get('type')}")
    
    # 2. Try Local File (Dev / Test)
    files = glob.glob("*.json")
    for f in files:
        if "client_secret" in f: continue # Skip oauth client secrets
        try:
            with open(f) as j:
                data = json.load(j)
                if data.get("type") == "service_account":
                    print(f"🔑 Loading Service Account from file: {f}")
                    return service_account.Credentials.from_service_account_file(f, scopes=SCOPES)
                elif data.get("type") == "authorized_user":
                    print(f"🔑 Loading User Credentials from file: {f}")
                    return Credentials.from_authorized_user_file(f, scopes=SCOPES)
        except:
            pass
            
    print("❌ No valid credentials found (Env Var or File).")
    return None

def upload_file(file_path, folder_id=None):
    creds = get_credentials()
    if not creds:
        return False

    try:
        service = build('drive', 'v3', credentials=creds)
        
        file_name = os.path.basename(file_path)
        print(f"📤 Uploading: {file_name}...")

        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(file_path, resumable=True)
        
        # supportsAllDrives=True is generally safe for v3
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink',
            supportsAllDrives=True
        ).execute()

        print(f"✅ Upload Complete! File ID: {file.get('id')}")
        print(f"🔗 Link: {file.get('webViewLink')}")
        return True

    except Exception as e:
        print(f"❌ Upload Failed: {e}")
        # Debug info for quota issues
        if "quota" in str(e).lower():
            print("ℹ️ Tip: Service Accounts have 0GB quota. Use OAuth2 (User Credentials) or a Shared Drive.")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_to_drive.py <video_file_path> [folder_id]")
        sys.exit(1)

    video_path = sys.argv[1]
    folder_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(video_path):
        print(f"❌ File not found: {video_path}")
        sys.exit(1)

    upload_file(video_path, folder_id)