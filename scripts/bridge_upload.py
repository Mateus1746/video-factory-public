import os
import time
import json
import glob
import re
import sys
from pathlib import Path

# Add brain parent directory to path to allow 'from brain.modules import ...'
# Structure: /home/mateus/projetos/orquestrador/youtube/youtube_factory/scripts/bridge_upload.py
# Brain:     /home/mateus/projetos/orquestrador/brain
# Parent:    /home/mateus/projetos/orquestrador

CURRENT_DIR = Path(__file__).resolve().parent
ORCHESTRATOR_ROOT = CURRENT_DIR.parents[2] # youtube_factory -> youtube -> orquestrador
BRAIN_PATH = ORCHESTRATOR_ROOT / "brain"

if str(ORCHESTRATOR_ROOT) not in sys.path:
    sys.path.append(str(ORCHESTRATOR_ROOT))

print(f"📂 Added to PYTHONPATH: {ORCHESTRATOR_ROOT}")

try:
    from brain.modules.youtube_uploader import YouTubeUploader
    from brain.modules.database import DatabaseManager # Import DatabaseManager
    print("✅ Successfully imported YouTubeUploader and DatabaseManager from brain!")
except ImportError as e:
    print(f"❌ Error: Could not import modules from brain. Details: {e}")
    print(f"PYTHONPATH: {sys.path}")
    sys.exit(1)

# Google Drive Imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError # Moved here

# Config
DRIVE_FOLDER_ID = "101AIv9yfWOGfLl29gb74-n49xzcL2iCn"
DOWNLOAD_DIR = "downloaded_videos"
SCOPES = ['https://www.googleapis.com/auth/drive']
DB_PATH = BRAIN_PATH / "youtube_history.db" # Database location

def get_drive_service():
    creds = None
    # Path to token file (in youtube_factory root)
    token_path = CURRENT_DIR.parent / 'token_drive.json'

    # Try to load token.json (saved user creds)
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            # Look for client_secret in multiple locations
            search_paths = [
                CURRENT_DIR.parent,       # youtube_factory/
                ORCHESTRATOR_ROOT,        # orquestrador/
                Path.cwd()                # Current dir
            ]
            
            secret_file = None
            for path in search_paths:
                found = list(path.glob("client_secret*.json"))
                if found:
                    secret_file = found[0]
                    print(f"🔑 Found client_secret at: {secret_file}")
                    break
            
            if not secret_file:
                print(f"❌ No client_secret found for Drive auth in: {[str(p) for p in search_paths]}")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(str(secret_file), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save creds
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
    return build('drive', 'v3', credentials=creds)

def load_accounts():
    accounts_file = BRAIN_PATH / "accounts.json"
    if not accounts_file.exists():
        print(f"❌ accounts.json not found at {accounts_file}")
        return []
    with open(accounts_file, 'r') as f:
        return json.load(f)

def get_account_for_file(filename, accounts):
    # Normalize filename: remove brackets, extension, and lowercase
    filename_clean = filename.lower().replace("[", "").replace("]", "")
    filename_clean = os.path.splitext(filename_clean)[0]
    
    # Explicit Mappings (Short name in file -> Project ID in accounts.json)
    # Update these keys based on what your filenames look like
    mappings = {
        "fortress": "Fortress Merge",
        "velocity": "Velocity Odds",
        "sim": "Commander Sim",
        "commander": "Commander Sim",
        "neon": "roguelike_survival_", # Corrected ID
        "roguelike": "roguelike_survival_", # Corrected ID
        "marble": "Marble War",
        "paint_war": "Marble War",
        "arena": "The Arena of Algoritms",
        "tower": "Tower Defense",
        "vibe": "Vibe Geometry"
    }

    # 1. Try Explicit Mapping
    for key, project_id in mappings.items():
        if key in filename_clean:
            # Find the account object for this ID
            for acc in accounts:
                # Compare fuzzy match against account ID
                acc_id_clean = acc['id'].lower().replace("_", " ")
                target_id_clean = project_id.lower().replace("_", " ")
                
                if acc_id_clean == target_id_clean:
                    return acc

    # 2. Try Standard Fuzzy Match
    best_match = None
    max_len = 0
    
    for acc in accounts:
        proj_id = acc['id'].lower()
        proj_id_clean = proj_id.replace(" ", "_").replace("-", "_")
        
        # Check if project ID is inside filename
        if proj_id in filename_clean or proj_id_clean in filename_clean:
            if len(proj_id) > max_len:
                best_match = acc
                max_len = len(proj_id)
                
    return best_match

import pickle
from google.auth.transport.requests import Request

# ... (rest of imports)

# ... (Config and Drive Service functions remain same)

def validate_youtube_token(token_path):
    """Checks if a YouTube token is valid or can be refreshed. Returns True if usable."""
    if not token_path.exists():
        print(f"❌ Token file missing: {token_path}")
        return False
        
    try:
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    except Exception as e:
        print(f"❌ Failed to load token {token_path.name}: {e}")
        return False

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f"🔄 Refreshing expired token: {token_path.name}")
            try:
                creds.refresh(Request())
                # Save refreshed token
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
                print(f"✅ Token refreshed and saved: {token_path.name}")
                return True
            except Exception as e:
                print(f"❌ Token refresh failed for {token_path.name}: {e}")
                return False
        else:
            print(f"❌ Token invalid and no refresh possible: {token_path.name}")
            return False
            
    return True

