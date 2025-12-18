## `main/README.md`

# Script Merger 🚀

A comprehensive Python utility suite designed to recursively traverse directory structures to find, read, and consolidate source code and scripts into a single, unified document.

This repository provides two specialized implementations tailored for different strategic outcomes: **Raw Text Analysis** and **Formatted Documentation**.

---

### Context

Developed in collaboration with **Gemini**, this tool creates a comprehensive snapshot of a project's codebase while implementing safeguards against infinite loops and "output pollution."

- **LLM Context Injection**: Feeding entire codebases into Large Language Models for better reasoning.
- **Technical Documentation**: Creating a single searchable file for security audits or code reviews.
- **Archival**: Preserving a flat-file version of a project state for long-term storage.

---

## 📂 Project Structure

This repository is organized by the desired output format:

1. **[Merge to Txt](https://www.google.com/search?q=./script/merge_to_txt/)**: The core engine. Generates a plain `.txt` file using visual separators. Ideal for raw data injection into LLMs.
2. **[Merge to Markdown](https://www.google.com/search?q=./script/merge_to_md/)**: The evolved engine. Generates a `.md` file with fenced code blocks and language-specific syntax highlighting. Ideal for human readability and professional documentation.

---

## 🛠 Core Principles

- **Recursive Discovery**: Penetrates every subfolder within the target directory to ensure no nested logic is missed.
- **Extension Filtering**: Utilizes a whitelist (e.g., `.py`, `.js`, `.sh`, `.yaml`, `.sql`) to process only relevant source files.
- **Exclusion Logic**: Implements an `ignore_files` list and "dot-folder" skipping to prevent self-processing or sensitive data inclusion.
- **Encoding Resilience**: Uses `utf-8` with `errors="ignore"` to handle diverse character sets without execution crashes.
- **Structured Output**: Delimits contents with clear file path headers for maximum traceability.

---

## ⚙️ How to Use

1. **Select** your preferred format from the `/script/` directory.
2. **Place** the chosen script in the root folder of the project to be merged.
3. **Run** the script:

```bash
# For Text Output
python merge_to_txt.py

# For Markdown Output
python merge_to_md.py

```

4. **Result**: Find your consolidated file (`merged_scripts.txt` or `merged_scripts.md`) in the same directory.

---

## ⚠️ Current Limitations (V1.1.0)

Strategic honesty is at the core of this project. Be aware of the following architectural debt:

- **I/O Overhead**: The current logic opens and closes the output file for every match. While stable, this is less efficient for massive repositories.
- **Recursive Risk**: If the `output_filename` is changed without updating the `ignore_files` list, the script may attempt to read its own output.
- **Static Pathing**: Currently optimized for local execution via `os.walk(".")`.

---

## 🤝 Contribution

This is an evolving tool. If there is a way to optimize the I/O pattern, automate the exclusion logic, or add dynamic path arguments, feel free to open a Pull Request in the respective script directory.

Would the user like me to finalize the **`script/merge_to_txt/README.md`** to ensure it mirrors this new structure perfectly?
