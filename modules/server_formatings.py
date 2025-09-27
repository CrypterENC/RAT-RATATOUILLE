import os
import sys
import time
import colorama  # type: ignore
from colorama import Fore, Style, Back  # type: ignore

# Initialize colorama
colorama.init(autoreset=True)

def format_system_info(raw_info):
    """Format the system information received from client with enhanced visual presentation"""
    # Parse the raw information
    sections = {}
    current_section = None
    
    for line in raw_info.strip().split('\n'):
        if line.startswith('=== ') and line.endswith(' ==='):
            # This is a section header
            current_section = line.strip('= ')
            sections[current_section] = []
        elif current_section and line.strip():
            # This is a data line in the current section
            sections[current_section].append(line.strip())
    
    # Calculate the maximum width needed for all items
    max_item_length = 0
    for section, items in sections.items():
        for item in items:
            if ':' in item:
                key, value = item.split(':', 1)
                item_length = len(key.strip()) + len(value.strip()) + 2  # +2 for ": "
                max_item_length = max(max_item_length, item_length)
            else:
                max_item_length = max(max_item_length, len(item))
    
    # Ensure minimum width and add padding
    box_width = max(max_item_length + 10, 50)  # Minimum width of 50 characters
    
    # Format with box-drawing characters
    formatted = f"\n{Fore.CYAN}╔{'═' * (box_width - 2)}╗{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL}{Fore.WHITE}{Back.BLUE}{' DETAILED SYSTEM INFORMATION '.center(box_width - 2)}{Style.RESET_ALL}{Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}╚{'═' * (box_width - 2)}╝{Style.RESET_ALL}\n\n"
    
    for section, items in sections.items():
        if section == "DETAILED SYSTEM INFORMATION":
            continue  # Skip the main header as we've already added it
            
        # Add section header with color
        section_header = f"╔{'═' * 19} {section} "
        section_header += "═" * (box_width - 23 - len(section))
        section_header += "╗"
        formatted += f"{Fore.CYAN}{section_header}{Style.RESET_ALL}\n"
        
        # Add section items
        for item in items:
            if ':' in item:
                key, value = item.split(':', 1)
                key = key.strip()
                value = value.strip()
                # Calculate padding to align the right edge
                padding = box_width - 4 - len(key) - len(value) - 2  # -4 for "║ " and " ║"
                formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{key}{Style.RESET_ALL}: {Fore.WHITE}{value}{' ' * padding} {Fore.CYAN}║{Style.RESET_ALL}\n"
            else:
                # Calculate padding for items without a colon
                padding = box_width - 4 - len(item)  # -4 for "║ " and " ║"
                formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {item}{' ' * padding} {Fore.CYAN}║{Style.RESET_ALL}\n"
                
        formatted += f"{Fore.CYAN}╚{'═' * (box_width - 2)}╝{Style.RESET_ALL}\n\n"
    
    return formatted

