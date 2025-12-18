# Script Merger 🚀

A Python utility designed to recursively traverse a directory structure to find, read, and append the contents of source code and script files into a single, unified text document.

### Context

This tool was developed in collaboration with **Gemini**. The first implementation is to create a comprehensive snapshot of a project's codebase while filtering out irrelevant files or the output file itself to prevent infinite loops, to facilitate:

- **LLM Context Injection**: Feeding entire codebases into Large Language Models.
- **Technical Documentation**: Creating a single searchable file for audits.
- **Archival**: Preserving a flat-file version of a project state.

## 🛠 Core Principles

- **Recursive Discovery**

  Penetrates every subfolder within the target directory to ensure no nested logic is missed.

- **Extension Filtering**

  Utilizes a whitelist (e.g., `.py`, `.js`, `.sh`, `.yaml`) to filter for text-based source files only.

- **Exclusion Logic**

  Implements an `ignore_files` list to prevent self-processing, infinite loops, or the inclusion of sensitive data.

- **Encoding Resilience**

  Uses `utf-8` with `errors="ignore"` to handle diverse character sets without execution crashes.

- **Structured Output**

  Delimits contents with visual headers (`:: FILE: ./path/to/script.py`) for maximum readability.

## ⚙️ How to Use

1.  **Place** the script in the root of the project to be merged.
2.  **Configure** the `script_extensions` list in the code to include your specific file types.
3.  **Run** the script:
    ```bash
    python merge_script.py
    ```
4.  **Find** the consolidated output in `merged_scripts.txt`.

## ⚠️ Current Limitations (V1.0.0)

Honesty is at the core of this project. Users should be aware of the following:

- **I/O Overhead**: Currently opens and closes the output file for every match. While stable, this is less efficient for massive repositories.
- **Recursive Risk**: If the `output_filename` is changed but not added to the `ignore_files` list, the script may attempt to read its own output.
- **Static Pathing**: Currently locked to the directory it resides in via `os.walk(".")`.

## 🤝 Contribution

This is an evolving tool. If you see a way to optimize the I/O pattern or add dynamic path arguments, feel free to open a Pull Request.