def handle_video_upload(local_path, file_name, account, service=None, drive_file_id=None):
    """Handles upload to YouTube, DB registration, and cleanup."""
    # Upload to YouTube
    token_file = BRAIN_PATH / account['youtube_token']
    if not token_file.exists():
            # Try in root of brain if not found
            token_file = BRAIN_PATH / ".." / account['youtube_token'] 
            if not token_file.exists():
                print(f"❌ Token not found: {token_file}")
                return False
    
    # Pre-validate token to avoid interactive prompt in YouTubeUploader
    if not validate_youtube_token(token_file):
        print(f"🚫 Skipping upload for {account['id']} due to invalid token. Manual auth required.")
        return False

    # Load metadata
    metadata_file = BRAIN_PATH / "video_metadata.json"
    metadata_db = {}
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata_db = json.load(f)
    
    # Get project specific metadata
    project_meta = metadata_db.get(account['id'], {})
    default_meta = metadata_db.get('default_metadata', {})
    
    try:
        uploader = YouTubeUploader(str(token_file))
        
        # Metadata Generation
        base_title = project_meta.get('title', f"Amazing {account['id'].replace('_', ' ').title()} Simulation")
        title = base_title
        
        description = project_meta.get('description', "Automated upload via Nexus Factory.")
        tags = project_meta.get('tags', ["simulation", "ai", account['id']])
        
        category_id = project_meta.get('category_id') or project_meta.get('categoryId') or default_meta.get('category_id', "28")
        
        video_id = uploader.upload_video(
            local_path,
            title=title,
            description=description,
            tags=tags,
            category_id=category_id,
            privacy_status="private"
        )
        
        if video_id:
            print(f"🚀 Uploaded to YouTube! ID: {video_id}")
            
            # Register in Database
            try:
                db = DatabaseManager(DB_PATH)
                video_data = {
                    "video_id": video_id,
                    "title": title,
                    "description": description,
                    "uploaded_at": time.time(),
                    "path": str(Path(local_path).absolute()),
                    "account_id": account['id']
                }
                db.add_to_pending(video_data)
                print(f"📝 Registered in Autopilot DB: {title}")
            except Exception as db_err:
                print(f"⚠️ Failed to register in DB: {db_err}")
            
            # Delete from Drive if applicable
            if service and drive_file_id:
                try:
                    service.files().delete(fileId=drive_file_id).execute()
                    print("🗑️ Deleted from Drive.")
                except Exception as e:
                    print(f"⚠️ Failed to delete from Drive: {e}")
            
            # Delete local file
            if os.path.exists(local_path):
                os.remove(local_path)
                print("🗑️ Deleted local file.")
            
            return True
        
    except Exception as e:
        print(f"❌ Upload Failed: {e}")
        
        # Check for Quota/Limit errors
        error_str = str(e)
        if "uploadLimitExceeded" in error_str or "quotaExceeded" in error_str:
            print(f"🛑 Daily Upload Limit Reached for {account['id']}. Moving/Keeping in postponed.")
            
            postponed_dir = os.path.join(CURRENT_DIR, "postponed_uploads")
            if not os.path.exists(postponed_dir):
                os.makedirs(postponed_dir)
            
            target_path = os.path.join(postponed_dir, file_name)
            
            # If it's not already in postponed (i.e. we are processing from downloaded_videos)
            if str(local_path) != str(target_path):
                 os.rename(local_path, target_path)
                 print(f"📦 Moved {file_name} to {postponed_dir}")
            
            # If it was a Drive file, delete it from Drive because we have it local now
            if service and drive_file_id:
                try:
                    service.files().delete(fileId=drive_file_id).execute()
                    print("🗑️ Deleted from Drive (saved locally in postponed).")
                except:
                    pass
            return False
        return False

def process_postponed_videos():
    """Retries uploading videos from the postponed folder."""
    postponed_dir = CURRENT_DIR / "postponed_uploads"
    if not postponed_dir.exists():
        return

    files = list(postponed_dir.glob("*.mp4"))
    if not files:
        return

    print(f"\n📦 Processing {len(files)} postponed videos...")
    accounts = load_accounts()

    for file_path in files:
        file_name = file_path.name
        print(f"🔄 Retrying postponed: {file_name}")
        
        account = get_account_for_file(file_name, accounts)
        if not account:
            print(f"⚠️ Could not identify project for postponed file: {file_name}. Skipping.")
            continue
        
        success = handle_video_upload(str(file_path), file_name, account)
        if not success:
            print(f"⚠️ Failed to retry {file_name}. Keeping in postponed.")

def process_videos():
    service = get_drive_service()
    if not service: return

    accounts = load_accounts()
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    # List files in folder
    results = service.files().list(
        q=f"'{DRIVE_FOLDER_ID}' in parents and mimeType contains 'video/' and trashed = false",
        fields="nextPageToken, files(id, name)"
    ).execute()
    
    items = results.get('files', [])
    if not items:
        print("📭 No new videos in Drive folder.")
        return

    print(f"found {len(items)} videos to process...")

    for item in items:
        file_id = item['id']
        file_name = item['name']
        print(f"\n🎬 Processing: {file_name}")
        
        account = get_account_for_file(file_name, accounts)
        if not account:
            print(f"⚠️ Could not identify project for file: {file_name}. Skipping.")
            continue
            
        print(f"✅ Matched Account: {account['id']}")
        
        # Download
        local_path = os.path.join(DOWNLOAD_DIR, file_name)
        try:
            request = service.files().get_media(fileId=file_id)
            fh = open(local_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Downloading {int(status.progress() * 100)}%...")
            fh.close()
        except Exception as e:
            print(f"❌ Download failed for {file_name}: {e}")
            if os.path.exists(local_path):
                fh.close()
                os.remove(local_path)
            continue
        
        # Handle Upload
        handle_video_upload(local_path, file_name, account, service, file_id)

if __name__ == "__main__":
    while True:
        process_postponed_videos()
        process_videos()
        print("💤 Sleeping 60s...")
        time.sleep(60)
