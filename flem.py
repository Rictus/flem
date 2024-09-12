#!/usr/bin/env python3
"""
Command Line Tool for Fixing Bash Commands

This script provides functionality to retrieve the last executed bash command
from the user's history, send it to GPT for correction, and then
execute the corrected command.

Usage:
    python fix_cmd_with_llm.py [options]

Options:
    -h, --help    Show this help message and exit
    --dry-run     Print the fixed command without executing it

Author: Dylan Leroux
Date: 2024/09/12
"""

import os
import urllib.request
import json
import subprocess
import sys
from functools import partial
import argparse


def get_last_command_from_history():
    last_command = subprocess.getoutput('tail -n 3 ~/.bash_history | head -n 1 ').strip()
    return last_command

def ask_gpt_to_fix_command(command):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['FLEM_OPENAI_API_KEY']}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that fixes bash commands. Provide only the fixed command without any additional explanation."},
            {"role": "user", "content": f"Fix this bash command: {command}"}
        ],
        "max_tokens": len(command) + 20,
        "temperature": 0
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['choices'][0]['message']['content'].strip()
    except urllib.error.URLError as e:
        print(f"Error making request to OpenAI API: {e}")
        return None
    except Exception as e:
        print(f"Failed: {e}")
        return None

def run_command(command):
    dangerous_commands = ["rm", "dd", "mkfs", "fdisk", "mkswap", "mkfs.ext3", "mkfs.ext4", "mkfs.vfat"]
    if any(command.strip().startswith(cmd) for cmd in dangerous_commands):
        print(f"\033[1;31mWarning: The command '{command}' may be dangerous. Are you sure you want to proceed? [y/N]\033[0m")
        if input().lower() != 'y':
            print("Command execution cancelled.")
            sys.exit(1)
    try:
        result = subprocess.run(command, shell=True, check=False)
        return_code = result.returncode
    except Exception:
        return_code = 1
    sys.exit(return_code)
def maybe_print(verbose, message):
    if verbose:
        print(message)

def main(verbose = False):
    vprint = partial(maybe_print, verbose)
    vprint("Starting the command fixing process...")
    last_command = get_last_command_from_history()
    
    if not last_command:
        vprint("No previous command found in bash history.")
        return

    print(f"Last command found: {last_command}")
    vprint("Asking GPT to fix the command...")
    fixed_command = ask_gpt_to_fix_command(last_command)
    
    if fixed_command:
        vprint("GPT suggested a fix.")
        vprint(f"Original command: {last_command}")
        print(f"\033[1m{fixed_command}\033[0m   [\033[1;32mE]nter\033[0m \033[1;31m[C]ancel\033[0m")
        user_input = input("")
        
        if user_input in ["", "e", "E"]:
            run_command(fixed_command)
        else:
            vprint("Operation cancelled by user.")
    else:
        vprint("GPT did not suggest any fix for the command.")
        
def print_help():
    print("Usage: python fix_cmd_with_llm.py [-v] [-h]")
    print("Fix the last executed command using GPT.")
    print("")
    print("Options:")
    print("  -v, --verbose    Enable verbose output")
    print("  -h, --help       Show this help message and exit")

def cli():
    def print_help():
        print("Usage: python fix_cmd_with_llm.py [-v] [-h]")
        print("Fix the last executed command using GPT.")
        print("")
        print("Options:")
        print("  -v, --verbose    Enable verbose output")
        print("  -h, --help       Show this help message and exit")

    parser = argparse.ArgumentParser(description="Fix the last executed command using GPT.", add_help=False)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit")
    args = parser.parse_args()

    if args.help:
        print_help()
        sys.exit(0)

    main(verbose=args.verbose)

if __name__ == "__main__":
    cli()
