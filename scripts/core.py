# scripts/core.py
import os
import json
import fnmatch
from datetime import datetime
from config_defaults import DEFAULT_CONFIG

# This file contains the core logic, shared by both the CLI and GUI.
# It has no print statements and returns data structures.

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_DIR = os.path.join(PROJECT_ROOT, "configs")


def load_json_config(filename, default_value):
    """Loads a JSON config file or creates it with defaults if missing."""
    file_path = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass  # Fail silently in core logic

    # Create default file if missing or corrupted
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_value, f, indent=4)
    except Exception:
        pass

    return default_value


def save_json_config(filename, data):
    """Saves a dictionary or list to a JSON config file."""
    file_path = os.path.join(CONFIG_DIR, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False


def get_full_config():
    """Builds the full CONFIG dictionary from modular files."""
    return {
        "output_folder": load_json_config("settings.json", DEFAULT_CONFIG["settings"]).get(
            "output_folder", "output"
        ),
        "ignore_files": load_json_config(
            "ignore_files.json", DEFAULT_CONFIG["ignore_files"]
        ),
        "ignore_dirs": load_json_config(
            "ignore_dirs.json", DEFAULT_CONFIG["ignore_dirs"]
        ),
        "lang_map": load_json_config("extensions.json", DEFAULT_CONFIG["extensions"]),
    }


def estimate_tokens(text_content):
    """Rough estimation: 1 Token ~= 4 Characters."""
    return len(text_content) // 4


class RepoLiner:
    def __init__(self, target_dir, manually_included=None, manually_excluded=None):
        if not os.path.isdir(target_dir):
            raise ValueError(f"Target directory does not exist: {target_dir}")
        self.target_dir = os.path.abspath(target_dir)
        self.config = get_full_config()
        self.ignore_files = set(f.lower() for f in self.config["ignore_files"])
        self.ignore_dirs = set(d.lower() for d in self.config["ignore_dirs"])
        self.lang_map = self.config["lang_map"]
        self.gitignore_patterns = self._load_gitignore()
        self.manually_included = set(p.replace("\\", "/") for p in (manually_included or []))
        self.manually_excluded = set(p.replace("\\", "/") for p in (manually_excluded or []))

    def _load_gitignore(self):
        patterns = []
        gitignore_path = os.path.join(self.target_dir, ".gitignore")
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.append(line)
            except Exception:
                pass  # Fail silently
        return patterns

    def _is_path_ignored(self, rel_path, is_dir=False):
        """
        Determines if a path should be ignored based on the hierarchy:
        1. Manual Exclude (Highest)
        2. Manual Include
        3. .gitignore
        4. Global Config
        """
        rel_path = rel_path.replace("\\", "/")
        name = os.path.basename(rel_path)
        
        # 1. Manual Overrides
        if rel_path in self.manually_excluded:
            return True
        if rel_path in self.manually_included:
            return False
            
        # 2. .gitignore (Local Rules)
        for pattern in self.gitignore_patterns:
            if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel_path, pattern):
                return True
                
        # 3. Global Config
        if is_dir:
            if name.lower() in self.ignore_dirs:
                return True
        else:
            if name.lower() in self.ignore_files:
                return True
                
        return False

    def _safe_walker(self):
        for root, dirs, files in os.walk(self.target_dir, topdown=True):
            rel_root = os.path.relpath(root, self.target_dir)
            if rel_root == ".":
                rel_root = ""

            # Filter directories
            new_dirs = []
            for d in dirs:
                rel_path = os.path.join(rel_root, d).replace("\\", "/")
                if not self._is_path_ignored(rel_path, is_dir=True):
                    new_dirs.append(d)
                elif rel_path in self.manually_included:
                    # Even if ignored by config/.gitignore, if manually included, traverse it
                    new_dirs.append(d)
            
            dirs[:] = new_dirs
            yield root, dirs, files

    def generate_tree_text(self):
        """Generates the directory tree as a string."""
        tree_lines = ["Directory Tree:", "```text"]
        allowed_extensions = set(self.lang_map.keys())

        for root, dirs, files in self._safe_walker():
            rel_root = os.path.relpath(root, self.target_dir)
            if rel_root == ".":
                rel_root = ""
            
            level = rel_root.count(os.sep) if rel_root else 0
            indent = "    " * level
            tree_lines.append(f"{indent}{os.path.basename(root)}/")

            subindent = "    " * (level + 1)
            for f in files:
                rel_path = os.path.join(rel_root, f).replace("\\", "/")
                
                # Check overrides and filters
                if rel_path in self.manually_excluded:
                    continue
                if rel_path not in self.manually_included:
                    if f.lower() in self.ignore_files:
                        continue
                    if self._is_path_ignored(rel_path, is_dir=False):
                        continue
                    file_extension = os.path.splitext(f)[1].lower()
                    if file_extension not in allowed_extensions:
                        continue
                
                tree_lines.append(f"{subindent}{f}")

        tree_lines.append("```")
        return "\n".join(tree_lines)

    def merge(self, mode="folder"):
        """Performs the merge and returns a status dictionary."""
        result = {
            "success": False,
            "output_path": None,
            "files_merged": 0,
            "total_chars": 0,
            "file_stats": [],
            "error": None,
        }

        try:
            # --- OUTPUT SETUP ---
            if mode == "dump":
                output_filepath = os.path.join(self.target_dir, "repoliner_dump.md")
            else:
                output_dir = os.path.join(PROJECT_ROOT, self.config["output_folder"])
                os.makedirs(output_dir, exist_ok=True)
                project_name = os.path.basename(os.path.normpath(self.target_dir))
                timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                output_filename = f"{project_name} {timestamp}.md"
                output_filepath = os.path.join(output_dir, output_filename)

            result["output_path"] = output_filepath

            with open(output_filepath, "w", encoding="utf-8") as outfile:
                project_name = os.path.basename(os.path.normpath(self.target_dir))
                outfile.write(f"# RepoLiner: Merged Code for '{project_name}'\n")
                timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                outfile.write(f"Scanned on: {timestamp}\n\n")

                tree_content = self.generate_tree_text()
                outfile.write(tree_content)
                outfile.write("\n\n" + ("=" * 50) + "\n\n")

                total_chars = len(tree_content)
                found_files_count = 0
                file_stats = []
                allowed_extensions = set(self.lang_map.keys())

                for root, dirs, files in self._safe_walker():
                    rel_root = os.path.relpath(root, self.target_dir)
                    if rel_root == ".":
                        rel_root = ""

                    for filename in files:
                        file_path = os.path.join(root, filename)
                        relative_path = os.path.relpath(file_path, self.target_dir).replace("\\", "/")
                        file_extension = os.path.splitext(filename)[1].lower()

                        if os.path.abspath(file_path) == os.path.abspath(output_filepath):
                            continue

                        # Check overrides and filters
                        should_include = False
                        if relative_path in self.manually_included:
                            should_include = True
                        elif relative_path in self.manually_excluded:
                            should_include = False
                        else:
                            if filename.lower() in self.ignore_files:
                                should_include = False
                            elif self._is_path_ignored(relative_path, is_dir=False):
                                should_include = False
                            elif file_extension in allowed_extensions:
                                should_include = True

                        if should_include:
                            try:
                                with open(
                                    file_path, "r", encoding="utf-8", errors="ignore"
                                ) as infile:
                                    content = infile.read()

                                found_files_count += 1
                                lang_identifier = self.lang_map.get(
                                    file_extension, "text"
                                )

                                markdown_chunk = (
                                    f'\n<file path="{relative_path}">\n'
                                    f"\n~~~~{lang_identifier}\n"
                                    f"\n{content.strip()}\n"
                                    "\n~~~~\n"
                                    "</file>\n\n"
                                )
                                outfile.write(markdown_chunk)

                                chunk_len = len(markdown_chunk)
                                total_chars += chunk_len
                                file_tokens = estimate_tokens(markdown_chunk)
                                file_stats.append((file_tokens, relative_path))

                            except Exception as e:
                                # We could log this or add it to an errors list in result
                                pass

                result["success"] = True
                result["files_merged"] = found_files_count
                result["total_chars"] = total_chars
                result["file_stats"] = file_stats

        except Exception as e:
            result["success"] = False
            result["error"] = str(e)

        return result
