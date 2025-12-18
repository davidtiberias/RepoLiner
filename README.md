# Script Merger 🚀

A multi-purpose Python ecosystem designed to recursively traverse directory structures and consolidate fragmented source code into unified, high-utility documents. This project bridges the gap between complex file architectures and the linear context requirements of Large Language Models (LLMs).

### Strategic Objective

The ecosystem provides specialized tools to create comprehensive project snapshots while strictly filtering out noise and preventing recursive infinite loops. It serves three primary functions:

- **LLM Context Injection**: Feeding entire codebases into Large Language Models in a single pass.
- **Technical Documentation**: Creating searchable, flat-file versions of projects for security audits and peer reviews.
- **Archival**: Preserving a point-in-time "Conceptual Gist" of a project's logic.

---

## 📂 Project Structure

The repository is organized by output specialization, allowing users to choose between raw data or structured documentation:

- **`main/script/merge_to_txt/`**: The "Performance" branch. Produces a plain `.txt` file with minimal overhead. Ideal for raw data processing.
- **`main/script/merge_to_md/`**: The "Presentation" branch. Produces a formatted `.md` file with syntax highlighting (fenced code blocks) and visual headers.

---

## 🛠 Core Principles

- **Recursive Discovery**: Penetrates every subfolder (excluding hidden directories like `.git`) to ensure no nested logic is missed.
- **Extension Filtering**: Utilizes robust whitelists (e.g., `.py`, `.js`, `.ts`, `.sh`, `.yaml`) to target only relevant source files.
- **Exclusion Logic**: Implements `ignore_files` protection to prevent self-processing and data leaks.
- **Encoding Resilience**: Uses `utf-8` with `errors="ignore"` to handle diverse character sets without execution crashes.

---

## ⚙️ Quick Start

1. **Navigate** to the specific script folder (`txt` or `md`) based on the desired output.
2. **Move** the script to your project's root directory.
3. **Execute** via Python or the provided Windows `.bat` wrapper:

```bash
python merge_script.py

```

4. **Analyze** the resulting `merged_scripts` file in the same directory.

---

## ⚠️ The "Advisor's" Disclosure (V1.0.0)

In the spirit of brutal honesty, this project is currently in its initial phase. Users should note:

- **Operational Inefficiency**: Early versions use a sequential append pattern. This is stable but creates disk overhead on massive repositories (thousands of files).
- **The Ouroboros Risk**: If the `output_filename` is changed but not updated in the ignore list, the script will attempt to read its own output—creating a massive, corrupted file.
- **Manual Mobility**: The scripts currently rely on being physically present in the directory they are scanning.

---

## 🤝 Contributing

This project is an evolving synthesis of human intent and AI collaboration. If the user identifies a way to automate the "Single-Handle" I/O refactor or implement dynamic path arguments, Pull Requests are encouraged.

**Next Step**: Should the focus move to generating the **main/script/merge_to_txt/README.md** to complete the repository documentation?
