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
        if not event.is_directory: self.api._evaluate_and_queue(event.src_path)
    def on_modified(self, event):
        if not event.is_directory: self.api._evaluate_and_queue(event.src_path)

# ==========================================
# THE BRIDGE API (Connects Python to HTML)
# ==========================================
class RDefenderAPI:
    def __init__(self):
        # Using underscores hides these from PyWebView's JS converter, preventing the recursion crash!
        self._window = None
        self._monitoring = False
        self._observer = None
        self._agent_process = psutil.Process(os.getpid())
        self._file_queue = queue.Queue()
        self._file_state_db = {} 
        self._db_lock = threading.Lock() 
        self._active_scans = set()
        self._active_scans_lock = threading.Lock()
        
        # --- NEW: Folder Scan Kill Switches ---
        self._folder_scan_active = False
        self._cancel_folder_scan = False
        
        self._whitelist = load_whitelist() # Now loads a dictionary
        self._whitelist_lock = threading.Lock()
        self._scanner = MLScannerEngine()
        
        self._start_queue_workers()
        threading.Thread(target=self._metrics_loop, daemon=True).start()

    def set_window(self, window):
        self._window = window
        self._update_ui_status("LOADED & READY", "#22c55e")

    # --- PUBLIC JAVASCRIPT CALLABLE METHODS (NO UNDERSCORES) ---
    def start_monitoring(self):
        if not self._monitoring:
            self._monitoring = True
            threading.Thread(target=self._build_initial_baseline, daemon=True).start()
            path = TARGET_WATCH_DIR
            event_handler = FileHandler(self)
            self._observer = Observer()
            self._observer.schedule(event_handler, path, recursive=True)
            self._observer.start()
            threading.Thread(target=self._sweeper_loop, daemon=True).start()

    def stop_monitoring(self):
        self._monitoring = False
        self._update_ui_status("IDLE", "#facc15")
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None

    def scan_folder(self):
        if not self._window: return
        
        # 1. KILL SWITCH: Intercept active scan
        if self._folder_scan_active:
            self._cancel_folder_scan = True
            return
            
        # 2. NORMAL START: Open dialog and scan
        folder = self._window.create_file_dialog(webview.FileDialog.FOLDER)
        if folder and len(folder) > 0:
            self._folder_scan_active = True
            self._cancel_folder_scan = False
            
            # Morph the UI button into a red CANCEL button
            self._window.evaluate_js("""
                var btn = document.getElementById('scanFolderBtn');
                if (btn) {
                    btn.innerText = 'CANCEL SCAN';
                    btn.style.background = 'linear-gradient(135deg, #ef4444, #b91c1c)';
                }
            """)
            
            threading.Thread(target=self._scan_folder_worker, args=(folder[0],), daemon=True).start()

    # --- MODAL DATA EXCHANGES (NO UNDERSCORES) ---
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
                            with self._whitelist_lock:
                                self._whitelist[f_hash] = os.path.basename(original_path)
                                save_whitelist(self._whitelist)
                        
                        del meta[q_id]
                        time_str = datetime.now().strftime("%H:%M:%S")
                        if self._window:
                            self._window.evaluate_js(f"addAlert('{time_str}', '{os.path.basename(original_path)}', 'RESTORED', 'Un-Quarantined', 'clean');")
                    except Exception as e: print(f"Restore failed: {e}")

            with open(METADATA_FILE, 'w') as f: json.dump(meta, f, indent=2)
        except Exception as e: print(f"Recovery Error: {e}")

    def get_whitelist_data(self):
        """Sends whitelist hashes AND names to HTML Modal."""
        with self._whitelist_lock:
            # Send an array of objects to javascript
            return [{"hash": k, "name": v} for k, v in self._whitelist.items()]

    def execute_whitelist_removal(self, selected_hashes):
        """Receives checked hashes from HTML and removes them from the dictionary."""
        with self._whitelist_lock:
            for h in selected_hashes:
                self._whitelist.pop(h, None) # Use pop to safely remove dictionary keys
            save_whitelist(self._whitelist)

    # --- INTERNAL CORE WORKERS (HIDDEN WITH UNDERSCORES) ---
    def _start_queue_workers(self):
        workers = os.cpu_count() or 4
        for _ in range(workers): threading.Thread(target=self._process_queue_loop, daemon=True).start()

    def _process_queue_loop(self):
        while True:
            filepath = self._file_queue.get() 
            try: self._process_file(filepath)
            except Exception: pass
            finally: self._file_queue.task_done()

    def _sweeper_loop(self):
        while True:
            if self._monitoring:
                try:
                    for root_dir, _, files in os.walk(TARGET_WATCH_DIR):
                        for file in files: self._evaluate_and_queue(os.path.join(root_dir, file))
                except Exception: pass
            time.sleep(3) 

    def _evaluate_and_queue(self, filepath):
        if filepath.endswith(".scanning"): return
        if not filepath.lower().endswith(SUPPORTED_EXTENSIONS): return
        lower_path = filepath.lower()
        if "$recycle.bin" in lower_path or "system volume information" in lower_path: return

        try:
            if os.path.getsize(filepath) > 10485760: return 
            file_hash = compute_file_hash(filepath)
            if file_hash:
                with self._whitelist_lock:
                    if file_hash in self._whitelist: return  # Checking 'in dict' perfectly matches keys

            current_mtime = os.path.getmtime(filepath)
            with self._db_lock:
                last_mtime = self._file_state_db.get(filepath, 0)
                if current_mtime == last_mtime: return 
                self._file_state_db[filepath] = current_mtime
                
            locked_path = filepath + ".scanning"
            os.rename(filepath, locked_path)
            self._file_queue.put(locked_path)
        except OSError: pass

    def _process_file(self, locked_path):
        original_path = locked_path.replace(".scanning", "")
        name = os.path.basename(original_path)

        if LOG_FILE.lower() in name.lower(): return

        with self._active_scans_lock: self._active_scans.add(name)

        try:
            label, score = self._scanner.scan_file(locked_path)
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
            if self._window:
                js_code = f"addAlert('{time_str}', '{name}', '{result_str}', '{action}', '{tag}');"
                self._window.evaluate_js(js_code)
        finally:
            with self._active_scans_lock: self._active_scans.discard(name)

    def _build_initial_baseline(self):
        self._update_ui_status("BUILDING BASELINE...", "#facc15")
        with self._db_lock:
            for root_dir, _, files in os.walk(TARGET_WATCH_DIR):
                for file in files:
                    if file.lower().endswith(SUPPORTED_EXTENSIONS):
                        filepath = os.path.join(root_dir, file)
                        try: self._file_state_db[filepath] = os.path.getmtime(filepath)
                        except OSError: pass 
        self._update_ui_status("ACTIVE SCANNING", "#22c55e")

    def _metrics_loop(self):
        while True:
            if self._window:
                try:
                    cpu = f"{self._agent_process.cpu_percent(interval=None):.2f}"
                    mem = f"{self._agent_process.memory_info().rss / (1024 * 1024):.2f}"
                    with self._active_scans_lock:
                        scans = "None" if not self._active_scans else "Scanning: " + " | ".join(list(self._active_scans)[:4])
                    self._window.evaluate_js(f"updateMetrics('{cpu}', '{mem}', document.getElementById('engineStatus').innerText, document.getElementById('engineStatus').style.color, '{scans}')")
                except Exception: pass
            time.sleep(1)

    def _update_ui_status(self, text, color):
        if self._window:
            self._window.evaluate_js(f"document.getElementById('engineStatus').innerText = '{text}'; document.getElementById('engineStatus').style.color = '{color}';")

    def _scan_folder_worker(self, folder_path):
        self._update_ui_status(f"FOLDER SCAN ACTIVE ({folder_path})", "#a855f7")
        detected_count = 0
        
        for root_dir, _, files in os.walk(folder_path):
            if self._cancel_folder_scan: break # [CANCELLED] Check if user clicked Cancel (Folder Level)
        
        for file in files:
            if self._cancel_folder_scan: break # [CANCELLED] Check if user clicked Cancel (File Level)
            if not file.lower().endswith(SUPPORTED_EXTENSIONS): continue
                
            filepath = os.path.join(root_dir, file)
            lower_path = filepath.lower()
            if "$recycle.bin" in lower_path or "system volume information" in lower_path: continue
                
            try:
                    # Size guardrail
                if os.path.getsize(filepath) > 10485760: continue
                    
                    # Whitelist check
                f_hash = compute_file_hash(filepath)
                if f_hash:
                    with self._whitelist_lock:
                        if f_hash in self._whitelist: continue
                    
                name = os.path.basename(filepath)
                with self._active_scans_lock: self._active_scans.add(f"[FOLDER] {name}")
                    
                try:
                        # SCAN DIRECTLY: Do not use the real-time queue or rename the file
                    label, score = self._scanner.scan_file(filepath)
                    if label == "ERROR": continue
                        
                    score_pct = float(score) * 100
                    result_str = f"{label} ({score_pct:.1f}%)"
                        
                    if label == "MALWARE":
                        detected_count += 1
                        tag = "malware"
                        success = quarantine_file(filepath, label)
                        action = "QUARANTINED" if success else "Q-FAILED (LOCKED)"
                    elif label == "SUSPICIOUS":
                        detected_count += 1
                        action, tag = "Logged/Flagged", "suspicious"
                        quarantine_file(filepath, label)
                    else:
                        action, tag = "Allowed", "clean"
                        
                    time_str = datetime.now().strftime("%H:%M:%S")
                    if self._window:
                        self._window.evaluate_js(f"addAlert('{time_str}', '{name}', '{result_str}', '{action}', '{tag}');")
                            
                finally:
                    with self._active_scans_lock: self._active_scans.discard(f"[FOLDER] {name}")
            except Exception: pass

        # --- CLEANUP STUCK .SCANNING FILES IN SCANNED FOLDER ---
        try:
            for root_dir, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(".scanning"):
                        stuck = os.path.join(root_dir, file)
                        original = stuck.replace(".scanning", "")
                        try: os.rename(stuck, original)
                        except OSError: pass
        except Exception: pass

        # --- CLEANUP AND RESET UI ---
        self._folder_scan_active = False
        self._cancel_folder_scan = False
        self._update_ui_status("ACTIVE SCANNING" if self._monitoring else "IDLE", "#22c55e" if self._monitoring else "#facc15")
        
        if self._window:
            self._window.evaluate_js(f"""
                var btn = document.getElementById('scanFolderBtn');
                if (btn) {{
                    btn.innerText = 'SCAN FOLDER';
                    btn.style.background = 'linear-gradient(135deg, #8b5cf6, #6d28d9)';
                }}
                alert('Folder Scan Stopped/Finished!\\n\\nDetected Threats: {detected_count}');
            """)


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
    
    webview.start(on_window_ready, (window, api))