import os
import sys
import time
import colorama  # type: ignore
from colorama import Fore, Style  # type: ignore

# Initialize colorama
colorama.init(autoreset=True)

def clear_screen():
    """Clear the terminal screen based on OS"""
    import platform
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_banner(center=False):
    """Print the RAT banner"""

    # Try to determine terminal width
    try:
        terminal_width, _ = os.get_terminal_size()
    except:
        terminal_width = 171  # Default fallback width



    # Use full-size banner always, no responsive selection
    full_banner = f"""
{Fore.RED}██████╗  {Fore.WHITE}█████╗  {Fore.LIGHTBLUE_EX}████████╗ {Fore.RED} █████╗  {Fore.WHITE}████████╗ {Fore.LIGHTBLUE_EX} ██████╗  {Fore.RED}██╗   ██╗ {Fore.WHITE}██╗ {Fore.LIGHTBLUE_EX}██╗     {Fore.RED}██╗        {Fore.WHITE}███████╗{Style.RESET_ALL}
{Fore.RED}██╔══██╗ {Fore.WHITE}██╔══██╗ {Fore.LIGHTBLUE_EX}╚══██╔══╝ {Fore.RED}██╔══██╗ {Fore.WHITE}╚══██╔══╝ {Fore.LIGHTBLUE_EX}██╔═══██╗ {Fore.RED}██║   ██║ {Fore.WHITE}██║ {Fore.LIGHTBLUE_EX}██║     {Fore.RED}██║       {Fore.WHITE}██╔════╝{Style.RESET_ALL}
{Fore.RED}██████╔╝ {Fore.WHITE}███████║ {Fore.LIGHTBLUE_EX}   ██║    {Fore.RED}███████║ {Fore.WHITE}   ██║    {Fore.LIGHTBLUE_EX}██║   ██║ {Fore.RED}██║   ██║ {Fore.WHITE}██║ {Fore.LIGHTBLUE_EX}██║     {Fore.RED}██║       {Fore.WHITE}█████╗  {Style.RESET_ALL}
{Fore.RED}██╔══██╗ {Fore.WHITE}██╔══██║ {Fore.LIGHTBLUE_EX}   ██║    {Fore.RED}██╔══██║ {Fore.WHITE}   ██║    {Fore.LIGHTBLUE_EX}██║   ██║ {Fore.RED}██║   ██║ {Fore.WHITE}██║ {Fore.LIGHTBLUE_EX}██║     {Fore.RED}██║       {Fore.WHITE}██╔══╝  {Style.RESET_ALL}
{Fore.RED}██║  ██║ {Fore.WHITE}██║  ██║ {Fore.LIGHTBLUE_EX}   ██║    {Fore.RED}██║  ██║ {Fore.WHITE}   ██║    {Fore.LIGHTBLUE_EX}╚██████╔╝ {Fore.RED}╚██████╔╝ {Fore.WHITE}██║ {Fore.LIGHTBLUE_EX}███████╗ {Fore.RED}███████╗ {Fore.WHITE}███████╗{Style.RESET_ALL}
{Fore.RED}╚═╝  ╚═╝ {Fore.WHITE}╚═╝  ╚═╝ {Fore.LIGHTBLUE_EX}   ╚═╝    {Fore.RED}╚═╝  ╚═╝ {Fore.WHITE}   ╚═╝    {Fore.LIGHTBLUE_EX}╚═════╝  {Fore.RED} ╚═════╝  {Fore.WHITE}╚═╝ {Fore.LIGHTBLUE_EX}╚══════╝ {Fore.RED}╚══════╝  {Fore.WHITE}╚══════╝{Style.RESET_ALL}
{Fore.CYAN}Remote Access Tool v1.5{Style.RESET_ALL}
{Fore.YELLOW}Created by: CrypterENC{Style.RESET_ALL}
"""
    
    #medium size banner
    medium_banner = f"""
{Fore.RED}██████ {Fore.WHITE}█████  {Fore.LIGHTBLUE_EX}████████ {Fore.RED}█████  {Fore.WHITE}████████ {Fore.LIGHTBLUE_EX}██████  {Fore.RED}██╗ ██ {Fore.WHITE}██ {Fore.LIGHTBLUE_EX}██╗   {Fore.RED}██╗   {Fore.WHITE}███████{Style.RESET_ALL}
{Fore.RED}██╔══█ {Fore.WHITE}██╔══█ {Fore.LIGHTBLUE_EX}╚══██╔═  {Fore.RED}██╔══█ {Fore.WHITE}╚══██╔═  {Fore.LIGHTBLUE_EX}██╔═══█ {Fore.RED}██║ ██ {Fore.WHITE}██ {Fore.LIGHTBLUE_EX}██║   {Fore.RED}██║   {Fore.WHITE}██╔════{Style.RESET_ALL}
{Fore.RED}█████╔ {Fore.WHITE}██████ {Fore.LIGHTBLUE_EX}   ██║   {Fore.RED}█████╔ {Fore.WHITE}   ██║   {Fore.LIGHTBLUE_EX}██║   █ {Fore.RED}██║ ██ {Fore.WHITE}██ {Fore.LIGHTBLUE_EX}██║   {Fore.RED}██║   {Fore.WHITE}█████╗ {Style.RESET_ALL}
{Fore.RED}██╔══█ {Fore.WHITE}██╔══█ {Fore.LIGHTBLUE_EX}   ██║   {Fore.RED}██╔══█ {Fore.WHITE}   ██║   {Fore.LIGHTBLUE_EX}██║   █ {Fore.RED}██║ ██ {Fore.WHITE}██ {Fore.LIGHTBLUE_EX}██║   {Fore.RED}██║   {Fore.WHITE}██╔══╝ {Style.RESET_ALL}
{Fore.RED}██║  █ {Fore.WHITE}██║  █ {Fore.LIGHTBLUE_EX}   ██║   {Fore.RED}██║  █ {Fore.WHITE}   ██║   {Fore.LIGHTBLUE_EX}╚█████╔ {Fore.RED}╚████╔ {Fore.WHITE}██ {Fore.LIGHTBLUE_EX}█████ {Fore.RED}█████ {Fore.WHITE}███████{Style.RESET_ALL}
{Fore.RED}╚═╝  ╚ {Fore.WHITE}╚═╝  ╚ {Fore.LIGHTBLUE_EX}   ╚═╝   {Fore.RED}╚═╝  ╚ {Fore.WHITE}   ╚═╝   {Fore.LIGHTBLUE_EX}╚════╝  {Fore.RED}╚═══╝  {Fore.WHITE}╚═ {Fore.LIGHTBLUE_EX}╚════ {Fore.RED}╚════ {Fore.WHITE}╚══════{Style.RESET_ALL}
{Fore.CYAN}Remote Access Tool v1.5{Style.RESET_ALL}
{Fore.YELLOW}Created by: CrypterENC{Style.RESET_ALL}
"""


    # Create a more compact banner that will fit in most terminal widths
    compact_banner = f"""
{Fore.RED}██████╗ {Fore.WHITE}█████╗ {Fore.LIGHTBLUE_EX}████████╗{Fore.RED}█████╗ {Fore.WHITE}████████╗{Fore.LIGHTBLUE_EX}██████╗ {Fore.RED}██╗   ██╗{Fore.WHITE}██╗{Fore.LIGHTBLUE_EX}██╗       {Fore.RED}██╗      {Fore.WHITE}███████╗{Style.RESET_ALL}
{Fore.RED}██╔══██╗{Fore.WHITE}██╔══██╗{Fore.LIGHTBLUE_EX}╚══██╔══╝{Fore.RED}██╔══██╗{Fore.WHITE}╚══██╔══╝{Fore.LIGHTBLUE_EX}██╔═══██╗{Fore.RED}██║   ██║{Fore.WHITE}██║{Fore.LIGHTBLUE_EX}██║    {Fore.RED}██║      {Fore.WHITE}██╔════╝{Style.RESET_ALL}
{Fore.RED}██████╔╝{Fore.WHITE}███████║{Fore.LIGHTBLUE_EX}   ██║   {Fore.RED}███████║{Fore.WHITE}   ██║   {Fore.LIGHTBLUE_EX}██║   ██║{Fore.RED}██║   ██║{Fore.WHITE}██║{Fore.LIGHTBLUE_EX}██║    {Fore.RED}██║      {Fore.WHITE}█████╗  {Style.RESET_ALL}
{Fore.RED}██╔══██╗{Fore.WHITE}██╔══██║{Fore.LIGHTBLUE_EX}   ██║   {Fore.RED}██╔══██║{Fore.WHITE}   ██║   {Fore.LIGHTBLUE_EX}██║   ██║{Fore.RED}██║   ██║{Fore.WHITE}██║{Fore.LIGHTBLUE_EX}██║    {Fore.RED}██║      {Fore.WHITE}██╔══╝  {Style.RESET_ALL}
{Fore.RED}██║  ██║{Fore.WHITE}██║  ██║{Fore.LIGHTBLUE_EX}   ██║   {Fore.RED}██║  ██║{Fore.WHITE}   ██║   {Fore.LIGHTBLUE_EX}╚██████╔╝{Fore.RED}╚██████╔╝{Fore.WHITE}██║{Fore.LIGHTBLUE_EX}███████╗{Fore.RED}███████╗{Fore.WHITE}███████╗{Style.RESET_ALL}
{Fore.RED}╚═╝  ╚═╝{Fore.WHITE}╚═╝  ╚═╝{Fore.LIGHTBLUE_EX}   ╚═╝   {Fore.RED}╚═╝  ╚═╝{Fore.WHITE}   ╚═╝   {Fore.LIGHTBLUE_EX}╚═════╝ {Fore.RED} ╚═════╝ {Fore.WHITE}╚═╝{Fore.LIGHTBLUE_EX}╚══════╝{Fore.RED}╚══════╝ {Fore.WHITE}╚══════╝{Style.RESET_ALL}
{Fore.CYAN}Remote Access Tool v1.5{Style.RESET_ALL}
{Fore.YELLOW}Created by: CrypterENC{Style.RESET_ALL}
"""
    
    # Create a more compact banner that will fit in most terminal widths
    small_banner = f"""
{Fore.RED}R{Fore.WHITE}A{Fore.LIGHTBLUE_EX}T{Fore.RED}A{Fore.WHITE}T{Fore.LIGHTBLUE_EX}O{Fore.RED}U{Fore.WHITE}I{Fore.LIGHTBLUE_EX}L{Fore.RED}L{Fore.WHITE}E{Style.RESET_ALL}

{Fore.CYAN}Remote Access Tool v1.5{Style.RESET_ALL}
{Fore.YELLOW}Created by: CrypterENC{Style.RESET_ALL}
"""
    
    
    
    # Select banner based on terminal width
    if terminal_width >= 171:  # No changes for 171x45
        selected_banner = full_banner
    elif terminal_width >= 120:
        selected_banner = full_banner
    elif terminal_width >= 80:
        selected_banner = medium_banner
    else:
        selected_banner = small_banner
    
    # Print the selected banner
    if center and terminal_width < 171:
        # Center the banner for smaller terminals
        lines = selected_banner.split('\n')
        for line in lines:
            if line.strip():
                padding = max(0, (terminal_width - len(line.strip())) // 2)
                print(' ' * padding + line)
            else:
                print(line)
    else:
        print(selected_banner)

def print_prompt():
    """Print the command prompt"""
    sys.stdout.write(f"{Fore.GREEN}RAT> {Style.RESET_ALL}")
    sys.stdout.flush()

def show_main_menu(server_running, host, port, client_sockets, max_clients, active_client=-1):
    """Display the main menu options in columns"""
    clear_screen()
    print_banner()
    
    # Center the main title with 15px left offset (7 + 8)
    menu_width = 60
    title = "=== MAIN MENU ==="
    padding1 = (menu_width - len(title)) // 2 - 21  # Subtract 15 to move left
    padding1 = max(0, padding1)  # Ensure padding doesn't go negative
    padding2 = (menu_width - len(title)) // 2 - 23  # Subtract 15 to move left
    padding2 = max(0, padding2)  # Ensure padding doesn't go negative
    padding3 = (menu_width - len(title)) // 2 - 22  # Subtract 15 to move left
    padding3 = max(0, padding3)  # Ensure padding doesn't go negative
    print(f"\n{' ' * padding1}{Fore.CYAN}{title}{Style.RESET_ALL}\n")  # Added extra newline for more space
    
    # Menu items organized in columns (4 items per column)
    col1 = [("1", "Start Server"), ("2", "Stop Server"), ("3", "List Clients"), ("4", "Select Client")]
    col2 = [("5", "Server Options"), ("6", "Clear Screen"), ("7", "Kill Client"), ("8", "Show Client Commands")]
    col3 = [("0", "Exit"), ("", "")]
    
    # Column widths for proper alignment
    col1_width = 20  # Width for column 1 items
    col2_width = 25  # Increased from 20 to 25 for more space
    col3_width = 20  # Width for column 3 items
    
    # Print menu items in rows with fixed column widths
    for i in range(4):  # 4 rows
        line = ""
        
        # Add item from column 1 with fixed width (if available)
        if i < len(col1):
            num, text = col1[i]
            line += f"{Fore.YELLOW}{num}.{Style.RESET_ALL} {text}"
            line += " " * (col1_width - len(text) - 3)  # Padding (3 = number + dot + space)
        else:
            line += " " * col1_width  # Empty column
        
        # Add item from column 2 with fixed width (if available)
        if i < len(col2):
            num, text = col2[i]
            line += f"{Fore.YELLOW}{num}.{Style.RESET_ALL} {text}"
            line += " " * (col2_width - len(text) - 3)  # Padding
        else:
            line += " " * col2_width  # Empty column
        
        # Add item from column 3 (if available and has a number)
        if i < len(col3) and col3[i][0]:
            num, text = col3[i]
            line += f"{Fore.YELLOW}{num}.{Style.RESET_ALL} {text}"
        
        print(line.rstrip())
    
    # Display server status with extra spacing before and after the section
    print(f"\n{' ' * padding2}{Fore.CYAN}=== SERVER STATUS ==={Style.RESET_ALL}")
    print()  # Add one blank line under the SERVER STATUS title
    if server_running:
        client_count = sum(1 for client in client_sockets if client is not None)
        print(f"{Fore.GREEN}● Server Running On {Fore.CYAN}{host}{Fore.WHITE}:{Fore.YELLOW}{port}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}● Connected Clients: {Fore.CYAN}{client_count}{Fore.WHITE}/{Fore.YELLOW}{max_clients} {Fore.LIGHTBLUE_EX}({(client_count/max_clients)*100:.1f}% capacity){Style.RESET_ALL}")
        if active_client >= 0:
            print(f"{Fore.GREEN}● Active Client: {active_client}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}● Server Stopped{Style.RESET_ALL}")
    
    print(f"\n{' ' * padding3}{Fore.CYAN}=== OUTPUT ==={Style.RESET_ALL}")

def show_options_panel(port, host, buffer_size, max_clients, client_sockets, handle_client_disconnect):
    """Display and modify server options"""
    restart_needed = False
    original_host = host
    original_port = port
    
    while True:
        clear_screen()
        print_banner()
        
        print(f"{Fore.CYAN}=== OPTIONS ==={Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Port: {Fore.CYAN}{port}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Host: {Fore.CYAN}{host}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Buffer Size: {Fore.CYAN}{buffer_size}{Style.RESET_ALL} bytes")
        print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Max Clients: {Fore.CYAN}{max_clients}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}5.{Style.RESET_ALL} {Fore.GREEN}Back to Main Menu{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.YELLOW}Enter option number {Fore.LIGHTBLUE_EX}[1-5]{Fore.YELLOW}: {Style.RESET_ALL}")
        
        # Process option choice
        if choice == "1":
            clear_screen()
            print_banner()
            print(f"{Fore.CYAN}=== OPTIONS ==={Style.RESET_ALL}\n")
            new_port_input = input(f"{Fore.YELLOW}Enter new port ({Fore.CYAN}1-65535{Fore.YELLOW}) [current: {Fore.GREEN}{port}{Fore.YELLOW}]: {Style.RESET_ALL}")
            if new_port_input.strip():
                try:
                    new_port = int(new_port_input)
                    if 1 <= new_port <= 65535:
                        if new_port != port:
                            port = new_port
                            restart_needed = True
                            print(f"{Fore.GREEN}Port updated to {port}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Invalid port number{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Must be a number{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Port unchanged{Style.RESET_ALL}")
            time.sleep(1)  # Brief pause to show the message
            
        elif choice == "2":
            clear_screen()
            print_banner()
            print(f"{Fore.CYAN}=== OPTIONS ==={Style.RESET_ALL}\n")
            new_host = input(f"{Fore.YELLOW}Enter new host IP (current: {Fore.GREEN}{host}{Fore.YELLOW}): {Style.RESET_ALL}")
            if new_host.strip():
                # Simple validation for IP format
                if all(part.isdigit() and 0 <= int(part) <= 255 for part in new_host.split('.')) and len(new_host.split('.')) == 4:
                    if new_host != host:
                        host = new_host
                        restart_needed = True
                        print(f"{Fore.GREEN}Host updated to {host}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Invalid IP address format{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Host unchanged{Style.RESET_ALL}")
            time.sleep(1)  # Brief pause to show the message
                
        elif choice == "3":
            clear_screen()
            print_banner()
            print(f"{Fore.CYAN}=== OPTIONS ==={Style.RESET_ALL}\n")
            try:
                new_buffer = int(input(f"{Fore.YELLOW}Enter new buffer size in bytes ({Fore.CYAN}1024-65536{Fore.YELLOW}) [current: {Fore.GREEN}{buffer_size}{Fore.YELLOW}]: {Style.RESET_ALL}"))
                if 1024 <= new_buffer <= 65536:
                    buffer_size = new_buffer
                    print(f"{Fore.GREEN}Buffer size updated to {buffer_size} bytes{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Invalid buffer size. Must be between 1024 and 65536 bytes{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Must be a number{Style.RESET_ALL}")
            time.sleep(1)  # Brief pause to show the message
                
        elif choice == "4":
            clear_screen()
            print_banner()
            print(f"{Fore.CYAN}=== OPTIONS ==={Style.RESET_ALL}\n")
            try:
                new_max = int(input(f"{Fore.YELLOW}Enter new maximum clients ({Fore.CYAN}1-100{Fore.YELLOW}) [current: {Fore.GREEN}{max_clients}{Fore.YELLOW}]: {Style.RESET_ALL}"))
                if 1 <= new_max <= 100:
                    # Check if we need to resize the client_sockets list
                    if new_max != max_clients:
                        if new_max < max_clients:
                            # Check if we're removing slots that have active clients
                            for i in range(new_max, max_clients):
                                if client_sockets[i] is not None:
                                    # Disconnect client
                                    try:
                                        client_sockets[i].send("server_shutdown".encode())
                                        client_sockets[i].close()
                                    except:
                                        pass
                                    handle_client_disconnect(i, client_sockets, -1)
                            # Resize the list
                            client_sockets = client_sockets[:new_max]
                        else:
                            # Expand the list
                            client_sockets.extend([None] * (new_max - max_clients))
                        
                        max_clients = new_max
                        print(f"{Fore.GREEN}Maximum clients updated to {max_clients}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Maximum clients unchanged{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Invalid number. Must be between 1 and 100{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Must be a number{Style.RESET_ALL}")
            time.sleep(1)  # Brief pause to show the message
        
        elif choice == "5":
            if restart_needed:
                print(f"{Fore.YELLOW}Changes detected! Restarting the server...{Style.RESET_ALL}")
                # Add your server restart logic here
                # For example, you can call a function to restart the server
                # restart_server()
                # Then, you can return the updated values
                return port, host, buffer_size, max_clients, restart_needed
            else:
                return port, host, buffer_size, max_clients, restart_needed
        else:
            print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and 5.{Style.RESET_ALL}")
            time.sleep(1)  # Brief pause to show the error message


    """Display the current terminal size"""
    clear_screen()
    print_banner()
    
    try:
        width, height = os.get_terminal_size()
        print(f"\n{Fore.CYAN}=== TERMINAL SIZE ==={Style.RESET_ALL}\n")
        print(f"{Fore.GREEN}Width: {Fore.YELLOW}{width} characters{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Height: {Fore.YELLOW}{height} lines{Style.RESET_ALL}")
        
        # Display a visual representation of the terminal size
        print(f"\n{Fore.CYAN}=== VISUAL REPRESENTATION ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Top-left corner{' ' * (width - 26)}Top-right corner{Style.RESET_ALL}")
        
        # Print middle rows with just the sides
        for i in range(min(10, height - 4)):  # Limit to 10 rows for large terminals
            if i == min(5, (height - 4) // 2):
                mid_text = f"{Fore.GREEN}Terminal size: {width}x{height}{Style.RESET_ALL}"
                left_space = (width - len(mid_text) - 12) // 2
                print(f"{Fore.YELLOW}|{' ' * left_space}{mid_text}{' ' * (width - left_space - len(mid_text) - 2)}{Fore.YELLOW}|{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}|{' ' * (width - 2)}|{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}Bottom-left corner{' ' * (width - 32)}Bottom-right corner{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
        input()
    except Exception as e:
        print(f"{Fore.RED}Error getting terminal size: {e}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
        input()



