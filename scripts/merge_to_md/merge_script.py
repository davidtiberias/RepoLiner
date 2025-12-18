import os


def merge_scripts_to_md(
    output_filename="merged_scripts.md",
    script_extensions=[
        ".py", ".js", ".html", ".css", ".json",
        ".md", ".txt", ".sh", ".bash", ".bat",
        ".cmd", ".ps1", ".vbs", ".yaml", ".yml",
        ".sql", ".java", ".cs", ".cpp", ".go", ".rb"
    ],
    ignore_files=[
        "merge_script.py",
        "merged_scripts.md",  # Updated to ignore the new output file
        "merge_script.bat",
    ],
):
    """
    Merges content of specified script files from the current directory and its
    subfolders into a single, formatted Markdown file with fenced code blocks.

    Args:
        output_filename (str): The name of the output Markdown file.
        script_extensions (list): A list of file extensions to merge.
        ignore_files (list): A list of filenames to ignore during merging.
    """

    # --- KEY ADDITION: Map file extensions to Markdown language identifiers ---
    lang_map = {
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
        ".txt": "text", # Use 'text' for plain text files
    }

    # Ensure extensions and ignore_files are lowercase for case-insensitive comparison
    script_extensions = [ext.lower() for ext in script_extensions]
    ignore_files = [f.lower() for f in ignore_files]

    print(f'Merging script files into "{output_filename}"...')
    print("-" * 50)

    found_files_count = 0

    # Clear the output file or create an empty one
    try:
        with open(output_filename, "w", encoding="utf-8") as outfile:
            outfile.write(f"# Merged Code from Project\n\n") # Add a main title to the MD file
    except IOError as e:
        print(f"ERROR: Could not create/clear output file '{output_filename}'. Reason: {e}")
        return

    # Walk through the directory tree
    for root, _, files in os.walk("."):
        for filename in files:
            # Skip dot-directories like .git, .vscode, etc.
            if any(os.path.sep + '.' in part for part in root.split(os.path.sep)):
                continue

            file_path = os.path.join(root, filename)
            file_extension = os.path.splitext(filename)[1].lower()
            file_name_only = os.path.basename(file_path).lower()

            if file_name_only in ignore_files:
                continue

            if file_extension in script_extensions:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as infile:
                        content = infile.read()

                    print(f'-> Adding "{file_path}"')
                    found_files_count += 1

                    # Get the language identifier for the fenced code block
                    lang_identifier = lang_map.get(file_extension, "")  # Fallback to empty for no highlighting

                    with open(output_filename, "a", encoding="utf-8") as outfile:
                        # --- NEW: Write in Markdown format ---
                        outfile.write(f"### `{file_path}`\n\n")
                        outfile.write(f"```{lang_identifier}\n")
                        outfile.write(content.strip())
                        outfile.write(f"\n```\n\n")
                        # ------------------------------------

                except Exception as e:
                    print(f"ERROR: Could not process file '{file_path}'. Reason: {e}")

    print("=" * 50)
    print("Merging complete.")
    print(f"Total files merged: {found_files_count}")
    print(f'Output saved to "{output_filename}".')
    print("=" * 50)


if __name__ == "__main__":
    merge_scripts_to_md()