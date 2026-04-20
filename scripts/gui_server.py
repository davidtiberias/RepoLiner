"""
RepoLiner GUI Server
A Flask-based local web server that provides a visual interface
for configuring and running the RepoLiner merge tool.
"""

import os
import sys
import json
import fnmatch
import webbrowser
import threading
import subprocess
from datetime import datetime

from flask import Flask, request, jsonify, send_file

# ---------------------------------------------------------------------------
# Resolve paths relative to this script so it works from any working directory
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
GUI_HTML_PATH = os.path.join(SCRIPT_DIR, "gui.html")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

app = Flask(__name__)

# ── Import CONFIG from the existing merge_script ──────────────────────────
sys.path.insert(0, SCRIPT_DIR)
import merge_script  # noqa: E402


# ═══════════════════════════════════════════════════════════════════════════
#  UTILITY HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def get_current_config():
    """Reloads and returns the fresh configuration from files."""
    return merge_script.get_full_config()

def load_gitignore(target_dir):
    """Read .gitignore patterns from a directory."""
    patterns = []
    gitignore_path = os.path.join(target_dir, ".gitignore")
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except Exception:
            pass
    return patterns


def should_ignore(name, patterns):
    """Check if a name matches any fnmatch pattern."""
    for pattern in patterns:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def estimate_tokens(char_count):
    """Rough token estimation: 1 token ≈ 4 chars."""
    return char_count // 4


def scan_directory_tree(target_dir):
    """
    Walk the target directory and return:
      - Full tree (unfiltered, for the UI)
      - All discovered file extensions
      - Gitignore patterns
    """
    gitignore_patterns = load_gitignore(target_dir)
    config = get_current_config()
    lang_map = config["lang_map"]
    ignore_dirs_set = set(d.lower() for d in config["ignore_dirs"])
    ignore_files_set = set(f.lower() for f in config["ignore_files"])
    all_extensions = set()
    all_dirs = set()

    def walk_node(dir_path, rel_prefix=""):
        children = []
        try:
            entries = sorted(os.listdir(dir_path), key=lambda x: (not os.path.isdir(os.path.join(dir_path, x)), x.lower()))
        except PermissionError:
            return children

        for entry in entries:
            full_path = os.path.join(dir_path, entry)
            rel_path = os.path.join(rel_prefix, entry) if rel_prefix else entry

            if os.path.isdir(full_path):
                # Determine exclusion reason
                excluded = False
                reason = None
                entry_lower = entry.lower()

                if entry_lower in ignore_dirs_set:
                    excluded = True
                    reason = "repoliner_config"
                elif should_ignore(entry, gitignore_patterns):
                    excluded = True
                    reason = "gitignore"

                all_dirs.add(entry_lower)

                node = {
                    "name": entry,
                    "path": rel_path.replace("\\", "/"),
                    "type": "dir",
                    "excluded": excluded,
                    "reason": reason,
                    "children": [] if excluded else walk_node(full_path, rel_path),
                }
                children.append(node)
            else:
                # File
                ext = os.path.splitext(entry)[1].lower()
                if ext:
                    all_extensions.add(ext)

                excluded = False
                reason = None
                entry_lower = entry.lower()

                if entry_lower in ignore_files_set:
                    excluded = True
                    reason = "repoliner_config"
                elif should_ignore(entry, gitignore_patterns):
                    excluded = True
                    reason = "gitignore"
                elif ext and ext not in lang_map:
                    excluded = True
                    reason = "extension_not_supported"

                node = {
                    "name": entry,
                    "path": rel_path.replace("\\", "/"),
                    "type": "file",
                    "ext": ext,
                    "excluded": excluded,
                    "reason": reason,
                }
                children.append(node)

        return children

    tree = walk_node(target_dir)

    # Categorize extensions
    supported_exts = set(lang_map.keys())
    all_ext_list = sorted(all_extensions)

    included_extensions = [e for e in all_ext_list if e in supported_exts]
    excluded_extensions = [e for e in all_ext_list if e not in supported_exts]

    # Categorize directories
    all_dirs_list = sorted(all_dirs)
    included_dirs = [d for d in all_dirs_list if d not in ignore_dirs_set]
    excluded_dirs = [d for d in all_dirs_list if d in ignore_dirs_set]

    return {
        "project_name": os.path.basename(os.path.normpath(target_dir)),
        "tree": tree,
        "gitignore_patterns": gitignore_patterns,
        "all_extensions": all_ext_list,
        "included_extensions": included_extensions,
        "excluded_extensions": excluded_extensions,
        "lang_map": lang_map,
        "included_dirs": included_dirs,
        "excluded_dirs": excluded_dirs,
        "ignore_files": list(config["ignore_files"]),
    }


