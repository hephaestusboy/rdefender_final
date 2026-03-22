import os
import warnings
import logging
import json
import hashlib

# --- KILL JOBLIB SPAM DEAD ---
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["LOKY_MAX_CPU_COUNT"] = "1"
os.environ["JOBLIB_MULTIPROCESSING"] = "0"
warnings.filterwarnings("ignore")
logging.getLogger('joblib').setLevel(logging.ERROR) 

import webview
from datetime import datetime
import psutil
import time
import shutil
import stat
import threading
import queue

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from rdefender_agent import MLScannerEngine, quarantine_file, SUPPORTED_EXTENSIONS, LOG_FILE, TARGET_WATCH_DIR

WHITELIST_FILE = "rdefender_whitelist.json"
QUARANTINE_ROOT = "C:\\RDefender_Quarantine"
METADATA_FILE = os.path.join(QUARANTINE_ROOT, "metadata.json")

# --- HELPER FUNCTIONS ---
def compute_file_hash(filepath):
    try:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""): sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception: return None

def load_whitelist():
    """Loads a dictionary of {hash: filename}"""
    if os.path.exists(WHITELIST_FILE):
        try:
            with open(WHITELIST_FILE, 'r') as f: 
                data = json.load(f)
                # Automatically upgrade legacy arrays to dictionaries!
                if "hashes" in data:
                    return {h: "Unknown_Legacy_File.exe" for h in data.get("hashes", [])}
                return data.get("items", {})
        except Exception: pass
    return {}

def save_whitelist(whitelist_dict):
    """Saves the dictionary format to disk"""
    try:
        with open(WHITELIST_FILE, 'w') as f: json.dump({"items": whitelist_dict}, f, indent=2)
    except Exception: pass

class FileHandler(FileSystemEventHandler):
    def __init__(self, api): self.api = api
    def on_created(self, event):
        if not event.is_directory: self.api.evaluate_and_queue(event.src_path)
    def on_modified(self, event):
        if not event.is_directory: self.api.evaluate_and_queue(event.src_path)

