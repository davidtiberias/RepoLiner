# scripts/gui_server.py
import os
import sys
import webbrowser
import threading
import subprocess

from flask import Flask, request, jsonify, send_file
from core import RepoLiner, save_json_config, estimate_tokens, PROJECT_ROOT

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GUI_HTML_PATH = os.path.join(SCRIPT_DIR, "gui.html")

app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route("/")
def index():
    return send_file(GUI_HTML_PATH)

@app.route("/api/config/update", methods=["POST"])
def update_config():
    data = request.get_json()
    config_type = data.get("type")
    new_data = data.get("data")
    
    if config_type not in ["extensions", "ignore_files", "ignore_dirs", "ignore_exts", "settings"]:
        return jsonify({"success": False, "error": "Invalid config type"}), 400

    from core import load_json_config
    filename = f"{config_type}.json"
    
    # Load current global config
    current_config = load_json_config(filename, {} if config_type == "extensions" else [])
    
    # Merge logic
    if config_type == "extensions":
        # Dictionary merge (Append/Update)
        current_config.update(new_data)
    else:
        # List merge (Append unique items)
        if isinstance(new_data, list):
            for item in new_data:
                if item not in current_config:
                    current_config.append(item)
        else:
            # Fallback for settings or single items
            current_config = new_data

    if save_json_config(filename, current_config):
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Failed to save"}), 500

@app.route("/api/browse", methods=["POST"])
def browse_folder():
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
    path = request.get_json().get("path", "").strip()
    if not path or not os.path.isdir(path):
        return jsonify({"success": False, "error": "Invalid directory path"}), 400

    try:
        liner = RepoLiner(path)
        result = liner.scan_for_gui()
        result["success"] = True
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/expand", methods=["POST"])
def expand_folder():
    """Endpoint for lazy-loading ignored directories in the GUI."""
    data = request.get_json()
    path = data.get("path", "").strip()
    sub_path = data.get("sub_path", "").strip()
    
    try:
        liner = RepoLiner(path)
        children = liner.scan_for_gui(sub_path=sub_path)
        return jsonify({"success": True, "children": children})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/merge", methods=["POST"])
def merge_project():
    data = request.get_json()
    path = data.get("path", "").strip()
    if not path or not os.path.isdir(path):
        return jsonify({"success": False, "error": "Invalid directory path"}), 400

    try:
        liner = RepoLiner(
            path, 
            manually_included=data.get("manually_included", []), 
            manually_excluded=data.get("manually_excluded", [])
        )
        
        # Apply UI overrides to the base configuration
        liner.ignore_dirs = set(d.lower() for d in data.get("excluded_dirs", []))
        liner.ignore_files = set(f.lower() for f in data.get("excluded_files", []))
        liner.gitignore_patterns = data.get("gitignore_patterns", [])
        liner.repoignore_patterns = data.get("repoignore_patterns", [])
        included_exts = data.get("included_extensions", [])
        liner.lang_map = {k: v for k, v in liner.lang_map.items() if k in included_exts}
        
        result = liner.merge(mode=data.get("mode", "folder"))
        
        if result["success"]:
            result["total_tokens"] = estimate_tokens(result["total_chars"])
            result["top_files"] = [{"path": p.replace("\\", "/"), "tokens": t} for t, p in sorted(result["file_stats"], key=lambda x: x[0], reverse=True)[:20]]
            result["output_path"] = os.path.abspath(result["output_path"])
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/open-folder", methods=["POST"])
def open_folder():
    folder = request.get_json().get("path", "").strip()
    if folder == "__output__":
        liner = RepoLiner(os.getcwd()) # Dummy path to load config
        folder = os.path.join(PROJECT_ROOT, liner.config.get("output_folder", "output"))

    if not os.path.isdir(folder):
        if "__output__" in request.get_json().values():
             os.makedirs(folder, exist_ok=True)
        else:
            return jsonify({"success": False, "error": "Directory does not exist"})

    try:
        if sys.platform == "win32": os.startfile(folder)
        elif sys.platform == "darwin": subprocess.Popen(["open", folder])
        else: subprocess.Popen(["xdg-open", folder])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def open_browser():
    import time
    time.sleep(1.2)
    webbrowser.open("http://localhost:5000")

if __name__ == "__main__":
    print("=" * 50)
    print("  RepoLiner GUI — Starting...")
    print("  Open your browser at: http://localhost:5000")
    print("=" * 50)
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
