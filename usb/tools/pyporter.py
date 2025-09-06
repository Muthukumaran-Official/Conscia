import socket
import re
import os
import time
import signal
import threading
import requests
import ssl
import sys
from colorama import Fore, Style, init
from scapy.all import ARP, Ether, srp
from rich.table import Table
from rich.console import Console
from rich import box
from scapy.layers.l2 import getmacbyip  # To get MAC addresses
from scapy.all import IP, TCP, sr1, conf

# Initialize colorama
init(autoreset=True)

# Handle Ctrl+C for a clean exit
def signal_handler(sig, frame):
    print(Fore.RED + "\n[!] Scan interrupted by user. Stopping scan..." + Style.RESET_ALL)
    global scanning
    scanning = False
    input("\n[!] Scan interrupted. Press Enter to exit...")
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Regex patterns for validation
ip_add_pattern_v4 = re.compile(r"^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}$")
ip_add_pattern_v6 = re.compile(r'^((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){1,7}:)|(:([0-9A-Fa-f]{1,4}:){1,7})|(([0-9A-Fa-f]{1,4}:){1,6}:[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){1,5}(:[0-9A-Fa-f]{1,4}){1,2})|(([0-9A-Fa-f]{1,4}:){1,4}(:[0-9A-Fa-f]{1,4}){1,3})|(([0-9A-Fa-f]{1,4}:){1,3}(:[0-9A-Fa-f]{1,4}){1,4})|(([0-9A-Fa-f]{1,4}:){1,2}(:[0-9A-Fa-f]{1,4}){1,5})|([0-9A-Fa-f]{1,4}:((:[0-9A-Fa-f]{1,4}){1,6}))|(:((:[0-9A-Fa-f]{1,4}){1,7}|:)))$')
port_range_pattern = re.compile("([0-9]+)-([0-9]+)")

# Common ports professionals check first
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP - Server",
    68: "DHCP - Client",
    69: "TFTP",
    80: "HTTP",
    88: "Kerberos",
    110: "POP3",
    111: "RPC",
    119: "NNTP",
    123: "NTP",
    135: "MSRPC",
    137: "NetBIOS Name Service",
    138: "NetBIOS Datagram Service",
    139: "NetBIOS Session Service",
    143: "IMAP",
    161: "SNMP",
    162: "SNMP Trap",
    179: "BGP",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    500: "IKE",
    514: "Syslog",
    546: "DHCPv6 Client",
    547: "DHCPv6 Server",
    587: "SMTP Submission",
    631: "IPP",
    636: "LDAPS",
    873: "Rsync",
    993: "IMAPS",
    995: "POP3S",
    1025: "NFS / IIS",
    1080: "SOCKS Proxy",
    1194: "OpenVPN",
    1352: "IBM Lotus Notes",
    1433: "MSSQL",
    1434: "MSSQL Monitor",
    1521: "Oracle DB",
    1723: "PPTP",
    2049: "NFS",
    2082: "cPanel",
    2083: "cPanel SSL",
    2086: "WHM",
    2087: "WHM SSL",
    2095: "Webmail",
    2096: "Webmail SSL",
    2222: "DirectAdmin",
    3306: "MySQL",
    3389: "RDP",
    3690: "SVN",
    4443: "HTTPS Alternate",
    5060: "SIP",
    5222: "XMPP",
    5432: "PostgreSQL",
    5900: "VNC",
    5938: "TeamViewer",
    6666: "IRC",
    6667: "IRC",
    7000: "Custom App",
    7070: "Real Server",
    8000: "HTTP Alternate",
    8080: "HTTP Proxy",
    8443: "HTTPS Alternate",
    9000: "PHP-FPM",
    9001: "DHCP Failover",
    9090: "OpenFire Admin",
    9200: "Elasticsearch",
    10000: "Webmin"
}

open_ports = set()

# Load banner
def resource_path(filename):
    # Go up one folder from 'tools' to project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, "PyPorter", filename)

file_path = resource_path("banner.txt")

try:
    with open(file_path, "r", encoding="utf-8") as file:
        banner = file.read()
    print(Fore.GREEN + banner + Style.RESET_ALL)
except FileNotFoundError:
    print(Fore.RED + "[!] Banner file not found. Proceeding without banner." + Style.RESET_ALL)

