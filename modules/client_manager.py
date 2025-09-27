import sys
from colorama import Fore, Style  # type: ignore

def list_clients(client_sockets, client_info=None):
    """List all connected clients in a table format with public IP addresses"""
    count = 0
    print(f"\n{Fore.CYAN}Connected clients:{Style.RESET_ALL}")
    
    # Table header - wider to accommodate public IPs
    print(f"┌───────┬─────────────────────────────────────────────┐")
    print(f"│ {Fore.CYAN}ID{Style.RESET_ALL}    │ {Fore.CYAN}Client Address (Public IP){Style.RESET_ALL}              │")
    print(f"├───────┼─────────────────────────────────────────────┤")
    
    for i, client in enumerate(client_sockets):
        if client:
            try:
                # Use stored client info if available, otherwise fallback to getpeername
                if client_info and client_info[i]:
                    public_ip = client_info[i]['public_ip']
                    status = client_info[i].get('ip_detection_status', 'unknown')
                    
                    if status == 'completed' and public_ip != client_info[i]['connection_ip']:
                        # Successfully detected different public IP
                        addr_str = f"{public_ip} (Public)"
                    elif status == 'pending':
                        # Still detecting
                        addr_str = f"{public_ip} (Detecting...)"
                    elif status == 'failed':
                        # Detection failed, show connection IP
                        addr_str = f"{public_ip} (Direct)"
                    else:
                        # Default case
                        addr_str = f"{public_ip} (Public)"
                    
                    if len(addr_str) > 37:
                        addr_str = addr_str[:34] + "..."
                else:
                    # Fallback to connection IP
                    addr = client.getpeername()
                    addr_str = f"{addr[0]}:{addr[1]} (Direct)"
                
                padding = 37 - len(addr_str)
                print(f"│ {Fore.YELLOW}[{i}]{Style.RESET_ALL}   │ {Fore.WHITE}{addr_str}{' ' * padding}   │")
                count += 1
            except:
                # Handle case where socket might be in an invalid state
                print(f"│ {Fore.YELLOW}[{i}]{Style.RESET_ALL}   │ {Fore.RED}Connection error{' ' * 22}{Style.RESET_ALL}   │")
                count += 1
    
    # Table footer
    print(f"└───────┴─────────────────────────────────────────────┘")
    
    if count == 0:
        print(f"{Fore.RED}No clients connected{Style.RESET_ALL}")
    
    return count

