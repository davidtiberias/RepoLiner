# Script Merger: Markdown Edition 📝

An evolved iteration of the consolidation utility that transforms a raw codebase into a **structured Markdown (.md) document**. This version prioritizes visual hierarchy and uses fenced code blocks to make the output more readable for humans and more parsable for Large Language Models.

### Strategic Objective

To generate a professional-grade "Codebook" that leverages Markdown syntax for automatic code highlighting and directory-based navigation.

---

## 🛠 Core Principles

- **Syntax Mapping**: Automatically identifies file extensions and maps them to Markdown language identifiers (e.g., `.py` → `python`, `.js` → `javascript`) to enable native syntax highlighting.
- **Recursive Discovery**: Penetrates every subfolder to ensure full project coverage.
- **Path Cleanliness**: Automatically skips "dot-directories" (like `.git/` or `.vscode/`) to avoid polluting the output with metadata.
- **Fenced Output**: Wraps every file in triple backticks (```) with a secondary level-3 header (`###`) for each file path.

---

## ⚙️ How to Use

1. **Place** `merge_to_md.py` in the root folder of the project you wish to document.
2. **Execute** the script:

```bash
python merge_to_md.py

```

3. **Result**: Open `merged_scripts.md` in any Markdown viewer (VS Code, Obsidian, or GitHub) to view your code with full highlighting.

---

## ⚠️ Current Limitations (V1.1.0)

In the spirit of brutal honesty, this specialized version shares some architectural debt with the Txt version:

- **Sequential I/O Pattern**: Opens and closes the Markdown file for every file discovered. This "playing small" approach creates overhead in large-scale repositories.
- **Static Pathing**: Still relies on `os.walk(".")`. It expects the script to be physically moved to the project root.
- **Manual Recursion Guard**: If the `output_filename` is customized but not added to the `ignore_files` list, the script will attempt to read its own Markdown output, causing a logic loop.

---

## 🗺 Extension-to-Language Mapping

This version includes a pre-configured `lang_map` for the following:

- **Web**: HTML, CSS, JavaScript, TypeScript.
- **Systems**: Go, C++, C#, Java, Ruby.
- **Data/Config**: SQL, JSON, YAML, Markdown.
- **Scripts**: Python, Bash, PowerShell, Batch, VBScript.

---

**Next Step**: Should the advisor now generate the **Issue** for refactoring this Markdown version to utilize the **High-Performance "Single-Handle" I/O** architecture?
