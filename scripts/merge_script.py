import os
import argparse
import fnmatch

from datetime import datetime

# --- 1. GLOBAL CONFIGURATION ---
CONFIG = {
    "output_folder": "output",  # RepoLiner Output Folder
    "ignore_files": [
        # OS Trash
        ".DS_Store",
        "thumbs.db",
        "desktop.ini",
        # Environment Files
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        # Security: Never read secrets!
        ".env",
        ".env.local",
        # User Defined
        "launch.bat",
    ],
    "ignore_dirs": [
        # RepoLiner Output (Ignore itself)
        "output",
        # Version Control
        ".git",
        ".svn",
        ".hg",
        # IDE settings
        ".vscode",
        ".idea",
        ".vs",
        # Python Cache
        "__pycache__",
        ".pytest_cache",
        # JS Dependencies
        "node_modules",
        # Python Environments
        ".venv",
        "venv",
        "env",
        # Web Build Artifacts
        ".next",
        "out",
        "build",
        "dist",
        # Rust/Java Build Artifacts
        "target",
        # C# Build Artifacts
        "bin",
        "obj",
        # PHP/Go Dependencies
        "vendor",
        # Other
        "gen",
        "schemas",
        "debug",
        ".fingerprint",
        "models",
        "site-packages"
        # User Defined
        ".refactor_backups",
        ".output",
        "log",
    ],
    "lang_map": {
        ".py": "python",
        ".js": "javascript",
        ".htm": "htm",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".md": "markdown",
        ".sh": "bash",
        ".txt": "text",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".rs": "rust",
    },
}

# --- 2. CALCULATE GLOBALS ONCE ---
IGNORE_FILES = set(f.lower() for f in CONFIG["ignore_files"])
IGNORE_DIRS = set(d.lower() for d in CONFIG["ignore_dirs"])
LANG_MAP = CONFIG["lang_map"]


def setup_parser():
    parser = argparse.ArgumentParser(description="RepoLiner: Merges project files.")
    parser.add_argument("target_directory", help="Path to project.")
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


def merge_scripts_to_md(target_dir):
    """Merges files using Global CONFIG + Local .gitignore."""

    # --- OUTPUT SETUP ---
    script_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
            outfile.write(f"# RepoLiner: Merged Code for '{project_name}'\n")
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
    if estimated_tokens > 200000:
        print(f"{RED}{BOLD}⚠️  WARNING: This exceeds Claude 3.5's context limit!{RESET}")
        print(f"{RED}⚠️  Burp: GPT-4 is full. Claude is unbuttoning his pants.{RESET}")
        print(
            f"{GREEN}{BOLD}🍽️  Take this all-you-can-eat buffet to Gemini 2.5/3 Pro at Google AI Studio.{RESET}"
        )
        print(f"{GREEN}🐷  It eats 1M tokens for breakfast.{RESET}")

    elif estimated_tokens > 128000:
        print(f"{YELLOW}{BOLD}⚠️  WARNING: This exceeds GPT-4's context limit!{RESET}")
        print(f"{YELLOW}⚠️  It's Over 9000! (Actually, it's over 128,000){RESET}")
        print(
            f"{GREEN}{BOLD}🏗️  Move this project to Claude 3.5; they have 200,000 sq. ft. of land.{RESET}"
        )
        print(f"{GREEN}{BOLD}🧠  Or ask Gemini 2.5/3 Pro at Google AI Studio.{RESET}")
        print(f"{GREEN}✨  They've got a rich parent.{RESET}")

    else:
        print(
            f"{GREEN}{BOLD}✅  Fits comfortably within modern LLM context windows.{RESET}"
        )
        print(f"{CYAN}✅  I think even Microsoft Copilot can read this.{RESET}")


if __name__ == "__main__":
    parser = setup_parser()
    args = parser.parse_args()
    merge_scripts_to_md(args.target_directory)
