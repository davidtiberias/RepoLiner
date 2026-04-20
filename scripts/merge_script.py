import os
import json
import argparse
import fnmatch

from datetime import datetime

from config_defaults import DEFAULT_CONFIG

# --- 1. CONFIGURATION LOADING ---
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
        except Exception as e:
            print(f"  -> WARNING: Could not load {filename}: {e}. Using defaults.")

    # Create default file if missing or corrupted
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_value, f, indent=4)
    except Exception as e:
        print(f"  -> WARNING: Could not save default {filename}: {e}")

    return default_value


def save_json_config(filename, data):
    """Saves a dictionary or list to a JSON config file."""
    file_path = os.path.join(CONFIG_DIR, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"  -> ERROR: Could not save {filename}: {e}")
        return False


def get_full_config():
    """Builds the full CONFIG dictionary from modular files."""
    return {
        "output_folder": load_json_config("settings.json", DEFAULT_CONFIG["settings"]).get("output_folder", "output"),
        "ignore_files": load_json_config("ignore_files.json", DEFAULT_CONFIG["ignore_files"]),
        "ignore_dirs": load_json_config("ignore_dirs.json", DEFAULT_CONFIG["ignore_dirs"]),
        "lang_map": load_json_config("extensions.json", DEFAULT_CONFIG["extensions"])
    }


# Load globals
CONFIG = get_full_config()
IGNORE_FILES = set(f.lower() for f in CONFIG["ignore_files"])
IGNORE_DIRS = set(d.lower() for d in CONFIG["ignore_dirs"])
LANG_MAP = CONFIG["lang_map"]


def setup_parser():
    parser = argparse.ArgumentParser(description="RepoLiner: Merges project files.")
    parser.add_argument("target_directory", help="Path to project.")
    parser.add_argument(
        "--mode",
        choices=["folder", "dump"],
        default="folder",
        help="Output mode: 'folder' (default /output) or 'dump' (repoliner_dump.md in target).",
    )
    return parser


def estimate_tokens(text_content):
    """
    Rough estimation of tokens.
    Rule of Thumb: 1 Token ~= 4 Characters in English code.
    """
    return len(text_content) // 4


