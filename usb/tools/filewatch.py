import hashlib
import os
import json
import sys
from colorama import Fore, Style, init
from rich.table import Table
from rich.console import Console

# Initialize colorama and rich
init(autoreset=True)
console = Console()

# Ensure DB file is always next to script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, "filewatch_db.json")

# ===== Banner Loader =====
def display_banner():
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
        banner_path = os.path.join(project_root, "filewatch", "filewatch_banner.txt")

        if not os.path.exists(banner_path):
            print(Fore.YELLOW + "[!] No banner file found in resources folder. Skipping banner display.")
            return

        with open(banner_path, "r", encoding="utf-8", errors="ignore") as banner_file:
            banner = banner_file.read()

        print(Fore.CYAN + banner + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"[!] Error displaying banner: {e}")

# ===== Hashing Functions =====
def calculate_hash(file_path):
    try:
        with open(file_path, 'rb') as f:
            sha256 = hashlib.sha256()
            while chunk := f.read(4096):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(Fore.RED + f"❌ Error: {e}")
        return None

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

def normalize_path(path):
    path = path.strip('"').strip("'").strip()
    return os.path.normpath(path)

def init_file(file_path):
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        print(Fore.RED + "❌ File not found.")
        return
    hash_value = calculate_hash(file_path)
    if hash_value:
        db = load_db()
        db[file_path] = hash_value
        save_db(db)
        print(Fore.GREEN + "✅ File hash saved successfully.")

def check_file(file_path):
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        print(Fore.RED + "❌ File not found.")
        return
    db = load_db()
    if file_path not in db:
        print(Fore.YELLOW + "⚠️ File not initialized. Please init first.")
        return
    current_hash = calculate_hash(file_path)
    table = Table(title="[bold magenta]FileWatch Result[/bold magenta]")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Status", style="bold")

    if current_hash == db[file_path]:
        table.add_row(file_path, "[bold green]UNCHANGED ✅[/bold green]")
    else:
        table.add_row(file_path, "[bold red]MODIFIED ⚠️[/bold red]")
        db[file_path] = current_hash
        save_db(db)
        print(Fore.YELLOW + "ℹ️ Auto rehashed with updated hash.")

    console.print(table)

# ===== Main Program =====
if __name__ == "__main__":
    display_banner()

    try:
        while True:
            print(Fore.YELLOW + "1. Init file hash")
            print(Fore.BLUE + "2. Check file integrity")
            print(Fore.RED + "3. Exit")
            choice = input(Fore.WHITE + "Enter your choice (1/2/3): ").strip()

            if choice == '1':
                path = normalize_path(input(Fore.LIGHTGREEN_EX + "Enter full file path to INIT: "))
                init_file(path)
            elif choice == '2':
                path = normalize_path(input(Fore.LIGHTBLUE_EX + "Enter full file path to CHECK: "))
                check_file(path)
            elif choice == '3':
                print(Fore.MAGENTA + "👋 Exiting.")
                break
            else:
                print(Fore.RED + "❌ Invalid choice.")
    except Exception as e:
        print(Fore.RED + f"\n[!] Unexpected error: {e}")

    input(Fore.YELLOW + "\nPress Enter to exit...")
