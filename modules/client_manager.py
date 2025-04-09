import sys
from colorama import Fore, Style  # type: ignore

def list_clients(client_sockets):
    """List all connected clients in a table format"""
    count = 0
    print(f"\n{Fore.CYAN}Connected clients:{Style.RESET_ALL}")
    
    # Table header
    print(f"┌───────┬─────────────────────────────────┐")
    print(f"│ {Fore.CYAN}ID{Style.RESET_ALL}    │ {Fore.CYAN}Client Address{Style.RESET_ALL}                  │")
    print(f"├───────┼─────────────────────────────────┤")
    
    for i, client in enumerate(client_sockets):
        if client:
            try:
                addr = client.getpeername()
                addr_str = f"{addr[0]}:{addr[1]}"
                print(f"│ {Fore.YELLOW}[{i}]{Style.RESET_ALL}   │ {Fore.WHITE}{addr_str}{' ' * (29 - len(addr_str))}   │")
                count += 1
            except:
                # Handle case where socket might be in an invalid state
                print(f"│ {Fore.YELLOW}[{i}]{Style.RESET_ALL}   │ {Fore.RED}Connection error{' ' * 14}{Style.RESET_ALL}   │")
                count += 1
    
    # Table footer
    print(f"└───────┴─────────────────────────────────┘")
    
    if count == 0:
        print(f"{Fore.RED}No clients connected{Style.RESET_ALL}")
    
    return count

