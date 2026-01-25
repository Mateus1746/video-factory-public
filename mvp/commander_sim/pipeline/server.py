import subprocess
import urllib.request
import urllib.error
import json
import time
import os
import sys
import threading
from config import WIDTH, HEIGHT, FPS, DURATION

SERVER_URL = "http://localhost:3000"

class RenderServer:
    def __init__(self, script_path, base_dir):
        self.script_path = script_path
        self.base_dir = base_dir
        self.process = None

    def start(self):
        print("🚀 Starting Render Server...")
        log_file = open(os.path.join(self.base_dir, "render_server.log"), "w")
        self.process = subprocess.Popen(
            ["node", self.script_path],
            stdout=log_file,
            stderr=log_file,
            cwd=self.base_dir
        )
        print("⏳ Waiting for server...")
        for _ in range(30):
            try:
                with urllib.request.urlopen(f"{SERVER_URL}/health") as response:
                    if response.status == 200:
                        print("✅ Server is ready!")
                        return True
            except Exception:
                time.sleep(1)
        
        print("❌ Server failed to start.")
        self.stop()
        return False

    def stop(self):
        print("💀 Shutting down Render Server...")
        try:
            req = urllib.request.Request(f"{SERVER_URL}/shutdown", method='POST')
            with urllib.request.urlopen(req) as response: pass
        except: pass
        
        if self.process:
            self.process.terminate()
            self.process.wait()

    def request_render(self, map_file, theme, names):
        map_type = 'JSON' 
        
        payload_data = {
            "mapFile": map_file,
            "type": map_type,
            "outputDir": self.base_dir,
            "config": {
                "width": WIDTH,
                "height": HEIGHT,
                "fps": FPS,
                "quality": 90,
                "maxFrames": DURATION * FPS,
                "THEME": theme,
                "NAMES": names
            }
        }
        
        payload = json.dumps(payload_data).encode('utf-8')
        req = urllib.request.Request(
            f"{SERVER_URL}/render",
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        stop_event = threading.Event()
        monitor_thread = threading.Thread(target=self._monitor_progress, args=(stop_event,))
        monitor_thread.start()

        try:
            with urllib.request.urlopen(req) as response:
                return json.load(response)
        except urllib.error.HTTPError as e:
            print(f"\n❌ Render Request Failed: {e.code}")
            return {"success": False}
        except Exception as e:
            print(f"\n❌ Connection Error: {e}")
            return {"success": False}
        finally:
            stop_event.set()
            monitor_thread.join()

    def _monitor_progress(self, stop_event):
        last_frame = -1
        while not stop_event.is_set():
            try:
                with urllib.request.urlopen(f"{SERVER_URL}/progress", timeout=1) as response:
                    data = json.load(response)
                    if data.get("isRendering"):
                        curr = data.get("frameCount", 0)
                        if curr != last_frame:
                            print(f"\r  📸 Rendering Frame: {curr}...", end="", flush=True)
                            last_frame = curr
            except: pass
            time.sleep(0.5)
        print("")
