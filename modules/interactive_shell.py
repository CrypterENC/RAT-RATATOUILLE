import sys
import time
import socket
import select
import threading
import colorama # type: ignore
from colorama import Fore, Style, Back # type: ignore

def interactive_shell_session(client_socket, buffer_size=1024):
    """
    Start an interactive shell session with the client.
    This function handles the bidirectional communication between the server and client shell.
    
    Args:
        client_socket: The socket connected to the client
        buffer_size: Size of the buffer for receiving data
    
    Returns:
        bool: True if shell session ended normally, False if there was an error
    """
    print(f"{Fore.YELLOW}[*] Starting interactive shell session...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[*] Type 'exit_shell' to return to command mode{Style.RESET_ALL}")
    
    # Send shell command to client
    try:
        client_socket.send("shell".encode())
    except Exception as e:
        print(f"{Fore.RED}[!] Failed to send shell command: {str(e)}{Style.RESET_ALL}")
        return False
    
    # Wait for acknowledgment
    try:
        client_socket.settimeout(5.0)
        initial_response = client_socket.recv(buffer_size).decode('utf-8', errors='replace')
        client_socket.settimeout(None)
        
        if "Starting interactive shell" not in initial_response:
            print(f"{Fore.RED}[!] Failed to start shell session: {initial_response}{Style.RESET_ALL}")
            return False
            
        print(f"{Fore.GREEN}[+] {initial_response}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error receiving shell acknowledgment: {str(e)}{Style.RESET_ALL}")
        client_socket.settimeout(None)
        return False
    
    # Wait for shell start marker
    shell_started = False
    start_time = time.time()
    timeout = 10.0  # 10 seconds timeout
    
    while not shell_started and (time.time() - start_time) < timeout:
        try:
            client_socket.settimeout(1.0)
            data = client_socket.recv(buffer_size).decode('utf-8', errors='replace')
            client_socket.settimeout(None)
            
            if data:
                if "##SHELL_SESSION_STARTED##" in data:
                    shell_started = True
                    # Remove the marker and print any remaining data
                    data = data.replace("##SHELL_SESSION_STARTED##", "")
                    if data.strip():
                        print(data, end='')
                else:
                    print(data, end='')
        except socket.timeout:
            continue
        except Exception as e:
            print(f"{Fore.RED}[!] Error during shell initialization: {str(e)}{Style.RESET_ALL}")
            client_socket.settimeout(None)
            return False
    
    if not shell_started:
        print(f"{Fore.RED}[!] Timeout waiting for shell session to start{Style.RESET_ALL}")
        client_socket.settimeout(None)
        return False
    
    # Set socket to non-blocking mode for interactive use
    client_socket.setblocking(False)
    
    # Create a thread to read from the socket and print to console
    stop_thread = threading.Event()
    
    def receive_output():
        """Thread function to receive and display shell output"""
        while not stop_thread.is_set():
            try:
                # Use select to check if there's data to read without blocking
                readable, _, _ = select.select([client_socket], [], [], 0.1)
                
                if client_socket in readable:
                    data = client_socket.recv(buffer_size).decode('utf-8', errors='replace')
                    
                    if not data:  # Connection closed
                        print(f"{Fore.RED}[!] Connection closed by client{Style.RESET_ALL}")
                        stop_thread.set()
                        break
                        
                    # Check for shell end marker
                    if "##SHELL_SESSION_ENDED##" in data:
                        data = data.replace("##SHELL_SESSION_ENDED##", "")
                        if data.strip():
                            print(data, end='')
                        print(f"{Fore.YELLOW}[*] Shell session ended by remote host{Style.RESET_ALL}")
                        stop_thread.set()
                        break
                        
                    # Print received data
                    print(data, end='')
                    sys.stdout.flush()
                    
            except Exception as e:
                if not stop_thread.is_set():  # Only print error if we're not already stopping
                    print(f"{Fore.RED}[!] Error receiving shell output: {str(e)}{Style.RESET_ALL}")
                    stop_thread.set()
                break
    
    # Start the receiver thread
    receiver_thread = threading.Thread(target=receive_output)
    receiver_thread.daemon = True
    receiver_thread.start()
    
    # Main loop for sending commands
    try:
        while not stop_thread.is_set():
            try:
                # Use select to check if stdin has data without blocking
                readable, _, _ = select.select([sys.stdin], [], [], 0.1)
                
                if sys.stdin in readable:
                    command = input()
                    
                    # Check for exit command
                    if command.strip().lower() == "exit_shell":
                        print(f"{Fore.YELLOW}[*] Exiting shell session...{Style.RESET_ALL}")
                        client_socket.send("exit_shell".encode())
                        # Wait for confirmation of exit
                        time.sleep(1.0)
                        stop_thread.set()
                        break
                        
                    # Send command to client
                    client_socket.send(command.encode())
            except KeyboardInterrupt:
                print(f"{Fore.YELLOW}[*] Shell session terminated by user{Style.RESET_ALL}")
                client_socket.send("exit_shell".encode())
                time.sleep(1.0)
                stop_thread.set()
                break
                
    except Exception as e:
        print(f"{Fore.RED}[!] Error in shell session: {str(e)}{Style.RESET_ALL}")
    finally:
        # Clean up
        stop_thread.set()
        receiver_thread.join(timeout=2.0)
        client_socket.setblocking(True)
        
        # Wait for shell end marker if not already received
        try:
            client_socket.settimeout(3.0)
            while True:
                data = client_socket.recv(buffer_size).decode('utf-8', errors='replace')
                if not data or "##SHELL_SESSION_ENDED##" in data:
                    break
                print(data, end='')
        except:
            pass
        finally:
            client_socket.settimeout(None)
    
    print(f"{Fore.GREEN}[+] Interactive shell session completed{Style.RESET_ALL}")
    return True
