"""
RepoLiner GUI Server
A Flask-based local web server that provides a visual interface
for configuring and running the RepoLiner merge tool.
"""

import os
import sys
import webbrowser
import threading
import subprocess
from datetime import datetime

from flask import Flask, request, jsonify, send_file

# Resolve paths relative to this script so it works from any working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
GUI_HTML_PATH = os.path.join(SCRIPT_DIR, "gui.html")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# Initialize Flask to serve static files from the 'static' directory
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Import core logic
from core import RepoLiner, get_full_config, save_json_config, estimate_tokens, CONFIG_DIR


# ═══════════════════════════════════════════════════════════════════════════
#  UTILITY HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def get_current_config():
    """Reloads and returns the fresh configuration from files."""
    return get_full_config()




# ═══════════════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Serve the GUI HTML."""
    return send_file(GUI_HTML_PATH)


@app.route("/api/config/update", methods=["POST"])
def update_config():
    """Updates one of the modular configuration files."""
    data = request.get_json()
    config_type = data.get("type")  # extensions, ignore_files, ignore_dirs, settings
    config_data = data.get("data")

    if config_type not in ["extensions", "ignore_files", "ignore_dirs", "settings"]:
        return jsonify({"success": False, "error": "Invalid config type"}), 400

    filename = f"{config_type}.json"
    success = save_json_config(filename, config_data)

    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": f"Failed to save {filename}"}), 500


@app.route("/api/browse", methods=["POST"])
def browse_folder():
    """Open a native OS folder picker dialog."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Select Project Root")
        root.destroy()
        if folder:
            return jsonify({"success": True, "path": folder})
        return jsonify({"success": False, "error": "No folder selected"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/scan", methods=["POST"])
def scan_project():
    """Scan a project directory and return full tree + config info."""
    data = request.get_json()
    path = data.get("path", "").strip()

    if not path or not os.path.isdir(path):
        return jsonify({"success": False, "error": "Invalid directory path"}), 400

    try:
        liner = RepoLiner(path)
        result = liner.scan()
        result["success"] = True
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/merge", methods=["POST"])
def merge_project():
    """Execute merge with the user's custom config."""
    data = request.get_json()
    path = data.get("path", "").strip()
    mode = data.get("mode", "folder")
    
    # These are currently provided by the UI, we can use them to override the liner config
    excluded_dirs = data.get("excluded_dirs", [])
    excluded_files = data.get("excluded_files", [])
    included_extensions = data.get("included_extensions", [])
    gitignore_patterns = data.get("gitignore_patterns", [])
    manually_included = data.get("manually_included", [])
    manually_excluded = data.get("manually_excluded", [])

    if not path or not os.path.isdir(path):
        return jsonify({"success": False, "error": "Invalid directory path"}), 400

    try:
        liner = RepoLiner(path, manually_included=manually_included, manually_excluded=manually_excluded)
        # Apply overrides from UI for global configs
        liner.ignore_dirs = set(d.lower() for d in excluded_dirs)
        liner.ignore_files = set(f.lower() for f in excluded_files)
        # We need to filter lang_map to only include selected extensions
        liner.lang_map = {ext: lang for ext, lang in liner.lang_map.items() if ext in included_extensions}
        # Note: gitignore_patterns override is not yet fully implemented in core.py (it uses the file)
        # But we'll follow the user's suggestion and use the core library.
        
        result = liner.merge(mode=mode)
        
        # Adapt result for frontend if needed
        if result["success"]:
            result["total_tokens"] = estimate_tokens(result["total_chars"])
            # Format file_stats for frontend
            result["top_files"] = [
                {"path": path.replace("\\", "/"), "tokens": tokens}
                for tokens, path in sorted(result["file_stats"], key=lambda x: x[0], reverse=True)[:20]
            ]
            result["output_path"] = os.path.abspath(result["output_path"])
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/open-folder", methods=["POST"])
def open_folder():
    """Open a folder in the OS file explorer."""
    data = request.get_json()
    folder = data.get("path", "").strip()

    if not folder:
        return jsonify({"success": False, "error": "No path provided"})

    # Handle sentinel value from the frontend
    if folder == "__output__":
        config = get_current_config()
        folder = os.path.join(PROJECT_ROOT, config.get("output_folder", "output"))

    if not os.path.isdir(folder):
        # Try to create if it's the output dir
        if "__output__" in request.get_json().values():
             os.makedirs(folder, exist_ok=True)
        else:
            return jsonify({"success": False, "error": "Directory does not exist"})

    try:
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

def open_browser():
    """Open the browser after a short delay to let the server start."""
    import time
    time.sleep(1.2)
    webbrowser.open("http://localhost:5000")


if __name__ == "__main__":
    print("=" * 50)
    print("  RepoLiner GUI — Starting...")
    print("  Open your browser at: http://localhost:5000")
    print("=" * 50)

    # Auto-open browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    app.run(host="127.0.0.1", port=5000, debug=False)
