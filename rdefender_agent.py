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
LOG_FILE              = "rdefender_events.log"
QUARANTINE_ROOT       = "C:\\RDefender_Quarantine"
QUARANTINE_MALWARE    = os.path.join(QUARANTINE_ROOT, "Malware")
QUARANTINE_SUSPICIOUS = os.path.join(QUARANTINE_ROOT, "Suspicious")
TARGET_WATCH_DIR      = "C:\\"

THRESHOLD_FILE        = "thresholds_v6.json"
MALWARE_THRESHOLD     = 0.55
SUSPICIOUS_THRESHOLD  = 0.40
SUPPORTED_EXTENSIONS  = (".exe", ".sys", ".dll", ".bat")

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
    target_dir = QUARANTINE_MALWARE if label == "MALWARE" else QUARANTINE_SUSPICIOUS

    # Strip .scanning suffix to get the real original path for metadata
    original_path = filepath.replace(".scanning", "") if filepath.endswith(".scanning") else filepath

    try:
        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(QUARANTINE_ROOT, exist_ok=True)

        filename        = os.path.basename(original_path)
        timestamp       = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_filename   = f"{os.path.splitext(filename)[0]}.{timestamp}.quarantine"
        quarantine_path = os.path.join(target_dir, safe_filename)

        # Use the actual file on disk (may be .scanning or original name)
        source = filepath if os.path.exists(filepath) else original_path
        if not os.path.exists(source):
            return None

        # Force GC to release any file handles from the scan
        import gc
        gc.collect()

        max_retries = 5
        for attempt in range(max_retries):
            try:
                shutil.move(source, quarantine_path)
                print(f"\033[91m[QUARANTINED] {filename} -> {label} vault\033[0m")
                metadata = load_quarantine_metadata()
                metadata[safe_filename] = {
                    "original_path": original_path,
                    "timestamp": timestamp,
                    "severity": label
                }
                save_quarantine_metadata(metadata)
                return quarantine_path
            except PermissionError:
                time.sleep(0.3 * (attempt + 1))

        print(f"\033[93m[WARNING] Could not quarantine {filename} after {max_retries} attempts.\033[0m")
        return None

    except Exception as e:
        print(f"\033[95m[ERROR] QUARANTINE ERROR: {str(e)}\033[0m")
        return None

# ==========================================
# MACHINE LEARNING ENGINE  — v6 (4-model fusion)
# ==========================================
class MLScannerEngine:
    """Loads the 5 v6 models (RF+XGB behavior/artifact + fusion) and runs
    the 25-feature meta array identical to evaluate_ensemble_v6.py."""

    def __init__(self):
        print("[LOADING] Loading R-Defender ML Engine v6 (4-model fusion) into RAM...")

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        self.models = {
            "rf_b":   joblib.load(os.path.join(base_path, "rf_behavior_model_v6.joblib")),
            "rf_a":   joblib.load(os.path.join(base_path, "rf_artifact_model_v6.joblib")),
            "xgb_b":  joblib.load(os.path.join(base_path, "xgb_behavior_model_v6.joblib")),
            "xgb_a":  joblib.load(os.path.join(base_path, "xgb_artifact_model_v6.joblib")),
            "fusion": joblib.load(os.path.join(base_path, "fusion_model_v6.joblib")),
        }

        self.mal_thresh, self.susp_thresh = _load_thresholds(base_path)
        print(f"[SUCCESS] Models loaded. Thresholds: MALWARE≥{self.mal_thresh}  SUSPICIOUS≥{self.susp_thresh}")

    # ------------------------------------------------------------------
    # 25-feature fusion array — must exactly match evaluate_ensemble_v6.py
    #
    #  1-4  : p_rf_b, p_rf_a, p_xgb_b, p_xgb_a
    #  5-6  : avg_behavior, avg_artifact
    #  7-8  : disagreement, prob_entropy
    #  9-10 : high_artifact_stealth, high_behavior_stealth
    #  11   : joint_conf
    #  12-13: (p_rf_a - p_rf_b), (p_xgb_a - p_xgb_b)
    #  14-15: max_sig, min_sig
    #  16-19: silver bullets (IS_SIGNATURE_VALID, SHADOW_COPY_DELETION_STRINGS,
    #                         VIRTUAL_RAW_SIZE_ANOMALY, FILE_ENTROPY)
    #  20   : extreme_artifact_loose
    #  21   : extreme_behavior_loose
    #  22   : consensus_soft
    #  23   : behavior_dominance
    #  24   : signed x avg_prob
    #  25   : entropy x avg_prob
    # ------------------------------------------------------------------
    def _build_fusion_features(self, p_rf_b, p_rf_a, p_xgb_b, p_xgb_a, raw_vec):
        probs = np.array([p_rf_b, p_rf_a, p_xgb_b, p_xgb_a])

        avg_behavior = (p_rf_b + p_xgb_b) / 2
        avg_artifact = (p_rf_a + p_xgb_a) / 2
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

        return np.array([[
            p_rf_b, p_rf_a, p_xgb_b, p_xgb_a,
            avg_behavior, avg_artifact,
            disagreement, prob_entropy,
            high_artifact_stealth, high_behavior_stealth,
            joint_conf,
            (p_rf_a - p_rf_b), (p_xgb_a - p_xgb_b),
            float(probs.max()), float(probs.min()),
            raw_silver[0], raw_silver[1], raw_silver[2], raw_silver[3],
            extreme_artifact_loose, extreme_behavior_loose,
            consensus_soft, behavior_dominance,
            signed_x_prob, entropy_x_prob,
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
                        p_rf_b  = self.models["rf_b"].predict_proba(vec1)[0][1]
                        p_rf_a  = self.models["rf_a"].predict_proba(vec2)[0][1]
                        p_xgb_b = self.models["xgb_b"].predict_proba(vec1)[0][1]
                        p_xgb_a = self.models["xgb_a"].predict_proba(vec2)[0][1]

                        fusion_in  = self._build_fusion_features(
                            p_rf_b, p_rf_a, p_xgb_b, p_xgb_a, raw_vec
                        )
                        final_prob = self.models["fusion"].predict_proba(fusion_in)[0][1]

                avg_behavior = (p_rf_b + p_xgb_b) / 2
                avg_artifact = (p_rf_a + p_xgb_a) / 2

                if final_prob >= self.mal_thresh:
                    label = "MALWARE"
                else:
                    extreme_artifact    = (p_xgb_a > 0.75) and (avg_behavior < 0.30) and raw_signed == 0
                    extreme_behavior    = (avg_behavior > 0.75) and (avg_artifact < 0.30) and raw_signed == 0
                    consensus_suspicion = (p_rf_b > 0.30 and p_rf_a > 0.30
                                          and p_xgb_b > 0.30 and p_xgb_a > 0.30)
                    shadow_override     = raw_shadow == 1 and avg_behavior > 0.15

                    if shadow_override or extreme_artifact or extreme_behavior or consensus_suspicion:
                        label      = "MALWARE"
                        final_prob = max(final_prob, 0.70)
                    elif final_prob >= self.susp_thresh:
                        label = "SUSPICIOUS"
                    else:
                        label = "CLEAN"

                if label == "MALWARE" and raw_signed == 1 and final_prob < 0.98:
                    label = "SUSPICIOUS"

                return label, final_prob

            except PermissionError:
                time.sleep(0.2)
            except ValueError:
                return "SKIP", 0.0
            except Exception as e:
                print(f"[SCAN ERROR] {os.path.basename(filepath)}: {type(e).__name__}: {e}")
                return "ERROR", str(e)

        return "ERROR", "File locked by another process after 3 retries."
