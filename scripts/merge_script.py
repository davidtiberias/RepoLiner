import os
import argparse
from datetime import datetime  # --- NEW: Import datetime for timestamps

# --- Centralized Configuration ---
CONFIG = {
    # This is now just a folder name, not a full path
    "output_folder": "output",
    "ignore_files": ["launch.bat", "package-lock.json"],
    "ignore_dirs": [
        ".git",
        ".vscode",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        "env",
        ".next",
        "out",
        "gen",
        "schemas",
        "target",
        "debug",
        ".fingerprint",
        "output",  # Also ignore the output directory itself
    ],
    "lang_map": {
        ".py": "python",
        ".js": "javascript",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".md": "markdown",
        ".sh": "bash",
        ".bash": "bash",
        ".bat": "batch",
        ".cmd": "batch",
        ".ps1": "powershell",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".sql": "sql",
        ".java": "java",
        ".cs": "csharp",
        ".cpp": "cpp",
        ".go": "go",
        ".rb": "ruby",
        ".vbs": "vbscript",
        ".txt": "text",
    },
}


def setup_parser():
    """Sets up the command-line argument parser."""
    parser = argparse.ArgumentParser(description="RepoLiner: Merges project files.")
    parser.add_argument(
        "target_directory", help="The path to the project directory you want to scan."
    )
    return parser


def merge_scripts_to_md(target_dir, config):
    """
    Merges content of specified script files into a single Markdown file.
    """
    # --- DYNAMIC OUTPUT PATH LOGIC (NEW) ---
    # 1. Create the output directory inside the project folder if it doesn't exist
    script_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(script_root_dir, config["output_folder"])
    os.makedirs(output_dir, exist_ok=True)

    # 2. Get the target project's folder name
    project_name = os.path.basename(os.path.normpath(target_dir))

    # 3. Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    # 4. Combine them into the final filename and path
    output_filename = f"{project_name} {timestamp}.md"
    output_filepath = os.path.join(output_dir, output_filename)

    script_extensions = list(config["lang_map"].keys())
    lang_map = config["lang_map"]
    ignore_files = [f.lower() for f in config["ignore_files"]]
    ignore_dirs = [d.lower() for d in config["ignore_dirs"]]

    print(f'Scanning project at: "{os.path.abspath(target_dir)}"')
    print(f'Output will be saved to: "{os.path.abspath(output_filepath)}"')
    print("-" * 50)

    found_files_count = 0
    try:
        with open(output_filepath, "w", encoding="utf-8") as outfile:
            outfile.write(f"# RepoLiner: Merged Code for '{project_name}'\n")
            outfile.write(f"Scanned on: {timestamp}\n\n")

            for root, dirs, files in os.walk(target_dir, topdown=True):
                dirs[:] = [d for d in dirs if d.lower() not in ignore_dirs]
                for filename in files:
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, target_dir)
                    file_extension = os.path.splitext(filename)[1].lower()

                    if os.path.basename(filename).lower() in ignore_files:
                        continue
                    if os.path.abspath(file_path) == os.path.abspath(output_filepath):
                        continue

                    if file_extension in script_extensions:
                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as infile:
                                content = infile.read()
                            print(f"  -> Adding: {relative_path}")
                            found_files_count += 1
                            lang_identifier = lang_map.get(file_extension, "")
                            markdown_chunk = (
                                f"### `{relative_path}`\n\n"
                                f"```{lang_identifier}\n"
                                f"{content.strip()}\n"
                                "```\n\n"
                            )
                            outfile.write(markdown_chunk)
                        except Exception as e:
                            print(f"ERROR processing '{relative_path}': {e}")

    except IOError as e:
        print(f"FATAL ERROR: Could not write to output file '{output_filepath}': {e}")
        return

    print("-" * 50)
    print(f"Merging complete. Total files merged: {found_files_count}")


if __name__ == "__main__":
    parser = setup_parser()
    args = parser.parse_args()
    merge_scripts_to_md(args.target_directory, CONFIG)
