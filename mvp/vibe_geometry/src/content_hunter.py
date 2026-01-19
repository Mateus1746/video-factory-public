import json
import os
import subprocess
import glob
from datetime import datetime

HISTORY_FILE = "data/posted_history.json"
DOWNLOAD_DIR = "downloads/raw_hunter"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return []

def save_to_history(video_id, title):
    history = load_history()
    history.append({
        "id": video_id,
        "title": title,
        "date": datetime.now().isoformat()
    })
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def search_and_download(query, limit=1):
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    print(f"🕵️ Hunter: Buscando por '{query}' (Filtro: < 6min, No Playlists)...")
    
    # 1. Get Metadata first to check history
    # yt-dlp "ytsearchN:query" --dump-json
    # Aumentamos o search scope para garantir que sobrem vídeos após a filtragem
    cmd_search = [
        "uv", "run", "yt-dlp",
        f"ytsearch{limit * 5}:{query}", 
        "--dump-json",
        "--default-search", "ytsearch",
        "--no-playlist", # Flag do yt-dlp para evitar baixar a playlist inteira se o link for uma
        "--quiet"
    ]
    
    try:
        result = subprocess.run(cmd_search, capture_output=True, text=True)
        # yt-dlp returns one JSON object per line
        results = [json.loads(line) for line in result.stdout.strip().split('\n') if line]
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        return None

    history = load_history()
    history_ids = {h['id'] for h in history}
    
    target_video = None
    
    # Palavras proibidas que indicam conteúdo longo/agregado
    blacklist_terms = ["full album", "compilation", " mix ", "1 hour", "10 hours"]

    for video in results:
        v_id = video.get('id')
        title = video.get('title', '').lower()
        v_type = video.get('_type', 'video') # Se for 'playlist', ignorar
        duration = video.get('duration', 0)
        
        # ---
        # FILTROS RÍGIDOS
        # ---
        
        # 1. Filtro de Tipo (Não pode ser playlist)
        if v_type == 'playlist':
            continue

        # 2. Filtro de Duração (Máx 6 minutos / 360s)
        if duration > 360: 
            continue
            
        # 3. Filtro de Histórico
        if v_id in history_ids:
            continue

        # 4. Filtro Semântico (Evitar Mixes que escaparam da duração)
        if any(bad_word in title for bad_word in blacklist_terms):
            continue
            
        # Se passou por tudo, é o escolhido
        target_video = video
        break
            
    if not target_video:
        print("⚠️ Nenhuma música válida encontrada após filtragem (Tempo > 6min, Playlist ou Duplicada).")
        return None

    print(f"🎯 Alvo Adquirido: {target_video['title']} (ID: {target_video['id']} | {int(target_video['duration'])}s)")
    
    # 2. Download
    output_template = f"{DOWNLOAD_DIR}/%(id)s.%(ext)s"
    
    cmd_download = [
        "uv", "run", "yt-dlp",
        "-f", "bestaudio/best",
        "-x", "--audio-format", "mp3",
        "-o", output_template,
        target_video['webpage_url']
    ]
    
    print("⬇️ Baixando áudio...")
    subprocess.run(cmd_download, check=True)
    
    # Find the file
    files = glob.glob(f"{DOWNLOAD_DIR}/{target_video['id']}.mp3")
    if not files:
        print("❌ Erro: Arquivo baixado não encontrado.")
        return None
        
    downloaded_file = files[0]
    
    # Update History
    save_to_history(target_video['id'], target_video['title'])
    
    return downloaded_file

if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "phonk drift 2026"
    f = search_and_download(q)
    if f:
        print(f"✅ Arquivo pronto: {f}")