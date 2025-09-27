# RAT_RATATOUILLE - Remote Access Tool

```
██████╗  █████╗ ████████╗ █████╗ ████████╗ ██████╗ ██╗   ██╗██╗     ██╗     ███████╗
██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗╚══██╔══╝██╔═══██╗██║   ██║██║     ██║     ██╔════╝
██████╔╝███████║   ██║   ███████║   ██║   ██║   ██║██║   ██║██║     ██║     █████╗
██╔══██╗██╔══██║   ██║   ██╔══██║   ██║   ██║   ██║██║   ██║██║     ██║     ██╔══╝
██║  ██║██║  ██║   ██║   ██║  ██║   ██║   ╚██████╔╝╚██████╔╝██║███████╗███████╗███████╗
╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚══════╝╚══════╝
```

A comprehensive client-server remote access tool with advanced monitoring and control capabilities.

## 🚀 Project Overview

RAT_RATATOUILLE is a sophisticated remote access tool designed for educational purposes and legitimate system administration. It provides a robust client-server architecture with advanced monitoring and control capabilities, allowing administrators to remotely manage systems securely and efficiently.

The project emphasizes:

- **Modularity**: Separate components that work together seamlessly
- **Flexibility**: Customizable configurations for various deployment scenarios
- **Usability**: Intuitive interfaces for both server and client components
- **Scalability**: Designed to handle multiple client connections efficiently

## 🧩 Project Components

RAT_RATATOUILLE v1.6 consists of four main components:

1. **Python RAT Server**: Command and control server with real-time monitoring dashboard
2. **C++ RAT Client v1.6**: Advanced client with screen sharing, interactive shell, and polymorphic features
3. **RAT Client Generator**: Tool to create customized client executables with polymorphic code generation
4. **RAT Client Binder v1.6**: Tool to bind the client with legitimate applications for seamless deployment

## 📋 Quick Start Guide

### Server Setup

1. ` Run .\install_depen.bat ` - Sets up the complete development environment
2. ` Run .\setup_and_run.bat ` - Configures and launches the server

### Client Deployment

1. ` Run .\RAT_Client_Generator\rat_client_generator.py ` - Creates customized client executable
2. ` Run .\RAT_Client_Binder\binder.py ` - Optionally binds client with legitimate application

## 💻 Installation

### Automatic Installation (Windows)

For a complete development environment setup, run the provided setup script:

```bash
install_depen.bat
```

This script will:

1. Install Python 3.12.9 with required configurations
2. Install MSYS2 with MinGW-w64 toolchain for C++ compilation
3. Configure system environment variables for both Python and MSYS2
4. Install required Python packages (colorama, pyinstaller, cx_Freeze, py2exe, requests)
5. Create verification instructions and backup installers on your desktop

The setup script features:

- Administrator privilege verification
- Colorful, informative progress indicators
- Automatic download of all required components
- Verification of successful installations
- Detailed error reporting

> **Note:** You must run the script as Administrator by right-clicking and selecting "Run as administrator"

### Quick Start (For Pre-configured Environments)

If you already have Python and the required dependencies installed, you can use the simplified setup script:

```bash
setup_and_run.bat
```

**Features:**

- Creates a Python virtual environment
- Updates pip to the latest version
- Installs required packages from requirements.txt
- Launches the RAT server automatically in a new window

### Post-Installation Steps

After running the setup scripts, complete these additional steps:

1. **Disable Python App Execution Aliases**

   - Open Windows Settings (Win+I)
   - Search for "Manage App Execution Aliases"
   - Turn OFF App Installer for both python.exe and python3.exe

2. **Configure Windows Defender Exclusions (Optional)**

   - Add the project directory to Windows Defender exclusions
   - This prevents false positives during development

3. **Restart Your Computer**

   - Ensures all PATH changes take effect
   - Completes the environment configuration

## ✅ Verification

Verify your installation with these steps:

1. **Check Python Installation**

   ```bash
   python --version
   ```

   Expected output: `Python 3.x.x` (3.6 or higher)

2. **Check G++ Installation**

   ```bash
   g++ --version
   ```

   Expected output: Version information for G++ compiler

