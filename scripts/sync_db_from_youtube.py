import json
import sqlite3
import time
import sys
from pathlib import Path

# Setup paths
CURRENT_DIR = Path(__file__).resolve().parent
ORCHESTRATOR_ROOT = CURRENT_DIR.parents[2]
BRAIN_PATH = ORCHESTRATOR_ROOT / "brain"

if str(ORCHESTRATOR_ROOT) not in sys.path:
    sys.path.append(str(ORCHESTRATOR_ROOT))

try:
    from brain.modules.youtube_uploader import YouTubeUploader
    from brain.modules.database import DatabaseManager
except ImportError as e:
    print(f"❌ Could not import brain modules: {e}")
    sys.exit(1)

def load_accounts():
    with open(BRAIN_PATH / "accounts.json", 'r') as f:
        return json.load(f)

def sync_account(account, db_manager):
    print(f"\n📡 Syncing account: {account['id']}...")
    token_file = BRAIN_PATH / account['youtube_token']
    
    if not token_file.exists():
        token_file = BRAIN_PATH / ".." / account['youtube_token']
        if not token_file.exists():
            print(f"  ❌ Token not found.")
            return

    try:
        uploader = YouTubeUploader(str(token_file))
        client = uploader._get_client()
        
        # List videos (snippets and status)
        request = client.search().list(
            part="snippet",
            forMine=True,
            type="video",
            order="date",
            maxResults=15 
        )
        response = request.execute()
        
        items = response.get("items", [])
        if not items:
            print("  📭 No recent videos found on channel.")
            return

        print(f"  🔍 Found {len(items)} recent videos on YouTube. Checking status...")

        conn = db_manager._get_conn()
        cursor = conn.cursor()

        for item in items:
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            
            # We need to fetch details to check privacy status (search.list doesn't give full status)
            video_request = client.videos().list(
                part="status,snippet",
                id=video_id
            )
            video_response = video_request.execute()
            if not video_response.get('items'):
                continue
                
            details = video_response['items'][0]
            privacy = details['status']['privacyStatus']
            
            if privacy == 'private':
                # Check if exists in DB
                cursor.execute("SELECT 1 FROM pending_queue WHERE video_id = ?", (video_id,))
                exists = cursor.fetchone()
                
                if not exists:
                    print(f"  📥 Recovering missing video: {title}")
                    
                    # Insert into DB
                    # We don't have the original description or local path, so we improvise
                    desc = details['snippet']['description']
                    
                    # Force insert
                    db_manager.add_to_pending({
                        "video_id": video_id,
                        "title": title,
                        "description": desc,
                        "uploaded_at": time.time(), # Now
                        "path": "REMOTE_RECOVERY", # Placeholder
                        "account_id": account['id']
                    })
                else:
                    # print(f"  ✅ Already in DB: {title}")
                    pass
            else:
                # print(f"  👀 Public/Unlisted (Skipping): {title}")
                pass

        conn.close()

    except Exception as e:
        error_msg = str(e)
        if "quotaExceeded" in error_msg:
            print("  🛑 QUOTA EXCEEDED. Cannot sync right now.")
            return False # Stop everything
        print(f"  ❌ Error checking channel: {e}")
    
    return True

def main():
    print("🚀 Starting Database <-> YouTube Sync...")
    accounts = load_accounts()
    db = DatabaseManager(BRAIN_PATH / "youtube_history.db")
    
    for account in accounts:
        success = sync_account(account, db)
        if success is False:
            print("\n🛑 Aborting sync due to critical API error (likely Quota).")
            break
            
    print("\n✅ Sync process finished.")

if __name__ == "__main__":
    main()
