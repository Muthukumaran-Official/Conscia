import psutil
import os
import sys
from prettytable import PrettyTable
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

# ===== Banner Loader =====
def display_banner():
    try:
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            # go one folder up from 'tools'
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # banner lives in resources/procpeek_banner.txt
        banner_path = os.path.join(base_dir, "procpeek", "procpeek_banner.txt")

        if not os.path.exists(banner_path):
            print(Fore.YELLOW + f"[!] No banner file found at {banner_path}. Skipping banner display.")
            return

        with open(banner_path, "r", encoding="utf-8", errors="ignore") as f:
            print(Fore.GREEN + f.read() + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"[!] Error displaying banner: {e}")


def get_status_color(status):
    if status == psutil.STATUS_RUNNING:
        return Fore.GREEN + "Running" + Style.RESET_ALL
    elif status == psutil.STATUS_SLEEPING:
        return Fore.YELLOW + "Sleeping" + Style.RESET_ALL
    elif status == psutil.STATUS_ZOMBIE:
        return Fore.RED + "Zombie" + Style.RESET_ALL
    elif status == psutil.STATUS_STOPPED:
        return Fore.MAGENTA + "Stopped" + Style.RESET_ALL
    else:
        return Fore.CYAN + status.capitalize() + Style.RESET_ALL

def format_time(timestamp):
    try:
        return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
    except:
        return "N/A"

def list_processes(sort_by='cpu'):
    table = PrettyTable()
    table.field_names = ["PID", "Name", "CPU %", "Memory MB", "Status", "Start Time", "Nice"]

    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status', 'create_time', 'nice']):
        try:
            mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'cpu': proc.info['cpu_percent'],
                'memory': mem_mb,
                'status': proc.info['status'],
                'start': format_time(proc.info['create_time']),
                'nice': proc.info['nice']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if sort_by == 'cpu':
        processes.sort(key=lambda x: x['cpu'], reverse=True)
    elif sort_by == 'mem':
        processes.sort(key=lambda x: x['memory'], reverse=True)

    for p in processes[:30]:  # Limit to top 30
        table.add_row([
            p['pid'],
            p['name'][:20],
            f"{p['cpu']:.1f}",
            f"{p['memory']:.1f}",
            get_status_color(p['status']),
            p['start'],
            p['nice']
        ])

    print(Fore.CYAN + "\n=== 🔍 ProcPeek: Process Info Viewer ===\n" + Style.RESET_ALL)
    print(table)

display_banner()

# === MAIN MENU ===
while True:
    print(Fore.BLUE + "\n--- ProcPeek Menu ---")
    print("1. View processes sorted by CPU usage")
    print("2. View processes sorted by Memory usage")
    print("3. Exit" + Style.RESET_ALL)
    choice = input(Fore.YELLOW + "Enter your choice (1/2/3): " + Style.RESET_ALL)

    if choice == '1':
        list_processes('cpu')
    elif choice == '2':
        list_processes('mem')
    elif choice == '3':
        print(Fore.GREEN + "👋 Exiting ProcPeek. Bye!\n")
        break
    else:
        print(Fore.RED + "❌ Invalid choice. Try again.")