3. **Verify Python Packages**

   ```bash
   pip list
   ```

   Confirm that colorama and other required packages are installed

4. **Test Server Launch**
   ```bash
   cd RAT_RATATOUILLE
   python rat_server.py
   ```
   The server should start with the colorful banner and menu

## 🖥️ About the Python RAT Server and Client

### Server Features

- **Interactive Interface**: Colorful, menu-driven command console
- **Multi-client Support**: Manage multiple client connections simultaneously
- **Real-time Monitoring**: View client status with visual indicators
- **Secure Communication**: Encrypted data transmission
- **Comprehensive Logging**: Record all activities for audit purposes
- **Customizable Configuration**: Adjust server settings through options menu

### Client Features (v1.6)

- **Persistent Connection**: Automatic reconnection if connection is lost
- **Interactive Shell**: Real-time command shell access with full terminal emulation
- **Screen Sharing**: Live screen monitoring at 10 FPS with JPEG compression
- **Enhanced File Transfer**: Reliable bidirectional file transfer with progress tracking
  * Clean and consistent progress box UI
  * Desktop-aware file placement with fallback
  * Automatic directory creation
  * Efficient socket buffer management
- **System Information Collection**: Hardware, software, and network details
- **Process Management**: List, search, and terminate processes
- **Screenshot Capability**: Capture screen content remotely
- **Keystroke Sending**: Send keystrokes to applications
- **Application Control**: Launch and interact with applications
- **System Logs Access**: Retrieve various system event logs
- **Polymorphic Code**: Unique builds with randomized functions and encryption
- **XOR Encryption**: Obfuscated strings and network traffic

## ⚙️ Server Configuration

The RAT server can be configured through multiple methods:

### Command-line Arguments

```bash
python rat_server.py -i 192.168.1.100 -p 8888 -b 1024 -m 10
```

Available options:

- `-i, --ip`: IP address to bind to (default: 0.0.0.0)
- `-p, --port`: Port to listen on (default: 8888)
- `-b, --buffer`: Buffer size for data transmission (default: 1024)
- `-m, --max-clients`: Maximum number of clients (default: 10)

### Configuration File

The server saves settings to `server_config.json` which is loaded on startup:

```json
{
  "server": {
    "ip": "0.0.0.0",
    "port": 8888,
    "buffer_size": 1024,
    "max_clients": 10
  },
  "ui": {
    "refresh_rate": 1,
    "show_notifications": true
  }
}
```

### Options Menu

Select `options` from the main menu to change settings interactively:

- Server IP and port
- Buffer size
- Maximum clients
- UI refresh rate
- Notification settings
> **Important**: After changing settings in the options menu, you must stop and restart the server for changes to take effect.

## 🔍 RAT Server Commands

### Server Control Commands

| Command       | Description                      |
| ------------- | -------------------------------- |
| `start`       | Start the server                 |
| `stop`        | Stop the server                  |
| `list`        | List all connected clients       |
| `select <id>` | Select a client to interact with |
| `clear`       | Clear the screen                 |
| `options`     | Configure server options         |
| `help`        | Display help information         |
| `quit`        | Exit the program                 |

### File Transfer Commands

| Command | Description | Features |
| ------- | ----------- | -------- |
| `upload_file <local_path>` | Upload file from server to client | • Visual progress tracking<br>• Desktop-aware placement<br>• Automatic directory creation<br>• Fallback to current directory |
| `download_file <remote_path>` | Download file from client to server | • Visual progress tracking<br>• Automatic downloads folder<br>• Progress percentage display<br>• Clean box UI |

### Client Mode Commands

#### Navigation Commands

| Command | Description                                          |
| ------- | ---------------------------------------------------- |
| `back`  | Return to main menu                                  |
| `help`  | Show help message                                    |
| `kill`  | Kill the client connection                           |
| `exit`  | Disconnect client (client will attempt to reconnect) |

#### Information Commands