def load_gitignore(target_dir):
    """
    Reads the .gitignore file from the project root (if it exists).
    Returns a list of patterns (e.g., ['*.log', 'secret_folder/']).
    """
    patterns = []
    gitignore_path = os.path.join(target_dir, ".gitignore")

    if os.path.exists(gitignore_path):
        print(f"  -> Found .gitignore at: {gitignore_path}")
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments (#) and empty lines
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except Exception as e:
            print(f"  -> WARNING: Could not read .gitignore: {e}")

    return patterns


def should_ignore(name, local_patterns):
    """
    The 'Bouncer' Logic.
    Checks if a file/folder name matches any of the wildcard patterns.
    """
    for pattern in local_patterns:
        # fnmatch handles the magic of converting "*.log" to match "error.log"
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def safe_walker(target_dir, local_patterns):
    """Yields valid paths using Global Rules AND Local .gitignore patterns."""
    for root, dirs, files in os.walk(target_dir, topdown=True):
        dirs[:] = [
            d
            for d in dirs
            if d.lower() not in IGNORE_DIRS and not should_ignore(d, local_patterns)
        ]
        yield root, dirs, files


def generate_tree(target_dir, local_patterns):
    """Generates a clean directory tree that mirrors the merged content."""
    tree_lines = ["Directory Tree:", "```text"]
    script_extensions = LANG_MAP.keys()  # Get the list of allowed file types

    for root, dirs, files in safe_walker(target_dir, local_patterns):
        level = root.replace(target_dir, "").count(os.sep)
        indent = "    " * level
        tree_lines.append(f"{indent}{os.path.basename(root)}/")

        subindent = "    " * (level + 1)
        for f in files:
            # --- APPLY ALL FILTERS, JUST LIKE THE MAIN LOOP ---
            # 1. Global File Check (e.g., .DS_Store)
            if f.lower() in IGNORE_FILES:
                continue
            # 2. Local .gitignore Check (e.g., /data/)
            if should_ignore(f, local_patterns):
                continue
            # 3. Extension Check (e.g., .jpg, .mp4, .db)
            file_extension = os.path.splitext(f)[1].lower()
            if file_extension not in script_extensions:
                continue

            # If all checks pass, add it to the tree
            tree_lines.append(f"{subindent}{f}")

    tree_lines.append("```")
    return "\n".join(tree_lines)


def merge_scripts_to_md(target_dir, mode="folder"):
    """Merges files using Global CONFIG + Local .gitignore."""

    # --- OUTPUT SETUP ---
    script_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if mode == "dump":
        output_filepath = os.path.join(target_dir, "repoliner_dump.md")
    else:
        output_dir = os.path.join(script_root_dir, CONFIG["output_folder"])
        os.makedirs(output_dir, exist_ok=True)

        project_name = os.path.basename(os.path.normpath(target_dir))
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        output_filename = f"{project_name} {timestamp}.md"
        output_filepath = os.path.join(output_dir, output_filename)

    print(f'Scanning project at: "{os.path.abspath(target_dir)}"')
    print(f'Output will be saved to: "{os.path.abspath(output_filepath)}"')

    # --- LOAD LOCAL RULES ---
    local_patterns = load_gitignore(target_dir)
    if local_patterns:
        print(f"  -> Loaded {len(local_patterns)} custom ignore rules.")

    print("-" * 50)

    found_files_count = 0
    total_chars = 0
    file_stats = []  # The Ledger to track individual file costs

    try:
        with open(output_filepath, "w", encoding="utf-8") as outfile:
            project_name = os.path.basename(os.path.normpath(target_dir))
            outfile.write(f"# RepoLiner: Merged Code for '{project_name}'\n")
            timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            outfile.write(f"Scanned on: {timestamp}\n\n")

            print("  -> Generating directory tree...")
            tree_content = generate_tree(target_dir, local_patterns)
            outfile.write(tree_content)
            outfile.write("\n\n" + ("=" * 50) + "\n\n")

            total_chars += len(tree_content)

            for root, dirs, files in safe_walker(target_dir, local_patterns):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, target_dir)
                    file_extension = os.path.splitext(filename)[1].lower()

                    if os.path.basename(filename).lower() in IGNORE_FILES:
                        continue
                    if should_ignore(filename, local_patterns):
                        continue
                    if os.path.abspath(file_path) == os.path.abspath(output_filepath):
                        continue

                    if file_extension in LANG_MAP:
                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as infile:
                                content = infile.read()

                            print(f"  -> Adding: {relative_path}")
                            found_files_count += 1

                            lang_identifier = LANG_MAP.get(file_extension, "text")

                            markdown_chunk = (
                                f'\n<file path="{relative_path}">\n'
                                f"\n~~~~{lang_identifier}\n"
                                f"\n{content.strip()}\n"
                                "\n~~~~\n"
                                "</file>\n\n"
                            )
                            outfile.write(markdown_chunk)

                            # --- NEW: Calculate and Record Stats ---
                            chunk_len = len(markdown_chunk)
                            total_chars += chunk_len
                            file_tokens = estimate_tokens(markdown_chunk)

                            # Add to our ledger: (Token Count, File Path)
                            file_stats.append((file_tokens, relative_path))

                        except Exception as e:
                            print(f"ERROR processing '{relative_path}': {e}")

    except IOError as e:
        print(f"FATAL ERROR: Could not write to output file '{output_filepath}': {e}")
        return

    print("-" * 50)
    print(f"Merging complete. Total files merged: {found_files_count}")

    # --- NEW: The Itemized Bill (Sorted by Cost) ---
    print("\n--- Token Consumption by File (Top 20) ---")

    # Sort the list: Highest tokens first
    file_stats.sort(key=lambda x: x[0], reverse=True)

    for tokens, path in file_stats[:20]:  # Show top 20 to avoid spamming console
        print(f"[{tokens:>6,} tokens]  {path}")

    if len(file_stats) > 20:
        print(f"... and {len(file_stats) - 20} smaller files.")

    print("-" * 50)

    # --- The Quantity Surveyor (Total) ---
    estimated_tokens = estimate_tokens(
        " " * total_chars
    )  # Quick hack to use the function
    print(f"Total Estimated Tokens: ~{estimated_tokens:,}")

    # --- Color Definitions (The Paint Buckets) ---
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # --- The Logic ---
    if estimated_tokens > 1000000:
        print(f"{RED}{BOLD}[!!!] EXTREME CAUTION: Over 1 Million Tokens!{RESET}")
        print(f"{RED}This will melt your credit card. Use Gemini 1.5/2.0.{RESET}")

    elif estimated_tokens > 200000:
        print(f"{RED}{BOLD}[!] WARNING: This exceeds Claude 3.5's context limit!{RESET}")
        print(f"{RED}It's too big for Claude (200k tokens). Use Gemini.{RESET}")
        print(f"{RED}Gemini 1.5/2.0 can handle up to 1-2 million tokens.{RESET}")

    elif estimated_tokens > 128000:
        print(f"{YELLOW}{BOLD}[!] WARNING: This exceeds GPT-4's context limit!{RESET}")
        print(f"{YELLOW}It's Over 9000! (Actually, it's over 128,000){RESET}")
        print(
            f"{GREEN}{BOLD}[-] Move this project to Claude 3.5; they have 200,000 sq. ft. of land.{RESET}"
        )
        print(f"{GREEN}{BOLD}[-] Or ask Gemini Pro at Google AI Studio.{RESET}")
        print(f"{GREEN}[-] They've got a rich parent.{RESET}")

    else:
        print(
            f"{GREEN}{BOLD}[OK] Fits comfortably within modern LLM context windows.{RESET}"
        )
        print(f"{CYAN}[OK] I think even Microsoft Copilot can read this.{RESET}")


if __name__ == "__main__":
    # Fix Windows console encoding if possible
    try:
        import sys
        if sys.platform == "win32":
            sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, ImportError):
        pass

    parser = setup_parser()
    args = parser.parse_args()
    merge_scripts_to_md(args.target_directory, args.mode)
