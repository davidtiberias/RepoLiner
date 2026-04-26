# scripts/core.py
import os
import json
import fnmatch
from datetime import datetime
from config_defaults import DEFAULT_CONFIG

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_DIR = os.path.join(PROJECT_ROOT, "configs")


def load_json_config(filename, default_value):
    file_path = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_value, f, indent=4)
    except Exception:
        pass
    return default_value


def save_json_config(filename, data):
    file_path = os.path.join(CONFIG_DIR, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False


def get_full_config():
    return {
        "output_folder": load_json_config("settings.json", DEFAULT_CONFIG["settings"]).get("output_folder", "output"),
        "ignore_files": load_json_config("ignore_files.json", DEFAULT_CONFIG["ignore_files"]),
        "ignore_dirs": load_json_config("ignore_dirs.json", DEFAULT_CONFIG["ignore_dirs"]),
        "ignore_exts": load_json_config("ignore_exts.json", DEFAULT_CONFIG["ignore_exts"]),
        "lang_map": load_json_config("extensions.json", DEFAULT_CONFIG["extensions"]),
    }


def estimate_tokens(text_or_len):
    """Rough estimation: 1 Token ~= 4 Characters. Accepts string or character count."""
    if isinstance(text_or_len, int):
        return text_or_len // 4
    return len(str(text_or_len)) // 4


class RepoLiner:
    def __init__(self, target_dir, manually_included=None, manually_excluded=None):
        if not os.path.isdir(target_dir):
            raise ValueError(f"Target directory does not exist: {target_dir}")
        self.target_dir = os.path.abspath(target_dir)
        self.config = get_full_config()
        self.ignore_files = set(f.lower() for f in self.config["ignore_files"])
        self.ignore_dirs = set(d.lower() for d in self.config["ignore_dirs"])
        self.ignore_exts = set(e.lower() for e in self.config["ignore_exts"])
        self.lang_map = self.config["lang_map"]
        
        # Load both ignore files
        self.gitignore_patterns = self._load_ignore_file(".gitignore")
        self.repoignore_patterns = self._load_ignore_file(".repoignore")
        
        self.manually_included = set(p.replace("\\", "/") for p in (manually_included or []))
        self.manually_excluded = set(p.replace("\\", "/") for p in (manually_excluded or []))

    def _get_extension(self, filename):
        """Robustly extracts extension, handling dotfiles like .gitignore or .flake8 correctly."""
        ext = os.path.splitext(filename)[1].lower()
        if not ext and filename.startswith('.'):
            return filename.lower()
        return ext

    def _load_ignore_file(self, filename):
        patterns = []
        filepath = os.path.join(self.target_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.append(line)
            except Exception:
                pass
        return patterns

    def _is_path_ignored_by_base(self, rel_path, is_dir=False):
        """Strictly checks base rules (Global Config & .gitignore). No manual overrides here."""
        rel_path = rel_path.replace("\\", "/")
        name = os.path.basename(rel_path)

        # 1. Global Configs
        if is_dir and name.lower() in self.ignore_dirs:
            return True, "global_config"
        if not is_dir and name.lower() in self.ignore_files:
            return True, "global_config"
            
        ext = self._get_extension(name) if not is_dir else None
        if ext and ext in self.ignore_exts:
            return True, "global_config"

        # Check Repoignore first, then Gitignore
        for ignore_type, patterns in [("repoignore", self.repoignore_patterns), ("gitignore", self.gitignore_patterns)]:
            for pattern in patterns:
                p = pattern[:-1] if pattern.endswith('/') else pattern
                if pattern.endswith('/') and not is_dir:
                    continue
                if fnmatch.fnmatch(name, p) or fnmatch.fnmatch(rel_path, p):
                    return True, ignore_type

        return False, None

    def get_final_paths(self):
        """Phase 1 & 2: Resolves the final flat list of file paths to process."""
        final_paths = set()
        allowed_extensions = set(self.lang_map.keys())

        # --- Phase 1: Strict Base Traversal ---
        for root, dirs, files in os.walk(self.target_dir, topdown=True):
            rel_root = os.path.relpath(root, self.target_dir).replace("\\", "/")
            if rel_root == ".": rel_root = ""

            # Filter dirs strictly. We never enter ignored dirs.
            valid_dirs = []
            for d in dirs:
                d_rel = f"{rel_root}/{d}" if rel_root else d
                is_ignored, _ = self._is_path_ignored_by_base(d_rel, is_dir=True)
                if not is_ignored:
                    valid_dirs.append(d)
            dirs[:] = valid_dirs  # Prune os.walk path

            for f in files:
                f_rel = f"{rel_root}/{f}" if rel_root else f
                
                if f_rel in self.manually_excluded:
                    continue  # Manual exclusion overrides
                    
                is_ignored, _ = self._is_path_ignored_by_base(f_rel, is_dir=False)
                if not is_ignored:
                    ext = self._get_extension(f)
                    if ext in allowed_extensions:
                        final_paths.add(f_rel)

        # --- Phase 2: Separated Logic for Manual Inclusions ---
        # Direct injection avoids walking through massive ignored folders unnecessarily
        for man_inc in self.manually_included:
            full_path = os.path.join(self.target_dir, man_inc)
            
            if os.path.isfile(full_path):
                final_paths.add(man_inc)
            
            elif os.path.isdir(full_path):
                # The user manually included a whole directory that was otherwise ignored.
                # Walk it and add its files (still respecting extensions & manual exclusions).
                for root, _, files in os.walk(full_path):
                    for f in files:
                        ext = os.path.splitext(f)[1].lower()
                        if ext in allowed_extensions:
                            f_rel = os.path.relpath(os.path.join(root, f), self.target_dir).replace("\\", "/")
                            if f_rel not in self.manually_excluded:
                                final_paths.add(f_rel)

        return sorted(list(final_paths))

    def generate_tree_text(self, final_paths):
        """Phase 3: Builds the visual tree strictly from the flat list of final paths."""
        tree_dict = {}
        for p in final_paths:
            parts = p.split("/")
            curr = tree_dict
            for part in parts[:-1]:
                if part not in curr:
                    curr[part] = {}
                curr = curr[part]
            curr[parts[-1]] = None # None signifies a file

        def recurse(node, level=0):
            lines = []
            # Sort: folders first (not None), then files (None), alphabetically
            sorted_keys = sorted(node.keys(), key=lambda k: (node[k] is None, k.lower()))
            for key in sorted_keys:
                if node[key] is None:
                    lines.append("    " * level + key)
                else:
                    lines.append("    " * level + key + "/")
                    lines.extend(recurse(node[key], level + 1))
            return lines

        lines = ["Directory Tree:", "```text"]
        if tree_dict:
            lines.extend(recurse(tree_dict))
        lines.append("```")
        return "\n".join(lines)

    def scan_for_gui(self, sub_path=None):
        """Single source of truth for generating the GUI file tree. Supports lazy loading."""
        all_extensions = set()
        
        def walk_node(dir_path, rel_prefix="", inherited_ignore=False, inherited_reason=None):
            children = []
            try:
                entries = sorted(os.listdir(dir_path), key=lambda x: (not os.path.isdir(os.path.join(dir_path, x)), x.lower()))
            except PermissionError:
                return children

            for entry in entries:
                full_path = os.path.join(dir_path, entry)
                rel_path = f"{rel_prefix}/{entry}" if rel_prefix else entry
                is_dir = os.path.isdir(full_path)
                
                is_ignored, reason = self._is_path_ignored_by_base(rel_path, is_dir=is_dir)
                
                # If a parent was ignored, all children inherit that ignored status
                if inherited_ignore and not is_ignored:
                    is_ignored = True
                    reason = inherited_reason

                ext = self._get_extension(entry) if not is_dir else None
                if ext:
                    all_extensions.add(ext)

                rules = [
                    {"name": "Manual Override", "status": "not_set"},
                    {"name": ".repoignore", "status": "matched" if reason == "repoignore" else "not_matched"},
                    {"name": ".gitignore", "status": "matched" if reason == "gitignore" else "not_matched"},
                    {"name": "Ignored Extension", "status": "matched" if (ext and ext in self.ignore_exts) else "not_matched"},
                    {"name": "Global Config", "status": "matched" if reason in ["global_config", "parent_ignored"] else "not_matched"}
                ]
                
                if not is_dir:
                    is_supported = ext in self.lang_map
                    rules.append({"name": "Extension", "status": "supported" if is_supported else "unsupported"})
                    if not is_ignored and not is_supported:
                        is_ignored = True
                        reason = "extension_not_supported"

                # Check if an ignored directory actually has contents to show the expand arrow
                has_hidden = False
                if is_dir and is_ignored:
                    try:
                        with os.scandir(full_path) as it:
                            has_hidden = any(it)
                    except: pass

                node = {
                    "name": entry,
                    "path": rel_path,
                    "type": "dir" if is_dir else "file",
                    "excluded": is_ignored,
                    "reason": reason,
                    "rules": rules,
                    "has_hidden": has_hidden,
                    # Stop traversing if ignored to save performance. GUI will lazy-load it.
                    "children": [] if (is_dir and is_ignored) else (walk_node(full_path, rel_path, is_ignored, reason) if is_dir else None)
                }
                
                if not is_dir:
                    del node["children"]
                    node["ext"] = ext
                    
                children.append(node)
            return children

        # If a sub_path is provided, we are lazy-loading an ignored directory
        if sub_path:
            full_sub_path = os.path.join(self.target_dir, sub_path)
            return walk_node(full_sub_path, sub_path, inherited_ignore=True, inherited_reason="global_config")

        # Normal full scan
        tree = walk_node(self.target_dir)
        all_ext_list = sorted(all_extensions)
        supported_exts = set(self.lang_map.keys())

        all_dirs = set()
        for root, dirs, _ in os.walk(self.target_dir):
            for d in dirs: all_dirs.add(d.lower())
        all_dirs_list = sorted(all_dirs)

        return {
            "project_name": os.path.basename(self.target_dir),
            "tree": tree,
            "gitignore_patterns": self.gitignore_patterns,
            "repoignore_patterns": self.repoignore_patterns,
            "all_extensions": all_ext_list,
            "included_extensions": [e for e in all_ext_list if e in supported_exts],
            "excluded_extensions": [e for e in all_ext_list if e not in supported_exts],
            "ignore_exts": list(self.ignore_exts),
            "included_dirs": [d for d in all_dirs_list if d not in self.ignore_dirs],
            "excluded_dirs": [d for d in all_dirs_list if d in self.ignore_dirs],
            "ignore_files": list(self.ignore_files),
            "lang_map": self.lang_map
        }

    def merge(self, mode="folder"):
        result = { "success": False, "output_path": None, "files_merged": 0, "total_chars": 0, "file_stats": [], "error": None }

        try:
            if mode == "dump":
                output_filepath = os.path.join(self.target_dir, "repoliner_dump.md")
            else:
                output_dir = os.path.join(PROJECT_ROOT, self.config["output_folder"])
                os.makedirs(output_dir, exist_ok=True)
                project_name = os.path.basename(os.path.normpath(self.target_dir))
                timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                output_filepath = os.path.join(output_dir, f"{project_name} {timestamp}.md")

            result["output_path"] = output_filepath
            final_paths = self.get_final_paths()
            tree_content = self.generate_tree_text(final_paths)
            
            # Send the tree back to the frontend
            result["tree_content"] = tree_content 

            with open(output_filepath, "w", encoding="utf-8") as outfile:
                outfile.write(f"# RepoLiner: Merged Code for '{os.path.basename(self.target_dir)}'\n")
                outfile.write(f"Scanned on: {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}\n\n")
                outfile.write(tree_content)
                outfile.write("\n\n" + ("=" * 50) + "\n\n")

                total_chars = len(tree_content)
                
                for rel_path in final_paths:
                    full_path = os.path.join(self.target_dir, rel_path)
                    file_extension = os.path.splitext(rel_path)[1].lower()

                    if os.path.abspath(full_path) == os.path.abspath(output_filepath):
                        continue

                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as infile:
                            content = infile.read()

                        lang_identifier = self.lang_map.get(file_extension, "text")
                        markdown_chunk = (
                            f'\n<file path="{rel_path}">\n'
                            f"\n~~~~{lang_identifier}\n"
                            f"\n{content.strip()}\n"
                            "\n~~~~\n"
                            "</file>\n\n"
                        )
                        outfile.write(markdown_chunk)

                        chunk_len = len(markdown_chunk)
                        total_chars += chunk_len
                        result["file_stats"].append((estimate_tokens(markdown_chunk), rel_path))
                        result["files_merged"] += 1
                    except Exception:
                        pass

            result["total_chars"] = total_chars
            result["success"] = True

        except Exception as e:
            result["success"] = False
            result["error"] = str(e)

        return result
