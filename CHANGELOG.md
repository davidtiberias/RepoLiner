# Changelog

All notable changes to the **RepoLiner** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- _(Future features will be listed here)_

---

## [1.2.0] - 2025-12-18

This is a major usability and quality release, focusing on making the tool accessible to non-developers and ensuring long-term maintainability for contributors.

### Added

- **Dependency Management:** Added `environment.yml` to define the project's Conda environment.
- **Automated Windows Setup:** Introduced a full suite of batch scripts (`0-` through `3-`) to automate the entire setup process, from installing Miniconda to setting up the environment and dependencies.
- **Interactive Launcher:** Created `launch.bat`, a user-friendly interactive script that prompts the user for a target directory, removing the need for command-line arguments.
- **Dynamic Output Filenames:** The script now generates uniquely named output files based on the target project's folder name and a precise timestamp (e.g., `MyWebApp 2025-12-18 15-30-56.md`).
- **Contributor Quality Control:** Integrated professional code quality tools:
  - **Black** for uncompromising code formatting.
  - **Flake8** for linting and error checking.
  - **Pre-Commit** framework to automate these checks on every commit.
- **Contributor Utility Scripts:** Added `4-run-quality-checks.bat` (for Git-free checks) and `5-run-pre-commit.bat` (to manage Git hooks).
- **Comprehensive Documentation:** Created `CONTRIBUTING.md` with detailed guidelines for the development workflow, code standards, and the mandatory use of pre-commit.

### Changed

- **Centralized Configuration:** Refactored the core script to use a single `CONFIG` dictionary, applying the DRY (Don't Repeat Yourself) principle and making the code much easier to maintain.

### Fixed

- **Code Quality Compliance:** Addressed all linter warnings from Flake8, including fixing long lines and removing unnecessary f-strings.

---

## [1.1.0] - 2025-12-18

This release transitioned RepoLiner from a simple script into a proper, documented project with significantly more readable output.

### Changed

- **Output Format:** The script now generates a richly formatted **Markdown (`.md`)** file instead of a plain `.txt` file. This is the primary feature of this release.

### Added

- **Syntax Highlighting:** The Markdown output now includes language identifiers in fenced code blocks (e.g., ```python), enabling syntax highlighting.
- **Professional Project Structure:** Organized the codebase into a standard layout with `scripts/` and `output/` directories.
- **Core Documentation:** Created the initial `README.md` file with usage instructions and a `LICENSE` file.

---

## [1.0.0] - 2025-12-18

The initial release of RepoLiner.

### Added

- Core functionality to recursively scan a directory and merge the contents of multiple script files into a single `.txt` output file.
- Basic configuration within the script to define which file extensions to include.
