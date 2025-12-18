import os


def merge_scripts_to_txt(
    output_filename="merged_scripts.txt",
    script_extensions=[
        ".bat",
        ".cmd",
        ".ps1",
        ".py",
        ".js",
        ".vbs",
        ".sh",
        ".yaml",
        ".yml",
        ".md",
        ".txt",
    ],
    ignore_files=[
        "merge_script.py",
        "merged_scripts.txt",
        "merge_script.bat",
    ],  # Add this new argument
):
    """
    Merges content of specified script files from the current directory and its subfolders
    into a single text file.

    Args:
        output_filename (str): The name of the output text file.
        script_extensions (list): A list of file extensions (e.g., ".py", ".bat") to merge.
        ignore_files (list): A list of filenames (case-insensitive) to ignore during merging.
    """

    # Ensure extensions are lowercase for case-insensitive comparison
    script_extensions = [ext.lower() for ext in script_extensions]
    # Ensure ignore_files are lowercase for case-insensitive comparison
    ignore_files = [f.lower() for f in ignore_files]

    print(f'Merging script files into "{output_filename}"...')
    print("-" * 50)

    found_files_count = 0

    # Clear the output file or create an empty one
    try:
        with open(output_filename, "w", encoding="utf-8") as outfile:
            outfile.write("")  # Ensure the file is empty or created
    except IOError as e:
        print(
            f"ERROR: Could not create/clear output file '{output_filename}'. Reason: {e}"
        )
        return

    # Walk through the directory tree
    for root, _, files in os.walk("."):  # Start from the current directory '.'
        for filename in files:
            file_path = os.path.join(root, filename)
            file_extension = os.path.splitext(filename)[
                1
            ].lower()  # Get extension and convert to lowercase

            # Get just the filename (without path) for ignore_files check
            file_name_only = os.path.basename(file_path).lower()

            # DEBUG: Show what file is being processed and its extracted extension
            print(f'DEBUG: Processing "{file_path}" (Extension: "{file_extension}")')

            if file_name_only in ignore_files:
                print(f'DEBUG: SKIPPING "{file_path}" (Explicitly ignored).')
                continue

            if file_extension in script_extensions:
                try:
                    with open(
                        file_path, "r", encoding="utf-8", errors="ignore"
                    ) as infile:
                        content = infile.read()

                    # DEBUG: Confirm match and addition
                    print(f'DEBUG: MATCHED! Adding "{file_path}" to output.')
                    found_files_count += 1

                    with open(output_filename, "a", encoding="utf-8") as outfile:
                        outfile.write("=" * 80 + "\n")
                        outfile.write(f":: FILE: {file_path}\n")
                        outfile.write("=" * 80 + "\n")
                        outfile.write(content)
                        outfile.write("\n\n")  # Add extra newlines for separation
                except (IOError, PermissionError) as e:
                    print(f"ERROR: Could not read file '{file_path}'. Reason: {e}")
                except UnicodeDecodeError:
                    print(
                        f"WARNING: Could not decode file '{file_path}' with utf-8. Skipping content."
                    )
            else:
                # DEBUG: Indicate skipped files
                print(
                    f'DEBUG: SKIPPED "{file_path}" (Extension "{file_extension}" not in list).'
                )

    print("=" * 50)
    print(f"Merging complete.")
    print(f"Total script files merged: {found_files_count}")
    print(f'All specified script files have been merged into "{output_filename}".')
    print(f"You can find the merged file in the current directory.")
    print("=" * 50)


if __name__ == "__main__":
    # You can customize ignore_files here when calling the function directly
    merge_scripts_to_txt(
        ignore_files=["merge_script.py", "merged_scripts.txt", "my_secret_file.txt"]
    )