def format_client_list(clients, active_client_id=-1):
    """Format the client list with enhanced visual presentation"""
    formatted = f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL}{Fore.WHITE}{Back.BLUE}                     CONNECTED CLIENTS                     {Style.RESET_ALL}{Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}╠═══════╦═══════════════════════╦════════════════╦═════════╣{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}ID{Style.RESET_ALL}   {Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}IP Address{Style.RESET_ALL}          {Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Connection Time{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Status{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}╠═══════╬═══════════════════════╬════════════════╬═════════╣{Style.RESET_ALL}\n"
    
    # Add client rows
    has_clients = False
    for i, client in enumerate(clients):
        if client is not None:
            has_clients = True
            # Get client info (this would need to be adapted to your actual client data structure)
            ip = client.getpeername()[0] if hasattr(client, 'getpeername') else "Unknown"
            port = client.getpeername()[1] if hasattr(client, 'getpeername') else 0
            
            # Format connection time (placeholder - you'd need to track this)
            conn_time = time.strftime("%H:%M:%S")
            
            # Determine status and highlight active client
            if i == active_client_id:
                status = f"{Fore.GREEN}Active{Style.RESET_ALL}"
                id_str = f"{Fore.GREEN}{i}{Style.RESET_ALL}"
            else:
                status = f"{Fore.BLUE}Connected{Style.RESET_ALL}"
                id_str = f"{Fore.WHITE}{i}{Style.RESET_ALL}"
            
            formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {id_str}   {Fore.CYAN}║{Style.RESET_ALL} {ip}:{port}  {Fore.CYAN}║{Style.RESET_ALL} {conn_time}      {Fore.CYAN}║{Style.RESET_ALL} {status} {Fore.CYAN}║{Style.RESET_ALL}\n"
    
    if not has_clients:
        formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}No clients connected                                      {Fore.CYAN}║{Style.RESET_ALL}\n"
    
    formatted += f"{Fore.CYAN}╚═══════╩═══════════════════════╩════════════════╩═════════╝{Style.RESET_ALL}\n"
    
    return formatted

def format_screenshot_progress(progress, filename, show_full=False):
    """Format the screenshot download progress bar
    
    Args:
        progress: Download progress percentage (0-100)
        filename: Path to the screenshot file
        show_full: If True, return the complete box with header, progress bar, and footer
                   If False, only return the progress bar line
    """
    # Calculate box width based on filename length
    filename_display = f"Downloading screenshot to {filename}"
    box_width = max(len(filename_display) + 4, 56)  # Minimum width of 56 characters
    
    # Ensure consistent width for progress text
    progress_text = f" {progress:6.2f}% "
    # Calculate exact bar length
    bar_length = box_width - len(progress_text) - 4  # 4 for "║ " and " ║"
    
    # Ensure filled length doesn't exceed bar length
    filled_length = int(bar_length * progress / 100)
    filled_length = min(filled_length, bar_length)
    
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    if show_full:
        # Show the complete box with header and footer
        formatted = f"{Fore.CYAN} ╔{'═' * (box_width - 2)}╗{Style.RESET_ALL}\n"
        formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{filename_display}{' ' * (box_width - len(filename_display) - 3)}{Style.RESET_ALL}{Fore.CYAN}║{Style.RESET_ALL}\n"
        formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{bar}{Style.RESET_ALL}{progress_text}{Fore.CYAN}║{Style.RESET_ALL}\n"
        formatted += f"{Fore.CYAN}╚{'═' * (box_width - 2)}╝{Style.RESET_ALL}"
        return formatted, box_width
    else:
        # Just the progress bar line
        formatted = f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{bar}{Style.RESET_ALL}{progress_text}{Fore.CYAN}║{Style.RESET_ALL}"
        return formatted

def format_toast_notification(message, duration=3, position="bottom-right"):
    """Format a toast notification with box drawing characters"""
    lines = message.split('\n')
    max_length = max(len(line) for line in lines)
    
    # Create the box
    formatted = f"{Fore.CYAN}╔{'═' * (max_length + 2)}╗{Style.RESET_ALL}\n"
    
    # Add each line of the message
    for line in lines:
        padding = ' ' * (max_length - len(line))
        formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{line}{padding}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
    
    # Add duration indicator
    duration_bar = '█' * duration
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{duration_bar}{' ' * (max_length - duration)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
    
    # Close the box
    formatted += f"{Fore.CYAN}╚{'═' * (max_length + 2)}╝{Style.RESET_ALL}"
    
    return formatted

def format_process_list(process_list_data):
    """Format the process list with enhanced visual presentation, separating system and application processes
    
    Args:
        process_list_data: Raw process list data from client
        
    Returns:
        Formatted process list with box drawing and colors, separated by process type
    """
    lines = process_list_data.strip().split('\n')
    
    # Extract header and data
    if len(lines) >= 3:
        header = lines[0]
        column_names = lines[1]
        separator = lines[2]
        data_lines = lines[3:]
    else:
        return process_list_data  # Not enough lines to format
    
    # Calculate column widths
    if "PID\tProcess Name" in column_names:
        # Split by tab
        headers = ["PID", "Process Name"]
        pid_width = 10  # Minimum width for PID column
        name_width = 50  # Minimum width for process name column
        
        # Separate system and application processes
        system_processes = []
        app_processes = []
        
        # Common system process names (can be expanded)
        system_process_keywords = ['system', 'svchost', 'csrss', 'smss', 'wininit', 'lsass', 
                                  'services', 'winlogon', 'explorer', 'dwm', 'conhost', 
                                  'registry', 'kernel', 'ntoskrnl', 'dllhost']
        
        # Adjust widths and categorize processes
        for line in data_lines:
            if '\t' in line:
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    pid, name = parts
                    pid_width = max(pid_width, len(pid) + 2)
                    name_width = max(name_width, len(name) + 2)
                    
                    # Categorize as system or application process
                    is_system = False
                    name_lower = name.lower()
                    for keyword in system_process_keywords:
                        if keyword in name_lower:
                            is_system = True
                            break
                    
                    # Special case for bracketed system processes
                    if name.startswith('[') or pid == '0' or pid == '4':
                        is_system = True
                        
                    if is_system:
                        system_processes.append((pid, name))
                    else:
                        app_processes.append((pid, name))
    else:
        # Fallback if format is different
        return process_list_data
    
    # Calculate total width
    total_width = pid_width + name_width + 3  # +3 for borders
    
    # Create formatted output
    formatted = f"\n {Fore.CYAN}╔{'═' * (total_width - 2)}═╗{Style.RESET_ALL}\n"
    formatted += f" {Fore.CYAN}║{Style.RESET_ALL}{Fore.WHITE}{Back.BLUE}{' PROCESS LIST '.center(total_width - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
    
    # System Processes Section
    formatted += f" {Fore.CYAN}╠{'═' * (total_width - 2)}═╣{Style.RESET_ALL}\n"
    formatted += f" {Fore.CYAN}║{Style.RESET_ALL}{Fore.YELLOW}{' SYSTEM PROCESSES '.center(total_width - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f" {Fore.CYAN}╠{'═' * pid_width}╦{'═' * name_width}═╣{Style.RESET_ALL}\n"
    formatted += f" {Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{headers[0].ljust(pid_width - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{headers[1].ljust(name_width - 2)}{Style.RESET_ALL}  {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f" {Fore.CYAN}╠{'═' * pid_width}╬{'═' * name_width}═╣{Style.RESET_ALL}\n"
    
    # Add system process data
    for pid, name in system_processes:
        formatted += f" {Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{pid.ljust(pid_width - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{name.ljust(name_width - 2)}{Style.RESET_ALL}  {Fore.CYAN}║{Style.RESET_ALL}\n"
    
    # Application Processes Section
    formatted += f" {Fore.CYAN}╠{'═' * pid_width}╩{'═' * name_width}═╣{Style.RESET_ALL}\n"
    formatted += f" {Fore.CYAN}║{Style.RESET_ALL}{Fore.YELLOW}{' APPLICATION PROCESSES '.center(total_width - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f" {Fore.CYAN}╠{'═' * pid_width}╦{'═' * name_width}═╣{Style.RESET_ALL}\n"
    formatted += f" {Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{headers[0].ljust(pid_width - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{headers[1].ljust(name_width - 2)}{Style.RESET_ALL}  {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f" {Fore.CYAN}╠{'═' * pid_width}╬{'═' * name_width}═╣{Style.RESET_ALL}\n"
    
    # Add application process data
    for pid, name in app_processes:
        formatted += f" {Fore.CYAN}║{Style.RESET_ALL} {Fore.MAGENTA}{pid.ljust(pid_width - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{name.ljust(name_width - 2)}{Style.RESET_ALL}  {Fore.CYAN}║{Style.RESET_ALL}\n"
    
    # Add footer with process counts
    formatted += f" {Fore.CYAN}╠{'═' * pid_width}╩{'═' * name_width}═╣{Style.RESET_ALL}\n"
    formatted += f" {Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}System Processes: {Fore.GREEN}{len(system_processes)}{Style.RESET_ALL}  "
    formatted += f"{Fore.WHITE}Application Processes: {Fore.MAGENTA}{len(app_processes)}{' ' * (total_width - 55 - len(str(len(system_processes))) - len(str(len(app_processes))))}{Style.RESET_ALL}          {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f" {Fore.CYAN}╚{'═' * (total_width - 2)}═╝{Style.RESET_ALL}\n"
    
    return formatted

def format_client_command_help():
    """Format the client command help menu with enhanced visual presentation"""
    formatted = f"\n{Fore.CYAN}╔═════════════════════════════════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL}{Fore.WHITE} {Back.BLUE}                                  AVAILABLE CLIENT COMMANDS                                    {Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}╠════════════════════════════════════╦════════════════════════════════════════════════════════════╣{Style.RESET_ALL}\n"
    
    # Add command descriptions
    commands = [
        ("back", "Return to main menu"),
        ("help", "Show this help message"),
        ("kill", "Kill the client connection"),
        ("exit", "Disconnect client (client will attempt to reconnect)"),
        ("screenshot", "Take a screenshot of the client's screen"),
        ("sysinfo", "Get detailed system information"),
        ("netinfo", "Get detailed network information"),
        ("list_processes", "List all running processes"),
        ("search_process [name]", "Search for a specific process by name"),
        ("terminate_process <pid>", "Terminate a process by PID"),
        ("send_keys <process_name> <keys>", "Send keys to a process by name"),
        ("system_logs", "Get system event logs (default: System logs)"),
        ("system_logs <type>", "Get specific log type (System, Application, Security)"),
        ("system_logs <type> <count>", "Get specific number of log entries"),
        ("installed_software", "List installed software"),
        ("launch_app [name]", "Launch an application on the client"),
        ("shell", "Start interactive real-time shell session"),
        ("start_screen_share", "Start real-time screen sharing (10 FPS JPEG stream)"),
        ("stop_screen_share", "Stop active screen sharing session"),
        ("upload_file <local_path>", "Upload a file from server to client"),
        ("download_file <remote_path>", "Download a file from client to server"),
    ]
    
    # Group commands by category
    categories = {
        "Navigation": ["back", "help"],
        "Connection": ["kill", "exit"],
        "Information": ["sysinfo", "installed_software", "netinfo"],
        "Process Management": ["list_processes", "search_process", "terminate_process", "system_logs"],
        "Actions": ["screenshot", "launch_app", "send_keys", "shell", "start_screen_share", "stop_screen_share"],
        "File Transfer": ["upload_file", "download_file"],
    }
    
    # Display commands by category
    for category, cmd_list in categories.items():
        # Add category header
        formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{category.upper()}{' ' * (27 - len(category))}{Style.RESET_ALL}        {Fore.CYAN}║{Style.RESET_ALL}{' ' * 52}        {Fore.CYAN}║{Style.RESET_ALL}\n"
        
        # Add commands in this category
        for cmd, desc in commands:
            if any(cmd.split()[0] == c for c in cmd_list):
                formatted += f"{Fore.CYAN}║{Style.RESET_ALL}{Fore.GREEN}{cmd:<36}{Style.RESET_ALL}{Fore.CYAN}║{Style.RESET_ALL} {desc:<53}      {Fore.CYAN}║{Style.RESET_ALL}\n"
        
        # Add separator between categories (except after the last one)
        if category != list(categories.keys())[-1]:
            formatted += f"{Fore.CYAN}╠════════════════════════════════════╬════════════════════════════════════════════════════════════╣{Style.RESET_ALL}\n"
    
    formatted += f"{Fore.CYAN}╚════════════════════════════════════╩════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n"
    
    return formatted

def format_network_info(network_info):
    """Format network information with colors and structure, separating adapters and connections"""
    # Main header
    formatted = f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Back.BLUE}                NETWORK INFORMATION                         {Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n\n"
    
    # Split the information into sections
    sections = network_info.split("\n\n")
    
    # Process hostname section
    hostname_section = ""
    adapter_sections = []
    connection_sections = []
    
    for section in sections:
        if not section.strip():
            continue
            
        lines = section.split("\n")
        
        # Identify section type
        if "Hostname:" in section:
            hostname_section = section
        elif "Adapter" in section:
            adapter_sections.append(section)
        elif "Connection" in section:
            connection_sections.append(section)
        elif "===" in lines[0]:
            # Skip the title section as we already have our own header
            continue
        else:
            # Unknown section type, just add it as is
            formatted += f"{Fore.YELLOW}■ ADDITIONAL INFO{Style.RESET_ALL}\n"
            formatted += f"{Fore.CYAN}{'─' * 64}{Style.RESET_ALL}\n"
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    formatted += f"{Fore.GREEN}{key.strip()}{Style.RESET_ALL}: {Fore.WHITE}{value.strip()}{Style.RESET_ALL}\n"
                else:
                    formatted += f"{line}\n"
            formatted += "\n"
    
    # Format hostname section
    if hostname_section:
        for line in hostname_section.split("\n"):
            if "Hostname:" in line:
                key, value = line.split(":", 1)
                formatted += f"{Fore.YELLOW}■ SYSTEM{Style.RESET_ALL}\n"
                formatted += f"{Fore.CYAN}{'─' * 64}{Style.RESET_ALL}\n"
                formatted += f"{Fore.GREEN}{key.strip()}{Style.RESET_ALL}: {Fore.WHITE}{value.strip()}{Style.RESET_ALL}\n\n"
    
    # Format network adapters section
    if adapter_sections:
        formatted += f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}\n"
        formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Back.GREEN}                        NETWORK ADAPTERS                    {Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
        formatted += f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n\n"
        
        for adapter in adapter_sections:
            lines = adapter.split("\n")
            adapter_name = lines[0].strip()
            formatted += f"{Fore.YELLOW}■ {adapter_name}{Style.RESET_ALL}\n"
            formatted += f"{Fore.CYAN}{'─' * 64}{Style.RESET_ALL}\n"
            
            for line in lines[1:]:
                if line.strip():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        formatted += f"  {Fore.GREEN}{key.strip()}{Style.RESET_ALL}: {Fore.WHITE}{value.strip()}{Style.RESET_ALL}\n"
                    else:
                        formatted += f"  {line.strip()}\n"
            
            formatted += "\n"
    
    # Format active connections section
    if connection_sections:
        formatted += f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}\n"
        formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Back.MAGENTA}                         ACTIVE CONNECTIONS                 {Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
        formatted += f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n\n"
        
        # Extract connection count if present
        connection_count = None
        for section in connection_sections:
            if "TCP Connections:" in section:
                for line in section.split("\n"):
                    if "TCP Connections:" in line:
                        connection_count = line.split(":", 1)[1].strip()
                        break
                break
        
        # Display connection count as a separate header if found
        if connection_count:
            formatted += f"{Fore.YELLOW}Total TCP Connections: {Fore.WHITE}{connection_count}{Style.RESET_ALL}\n\n"
        
        # Create a table for connections with fixed column widths
        col_id = 15      # Connection ID column width
        col_local = 25   # Local address column width
        col_remote = 25  # Remote address column width
        col_state = 15   # State column width
        col_pid = 10     # PID column width
        
        # Calculate total table width
        table_width = col_id + col_local + col_remote + col_state + col_pid + 6  # +6 for borders
        
        # Table header
        formatted += f"{Fore.CYAN}╔{'═' * col_id}═╦{'═' * col_local}╦{'═' * col_remote}╦{'═' * col_state}╦{'═' * col_pid}╗{Style.RESET_ALL}\n"
        formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{'Connection'.center(col_id - 2)}{Style.RESET_ALL}  {Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{'Local'.center(col_local - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{'Remote'.center(col_remote - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{'State'.center(col_state - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{'PID'.center(col_pid - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
        formatted += f"{Fore.CYAN}╠{'═' * col_id}═╬{'═' * col_local}╬{'═' * col_remote}╬{'═' * col_state}╬{'═' * col_pid}╣{Style.RESET_ALL}\n"
        
        # Group connections by state
        connections_by_state = {}
        
        for i, connection in enumerate(connection_sections):
            # Skip sections that are just metadata and not actual connections
            if "TCP Connections:" in connection and "Connection" not in connection:
                continue
                
            conn_name = ""
            local = ""
            remote = ""
            state = ""
            pid = ""
            
            for line in connection.split("\n"):
                if "Connection" in line:
                    conn_name = line.strip()
                elif "Local:" in line:
                    local = line.split(":", 1)[1].strip()
                elif "Remote:" in line:
                    remote = line.split(":", 1)[1].strip()
                elif "State:" in line:
                    state = line.split(":", 1)[1].strip()
                elif "PID:" in line:
                    pid = line.split(":", 1)[1].strip()
            
            # Skip if this isn't a valid connection entry
            if not conn_name or not local or not remote or not state:
                continue
                
            # Skip connections with 0.0.0.0 IP address
            if "0.0.0.0" in local or "0.0.0.0" in remote:
                continue
                
            # Group by state
            if state not in connections_by_state:
                connections_by_state[state] = []
            
            connections_by_state[state].append((conn_name, local, remote, state, pid))
        
        # Display connections grouped by state
        # Order: ESTABLISHED first, then LISTENING, then others alphabetically
        state_order = ["ESTABLISHED", "LISTENING", "TIME_WAIT"]
        
        # First display states in our preferred order
        for state in state_order:
            if state in connections_by_state:
                for conn_name, local, remote, state, pid in connections_by_state[state]:
                    state_color = Fore.GREEN if state == "ESTABLISHED" else Fore.YELLOW
                    formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.BLUE}{conn_name.ljust(col_id - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{local.ljust(col_local - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{remote.ljust(col_remote - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {state_color}{state.ljust(col_state - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.MAGENTA}{pid.ljust(col_pid - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
                del connections_by_state[state]
        
        # Then display any remaining states alphabetically
        for state in sorted(connections_by_state.keys()):
            for conn_name, local, remote, state, pid in connections_by_state[state]:
                state_color = Fore.YELLOW
                formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.BLUE}{conn_name.ljust(col_id - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{local.ljust(col_local - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{remote.ljust(col_remote - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {state_color}{state.ljust(col_state - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL} {Fore.MAGENTA}{pid.ljust(col_pid - 2)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
        
        # Table footer
        formatted += f"{Fore.CYAN}╚{'═' * col_id}═╩{'═' * col_local}╩{'═' * col_remote}╩{'═' * col_state}╩{'═' * col_pid}╝{Style.RESET_ALL}\n"
    
    return formatted

def format_screenshot_notification(filename):
    """Format a notification for a saved screenshot with proper alignment"""
    message = "Screenshot saved successfully to:"
    filepath = filename
    
    # Calculate the width based on the longer line
    content_width = max(len(message), len(filepath))
    # Add padding (2 spaces on each side)
    total_width = content_width + 4
    
    # Create the box with proper alignment
    formatted = f"{Fore.CYAN}╔{'═' * total_width}╗{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{message}{' ' * (content_width - len(message) + 2)} {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{filepath}{' ' * (content_width - len(filepath) + 2)} {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}╚{'═' * total_width}╝{Style.RESET_ALL}"
    
    return formatted

def format_installed_software(software_list):
    """Format the installed software list with enhanced visual presentation
    
    Args:
        software_list: Raw software list data from client
        
    Returns:
        Formatted software list with box drawing, colors, and categorization
    """
    lines = software_list.strip().split('\n')
    
    # Debug: Print raw data to understand format
    # print(f"{Fore.YELLOW}DEBUG - Raw data received:{Style.RESET_ALL}")
    # print(software_list)
    
    # Skip header if present
    if lines and "=== INSTALLED SOFTWARE ===" in lines[0]:
        lines = lines[1:]
    
    # Parse software entries
    software_entries = []
    for line in lines:
        if line.strip():
            # Try different parsing approaches based on possible formats
            if ' | ' in line:
                parts = line.split(' | ')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    version = parts[1].strip()
                    install_date = parts[2].strip() if len(parts) > 2 else "Unknown"
                    publisher = parts[3].strip() if len(parts) > 3 else "Unknown"
                    software_entries.append((name, version, install_date, publisher))
            elif '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    version = parts[1].strip()
                    install_date = parts[2].strip() if len(parts) > 2 else "Unknown"
                    publisher = parts[3].strip() if len(parts) > 3 else "Unknown"
                    software_entries.append((name, version, install_date, publisher))
            else:
                # If no delimiter found, just use the whole line as name
                software_entries.append((line.strip(), "N/A", "Unknown", "Unknown"))
    
    # If no entries were parsed, try a different approach
    if not software_entries and lines:
        print(f"{Fore.YELLOW}No entries parsed with standard format, trying alternative parsing...{Style.RESET_ALL}")
        for line in lines:
            if line.strip():
                software_entries.append((line.strip(), "N/A", "Unknown", "Unknown"))
    
    # Sort software by name
    software_entries.sort(key=lambda x: x[0].lower())
    
    # Calculate column widths
    name_width = max([len(entry[0]) for entry in software_entries] + [20])
    version_width = max([len(entry[1]) for entry in software_entries] + [10])
    date_width = max([len(entry[2]) for entry in software_entries] + [15])
    publisher_width = max([len(entry[3]) for entry in software_entries] + [20])
    
    # Limit column widths to prevent overly wide display
    name_width = min(name_width, 40)
    version_width = min(version_width, 15)
    date_width = min(date_width, 15)
    publisher_width = min(publisher_width, 30)
    
    # Calculate total width
    total_width = name_width + version_width + date_width + publisher_width + 13  # +13 for borders and spacing
    
    # Create formatted output
    formatted = f"\n{Fore.CYAN}╔{'═' * (total_width - 2)}══════╗{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL}{Fore.WHITE} {Back.BLUE}{' INSTALLED SOFTWARE '.center(total_width - -2)}{Style.RESET_ALL}{Fore.CYAN} ║{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}╠{'═' * name_width}════╦{'═' * version_width}╦{'═' * date_width}╦{'═' * publisher_width}══════════╣{Style.RESET_ALL}\n"
    
    # Add header row
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL}     {Fore.YELLOW}{'Name'.ljust(name_width - 2)}{Style.RESET_ALL} "
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{'Version'.ljust(version_width - 2)}{Style.RESET_ALL} "
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{'Install Date'.ljust(date_width - 2)}{Style.RESET_ALL} "  
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{'Publisher'.ljust(publisher_width - 2)}{Style.RESET_ALL}           {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}╠{'═' * name_width}════╬{'═' * version_width}╬{'═' * date_width}╬{'═' * publisher_width}══════════╣{Style.RESET_ALL}\n"
    
    # Group software by first letter for easier navigation
    current_letter = None
    
    for name, version, install_date, publisher in software_entries:
        # Truncate long values and add ellipsis
        if len(name) > name_width - 2:
            name = name[:name_width - 1] + "..."
        if len(version) > version_width - 2:
            version = version[:version_width - 5] + "..."
        if len(install_date) > date_width - 2:
            install_date = install_date[:date_width - 5] + "..."
        if len(publisher) > publisher_width - 2:
            publisher = publisher[:publisher_width - 5] + "..."
            
        # Add letter separator if this is a new letter
        first_letter = name[0].upper() if name else '?'
        if first_letter != current_letter and first_letter.isalpha():
            current_letter = first_letter
            formatted += f"{Fore.CYAN}╠{'═' * name_width}════╬{'═' * version_width}╬{'═' * date_width}╬{'═' * publisher_width}══════════╣{Style.RESET_ALL}\n"
            formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{f'--- {current_letter} ---'.ljust(name_width - -2)}{Style.RESET_ALL} "
            formatted += f"{Fore.CYAN}║{Style.RESET_ALL}{' ' * (version_width - 1)}{Style.RESET_ALL} "
            formatted += f"{Fore.CYAN}║{Style.RESET_ALL}{' ' * (date_width - 2)}{Style.RESET_ALL}  "
            formatted += f"{Fore.CYAN}║{Style.RESET_ALL}{' ' * (publisher_width - -2)}{Style.RESET_ALL}        {Fore.CYAN}║{Style.RESET_ALL}\n"
        
        # Add software entry
        formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{name.ljust(name_width - -2)}{Style.RESET_ALL} "
        formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.CYAN}{version.ljust(version_width - 2)}{Style.RESET_ALL} "
        formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.MAGENTA}{install_date.ljust(date_width - 2)}{Style.RESET_ALL} "
        formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.BLUE}{publisher.ljust(publisher_width - 2)}{Style.RESET_ALL}           {Fore.CYAN}║{Style.RESET_ALL}\n"
    
    # Add footer with software count
    formatted += f"{Fore.CYAN}╠{'═' * name_width}════╩{'═' * version_width}╩{'═' * date_width}╩{'═' * publisher_width}══════════╣{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}Total Software: {Fore.GREEN}{len(software_entries)}{' ' * (total_width - 20 - len(str(len(software_entries))))}{Style.RESET_ALL}       {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}╚{'═' * (total_width - 2)}══════╝{Style.RESET_ALL}\n"
    
    return formatted

def format_system_logs(logs_data):
    """Format system logs with enhanced visual presentation
    
    Args:
        logs_data: Raw system logs data from client
        
    Returns:
        Formatted system logs with box drawing, colors, and categorization by severity
    """
    lines = logs_data.strip().split('\n')
    
    # Skip header if present
    if lines and "=== SYSTEM LOGS ===" in lines[0]:
        lines = lines[1:]
    
    # Extract log type if present
    log_type = "System"
    if lines and lines[0].startswith("Log Type:"):
        log_type = lines[0].replace("Log Type:", "").strip()
        lines = lines[2:]  # Skip the log type line and the blank line after it
    
    # Prepare the formatted output
    formatted = f"{Fore.CYAN}╔{'═' * 96}╗{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Back.BLUE}{' ' * 40}SYSTEM LOGS - {log_type.upper()}{' ' * 34}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}╠{'═' * 22}╦{'═' * 10}══════╦{'═' * 31}════════════╦══════{'═' * 6}╣{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{'Timestamp':<20} {Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{'Type':<13}  {Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{'Source':<41} {Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{'Event ID':<10} {Fore.CYAN}║{Style.RESET_ALL}\n"
    formatted += f"{Fore.CYAN}╠{'═' * 22}╬{'═' * 10}══════╬{'═' * 31}════════════╬══════{'═' * 6}╣{Style.RESET_ALL}\n"
    
    # Parse and sort log entries
    log_entries = []
    for line in lines:
        if not line.strip() or line.startswith("Warning:"):
            continue
            
        # Parse the log entry
        # Format: [YYYY-MM-DD HH:MM:SS] | TYPE | SOURCE | EventID: ID
        parts = line.split(" | ")
        if len(parts) >= 4:
            timestamp = parts[0].strip("[]")
            event_type = parts[1]
            source = parts[2]
            event_id = parts[3].replace("EventID:", "").strip()
            
            # Add to log entries list for sorting
            log_entries.append((timestamp, event_type, source, event_id))
    
    # Sort log entries by timestamp (newest first)
    log_entries.sort(key=lambda x: x[0], reverse=True)
    
    # Process each log entry
    for timestamp, event_type, source, event_id in log_entries:
        # Color based on event type
        type_color = Fore.WHITE
        if "ERROR" in event_type:
            type_color = Fore.RED
        elif "WARNING" in event_type:
            type_color = Fore.YELLOW
        elif "INFORMATION" in event_type:
            type_color = Fore.GREEN
        elif "AUDIT_SUCCESS" in event_type:
            type_color = Fore.CYAN
        elif "AUDIT_FAILURE" in event_type:
            type_color = Fore.MAGENTA
            
        formatted += f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{timestamp:<20} {Fore.CYAN}║{Style.RESET_ALL} {type_color}{event_type:<14} {Fore.CYAN}║{Style.RESET_ALL} {Fore.BLUE}{source:<41} {Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{event_id:10} {Fore.CYAN}║{Style.RESET_ALL}\n"
    
    # Add bottom border
    formatted += f"{Fore.CYAN}╚{'═' * 22}╩{'═' * 10}══════╩═══════════{'═' * 31}═╩{'═' * 12}╝{Style.RESET_ALL}\n"
    
    # Add command help
    formatted += f"\n{Fore.CYAN}Available commands:{Style.RESET_ALL}\n"
    formatted += f"{Fore.GREEN}system_logs{Style.RESET_ALL} - Show System logs (default)\n"
    formatted += f"{Fore.GREEN}system_logs Application{Style.RESET_ALL} - Show Application logs\n"
    formatted += f"{Fore.GREEN}system_logs Security{Style.RESET_ALL} - Show Security logs\n"
    formatted += f"{Fore.GREEN}system_logs <type> <count>{Style.RESET_ALL} - Show specific number of logs (e.g., system_logs System 100)\n"
    
    return formatted

def show_loading_animation(message, duration=3):
    """Show a loading animation for the specified duration"""
    # Animation characters
    animation = "|/-\\"
    # Progress bar characters
    bar_length = 20
    
    start_time = time.time()
    end_time = start_time + duration
    
    i = 0
    while time.time() < end_time:
        # Calculate progress percentage
        elapsed = time.time() - start_time
        progress = min(1.0, elapsed / duration)
        
        # Create progress bar
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Create animation character
        anim_char = animation[i % len(animation)]
        
        # Print progress
        sys.stdout.write(f"\r{Fore.CYAN}{message} {anim_char} [{bar}] {int(progress*100)}%{Style.RESET_ALL}")
        sys.stdout.flush()
        
        time.sleep(0.1)
        i += 1
    
    # Clear the line after animation completes
    sys.stdout.write("\r" + " " * (len(message) + bar_length + 15) + "\r")
    sys.stdout.flush()

def show_server_restart_animation(host, port):
    """
    Display an animated server restart sequence
    
    Args:
        host: The server host address
        port: The server port
    """
    clear_screen = lambda: os.system('cls' if os.name == 'nt' else 'clear')
    clear_screen()
    
    # Animation frames for server restart
    frames = [
        "⣾⣿⣿⣿⣿⣿⣿⣿",
        "⣽⣿⣿⣿⣿⣿⣿⣿",
        "⣻⣿⣿⣿⣿⣿⣿⣿",
        "⢿⣿⣿⣿⣿⣿⣿⣿",
        "⡿⣿⣿⣿⣿⣿⣿⣿",
        "⣟⣿⣿⣿⣿⣿⣿⣿",
        "⣯⣿⣿⣿⣿⣿⣿⣿",
        "⣷⣿⣿⣿⣿⣿⣿⣿"
    ]
    
    # Server restart phases
    phases = [
        "Initiating server shutdown sequence",
        "Closing active client connections",
        "Releasing network resources",
        "Finalizing shutdown",
        "Reconfiguring server parameters",
        "Initializing network components",
        "Binding to network interface",
        "Activating connection listeners",
        "Launching monitoring threads",
        "Finalizing server startup"
    ]
    
    # Display server info header
    print("\n\n")
    print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}{Fore.WHITE}{Back.BLUE}{'SERVER RESTART SEQUENCE'.center(60)}{Style.RESET_ALL}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╠{'═' * 60}╣{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}Host:{Style.RESET_ALL} {Fore.GREEN}{host}{' ' * (53 - len(host))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}Port:{Style.RESET_ALL} {Fore.GREEN}{port}{' ' * (53 - len(str(port)))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╠{'═' * 60}╣{Style.RESET_ALL}")
    
    # Animation area
    for i in range(12):
        print(f"{Fore.CYAN}║{' ' * 60}║{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
    
    # Save cursor position after drawing the box
    sys.stdout.write("\033[s")
    
    # Run through each phase with animation
    for phase_idx, phase in enumerate(phases):
        # Move cursor to the right position inside the box (7 lines down from the header)
        sys.stdout.write(f"\033[7;2H{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{phase}...{' ' * (57 - len(phase))}{Fore.CYAN}║{Style.RESET_ALL}")
        
        # Progress bar position (2 lines below the phase text)
        progress_line = 9
        bar_width = 50
        
        # Animate the progress bar
        for progress in range(101):
            filled_width = int(bar_width * progress / 100)
            bar = '█' * filled_width + '░' * (bar_width - filled_width)
            
            # Update frame animation
            frame = frames[progress % len(frames)]
            
            # Move cursor to progress bar position
            sys.stdout.write(f"\033[{progress_line};2H{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{bar}{Style.RESET_ALL} {progress}% {Fore.CYAN}║{Style.RESET_ALL}")
            
            # Animation character
            sys.stdout.write(f"\033[{progress_line+2};2H{Fore.CYAN}║{Style.RESET_ALL} {Fore.MAGENTA}{frame}{Style.RESET_ALL}{' ' * 52}{Fore.CYAN}║{Style.RESET_ALL}")
            
            sys.stdout.flush()
            time.sleep(0.01)
        
        # Mark phase as complete
        sys.stdout.write(f"\033[7;2H{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}✓ {phase} complete{' ' * (57 - len(phase) - 10)}{Fore.CYAN}║{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.3)
    
    # Final success message
    sys.stdout.write(f"\033[11;2H{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}SERVER RESTART COMPLETED SUCCESSFULLY!{' ' * 26}{Fore.CYAN}║{Style.RESET_ALL}")
    sys.stdout.write(f"\033[12;2H{Fore.CYAN}║{Style.RESET_ALL} {Fore.CYAN}Now listening on {Fore.WHITE}{host}{Fore.CYAN}:{Fore.WHITE}{port}{' ' * (40 - len(host) - len(str(port)))}{Fore.CYAN}║{Style.RESET_ALL}")
    sys.stdout.flush()
    
    # Restore cursor position
    time.sleep(1.5)
    sys.stdout.write("\033[u")
    sys.stdout.flush()

