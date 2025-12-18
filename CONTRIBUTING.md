# Contributing to RepoLiner

First off, thank you for considering contributing to RepoLiner! It's people like you that make open source great. Following these guidelines helps us respect each other's time and ensures a smooth collaboration process.

We welcome all contributions, from simple bug reports to major new features.

## Table of Contents

- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
- [Development Workflow](#development-workflow)
- [Code Quality and Style Guide](#code-quality-and-style-guide)
  - [One-Time Setup for Pre-Commit](#one-time-setup-for-pre-commit)
  - [How It Works](#how-it-works)
  - [Manually Checking All Files](#manually-checking-all-files)
- [Pull Request (PR) Guidelines](#pull-request-pr-guidelines)
- [Handling Merge Conflicts](#handling-merge-conflicts)

## How Can I Contribute?

### Reporting Bugs

Bugs are tracked as [GitHub issues](https://github.com/davidtiberias/RepoLiner/issues). Before creating a bug report, please check the existing issues to see if someone has already reported it.

When creating a bug report, please include as many details as possible:

- **A clear and descriptive title.**
- **Steps to reproduce the bug.**
- **What you expected to happen.**
- **What actually happened.** Include any error messages and stack traces.
- **Your operating system** and the version of RepoLiner you are using.

### Suggesting Enhancements

Enhancement suggestions are also tracked as [GitHub issues](https://github.com/davidtiberias/RepoLiner/issues). Please check the [Roadmap in the README](README.md#future-plans-/-roadmap) and existing issues before creating a new one.

When creating an enhancement suggestion, please:

- **Provide a clear and descriptive title.**
- **Explain the problem or limitation** you are trying to solve. Why is this enhancement needed?
- **Describe your ideal solution.** How would it work?
- **Discuss any potential alternative solutions** or features you've considered.

## Development Workflow

Ready to contribute some code? Here is the standard workflow.

1.  **Fork the repository** to your own GitHub account.
2.  **Clone your fork** to your local machine: `git clone https://github.com/your-username/RepoLiner.git`
3.  **Navigate to the project directory:** `cd RepoLiner`
4.  **Create a new branch** for your changes. Please use a descriptive name.
    - For a new feature: `git checkout -b feat/add-html-output`
    - For a bug fix: `git checkout -b fix/crash-on-empty-file`
5.  **Make your changes!** Write clean, readable code and any necessary tests.
6.  **Commit your changes** with a clear and concise commit message.
7.  **Push your branch** to your fork on GitHub: `git push origin feat/add-html-output`
8.  **Open a Pull Request (PR)** from your fork's branch to the `main` branch of the original RepoLiner repository.

## Code Quality and Style Guide

To guarantee a high standard of code quality and consistency, the RepoLiner project **requires** the use of `pre-commit` for all contributions. This framework automatically runs our chosen tools—**Black** for formatting and **Flake8** for linting—before every commit.

### One-Time Setup for Pre-Commit

Before you make your first commit, you must install the Git hooks.

1.  Make sure you have completed the main project setup (scripts 0, 1, 2, and 3).
2.  Navigate to the RepoLiner root directory.
3.  Double-click the **`5-run-pre-commit.bat`** script.
4.  From the menu, choose option **1** to **Install Hooks**.

That's it! The hooks are now active.

### How it Works

Once the hooks are installed, you don't have to do anything else. Just work and commit as you normally would.

- Every time you run `git commit`, `pre-commit` will automatically check the files you are about to commit.
- If **Black** reformats a file, your commit will be stopped. This is normal. Just `git add` the newly formatted file and commit again.
- If **Flake8** finds an error, your commit will be stopped. You must fix the error before you can commit.

This process ensures that no code that violates our quality standards ever gets committed to the repository.

### Manually Checking All Files

If you want to run the checks on the entire project at once (for example, after a large refactor), you can:

1.  Run the **`5-run-pre-commit.bat`** script.
2.  Choose option **2** to **Run on All Files**.

## Pull Request (PR) Guidelines

- **Fill out the PR template.** Do not submit an empty PR description.
- **Explain the "what" and "why"** of your changes. Link to the issue your PR resolves using keywords like `Fixes #123`.
- **Keep PRs focused.** Each PR should address a single issue or feature. Do not mix bug fixes and new features in the same PR.
- **Ensure your code is well-documented** with comments and docstrings where necessary.
- **(Future) Ensure all tests are passing.** Once a test suite is established, your PR will be checked automatically.

## Handling Merge Conflicts

It is common for the `main` branch to be updated while you are working on your feature branch. If your PR has a merge conflict, it is your responsibility to resolve it.

Here is the recommended way to sync your branch and resolve conflicts:

1.  **Add the original repository as an "upstream" remote:**
    `git remote add upstream https://github.com/your-username/RepoLiner.git`
2.  **Fetch the latest changes from upstream:**
    `git fetch upstream`
3.  **Rebase your branch onto the upstream main branch:**
    `git rebase upstream/main`
4.  Git will now walk you through any conflicts. Fix the conflicting files in your editor.
5.  **Once all conflicts are resolved, push the changes to your fork.** You will need to use a force-push since you rebased.
    `git push --force-with-lease origin your-branch-name`

Thank you for your contribution!
