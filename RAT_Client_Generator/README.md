# RAT Client Generator v1.6

A utility for generating customized Remote Access Tool (RAT) client executables with advanced features and polymorphic capabilities.

## Quick Start Guide

### Basic Usage

1. **Run the generator script**

   ```bash
   python rat_client_generator.py
   ```

2. **Follow the prompts**

   - Enter the server IP address (required)
   - Enter the server port (default: 8888)
   - Enter the output filename (default: rat_client.exe)
   - Choose additional options (polymorphic features, encryption, etc.)

3. **Compilation process**

   The generator will:
   - Create a modified version of the RAT client source code with your settings
   - Apply polymorphic transformations for evasion (v1.6+)
   - Compile it with the specified settings
   - Output the executable to your specified filename

### Example

```
╔══════════════════════════════════════════════════╗
║ Enter the server details:                        ║
╚════════════════════════════════════════════════╝

[+] Server IP ➤ 192.168.1.100
[+] Server Port [8888] ➤ 9999
[+] Output filename [rat_client.exe] ➤ my_client.exe
[+] Enable polymorphic features? [Y/n] ➤ Y
[+] Show console window? [y/N] ➤ N

╔══════════════════════════════════════════════════╗
║ Generating client with the following settings:   ║
╠══════════════════════════════════════════════════╣
║  • Server IP:      192.168.1.100                 ║
║  • Server Port:    9999                          ║
║  • Output filename: my_client.exe                ║
║  • Polymorphic:    Yes                           ║
║  • Console mode:   Hidden                        ║
╚══════════════════════════════════════════════════╝

[*] Initializing polymorphic code generation engine...
[*] Applying server configuration...
[*] Applying polymorphic transformations and evasion techniques...
[+] Updated XOR encryption key to 0xF3
[+] Randomized function names
[+] Randomized sleep intervals
[+] Randomized persistence names
[+] Generated unique build signature: c9defa1b
Compiling...
Compilation successful!
Client executable saved to: my_client.exe
```

## Features in v1.6

### Core Features
- **Interactive Shell**: Real-time command shell access
- **Screen Sharing**: Live screen monitoring at 10 FPS with JPEG compression
- **Enhanced File Transfer**: Reliable bidirectional file transfer system
  * Clean and consistent progress box UI
  * Desktop-aware file placement with fallback
  * Automatic directory creation
  * Efficient socket buffer management
- **Process Control**: List, search, and terminate processes
- **System Information**: Detailed hardware and software information
- **Network Monitoring**: Connection details and active network interfaces
- **Persistence**: Automatic startup via registry (with randomized names)

### Security Features
- **Polymorphic Code Generation**: Each build is unique to avoid detection
- **XOR Encryption**: Obfuscates strings and network traffic
- **Function Name Randomization**: Makes reverse engineering more difficult
- **Randomized Sleep Intervals**: Evades timing-based detection
- **Build Signatures**: Each build has a unique identifier

### Compilation Options
- **Console/Hidden Mode**: Choose whether the client shows a console window
- **Icon Customization**: Embed custom icons in the executable
- **Static Linking**: No external DLL dependencies
- **Optimization Levels**: Balance between size and performance

### Troubleshooting

If you encounter compilation errors:

1. Ensure g++ is properly installed and in your PATH
2. Verify all required libraries are available
3. Check that the source file exists and is readable

For Windows users, you may need to install MinGW-w64 if not already installed:
1. Download from [MSYS2](https://www.msys2.org/)
2. Follow installation instructions to set up the C++ compiler
3. Add the MinGW bin directory to your PATH

## Changelog

### v1.6 (Current)
- **Added**: Polymorphic code generation engine
- **Added**: XOR encryption for strings and network traffic
- **Added**: Function and variable name randomization
- **Added**: Sleep timing randomization
- **Added**: Build signature generation
- **Added**: Interactive shell with full terminal emulation
- **Added**: Screen sharing capability (10 FPS with JPEG compression)
- **Added**: Enhanced file transfer system with visual progress
  * Clean and consistent progress box UI
  * Desktop-aware file placement with fallback
  * Automatic directory creation
  * Efficient socket buffer management
- **Added**: Console/Hidden mode selection
- **Added**: Static linking improvements for better portability
- **Added**: Persistence name randomization
- **Fixed**: Binary data handling in file transfers
- **Fixed**: Socket buffer management for large files
- **Fixed**: Directory creation issues in file transfers

### v1.5
- **Added**: Persistence mechanism via registry
- **Added**: Screenshot capability
- **Added**: Process management (list, search, terminate)
- **Added**: System information collection
- **Added**: Network information gathering
- **Added**: Application control features
- **Fixed**: Connection stability issues
- **Fixed**: Memory leaks in long-running sessions

### v1.0
- Initial release
- Basic remote command execution
- File transfer capabilities
- Simple system information gathering
- Automatic reconnection mechanism

## Educational Use Only

This tool is intended for educational purposes and legitimate system administration only. Unauthorized access to computer systems is illegal and unethical.