import subprocess              # helps to run system commands in cmd/terminal
import re                      # helps to use regular expressions
from colorama import Fore, Style, init  # to add colors and style
import os                      # to handle file paths
import sys                     # to access sys._MEIPASS for bundled files in an exe

# Initialize colorama
init(autoreset=True)

# Determine if running as an executable or script
if getattr(sys, 'frozen', False):
    # Running as an executable (PyInstaller)
    base_dir = sys._MEIPASS
else:
    # Running as a script
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level (if script is in tools/) and then into resources/
project_root = os.path.dirname(base_dir)
banner_file = os.path.join(project_root, "wpassrecon", "WPassRecon.txt")

# Read the ASCII banner from the file
try:
    with open(banner_file, "r", encoding="utf-8", errors="ignore") as file:
        ascii_banner = file.read()
except FileNotFoundError:
    ascii_banner = "Wi-Fi Password Viewer"  # Fallback banner

# Print the banner in fiery orange (red + yellow)
print(f"{Style.BRIGHT}{Fore.RED}{ascii_banner}{Fore.YELLOW}")

# Find the name of the network profiles available
command_output = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True).stdout.decode()

# Use regular expressions to find network profiles that have ALL user Profiles
profile_names = re.findall("All User Profile     : (.*)\r", command_output)

# Create a list to store the details of the network profiles
wifi_lists = []

# Check if there are any profiles
if len(profile_names) != 0:
    # Loop through each network profile
    for name in profile_names:
        wifi_profile = dict()

        # Check if the security key is available
        profile_info = subprocess.run(["netsh", "wlan", "show", "profile", name], capture_output=True).stdout.decode()
        if re.search("Security key           : Absent", profile_info):
            wifi_profile["ssid: "] = name
            wifi_profile["passwd: "] = None
        else:
            wifi_profile["ssid: "] = name

            # Get the password
            profile_info_passwd = subprocess.run(["netsh", "wlan", "show", "profiles", name, "key=clear"], capture_output=True).stdout.decode()

            # Store the password obtained
            passwd = re.search("Key Content            : (.*)\r", profile_info_passwd)

            # Check if password exists
            if passwd is None:
                wifi_profile["passwd: "] = None
            else:
                wifi_profile["passwd: "] = passwd[1]

        # Add the wifi profile to the list
        wifi_lists.append(wifi_profile)

# Get the absolute path for the output file to be saved in the same directory as the exe
# Get the folder where the banner is located
banner_dir = os.path.dirname(banner_file)

# Save the output file in the same folder as the banner
output_file = os.path.join(banner_dir, "wifi_passwords.txt")
# Save profiles and passwords to a file for future reference
with open(output_file, "a") as file:
    file.write(f"{'='*50}\n")
    file.write("Wi-Fi Profiles and Passwords\n")
    file.write(f"{'='*50}\n")
    for wifi in wifi_lists:
        ssid = wifi.get("ssid: ")
        password = wifi.get("passwd: ")
        file.write(f"SSID: {ssid}\n")
        file.write(f"Password: {password if password else 'None'}\n")
        file.write("--------------------------------------------\n")

# Directly print all profiles and their passwords with colors
for wifi in wifi_lists:
    ssid = wifi.get("ssid: ")
    password = wifi.get("passwd: ")

    # Print SSID and password in the desired format
    print(f"{Style.BRIGHT}{Fore.GREEN}ssid: {Fore.GREEN}{ssid}")
    if password:
        print(f"{Style.BRIGHT}{Fore.GREEN}passwd: {Fore.GREEN}{password}")
    else:
        print(f"{Style.BRIGHT}{Fore.GREEN}passwd: {Fore.RED}None")
    print("--------------------------------------------")

# Prevent the console from closing immediately
input("Press Enter to exit...")