def run_merge(target_dir, mode, excluded_dirs, excluded_files, included_extensions, gitignore_patterns):
    """
    Run the merge logic with the user's custom configuration.
    Returns a result summary dict.
    """
    ignore_dirs_set = set(d.lower() for d in excluded_dirs)
    ignore_files_set = set(f.lower() for f in excluded_files)
    included_ext_set = set(e.lower() for e in included_extensions)

    # Determine output path
    if mode == "dump":
        output_filepath = os.path.join(target_dir, "repoliner_dump.md")
    else:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        project_name = os.path.basename(os.path.normpath(target_dir))
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        output_filename = f"{project_name} {timestamp}.md"
        output_filepath = os.path.join(OUTPUT_DIR, output_filename)

    project_name = os.path.basename(os.path.normpath(target_dir))
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    found_files = 0
    total_chars = 0
    file_stats = []

    def safe_walk(dir_path):
        for root, dirs, files in os.walk(dir_path, topdown=True):
            dirs[:] = [
                d for d in dirs
                if d.lower() not in ignore_dirs_set
                and not should_ignore(d, gitignore_patterns)
            ]
            yield root, dirs, files

    # Generate tree text
    tree_lines = ["Directory Tree:", "```text"]
    for root, dirs, files in safe_walk(target_dir):
        level = root.replace(target_dir, "").count(os.sep)
        indent = "    " * level
        tree_lines.append(f"{indent}{os.path.basename(root)}/")
        subindent = "    " * (level + 1)
        for f in files:
            if f.lower() in ignore_files_set:
                continue
            if should_ignore(f, gitignore_patterns):
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext not in included_ext_set:
                continue
            tree_lines.append(f"{subindent}{f}")
    tree_lines.append("```")
    tree_content = "\n".join(tree_lines)

    try:
        with open(output_filepath, "w", encoding="utf-8") as outfile:
            outfile.write(f"# RepoLiner: Merged Code for '{project_name}'\n")
            outfile.write(f"Scanned on: {timestamp}\n\n")
            outfile.write(tree_content)
            outfile.write("\n\n" + ("=" * 50) + "\n\n")
            total_chars += len(tree_content)

            for root, dirs, files in safe_walk(target_dir):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, target_dir)
                    file_extension = os.path.splitext(filename)[1].lower()

                    if filename.lower() in ignore_files_set:
                        continue
                    if should_ignore(filename, gitignore_patterns):
                        continue
                    if os.path.abspath(file_path) == os.path.abspath(output_filepath):
                        continue
                    if file_extension not in included_ext_set:
                        continue

                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                            content = infile.read()

                        # Get fresh lang_map for merge identifiers
                        config = get_current_config()
                        lang_id = config["lang_map"].get(file_extension, "text")
                        markdown_chunk = (
                            f'\n<file path="{relative_path}">\n'
                            f"\n~~~~{lang_id}\n"
                            f"\n{content.strip()}\n"
                            "\n~~~~\n"
                            "</file>\n\n"
                        )
                        outfile.write(markdown_chunk)

                        chunk_len = len(markdown_chunk)
                        total_chars += chunk_len
                        found_files += 1
                        file_stats.append({
                            "path": relative_path.replace("\\", "/"),
                            "tokens": estimate_tokens(chunk_len),
                        })
                    except Exception:
                        pass

    except IOError as e:
        return {"success": False, "error": str(e)}

    total_tokens = estimate_tokens(total_chars)
    file_stats.sort(key=lambda x: x["tokens"], reverse=True)

    return {
        "success": True,
        "output_path": os.path.abspath(output_filepath),
        "files_merged": found_files,
        "total_tokens": total_tokens,
        "top_files": file_stats[:20],
        "mode": mode,
    }


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
    success = merge_script.save_json_config(filename, config_data)

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
        result = scan_directory_tree(path)
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
    excluded_dirs = data.get("excluded_dirs", [])
    excluded_files = data.get("excluded_files", [])
    included_extensions = data.get("included_extensions", [])
    gitignore_patterns = data.get("gitignore_patterns", [])

    if not path or not os.path.isdir(path):
        return jsonify({"success": False, "error": "Invalid directory path"}), 400

    result = run_merge(path, mode, excluded_dirs, excluded_files, included_extensions, gitignore_patterns)
    return jsonify(result)


@app.route("/api/open-folder", methods=["POST"])
def open_folder():
    """Open a folder in the OS file explorer."""
    data = request.get_json()
    folder = data.get("path", "").strip()

    if not folder:
        return jsonify({"success": False, "error": "No path provided"})

    # Handle sentinel value from the frontend
    if folder == "__output__":
        folder = OUTPUT_DIR

    if not os.path.isdir(folder):
        # Try to create if it's the output dir
        if folder == OUTPUT_DIR:
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
