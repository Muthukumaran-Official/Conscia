from PIL import Image
import string
import sys
import os
from rich.console import Console
from rich.table import Table
from colorama import Fore, Style, init

init(autoreset=True)
console = Console()

# ===== Banner Loader =====
def display_banner():
    try:
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            # Go up one level from 'tools'
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        banner_path = os.path.join(base_dir, "stegsniff", "stegsnif_banner.txt")

        if not os.path.exists(banner_path):
            print(Fore.YELLOW + f"[!] No banner file found at {banner_path}. Skipping banner display.")
            return

        with open(banner_path, "r", encoding="utf-8", errors="ignore") as f:
            print(Fore.CYAN + f.read() + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"[!] Error displaying banner: {e}")

def extract_lsb(image_path):
    try:
        img = Image.open(image_path)
        pixels = list(img.getdata())
        bits = ''

        for pixel in pixels:
            for channel in pixel[:3]:  # R, G, B
                bits += str(channel & 1)

        chars = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
        message = ''.join(chars)
        return message
    except Exception as e:
        console.print(f"[bold red]❌ Error while reading image:[/bold red] {e}")
        return None

def is_readable(text, threshold=0.85):
    readable_chars = string.ascii_letters + string.digits + string.punctuation + " \n\t\r"
    readable_count = sum(c in readable_chars for c in text)
    return readable_count / len(text) >= threshold if text else False

def scan_stego(image_path):
    console.print(f"\n[bold cyan]🔍 Scanning:[/bold cyan] [bold white]{image_path}[/bold white]\n")
    extracted_msg = extract_lsb(image_path)

    if not extracted_msg:
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Status", style="bold", justify="center")
    table.add_column("Details", style="bold white")

    if extracted_msg.startswith("STEGO:") and is_readable(extracted_msg):
        table.add_row("[green]✅ Hidden Message Found[/green]", extracted_msg[6:].split('#')[0])
    elif is_readable(extracted_msg):
        table.add_row("[yellow]⚠️ Possibly Hidden[/yellow]", extracted_msg.split('#')[0])
    else:
        table.add_row("[red]❌ No Valid Message[/red]", "Non-readable or invalid message detected.")
        choice = input(Fore.CYAN + "\n🔧 Show raw binary output anyway? (y/n): ").strip().lower()
        if choice == 'y':
            table.add_row("[blue]🧪 Raw Output[/blue]", extracted_msg[:200] + "..." if len(extracted_msg) > 200 else extracted_msg)

    console.print(table)

if __name__ == "__main__":

    display_banner()
    console.print("[bold cyan]🖼️ StegaSniff – LSB Steganography Detector[/bold cyan]\n")
    path = input(Fore.YELLOW + "📂 Enter the path of the image file: ").strip()

    if not os.path.exists(path):
        console.print("[bold red]🚫 File not found! Please check the path and try again.[/bold red]")
    else:
        scan_stego(path)

    # Pause so window doesn't close instantly
    input(Fore.MAGENTA + "\nPress Enter to exit...")
