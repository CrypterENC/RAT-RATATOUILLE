# Remote Access Tool (RAT)

```
██████╗  █████╗ ████████╗ █████╗ ████████╗ ██████╗ ██╗   ██╗██╗     ██╗     ███████╗
██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗╚══██╔══╝██╔═══██╗██║   ██║██║     ██║     ██╔════╝
██████╔╝███████║   ██║   ███████║   ██║   ██║   ██║██║   ██║██║     ██║     █████╗  
██╔══██╗██╔══██║   ██║   ██╔══██║   ██║   ██║   ██║██║   ██║██║     ██║     ██╔══╝  
██║  ██║██║  ██║   ██║   ██║  ██║   ██║   ╚██████╔╝╚██████╔╝██║███████╗███████╗███████╗
╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚══════╝╚══════╝
```

A simple client-server remote access tool with basic monitoring capabilities.

## Components

This project consists of two main components:

- Python RAT Server: Command and control server
- C++ RAT Client: Client application that connects to the server

## Python RAT Server

### Requirements

- Python 3.6+
- colorama package

### Installation

```bash
pip install -r requirements.txt
```

### Usage

```bash
python python_rat_server.py
```

### Features

- Interactive menu-based interface
- Support for multiple client connections
- Client management (list, select, disconnect)
- System information retrieval
- Screenshot capture
- Server configuration options

### Commands

- `start` - Start the server
- `stop` - Stop the server
- `list` - List all connected clients
- `select <id>` - Select a client to interact with
- `sysinfo` - Get detailed system information from selected client
- `screenshot` - Capture and download screenshot from client
- `exit` - Close connection with selected client
- `clear` - Clear the screen
- `options` - Configure server options
- `quit` - Exit the program

## C++ RAT Client

### Requirements

- Windows operating system
- C++11 compatible compiler (MinGW-w64 or Visual C++)
- Windows Socket API (WinSock2)
- Windows API
- GDI+ (Graphics Device Interface)
- OLE32 (Component Object Model)

### Compilation

```bash
g++ -o rat_client simple_rat_client.cpp -lws2_32 -lgdiplus -lgdi32 -lole32
```

### Configuration

Before running the client, edit the `simple_rat_client.cpp` file to set the server IP address:

```cpp
#define SERVER_IP "127.0.0.1" // Change to your server IP
```

### Features

- Automatic connection and reconnection to server
- System information collection
- Screenshot capability

## Security Notice

This tool is intended for educational purposes and legitimate system administration only. Unauthorized access to computer systems is illegal and unethical. Use responsibly and only on systems you own or have permission to access.

## License

This project is provided for educational purposes only. Use at your own risk.


