# scripts/merge_cli.py
import argparse
import sys
import os
from core import RepoLiner, estimate_tokens

# Color definitions for console output
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def setup_parser():
    parser = argparse.ArgumentParser(description="RepoLiner: Merges project files.")
    parser.add_argument("target_directory", help="Path to project.")
    parser.add_argument(
        "--mode",
        choices=["folder", "dump"],
        default="folder",
        help="Output mode: 'folder' (default /output) or 'dump' (repoliner_dump.md in target).",
    )
    return parser

def print_token_report(file_stats, total_chars):
    print("\n--- Token Consumption by File (Top 20) ---")
    file_stats.sort(key=lambda x: x[0], reverse=True)
    for tokens, path in file_stats[:20]:
        print(f"[{tokens:>6,} tokens]  {path}")
    if len(file_stats) > 20:
        print(f"... and {len(file_stats) - 20} smaller files.")
    print("-" * 50)

    estimated_tokens = estimate_tokens(" " * total_chars)
    print(f"Total Estimated Tokens: ~{estimated_tokens:,}")

    if estimated_tokens > 1000000:
        print(f"{RED}{BOLD}[!!!] EXTREME CAUTION: Over 1 Million Tokens!{RESET}")
        print(f"{RED}This will melt your credit card. Use Gemini 1.5/2.0.{RESET}")
    elif estimated_tokens > 200000:
        print(f"{RED}{BOLD}[!] WARNING: This exceeds Claude 3.5's context limit!{RESET}")
        print(f"{RED}It's too big for Claude (200k tokens). Use Gemini.{RESET}")
    elif estimated_tokens > 128000:
        print(f"{YELLOW}{BOLD}[!] WARNING: This exceeds GPT-4's context limit!{RESET}")
        print(f"{YELLOW}It's Over 9000! (Actually, it's over 128,000){RESET}")
        print(f"{GREEN}{BOLD}[-] Move this project to Claude 3.5; they have 200,000 sq. ft. of land.{RESET}")
    else:
        print(f"{GREEN}{BOLD}[OK] Fits comfortably within modern LLM context windows.{RESET}")

def main():
    # Fix Windows console encoding if possible
    try:
        if sys.platform == "win32":
            sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, ImportError):
        pass

    parser = setup_parser()
    args = parser.parse_args()

    try:
        liner = RepoLiner(args.target_directory)
        print(f'Scanning project at: "{os.path.abspath(args.target_directory)}"')
        
        result = liner.merge(mode=args.mode)

        if result["success"]:
            print(f'Output saved to: "{os.path.abspath(result["output_path"])}"')
            print("-" * 50)
            print(f"Merging complete. Total files merged: {result['files_merged']}")
            print_token_report(result["file_stats"], result["total_chars"])
        else:
            print(f"FATAL ERROR: {result['error']}")
    except Exception as e:
        print(f"FATAL ERROR: {e}")

if __name__ == "__main__":
    main()
