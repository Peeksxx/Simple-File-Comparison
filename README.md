# Simple File Comparison Tools

This repo contains four small Python scripts to compare two directories either locally or between a local machine and a remote server (via SFTP).

# Requirements
- Python 3.7+ (these scripts use standard library modules available in Python 3).
- For remote scripts (`compareremote.py`, `compareremote_simple.py`): install `paramiko`.

Install dependencies (PowerShell)
```powershell
python -m pip install --upgrade pip
pip install paramiko
```

# Which one do I pick?
- `compare.py` - Deep local comparison. 
    - Compares directory trees and performs byte-for-byte file comparisons (SHA-level via Python's filecmp module) for common files. 
    - Use this when you need a definitive content check.
- `compare_simple.py` - Shallow local comparison. 
    - Compares directory trees and uses metadata (names, sizes, timestamps) for a fast, heuristic check. 
    - Use this when you want speed over absolute certainty. Especially useful on HDD-based devices.
- `compareremote.py` - Deep remote comparison (SFTP).
    - Connects to a remote host over SSH/SFTP and performs SHA256-based comparisons between local files and remote files. 
    - Requires `paramiko`.
- `compareremote_simple.py` - Shallow remote comparison (SFTP).
    - Compares local files to remote files using metadata (size and modification time) via SFTP. 
    - Use this when you want speed over absolute certainty. Especially useful on HDD-based devices.
    - Also requires `paramiko`.

# Behavior
- **Local deep:** `compare.py` uses `filecmp.cmp(..., shallow=False)` to compare file contents.
- **Local shallow:** `compare_simple.py` uses `filecmp.cmp(..., shallow=True)` and checks names/sizes/timestamps.
- **Remote deep:** `compareremote.py` streams files and computes SHA256 hashes; reports exact content mismatches.
- **Remote shallow:** `compareremote_simple.py` compares size and mtime with a small tolerance (2 seconds) to accommodate common timestamp granularity differences.

# How to run

## Local Comparison

Local deep comparison
```powershell
python "c:\Users\xxx\Downloads\compare.py"
```
Local shallow comparison
```powershell
python "c:\Users\xxx\Downloads\compare_simple.py"
```

You will be prompted for two folder paths. Example input:
```
Enter path to first folder: "C:\path\to\folderA"
Enter path to second folder: "C:\path\to\folderB"
```

## Remote Comparison

Remote deep comparison
```powershell
python "c:\Users\xxx\Downloads\compareremote.py"
```

Remote shallow comparison
```powershell
python "c:\Users\xxx\Downloads\compareremote_simple.py"
```

You will be prompted for:
- Remote server IP or hostname (the scripts assume SSH/SFTP access)
- SSH username
- SSH password (leave blank to use your SSH key if configured)
- Local folder path
- Remote folder path

# Notes and tips
- You can wrap paths in double quotes when entering them. The scripts strip extra quotes automatically.
- Ensure the SSH user has read access to the remote directories and files.
- Deep comparisons stream and hash files so they are IO-bound and can be slow over high-latency links. Use the "simple" variants for faster checks when exact byte equality isn't required.
- The metadata-based checks allow a small tolerance for modification time differences (2 seconds) to avoid false positives on filesystems with different timestamp resolution.
- Remote scripts will report missing directories or files explicitly and continue scanning the rest of the tree.

# Troubleshooting
- **paramiko ImportError:** install `paramiko` with pip.
- **SSH connection failures:** verify host/reachability, username, and authentication method (password vs key). If using keys, make sure your SSH agent or key files are available to the Python process.
- **Unicode/encoding:** These scripts assume binary-safe comparison for deep checks. File names with unusual characters might behave differently depending on platform encoding; ensure consistent locale settings.

---
Problems? Questions? Text me at @peeksxx on Telegram or Discord!