# ==========================================
# THE BRIDGE API (Connects Python to HTML)
# ==========================================
class RDefenderAPI:
    def __init__(self):
        self.window = None
        self.monitoring = False
        self.observer = None
        self.agent_process = psutil.Process(os.getpid())
        self.file_queue = queue.Queue()
        self.file_state_db = {} 
        self.db_lock = threading.Lock() 
        self.active_scans = set()
        self.active_scans_lock = threading.Lock()
        
        self.whitelist = load_whitelist() # Now loads a dictionary
        self.whitelist_lock = threading.Lock()
        self.scanner = MLScannerEngine()
        
        self.start_queue_workers()
        threading.Thread(target=self.metrics_loop, daemon=True).start()

    def set_window(self, window):
        self.window = window
        self._update_ui_status("LOADED & READY", "#22c55e")

    # --- JAVASCRIPT CALLABLE METHODS ---
    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            threading.Thread(target=self._build_initial_baseline, daemon=True).start()
            path = TARGET_WATCH_DIR
            event_handler = FileHandler(self)
            self.observer = Observer()
            self.observer.schedule(event_handler, path, recursive=True)
            self.observer.start()
            threading.Thread(target=self._sweeper_loop, daemon=True).start()

    def stop_monitoring(self):
        self.monitoring = False
        self._update_ui_status("IDLE", "#facc15")
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

    def scan_folder(self):
        folder = self.window.create_file_dialog(webview.FOLDER_DIALOG)
        if folder and len(folder) > 0:
            threading.Thread(target=self._scan_folder_worker, args=(folder[0],), daemon=True).start()

    # --- MODAL DATA EXCHANGES ---
    def get_quarantine_data(self):
        """Reads metadata.json and sends it to the HTML Modal."""
        if not os.path.exists(METADATA_FILE): return []
        try:
            with open(METADATA_FILE, 'r') as f: meta = json.load(f)
            data_list = []
            for q_id, info in meta.items():
                data_list.append({
                    "id": q_id,
                    "name": os.path.basename(info.get("original_path", "Unknown")),
                    "path": info.get("original_path", "Unknown"),
                    "severity": info.get("severity", "Unknown")
                })
            return data_list
        except Exception: return []

    def execute_recovery(self, selected_ids):
        """Receives checked items from HTML, moves them back, and updates whitelist dictionary."""
        if not os.path.exists(METADATA_FILE): return
        try:
            with open(METADATA_FILE, 'r') as f: meta = json.load(f)
            
            for q_id in selected_ids:
                if q_id not in meta: continue
                info = meta[q_id]
                original_path = info["original_path"]
                
                quarantine_path = None
                for root, _, files in os.walk(QUARANTINE_ROOT):
                    if q_id in files:
                        quarantine_path = os.path.join(root, q_id)
                        break
                
                if quarantine_path and os.path.exists(quarantine_path):
                    try:
                        os.makedirs(os.path.dirname(original_path), exist_ok=True)
                        os.chmod(quarantine_path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                        shutil.move(quarantine_path, original_path)
                        
                        # Auto-Whitelist the recovered file with its actual NAME
                        f_hash = compute_file_hash(original_path)
                        if f_hash:
                            with self.whitelist_lock:
                                self.whitelist[f_hash] = os.path.basename(original_path)
                                save_whitelist(self.whitelist)
                        
                        del meta[q_id]
                        time_str = datetime.now().strftime("%H:%M:%S")
                        self.window.evaluate_js(f"addAlert('{time_str}', '{os.path.basename(original_path)}', 'RESTORED', 'Un-Quarantined', 'clean');")
                    except Exception as e: print(f"Restore failed: {e}")

            with open(METADATA_FILE, 'w') as f: json.dump(meta, f, indent=2)
        except Exception as e: print(f"Recovery Error: {e}")

    def get_whitelist_data(self):
        """Sends whitelist hashes AND names to HTML Modal."""
        with self.whitelist_lock:
            # Send an array of objects to javascript
            return [{"hash": k, "name": v} for k, v in self.whitelist.items()]

    def execute_whitelist_removal(self, selected_hashes):
        """Receives checked hashes from HTML and removes them from the dictionary."""
        with self.whitelist_lock:
            for h in selected_hashes:
                self.whitelist.pop(h, None) # Use pop to safely remove dictionary keys
            save_whitelist(self.whitelist)

    # --- CORE WORKERS (UNCHANGED) ---
    def start_queue_workers(self):
        workers = os.cpu_count() or 4
        for _ in range(workers): threading.Thread(target=self._process_queue_loop, daemon=True).start()

    def _process_queue_loop(self):
        while True:
            filepath = self.file_queue.get() 
            try: self.process_file(filepath)
            except Exception: pass
            finally: self.file_queue.task_done()

    def _sweeper_loop(self):
        while True:
            if self.monitoring:
                try:
                    for root_dir, _, files in os.walk(TARGET_WATCH_DIR):
                        for file in files: self.evaluate_and_queue(os.path.join(root_dir, file))
                except Exception: pass
            time.sleep(3) 

    def evaluate_and_queue(self, filepath):
        if not filepath.lower().endswith(SUPPORTED_EXTENSIONS): return
        lower_path = filepath.lower()
        if "$recycle.bin" in lower_path or "system volume information" in lower_path: return

        try:
            if os.path.getsize(filepath) > 10485760: return 
            file_hash = compute_file_hash(filepath)
            if file_hash:
                with self.whitelist_lock:
                    if file_hash in self.whitelist: return  # Checking 'in dict' perfectly matches keys

            current_mtime = os.path.getmtime(filepath)
            with self.db_lock:
                last_mtime = self.file_state_db.get(filepath, 0)
                if current_mtime == last_mtime: return 
                self.file_state_db[filepath] = current_mtime
                
            locked_path = filepath + ".scanning"
            os.rename(filepath, locked_path)
            self.file_queue.put(locked_path)
        except OSError: pass

    def process_file(self, locked_path):
        original_path = locked_path.replace(".scanning", "")
        name = os.path.basename(original_path)

        if LOG_FILE.lower() in name.lower(): return

        with self.active_scans_lock: self.active_scans.add(name)

        try:
            label, score = self.scanner.scan_file(locked_path)
            if label == "ERROR":
                result_str, action, tag = "SCAN FAILED", "Ignored", "error"
                try: os.rename(locked_path, original_path) 
                except: pass
            else:
                score_pct = float(score) * 100
                result_str = f"{label} ({score_pct:.1f}%)"
                if label == "MALWARE":
                    tag = "malware"
                    success = quarantine_file(locked_path, label)
                    action = "QUARANTINED" if success else "Q-FAILED (LOCKED)"
                elif label == "SUSPICIOUS":
                    action, tag = "Logged/Flagged", "suspicious"
                    quarantine_file(locked_path, label)
                else:
                    action, tag = "Allowed", "clean"
                    try: os.rename(locked_path, original_path)
                    except: pass

            time_str = datetime.now().strftime("%H:%M:%S")
            if self.window:
                js_code = f"addAlert('{time_str}', '{name}', '{result_str}', '{action}', '{tag}');"
                self.window.evaluate_js(js_code)
        finally:
            with self.active_scans_lock: self.active_scans.discard(name)

    def _build_initial_baseline(self):
        self._update_ui_status("BUILDING BASELINE...", "#facc15")
        with self.db_lock:
            for root_dir, _, files in os.walk(TARGET_WATCH_DIR):
                for file in files:
                    if file.lower().endswith(SUPPORTED_EXTENSIONS):
                        filepath = os.path.join(root_dir, file)
                        try: self.file_state_db[filepath] = os.path.getmtime(filepath)
                        except OSError: pass 
        self._update_ui_status("ACTIVE SCANNING", "#22c55e")

    def metrics_loop(self):
        while True:
            if self.window:
                try:
                    cpu = f"{self.agent_process.cpu_percent(interval=None):.2f}"
                    mem = f"{self.agent_process.memory_info().rss / (1024 * 1024):.2f}"
                    with self.active_scans_lock:
                        scans = "None" if not self.active_scans else "Scanning: " + " | ".join(list(self.active_scans)[:4])
                    self.window.evaluate_js(f"updateMetrics('{cpu}', '{mem}', document.getElementById('engineStatus').innerText, document.getElementById('engineStatus').style.color, '{scans}')")
                except Exception: pass
            time.sleep(1)

    def _update_ui_status(self, text, color):
        if self.window:
            self.window.evaluate_js(f"document.getElementById('engineStatus').innerText = '{text}'; document.getElementById('engineStatus').style.color = '{color}';")

    def _scan_folder_worker(self, folder_path):
        self._update_ui_status(f"FOLDER SCAN ACTIVE ({folder_path})", "#a855f7")
        for root_dir, _, files in os.walk(folder_path):
            for file in files:
                filepath = os.path.join(root_dir, file)
                self.evaluate_and_queue(filepath)
        while not self.file_queue.empty(): time.sleep(1)
        self._update_ui_status("ACTIVE SCANNING" if self.monitoring else "IDLE", "#22c55e" if self.monitoring else "#facc15")


# ==========================================
# LAUNCH THE WEBVIEW APP
# ==========================================
def on_window_ready(window, api_instance):
    api_instance.set_window(window)

if __name__ == '__main__':
    api = RDefenderAPI()
    
    window = webview.create_window(
        title='RDefender',
        url='gui/index.html',
        js_api=api,
        width=1100,
        height=750,
        background_color='#0f172a'
    )
    
    webview.start(on_window_ready, (window, api), gui='qt')