# Get and validate the IP address or domain name
while True:
    target = input("Enter target IP address or domain name: ")

    try:
        addr_info = socket.getaddrinfo(target, None)[0]
        ip_add_entered = addr_info[4][0]

        # Detect IPv6 or IPv4 using ':' presence
        if ':' in ip_add_entered:
            ip_version = 6
            if ip_add_pattern_v6.match(ip_add_entered):
                print(f"{Fore.CYAN}IPv6 detected: {ip_add_entered}{Style.RESET_ALL}")
                break
            else:
                print(Fore.RED + "Invalid IPv6 address format." + Style.RESET_ALL)
        else:
            ip_version = 4
            if ip_add_pattern_v4.match(ip_add_entered):
                print(f"{Fore.CYAN}IPv4 detected: {ip_add_entered}{Style.RESET_ALL}")
                break
            else:
                print(Fore.RED + "Invalid IPv4 address format." + Style.RESET_ALL)

    except socket.gaierror:
        print(Fore.RED + "Invalid domain name or IP address. Please try again." + Style.RESET_ALL)


scan_results = []  # This will store detailed info about open ports

# ------------------- Extra Features -------------------

# MAC Vendor Lookup
def get_mac_vendor(mac):
    oui = mac[:8].replace(':', '').upper()
    vendors = {
        '00:00:0C': 'Cisco',
        '00:1A:2B': 'Dell',
        '00:50:56': 'VMware',
        '00:0C:29': 'VMware',
        '00:25:B3': 'Apple',
        '00:1D:0F': 'Huawei',
        '00:1E:68': 'HP',
        '00:24:81': 'Intel',
        '00:26:B0': 'Microsoft',
        '00:15:5D': 'Microsoft Hyper-V',
        '00:0D:3A': 'IBM',
        '00:1B:21': 'Netgear',
        '00:1C:B3': 'ASUS',
        '00:1E:8C': 'Samsung',
        '00:23:15': 'LG',
        '00:1F:3A': 'Sony',
        '00:22:5F': 'TP-Link',
        '00:26:18': 'Belkin',
        '00:1A:11': 'Roku',
        '00:1E:33': 'Google'
    }  # Replace with your mac-vendors.json data
    return vendors.get(oui, "Unknown")