| Command                      | Description                                           |
| ---------------------------- | ----------------------------------------------------- |
| `sysinfo`                    | Get detailed system information                       |
| `netinfo`                    | Get detailed network information                      |
| `installed_software`         | List installed software                               |
| `system_logs`                | Get system event logs (default: System logs)          |
| `system_logs <type>`         | Get specific log type (System, Application, Security) |
| `system_logs <type> <count>` | Get specific number of log entries                    |

#### Process Management Commands

| Command                   | Description                           |
| ------------------------- | ------------------------------------- |
| `list_processes`          | List all running processes            |
| `search_process [name]`   | Search for a specific process by name |
| `terminate_process <pid>` | Terminate a process by PID            |

#### Action Commands

| Command                           | Description                              |
| --------------------------------- | ---------------------------------------- |
| `screenshot`                      | Take a screenshot of the client's screen |
| `shell`                           | Start an interactive shell session       |
| `start_screen_share`              | Begin real-time screen sharing (10 FPS)  |
| `stop_screen_share`               | Stop the active screen sharing session   |
| `launch_app [name]`               | Launch an application on the client      |
| `send_keys <process_name> <keys>` | Send keys to a process by name           |
| `type <keys>`                     | Send keystrokes to the active window     |

## 🛡️ Advanced Security Features (v1.6)

Version 1.6 introduces several advanced security and evasion features:

### Polymorphic Code Generation

Each build of the RAT client is unique, making detection more difficult:

- **Function Name Randomization**: All internal function names are randomized
- **Variable Name Randomization**: Key variables receive unique names per build
- **Code Flow Variation**: Execution paths vary between builds
- **Build Signatures**: Each build has a unique identifier for tracking

### Encryption and Obfuscation

- **XOR Encryption**: All sensitive strings and network traffic are XOR-encrypted
- **Encryption Key Rotation**: Each build uses a different XOR key
- **Sleep Timing Randomization**: Avoids detection by timing-based analysis
- **Persistence Name Randomization**: Registry entries use different names per build

### Static Linking Improvements

- **No External Dependencies**: All required libraries are statically linked
- **Reduced Detection Surface**: No suspicious DLL loading operations
- **Improved Portability**: Works on systems without additional runtimes

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Server Won't Start

- **Issue**: Server fails to start or crashes immediately
- **Solution**:
  - Check if the port is already in use
  - Verify you have administrator privileges
  - Ensure Python and required packages are installed correctly

#### Client Can't Connect to Server

- **Issue**: Client executable runs but doesn't connect to server
- **Solution**:
  - Verify server is running and listening on the correct IP and port
  - Check firewall settings on both server and client machines
  - Ensure client is configured with the correct server IP and port

#### Compilation Errors

- **Issue**: Client generator fails to compile the client
- **Solution**:
  - Ensure MinGW-w64 is properly installed and in your PATH
  - Check that all required libraries are available
  - Try running the compilation command manually to see detailed errors

#### Configuration Changes Not Taking Effect

- **Issue**: Changes to server settings don't seem to work
- **Solution**:
  - After changing settings in the options menu, you must stop and restart the server
  - Verify changes were saved to `server_config.json`
  - Check for syntax errors in the configuration file

#### Pip Update Notices

- **Issue**: You see notices about pip being outdated
- **Solution**:
  - The setup scripts automatically update pip to the latest version
  - If you still see update notices, manually run: `python -m pip install --upgrade pip`

## ⚠️ Security Notice

This tool is intended for **educational purposes** and **legitimate system administration only**. Unauthorized access to computer systems is illegal and unethical.

### Legal Considerations

- Only use this tool on systems you own or have explicit permission to access
- Obtain written consent before installing on any system
- Comply with all applicable laws and regulations
- Maintain proper documentation of authorized use

### Ethical Guidelines

- Respect privacy and confidentiality
- Use the minimum level of access necessary
- Remove the tool when it is no longer needed
- Do not use for surveillance without proper authorization

### Disclaimer

The developers of RAT_RATATOUILLE are not responsible for any misuse of this software. Users bear sole responsibility for ensuring their use complies with all applicable laws and regulations.

---

<div align="center">
  <sub>RAT_RATATOUILLE © 2023 - For Educational Purposes Only</sub>
</div>
