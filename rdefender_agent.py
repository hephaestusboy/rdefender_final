import os
import sys
import time
import stat
import shutil
import warnings
import logging
import base64
import json
import hashlib
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- FIX WINDOWS EMOJI CRASH ---
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["LOKY_MAX_CPU_COUNT"] = "1"
os.environ["JOBLIB_MULTIPROCESSING"] = "0"

warnings.filterwarnings("ignore")
warnings.simplefilter(action='ignore', category=UserWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore", message="X does not have valid feature names")

logging.getLogger('joblib').setLevel(logging.ERROR)

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import joblib
import numpy as np

from static_feature_extractor import extract_features_from_binary
from feature_vectorizer import vectorize_features
from model_feature_groups import MODEL1_INDICES, MODEL2_INDICES
from feature_schema import FEATURE_SCHEMA

# ==========================================
# CONFIGURATION
# ==========================================
LOG_FILE             = "rdefender_events.log"
QUARANTINE_ROOT      = "C:\\RDefender_Quarantine"
QUARANTINE_MALWARE   = os.path.join(QUARANTINE_ROOT, "Malware")
QUARANTINE_SUSPICIOUS = os.path.join(QUARANTINE_ROOT, "Suspicious")
TARGET_WATCH_DIR     = "C:\\"

THRESHOLD_FILE       = "thresholds_v5.json"
MALWARE_THRESHOLD    = 0.60
SUSPICIOUS_THRESHOLD = 0.45
SUPPORTED_EXTENSIONS = (".exe", ".sys", ".dll", ".bat")

SILVER_BULLETS = [
    "IS_SIGNATURE_VALID",
    "SHADOW_COPY_DELETION_STRINGS",
    "VIRTUAL_RAW_SIZE_ANOMALY",
    "FILE_ENTROPY"
]
SILVER_INDICES = [FEATURE_SCHEMA.index(f) for f in SILVER_BULLETS]

def _load_thresholds(base_path):
    tf = os.path.join(base_path, THRESHOLD_FILE)
    if os.path.exists(tf):
        try:
            with open(tf) as fh:
                t = json.load(fh)
            return t["malware_threshold"], t["suspicious_threshold"]
        except Exception:
            pass
    return MALWARE_THRESHOLD, SUSPICIOUS_THRESHOLD

# ==========================================
# QUARANTINE SYSTEM
# ==========================================
QUARANTINE_METADATA_FILE = os.path.join(QUARANTINE_ROOT, "metadata.json")

def load_quarantine_metadata():
    if os.path.exists(QUARANTINE_METADATA_FILE):
        try:
            with open(QUARANTINE_METADATA_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_quarantine_metadata(metadata):
    os.makedirs(QUARANTINE_ROOT, exist_ok=True)
    try:
        with open(QUARANTINE_METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
    except Exception:
        pass

def quarantine_file(filepath, label):
    max_retries = 8
    retry_delay = 1.5
    target_dir = QUARANTINE_MALWARE if label == "MALWARE" else QUARANTINE_SUSPICIOUS

    try:
        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(QUARANTINE_ROOT, exist_ok=True)

        filename  = os.path.basename(filepath)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_filename  = f"{os.path.splitext(filename)[0]}.{timestamp}.quarantine"
        quarantine_path = os.path.join(target_dir, safe_filename)

        for attempt in range(max_retries):
            try:
                shutil.move(filepath, quarantine_path)
                print(f"\033[91m[QUARANTINED] {filename} moved to {label} vault!\033[0m")
                metadata = load_quarantine_metadata()
                metadata[safe_filename] = {
                    "original_path": filepath,
                    "timestamp": timestamp,
                    "severity": label
                }
                save_quarantine_metadata(metadata)
                return quarantine_path
            except PermissionError:
                print(f"\033[93m[WARNING] File locked, retrying quarantine (Attempt {attempt+1}/{max_retries})...\033[0m")
                time.sleep(retry_delay)

        print("\033[93m[WARNING] Attempting active file permission lockdown...\033[0m")
        try:
            os.chmod(filepath, stat.S_IREAD | stat.S_IWRITE)
            os.chmod(filepath, 0)
            return "LOCKED_BUT_DEFANGED"
        except Exception:
            return None

    except Exception as e:
        print(f"\033[95m[ERROR] QUARANTINE ERROR: {str(e)}\033[0m")
        return None

# ==========================================
# MACHINE LEARNING ENGINE
# ==========================================
class MLScannerEngine:
    """Loads all 9 v5 models once into RAM and handles inference for live files."""

    def __init__(self):
        print("[LOADING] Loading R-Defender ML Engine v5 (8-model fusion) into RAM...")

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        self.models = {
            "rf_b":   joblib.load(os.path.join(base_path, "rf_behavior_model_v5.joblib")),
            "rf_a":   joblib.load(os.path.join(base_path, "rf_artifact_model_v5.joblib")),
            "xgb_b":  joblib.load(os.path.join(base_path, "xgb_behavior_model_v5.joblib")),
            "xgb_a":  joblib.load(os.path.join(base_path, "xgb_artifact_model_v5.joblib")),
            "lgbm_b": joblib.load(os.path.join(base_path, "lgbm_behavior_model_v5.joblib")),
            "lgbm_a": joblib.load(os.path.join(base_path, "lgbm_artifact_model_v5.joblib")),
            "cat_b":  joblib.load(os.path.join(base_path, "catboost_behavior_model_v5.joblib")),
            "cat_a":  joblib.load(os.path.join(base_path, "catboost_artifact_model_v5.joblib")),
            "fusion": joblib.load(os.path.join(base_path, "fusion_model_v5.joblib")),
        }

        self.mal_thresh, self.susp_thresh = _load_thresholds(base_path)
        print(f"[SUCCESS] Models loaded. Thresholds: MALWARE≥{self.mal_thresh}  SUSPICIOUS≥{self.susp_thresh}")

    # ------------------------------------------------------------------
    # 32-feature meta array — must exactly match train_ensemble_v5.py
    #
    #  1-8  : p_rb, p_ra, p_xb, p_xa, p_lb, p_la, p_cb, p_ca
    #  9-10 : avg_behavior, avg_artifact
    #  11   : disagreement
    #  12   : prob_entropy
    #  13-14: high_artifact_stealth, high_behavior_stealth
    #  15   : joint_conf
    #  16-19: per-algo behavior-artifact deltas (rf, xgb, lgbm, cat)
    #  20-21: max_sig, min_sig
    #  22-25: silver bullets
    #  26   : extreme_artifact_loose
    #  27   : extreme_behavior_loose
    #  28   : consensus_soft
    #  29   : behavior_dominance
    #  30   : signed x avg_prob
    #  31   : entropy x avg_prob
    #  32   : std across all 8 probs
    # ------------------------------------------------------------------
    def build_fusion_features(self, p_rb, p_ra, p_xb, p_xa, p_lb, p_la, p_cb, p_ca, raw_vec):
        probs = np.array([p_rb, p_ra, p_xb, p_xa, p_lb, p_la, p_cb, p_ca])

        avg_behavior = (p_rb + p_xb + p_lb + p_cb) / 4
        avg_artifact = (p_ra + p_xa + p_la + p_ca) / 4
        disagreement = abs(avg_behavior - avg_artifact)
        prob_entropy = -(probs * np.log(probs + 1e-9) + (1 - probs) * np.log(1 - probs + 1e-9)).mean()

        high_artifact_stealth  = 1.0 if (avg_artifact > 0.7  and avg_behavior < 0.2)  else 0.0
        high_behavior_stealth  = 1.0 if (avg_behavior > 0.7  and avg_artifact < 0.2)  else 0.0
        joint_conf             = avg_artifact * avg_behavior
        extreme_artifact_loose = 1.0 if (avg_artifact > 0.75 and avg_behavior < 0.30) else 0.0
        extreme_behavior_loose = 1.0 if (avg_behavior > 0.75 and avg_artifact < 0.30) else 0.0
        consensus_soft         = 1.0 if (avg_behavior > 0.30 and avg_artifact > 0.30) else 0.0
        behavior_dominance     = max(0.0, avg_behavior - avg_artifact)

        raw_silver     = np.array(raw_vec)[SILVER_INDICES]
        avg_prob       = (avg_behavior + avg_artifact) / 2
        signed_x_prob  = float(raw_silver[0]) * avg_prob
        entropy_x_prob = (float(raw_silver[3]) / 8.0) * avg_prob
        prob_std       = float(probs.std())

        return np.array([[
            p_rb, p_ra, p_xb, p_xa, p_lb, p_la, p_cb, p_ca,
            avg_behavior, avg_artifact,
            disagreement, prob_entropy,
            high_artifact_stealth, high_behavior_stealth,
            joint_conf,
            (p_ra - p_rb), (p_xa - p_xb), (p_la - p_lb), (p_ca - p_cb),
            float(probs.max()), float(probs.min()),
            raw_silver[0], raw_silver[1], raw_silver[2], raw_silver[3],
            extreme_artifact_loose, extreme_behavior_loose,
            consensus_soft, behavior_dominance,
            signed_x_prob, entropy_x_prob,
            prob_std,
        ]])

    def scan_file(self, filepath):
        """Scan a file. Returns (label, score). Includes retry logic for Windows file locks."""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                feats = extract_features_from_binary(filepath)

                raw_shadow  = feats.get("SHADOW_COPY_DELETION_STRINGS", 0)
                raw_entropy = feats.get("FILE_ENTROPY", 0.0)
                raw_anomaly = feats.get("VIRTUAL_RAW_SIZE_ANOMALY", 0)
                raw_signed  = feats.get("IS_SIGNATURE_VALID", 0)

                raw_vec = vectorize_features(feats)
                vec_np  = np.array(raw_vec)
                vec1    = vec_np[MODEL1_INDICES].reshape(1, -1)
                vec2    = vec_np[MODEL2_INDICES].reshape(1, -1)

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    with joblib.parallel_backend('threading', n_jobs=1):
                        p_rb = self.models["rf_b"].predict_proba(vec1)[0][1]
                        p_ra = self.models["rf_a"].predict_proba(vec2)[0][1]
                        p_xb = self.models["xgb_b"].predict_proba(vec1)[0][1]
                        p_xa = self.models["xgb_a"].predict_proba(vec2)[0][1]
                        p_lb = self.models["lgbm_b"].predict_proba(vec1)[0][1]
                        p_la = self.models["lgbm_a"].predict_proba(vec2)[0][1]
                        p_cb = self.models["cat_b"].predict_proba(vec1)[0][1]
                        p_ca = self.models["cat_a"].predict_proba(vec2)[0][1]

                        fusion_in  = self.build_fusion_features(
                            p_rb, p_ra, p_xb, p_xa, p_lb, p_la, p_cb, p_ca, raw_vec
                        )
                        final_prob = self.models["fusion"].predict_proba(fusion_in)[0][1]

                avg_behavior = (p_rb + p_xb + p_lb + p_cb) / 4
                avg_artifact = (p_ra + p_xa + p_la + p_ca) / 4

                if final_prob >= self.mal_thresh:
                    label = "MALWARE"
                else:
                    extreme_artifact    = (avg_artifact > 0.75) and (avg_behavior < 0.30) and raw_signed == 0
                    extreme_behavior    = (avg_behavior > 0.75) and (avg_artifact < 0.30) and raw_signed == 0
                    # consensus: ≥6 of 8 base models agree
                    consensus_suspicion = sum([
                        p_rb > 0.30, p_ra > 0.30, p_xb > 0.30, p_xa > 0.30,
                        p_lb > 0.30, p_la > 0.30, p_cb > 0.30, p_ca > 0.30
                    ]) >= 6
                    # shadow_del requires meaningful behavior signal to avoid low-signal FPs
                    shadow_override = raw_shadow == 1 and avg_behavior > 0.15

                    if shadow_override or extreme_artifact or extreme_behavior or consensus_suspicion:
                        label      = "MALWARE"
                        final_prob = max(final_prob, 0.70)
                    elif final_prob >= self.susp_thresh:
                        label = "SUSPICIOUS"
                    else:
                        label = "CLEAN"

                # signed file FP suppression
                if label == "MALWARE" and raw_signed == 1 and final_prob < 0.98:
                    label = "SUSPICIOUS"

                return label, final_prob

            except PermissionError:
                time.sleep(0.2)
            except Exception as e:
                return "ERROR", str(e)

        return "ERROR", "File locked by another process after 3 retries."