# Enhanced Target Information Gathering
def get_target_info(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except:
        hostname = "N/A"
    
    try:
        mac = getmacbyip(ip) or "N/A"
        vendor = get_mac_vendor(mac) if mac != "N/A" else "N/A"
    except:
        mac, vendor = "N/A", "N/A"
    
    try:
        geo = requests.get(f"https://ipinfo.io/{ip}/json", timeout=3).json()
        location = f"{geo.get('city', '?')}, {geo.get('country', '?')}"
        isp = geo.get('org', 'Unknown').split()[-1]
    except:
        location, isp = "Lookup failed", "Unknown"
    
    try:
        ping = os.popen(f"ping -c 1 {ip}").read()
        ttl = int(re.search(r"ttl=(\d+)", ping).group(1))
        os_guess = "Linux" if ttl <= 64 else "Windows" if ttl <= 128 else "Unknown"
    except:
        os_guess = "Unknown"
    
    return {
        'IP': ip,
        'Hostname': hostname,
        'MAC': f"{mac} ({vendor})",
        'OS Guess': os_guess,
        'Location': location,
        'ISP': isp
    }

# Improved Banner Grabbing
def grab_banner(ip, port):
    try:
        with socket.socket() as s:
            s.settimeout(3)
            s.connect((ip, port))
            
            if port == 80:
                s.send(b"GET / HTTP/1.1\r\nHost: %s\r\n\r\n" % ip.encode())
            elif port == 443:
                ctx = ssl.create_default_context()
                with ctx.wrap_socket(s, server_hostname=ip) as ss:
                    ss.send(b"GET / HTTP/1.1\r\nHost: %s\r\n\r\n" % ip.encode())
                    return ss.recv(1024).decode(errors="ignore").strip()
            elif port in [21, 22, 25]:
                return s.recv(1024).decode(errors="ignore").strip()
            
            return s.recv(1024).decode(errors="ignore").strip()
    except:
        return None

def check_ssl(ip, port, hostname=None):
    try:
        context = ssl._create_unverified_context()  # accept all certs
        with socket.create_connection((ip, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname or ip) as ssock:
                # If handshake works, SSL is supported
                return True
    except ssl.SSLError:
        return False
    except (socket.timeout, ConnectionRefusedError):
        return False
    except Exception:
        return False


# Function to scan a port
def scan_port(port, retries=2):
    global scanning
    if not scanning:
        return
    
    family = socket.AF_INET if ip_version == 4 else socket.AF_INET6
    slow_ports = [21, 22, 25, 110, 143, 445, 587, 993, 995]  # ports known to respond slowly
    timeout = 5 if port in slow_ports else 3

    for attempt in range(retries):
        try:
            with socket.socket(family, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex((ip_add_entered, port)) == 0:  # 0 means open
                    if port not in open_ports:
                        open_ports.add(port)

                        banner = grab_banner(ip_add_entered, port)
                        ssl_status = check_ssl(ip_add_entered, port, hostname=target if not target.replace(".", "").isdigit() else None)
                        service = get_port_details(port)

                        scan_results.append({
                            'Port': port,
                            'Status': 'Open',
                            'Service': service,
                            'SSL': 'Yes' if ssl_status else 'No',
                            'Banner': (banner[:50] + '...') if banner else 'None'
                        })
                        print(f"{Fore.GREEN}[OPEN] Port {port} is open{Style.RESET_ALL}")
                    return
        except Exception:
            pass
    print(f"{Fore.RED}[CLOSED] Port {port} is closed{Style.RESET_ALL}")

# Function to get service details
def get_port_details(port):
    if port in common_ports:
        return common_ports[port]
    try:
        return socket.getservbyport(port)
    except (socket.error, OSError):
        return 'Unknown Service'


# ------------------- Main Execution Flow -------------------

if __name__ == "__main__":
    # Get target info
    target_info = get_target_info(ip_add_entered)
    
    # Display target summary
    print(Fore.CYAN + "\n[~] Target Summary:" + Style.RESET_ALL)
    for key, value in target_info.items():
        print(f"{Fore.BLUE}• {key}: {value}{Style.RESET_ALL}")
    
    # Scan common ports
    scanning = True
    threads = []
    for port in common_ports:
        thread = threading.Thread(target=scan_port, args=(port,))
        threads.append(thread)
        thread.start()
        time.sleep(0.05)
    for thread in threads:
        thread.join()
    
    # Ask for custom range
    print(Fore.YELLOW + "\n[!] Common port scan complete. Do you want to scan a custom range? (yes/no)" + Style.RESET_ALL)
    choice = input().strip().lower()
    if choice == 'yes':
        while True:
            port_range = input("Enter port range (e.g., 1-65535): ")
            port_range_valid = port_range_pattern.search(port_range.replace(" ", ""))
            if port_range_valid:
                port_min = int(port_range_valid.group(1))
                port_max = int(port_range_valid.group(2))
                break
        print("\n[+] Starting full port scan...\n")
        threads = []
        for port in range(port_min, port_max + 1):
            thread = threading.Thread(target=scan_port, args=(port,))
            threads.append(thread)
            thread.start()
            time.sleep(0.02)
        for thread in threads:
            thread.join()
    
    # Prepare PrettyTable for results

    console = Console()

    # Create rich table
    table = Table(title=f"[bold green]SCAN REPORT FOR {target}[/bold green]", box=box.SIMPLE)

    table.add_column("Category", style="bold cyan", no_wrap=True)
    table.add_column("Details", style="white")

    # Add target info
    for key, value in target_info.items():
        table.add_row(key, str(value))

    # Add port results
    if scan_results:
        for i, result in enumerate(scan_results):
            banner = result['Banner'] if result['Banner'] else 'None'
            if len(banner) > 45:
                banner = banner[:45] + "..."
            port_info = f"Port {result['Port']}: [green]{result['Service']}[/green] | SSL: {'[cyan]Yes[/cyan]' if result['SSL'] == 'Yes' else '[red]No[/red]'} | Banner: {banner}"
            if i == 0:
                table.add_row("Open Ports", port_info)
            else:
                table.add_row("", port_info)
    else:
        table.add_row("Open Ports", "[red]No open ports found[/red]")

    # Print table
    console.print(table)
    console.print("\n[bold yellow][!] Scan complete. Press Enter to exit...[/bold yellow]")
    input()
