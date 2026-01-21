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

# Config
DRIVE_FOLDER_ID = "101AIv9yfWOGfLl29gb74-n49xzcL2iCn"
DOWNLOAD_DIR = "downloaded_videos"
SCOPES = ['https://www.googleapis.com/auth/drive']
DB_PATH = BRAIN_PATH / "youtube_history.db" # Database location

def get_drive_service():
    creds = None
    # Try to load token.json (saved user creds)
    if os.path.exists('token_drive.json'):
        creds = Credentials.from_authorized_user_file('token_drive.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            # Look for client_secret
            files = glob.glob("client_secret*.json")
            if not files:
                print("❌ No client_secret found for Drive auth.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(files[0], SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save creds
        with open('token_drive.json', 'w') as token:
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
        "neon": "Neon Survivor Lab", # Assuming this ID in accounts.json
        "rogue": "Neon Survivor Lab",
        "marble": "Marble Paint War",
        "arena": "The Arena of Algoritms",
        "tower": "Tower Defense",
        "vibe": "Vibe Geometry"
    }

    # 1. Try Explicit Mapping
    for key, project_id in mappings.items():
        if key in filename_clean:
            # Find the account object for this ID
            for acc in accounts:
                if acc['id'].lower() == project_id.lower() or acc['id'].replace(" ", "_").lower() == project_id.replace(" ", "_").lower():
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
        
        # Upload to YouTube
        token_file = BRAIN_PATH / account['youtube_token']
        if not token_file.exists():
             # Try in root of brain if not found
             token_file = BRAIN_PATH / ".." / account['youtube_token'] # The git status showed tokens in ../../
             if not token_file.exists():
                 print(f"❌ Token not found: {token_file}")
                 continue

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
            
            # Handle both snake_case and camelCase for category_id
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
                
                # Register in Database for Autopilot
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
                    print(f"⚠️ Failed to register in DB (Autopilot might miss this): {db_err}")
                
                # Delete from Drive (or move)
                service.files().delete(fileId=file_id).execute()
                print("🗑️ Deleted from Drive.")
                
                # Delete local
                os.remove(local_path)
            
        except Exception as e:
            print(f"❌ Upload Failed: {e}")

if __name__ == "__main__":
    while True:
        process_videos()
        print("💤 Sleeping 60s...")
        time.sleep(60)
