import sys
import time
import socket
import colorama # type: ignore
from colorama import Fore, Style # type: ignore

from modules.server_ui_utils import print_banner # type: ignore

def process_command(command):
    """Process a command entered in the command line interface"""
    # This function should handle command processing logic
    # Currently it's a placeholder that needs to be implemented based on your requirements
    print(f"{Fore.CYAN}Processing command: {command}{Style.RESET_ALL}")
    return True

# Update the process_menu_choice function to handle the show_options_panel_wrapper
def process_menu_choice(choice, show_menu_func, start_server_func, stop_server_func, 
                        server_running, list_clients_func, client_sockets, 
                        active_client, client_handler_func, show_options_panel_func,
                        show_client_commands_func, running):
    """Process the user's menu choice"""
    # Handle empty input - just return without showing error message
    if not choice.strip():
        return True, active_client
        
    if choice == "1":
        if not server_running:
            start_server_func()
        else:
            print(f"{Fore.YELLOW}Server is already running.{Style.RESET_ALL}")
            time.sleep(1.5)
    elif choice == "2":
        if server_running:
            stop_server_func()
        else:
            print(f"{Fore.YELLOW}Server is not running.{Style.RESET_ALL}")
            time.sleep(1.5)
    elif choice == "3":
        list_clients_func(client_sockets)
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    elif choice == "4":
        if server_running:
            # Check if there are any connected clients
            if any(client is not None for client in client_sockets):
                list_clients_func(client_sockets)
                client_id = input(f"\n{Fore.YELLOW}Enter client ID to select: {Style.RESET_ALL}")
                try:
                    client_id = int(client_id)
                    if 0 <= client_id < len(client_sockets) and client_sockets[client_id] is not None:
                        active_client = client_id
                        active_client = client_handler_func(active_client, client_sockets, server_running, print_banner)
                    else:
                        print(f"{Fore.RED}Invalid client ID.{Style.RESET_ALL}")
                        time.sleep(1.5)
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Must be a number.{Style.RESET_ALL}")
                    time.sleep(1.5)
            else:
                print(f"{Fore.YELLOW}No clients connected.{Style.RESET_ALL}")
                time.sleep(1.5)
        else:
            print(f"{Fore.YELLOW}⚠ Server is not running. Please start the server first.{Style.RESET_ALL}")
            time.sleep(1.5)
    elif choice == "5":
        show_options_panel_func()
    elif choice == "6":
        # Clear screen is handled by show_menu_func
        pass
    elif choice == "7":
        if server_running:
            # Check if there are any connected clients
            if any(client is not None for client in client_sockets):
                list_clients_func(client_sockets)
                client_id = input(f"\n{Fore.YELLOW}Enter client ID to kill: {Style.RESET_ALL}")
                try:
                    client_id = int(client_id)
                    if 0 <= client_id < len(client_sockets) and client_sockets[client_id] is not None:
                        try:
                            client_sockets[client_id].send("kill".encode())
                            print(f"{Fore.GREEN}Kill command sent to client {client_id}.{Style.RESET_ALL}")
                        except:
                            print(f"{Fore.RED}Failed to send kill command. Client may be disconnected.{Style.RESET_ALL}")
                        time.sleep(1.5)
                    else:
                        print(f"{Fore.RED}Invalid client ID.{Style.RESET_ALL}")
                        time.sleep(1.5)
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Must be a number.{Style.RESET_ALL}")
                    time.sleep(1.5)
            else:
                print(f"{Fore.YELLOW}No clients connected.{Style.RESET_ALL}")
                time.sleep(1.5)
        else:
            print(f"{Fore.YELLOW}Server is not running.{Style.RESET_ALL}")
            time.sleep(1.5)
    elif choice == "8":
        # Show Client Commands
        show_client_commands_func()
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        return True, active_client
    elif choice == "0":
        # Exit the program with confirmation
        confirm = input(f"\n{Fore.YELLOW}Are you sure you want to exit? (y/n): {Style.RESET_ALL}").lower()
        if confirm == 'y' or confirm == 'yes':
            print(f"\n{Fore.GREEN}✓ {Fore.CYAN}Shutting down RAT server and exiting program...{Style.RESET_ALL}\n")
            return False, active_client
        return True, active_client
    else:
        print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
        time.sleep(1.5)
    
    return True, active_client






