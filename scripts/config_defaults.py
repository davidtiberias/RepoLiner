"""
Default configuration for RepoLiner.
Used as a fallback if JSON config files are missing.
"""

DEFAULT_CONFIG = {
    "settings": {"output_folder": "output"},
    "ignore_files": [
        ".DS_Store", "thumbs.db", "desktop.ini", "package-lock.json",
        "yarn.lock", "pnpm-lock.yaml", ".env", ".env.local",
        "launch.bat", "repoliner_dump.md"
    ],
    "ignore_dirs": [
        "output", ".git", ".svn", ".hg", ".vscode", ".idea", ".vs",
        "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv",
        "env", ".next", "out", "build", "dist", "target", "bin", "obj",
        "vendor", "gen", "schemas", "debug", ".fingerprint", "models",
        "site-packages", ".refactor_backups", ".output", "log", ".docs",
        "ffmpeg", "runtime", "reference_legacy", ".data"
    ],
    "extensions": {
        ".py": "python", ".js": "javascript", ".mjs": "ECMAScript",
        ".htm": "htm", ".html": "html", ".css": "css", ".json": "json",
        ".sh": "bash", ".txt": "text", ".ts": "typescript", ".tsx": "typescript",
        ".rs": "rust", ".bat": "batch", ".yaml": "yaml", ".yml": "yml",
        ".hlsl": "hlsl", ".toml": "toml", ".gitignore": "gitignore", "d.ts": "d.ts"
    }
}
