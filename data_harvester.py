# data_harvester.py - Automated AST Data Pipeline Ingestor
import os
import sys
import urllib.request
import time
import csv
import zipfile
import io
from analyzer import StaticDiagnosticEngine

# Reconfigure stdout to support UTF-8 characters on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Setup local storage directory
DATASET_DIR = "project_dataset"
RAW_FILES_DIR = os.path.join(DATASET_DIR, "raw_files")
FEATURES_CSV = os.path.join(DATASET_DIR, "code_features.csv")

# URLs of popular GitHub repository ZIP archives to harvest datasets
REPO_ZIP_URLS = {
    "requests.zip": "https://github.com/psf/requests/archive/refs/heads/main.zip",
    "flask.zip": "https://github.com/pallets/flask/archive/refs/heads/main.zip",
    "benchmark.zip": "https://github.com/google/benchmark/archive/refs/heads/main.zip"
}

def download_and_extract_zips():
    """Downloads ZIP archives of open-source projects and extracts them recursively."""
    os.makedirs(RAW_FILES_DIR, exist_ok=True)
    
    for filename, url in REPO_ZIP_URLS.items():
        folder_prefix = filename.split(".")[0] + "-main"
        dest_folder = os.path.join(RAW_FILES_DIR, folder_prefix)
        
        if os.path.exists(dest_folder):
            print(f"Directory {folder_prefix} already exists. Skipping download.")
            continue
            
        for attempt in range(1, 4):
            try:
                print(f"Downloading {filename} from {url} (Attempt {attempt}/3)...")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=30) as response:
                    zip_data = response.read()
                
                print(f"Extracting {filename} to {RAW_FILES_DIR}...")
                with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
                    zip_ref.extractall(RAW_FILES_DIR)
                print(f"Successfully extracted {filename}.")
                break
            except Exception as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt < 3:
                    time.sleep(2 ** attempt)  # Exponential backoff

    # Copy our local high-vulnerability demo files into raw_files to balance the dataset
    demo_dir = "demo_code"
    if os.path.exists(demo_dir):
        for file in os.listdir(demo_dir):
            src_path = os.path.join(demo_dir, file)
            dest_path = os.path.join(RAW_FILES_DIR, f"demo_{file}")
            if os.path.isfile(src_path):
                with open(src_path, "r", encoding="utf-8", errors="ignore") as src_f:
                    content = src_f.read()
                with open(dest_path, "w", encoding="utf-8") as dest_f:
                    dest_f.write(content)
                print(f"Copied local demo file {file} to dataset corpus.")

def extract_ast_features():
    """Runs StaticDiagnosticEngine to parse AST structures and write code_features.csv."""
    print("\nRunning Static AST Feature Extraction Pipeline...")
    engine = StaticDiagnosticEngine(RAW_FILES_DIR)
    
    # Run directory scan recursively
    findings = engine.scan_repository()
    
    # Track findings per file using absolute path keys
    file_findings = {}
    for f in findings:
        file_path = f["file"]
        file_findings.setdefault(os.path.abspath(file_path), []).append(f)
        
    # Headers for structured dataset output
    headers = [
        "file_path", "loc", "nested_loops", "silent_exceptions", 
        "mutable_defaults", "global_vars", "raw_new_count", 
        "unsafe_copies", "is_vulnerable"
    ]
    
    dataset_rows = []
    
    # Traverse RAW_FILES_DIR recursively to find all Python and C++ source code files
    for root, _, files in os.walk(RAW_FILES_DIR):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in [".py", ".cc", ".cpp", ".cxx", ".c", ".h", ".hpp"]:
                continue
                
            file_path = os.path.join(root, file)
            # Skip hidden files or __pycache__ or venv
            if any(part.startswith('.') or part == '__pycache__' for part in file_path.split(os.sep)):
                continue
                
            # Compute LOC (lines of code)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.read().splitlines()
                    loc = len(lines)
            except Exception:
                print(f"Skipping unreadable file: {file_path}")
                continue
                
            # Get findings for this file
            abs_path = os.path.abspath(file_path)
            anomalies = file_findings.get(abs_path, [])
            
            # Extract features from findings
            nested_loops = sum(1 for a in anomalies if a["issue"] == "O(N^2) Nested Loop")
            silent_exceptions = sum(1 for a in anomalies if a["issue"] == "Silent Exception Handling")
            mutable_defaults = sum(1 for a in anomalies if a["issue"] == "Mutable Default Argument")
            global_vars = sum(1 for a in anomalies if a["issue"] == "Global Variable Modification")
            raw_new_count = sum(1 for a in anomalies if a["issue"] == "Memory Leak Risk (Raw New)")
            unsafe_copies = sum(1 for a in anomalies if a["issue"] == "Unsafe Buffer Copy")
            
            is_vulnerable = 1 if len(anomalies) > 0 else 0
            
            rel_path = os.path.relpath(file_path, RAW_FILES_DIR)
            
            dataset_rows.append({
                "file_path": rel_path,
                "loc": loc,
                "nested_loops": nested_loops,
                "silent_exceptions": silent_exceptions,
                "mutable_defaults": mutable_defaults,
                "global_vars": global_vars,
                "raw_new_count": raw_new_count,
                "unsafe_copies": unsafe_copies,
                "is_vulnerable": is_vulnerable
            })
            
    # Save cleanly as CSV
    with open(FEATURES_CSV, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(dataset_rows)
        
    print(f"\nFeature extraction complete. Structured dataset saved at: {FEATURES_CSV}")
    print(f"Ingested {len(dataset_rows)} data rows.")

if __name__ == "__main__":
    download_and_extract_zips()
    extract_ast_features()
