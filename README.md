# RepoLiner

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**RepoLiner** is a self-contained utility that scans a project directory and consolidates all specified source code files into a single, well-formatted Markdown file. It's designed for developers, auditors, and AI enthusiasts who need a complete, flat representation of a codebase for review, archival, or analysis.

## Table of Contents

- [1. About The Project](#1-about-the-project)
- [2. Key Features](#2-key-features)
- [3. Getting Started (One-Time Setup)](#3-getting-started-one-time-setup)
  - [Method A: Easy Installer (Windows Only)](#method-a-easy-installer-windows-only)
  - [Method B: Manual Installation (All Platforms)](#method-b-manual-installation-all-platforms)
- [4. How to Use RepoLiner](#4-how-to-use-repoliner)
  - [Method A: Interactive Mode (Recommended)](#method-a-interactive-mode-recommended)
  - [Method B: Command-Line Mode (Advanced)](#method-b-command-line-mode-advanced)
- [5. The Output](#5-the-output)
- [6. Configuration (Optional)](#6-configuration-optional)
- [7. Project Structure](#7-project-structure)
- [8. Contributions](#8-contributions)
- [9. License](#9-license)

## 1. About The Project

Whether you're preparing for a code audit, onboarding a new developer, or feeding a codebase into a Large Language Model (LLM), it's incredibly useful to have an entire project's source code in one file. RepoLiner automates this process.

It recursively scans a target directory, finds all relevant files, and merges them into a single Markdown document. Each file's content is neatly placed within a fenced code block, complete with the correct language identifier for syntax highlighting.

## 2. Key Features

- **One-Click Setup:** Includes automated scripts to install all dependencies on Windows.
- **User-Friendly:** Run interactively via a simple batch file—no command-line expertise needed.
- **Self-Contained Output:** All generated reports are saved in RepoLiner's `output/` folder, keeping your projects clean.
- **Organized & Timestamped:** Output files are automatically named with the project's folder name and a timestamp, preventing overwrites.
- **Intelligent Scanning:** Automatically ignores common non-source directories like `.git`, `node_modules`, and virtual environments.
- **Syntax Highlighting:** Adds language identifiers to Markdown code blocks for improved readability.
- **Customizable:** Easily configure which file types to include or which directories to ignore.

## 3. Getting Started (One-Time Setup)

Follow these simple steps to get RepoLiner ready. You only need to do this once.

### Download and Unzip RepoLiner

- Go to the [Releases page](https://github.com/davidtiberias/RepoLiner/releases) of this repository.
- Download the `Source code (zip)` file from the latest release.
- Unzip the folder to a convenient location (e.g., `C:\Tools\RepoLiner`).
- Then, choose **one** of the following setup methods.

### Method A: Easy Installer (Windows Only)

This is the recommended method for Windows users.

1.  **Run the Miniconda Installer**

    - Inside the RepoLiner folder, double-click on `1-install-miniconda.bat`.
    - This will automatically download and install a private version of Python/Conda for you. It does not require admin rights and will not interfere with other programs. Wait for it to complete.

2.  **Create the Project Environment**

    - Once Step 2 is done, double-click on `2-create-environment.bat`.
    - This script sets up RepoLiner's specific dependencies.

3.  **Install Dependencies**
    - Finally, double-click on `3-install-dependencies-pip.bat`.
    - This installs all the necessary Python tools like Flake8 and Black into the environment.

### Method B: Manual Installation (All Platforms)

Use this method if you are on macOS/Linux or are an advanced Windows user who wants to manage Conda manually.

1.  **Prerequisite:** Ensure you have [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda installed.
2.  **Create the Environment:** Open your terminal or command prompt, navigate to the RepoLiner directory, and run the following command:
    ```bash
    # cd /path/to/RepoLiner
    conda env create -f environment.yml
    ```
3.  **Activate the Environment:** Before installing dependencies, you must activate the newly created environment.

    ```bash
    conda activate repoliner-env
    ```

    _You must activate this environment every time you wish to work on the project._

4.  **Install Dependencies:** With the environment active, install all required Python packages using pip and the `requirements.txt` file.

**Setup is now complete!** You are ready to use the tool.

## 4. How to Use RepoLiner

You can run RepoLiner in two ways.

### Method A: Interactive Mode (Recommended)

This is the easiest way to use the tool.

1.  Navigate to your `RepoLiner` folder.
2.  Double-click the **`launch.bat`** file.
3.  A command window will open and prompt you to enter the path to the project you want to scan.
4.  Paste the full directory path into the window and press `Enter`.
5.  RepoLiner will process the project. Once complete, you can find the output file in the `output` folder.

### Method B: Command-Line Mode (Advanced)

This method is useful for automation or if you prefer using the terminal.

1.  Open a command prompt or terminal.
2.  Run the `launch.bat` script with the target directory path as an argument. Make sure to use quotes if the path contains spaces.

    **Example:**

    ```bash
    C:\Tools\RepoLiner\launch.bat "D:\Path\To\Your Project"
    ```

3.  The script will run directly without prompting for input. The output will be saved in the `output` folder.

## 5. The Output

- **Location:** All merged files are saved inside the `RepoLiner/output/` directory.
- **Filename Format:** The output file is automatically named using the pattern: `[ProjectFolderName] [YYYY-MM-DD HH-MM-SS].md`.
  - _Example:_ `MyWebApp 2025-12-01 14-30-56.md`

## 6. Configuration (Optional)

You can customize RepoLiner's behavior by editing the `CONFIG` dictionary at the top of the `scripts/merge_script.py` file.

- **Add a file type:** Add a new entry to the `lang_map` (e.g., `".c": "c",`).
- **Ignore a directory:** Add the folder name to the `ignore_dirs` list (e.g., `"dist",`).
- **Ignore a file:** Add the filename to the `ignore_files` list.

## 7. Project Structure

```
RepoLiner/
├── .gitignore                  # Files to be ignored by Git
├── .flake8                     # Flake8 rules
├── .pre-commit-config.yaml     # Pre-commit hook definitions
├── LICENSE                     # Project license
├── README.md                   # This documentation file
├── CONTRIBUTING.md             # The contribution guidelines eventho i am not really stick to it ehe
│
├── environment.yml             # (Setup) Project dependencies
├── 0-initialize-git-repo.bat   # (Setup for Contributors)
├── 1-install-miniconda.bat     # (Setup) Installs Miniconda
├── 2-create-environment.bat    # (Setup) Creates the environment
├── 3-install-dependencies-pip.bat # (Setup) Installs dependencies
├── 4-run-quality-checks.bat    # (Utility)
│
├── launch.bat                  # The file you run to use the tool
├── output/                     # All your merged reports are saved here
│
└── scripts/
    └── merge_script.py         # The core Python logic
```

## 8. Contributions

### Contributing Guidelines

Contributions are welcome! Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

Please open an [**Github Issue**](https://github.com/davidtiberias/RepoLiner/issues) first to discuss what you would like to change or add.

We have a detailed guide to help you get started. Please see our [**Contributing Guidelines**](CONTRIBUTING.md) for information on how to:

- Report bugs and request features
- Set up your development environment
- Submit a high-quality Pull Request

### Known Limitations and Considerations (v1.2.0)

In the spirit of transparency, it's important to be aware of the project's current limitations and design choices. This helps users understand what the tool is (and isn't) and provides a clear path for future improvements.

- **Primarily Windows-Focused Setup**

  - The one-click setup process is built around Windows batch scripts (`.bat`). While the core Python script is cross-platform, users on **macOS and Linux** must follow the manual installation guide. Future versions aim to include equivalent shell scripts (`.sh`) for these platforms.

- **Configuration Requires Code Editing**

  - To customize the tool (e.g., add new file types or ignore different directories), a user must directly edit the `CONFIG` dictionary inside the `scripts/merge_script.py` file. A key goal on our [roadmap](CHANGELOG.md#unreleased) is to move this to an external `config.yml` file for much easier customization.

- **No Graphical User Interface (GUI)**

  - RepoLiner is designed as a command-line and script-based utility for developers and power users. There is currently no graphical interface for selecting folders or changing settings.

- **Assumes Text-Based Source Files**

  - The script is designed to read text-based files (like `.py`, `.js`, `.md`, etc.). It will attempt to process any file extension listed in the configuration. If it encounters a binary file (like a `.png` image or `.exe` executable) that happens to have a monitored extension, it may fail or produce garbled output. Ensure your `script_extensions` list only contains text-based file types.

- **Basic Error Handling**
  - The script uses `errors="ignore"` when reading files to prevent crashes on character encoding issues. This is robust but means that if a file cannot be read properly, its content might be silently skipped or partially included.

If you encounter any other limitations, please consider [opening an issue](https://github.com/your-username/RepoLiner/issues) on GitHub to discuss it!

### Future Plans / Roadmap

We have many ideas for making RepoLiner even better. Contributions to these features are highly welcome!

- [ ] **External Configuration File (`config.yml`)**

  - Move all settings from the Python script to a user-friendly `config.yml` file. This will allow users to customize RepoLiner without ever touching the source code, making updates easier.

- [ ] **Modular Output Architecture:**
  - Refactor the core logic to be more extensible. Create a main "engine" that scans files and then passes the data to pluggable "formatters" (e.g., `format_markdown.py`, `format_html.py`), making it easy to add new output types without duplicating code.
- [ ] **Customizable File Ordering:**

  - Allow users to define the order of files in the output. This could support both algorithmic sorting (e.g., alphabetical, by directory depth) and a user-defined sequence in the `config.yml` file to create a more logical, story-like output.

- [ ] **Automatic Table of Contents**

  - Generate a clickable Table of Contents at the top of the output file, with links pointing to each merged file's section.

- [ ] **Additional Output Formats**
  - Add support for different output types, such as a single plain `.txt` file or a formatted HTML document with syntax highlighting.
- [ ] **Pre-flight Summary**

  - Before merging, display a summary of the files and file types found and ask the user for confirmation to proceed. This will help prevent accidental scans of the wrong directory.

- [ ] **Advanced Filtering with Glob Patterns**
  - Implement more granular control over file selection, allowing users to include/exclude files based on glob patterns (e.g., `src/**/*.py`, `!**/*_test.py`).
- [ ] **Comprehensive Testing Suite:**
  - Create a `tests/` directory containing a sample project (a "benchmark dataset") and expected output files. This will allow contributors to verify their changes do not break existing functionality and ensure consistent results.
- [ ] **Cross-Platform Shell Scripts**
  - Create `setup.sh` and `launch.sh` scripts to provide a first-class, automated user experience for macOS and Linux users, similar to the `.bat` files for Windows.

## 9. License

Distributed under the MIT License. See `LICENSE` for more information.
