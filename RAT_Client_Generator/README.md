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

### 🔧 Enhanced Connection Management
- **Intelligent Connection State Tracking**: Prevents duplicate connections
- **Automatic Reconnection**: Up to 3 retry attempts with smart logic
- **Real-time Socket Health Monitoring**: Continuous connection validation
- **Enhanced Timeouts**: 60-second timeout for large operations
- **Improved Buffer Management**: 8KB buffer size (4x performance increase)
- **Comprehensive Error Handling**: Detailed WSA error codes and recovery

### 🛡️ Robust Command Processing
- **Safe Network Operations**: 100% safe_send() usage for reliability
- **Enhanced Error Diagnosis**: Detailed error reporting with specific codes
- **Thread-safe Operations**: Critical sections for all shared resources
- **Graceful Error Recovery**: Continues operation when possible

### 💻 Interactive Shell Improvements
- **Full Terminal Emulation**: Complete Windows command shell access
- **Enhanced Error Handling**: Detailed diagnosis for pipe/handle errors (fixes Error 6)
- **Multiple Exit Commands**: Support for "exit_shell", "##EXIT_SHELL##", "screenshot"
- **Proper Session Management**: Clean shell lifecycle with resource cleanup
- **Connection Loss Detection**: Automatic recovery from shell errors

### 📁 Enhanced File Operations
- **Reliable File Transfer**: Chunked transmission with 4KB chunks
- **Progress Tracking**: Real-time progress reporting with chunk counting
- **Desktop-aware Placement**: Intelligent file placement with fallback
- **Binary Data Handling**: Fixed binary data processing issues
- **Connection State Management**: Proper error handling during transfers

### 🖥️ Screen Sharing Enhancements
- **Live Monitoring**: 10 FPS with JPEG compression (75% quality)
- **Efficient Transmission**: 8KB chunk size for optimal performance
- **Thread-safe Capture**: Proper synchronization for frame capture
- **Graceful Termination**: Clean session cleanup on disconnection

### 🔐 Security & Authentication Features
- **Dynamic Key Authentication**: Server-client key validation system
- **Polymorphic Code Generation**: Each build is unique to avoid detection
- **XOR Encryption**: Obfuscates strings and network traffic
- **Function Name Randomization**: Makes reverse engineering more difficult
- **Randomized Sleep Intervals**: Evades timing-based detection
- **Build Signatures**: Each build has a unique identifier
- **Connection Validation**: Real-time authentication during handshake

### ⚙️ Compilation Options
- **Console/Hidden Mode**: Choose whether the client shows a console window
- **Authentication Key Integration**: Dynamic key replacement during compilation
- **Static Linking**: No external DLL dependencies
- **Optimization Levels**: Balance between size and performance
- **Enhanced Error Reporting**: Comprehensive compilation feedback

### 🔧 Troubleshooting

#### Compilation Issues
If you encounter compilation errors:
1. Ensure g++ is properly installed and in your PATH
2. Verify all required libraries are available
3. Check that the source file exists and is readable
4. Verify authentication key is properly set before compilation

#### Authentication Issues
If clients can't authenticate:
1. Ensure server authentication key is set in Server Options
2. Verify client AUTH_KEY matches server key exactly
3. Check server logs for authentication failure details
4. Regenerate client with correct authentication key

#### Connection Problems
If clients can't maintain stable connections:
1. v1.6.1 includes enhanced connection management
2. Automatic reconnection with intelligent retry logic
3. Increased timeouts for large operations (60 seconds)
4. Real-time connection health monitoring

#### Shell Command Errors
If you see "Error 6" or shell handle errors:
1. This is fixed in v1.6.1 with enhanced error handling
2. Shell now provides detailed error diagnosis
3. Proper handle validation prevents crashes
4. Multiple exit commands supported

#### File Transfer Issues
If download/upload shows "Unexpected response":
1. This is resolved in v1.6.1 with safe_send() implementation
2. All file operations now use reliable transmission
3. Binary data handling is properly implemented
4. Progress tracking shows real-time status

#### Windows Setup
For Windows users, you may need to install MinGW-w64 if not already installed:
1. Download from [MSYS2](https://www.msys2.org/)
2. Follow installation instructions to set up the C++ compiler
3. Add the MinGW bin directory to your PATH
4. Verify installation with `g++ --version`

## Changelog

### v1.6.1 (Latest - December 2024)
#### 🔧 **Major Stability & Performance Enhancements**
- **FIXED**: Shell Error 6 (Invalid Handle) with comprehensive handle validation
- **FIXED**: "Unexpected response" errors in download/upload file commands
- **FIXED**: Binary data processing issues in command loop
- **ENHANCED**: Connection management with intelligent state tracking
- **ENHANCED**: Socket timeouts increased to 60 seconds for large operations
- **ENHANCED**: Buffer size increased to 8KB (4x performance improvement)
- **ENHANCED**: All network operations now use safe_send() for 100% reliability

#### 🛡️ **Authentication & Security Improvements**
- **ADDED**: Dynamic authentication key system with server integration
- **ADDED**: Real-time key validation during connection handshake
- **ADDED**: File-based authentication key storage and management
- **ENHANCED**: Connection logging with detailed authentication attempts
- **FIXED**: Authentication key synchronization between client and server

#### 💻 **Interactive Shell Enhancements**
- **FIXED**: Shell handle validation preventing Error 6 crashes
- **ADDED**: Detailed error categorization (Invalid Handle, Broken Pipe, No Data)
- **ENHANCED**: Multiple exit command support with proper cleanup
- **IMPROVED**: Shell session lifecycle management
- **ADDED**: Real-time connection loss detection and recovery

#### 📁 **File Transfer Improvements**
- **FIXED**: Binary data handling in file transfer operations
- **ENHANCED**: Chunked transmission with 4KB chunks (4x improvement)
- **ADDED**: Real-time progress tracking with chunk counting
- **IMPROVED**: Desktop-aware file placement with intelligent fallback
- **ENHANCED**: Connection state management during file operations

#### 🖥️ **Screen Sharing & System Monitoring**
- **ENHANCED**: Screen sharing with 8KB chunk transmission
- **IMPROVED**: Thread-safe frame capture with proper synchronization
- **ADDED**: Progress reporting for system information commands
- **ENHANCED**: Network information gathering with detailed adapter data
- **IMPROVED**: System logs access with configurable entry counts

### v1.6.0 (Original)
- **Added**: Polymorphic code generation engine
- **Added**: XOR encryption for strings and network traffic
- **Added**: Function and variable name randomization
- **Added**: Sleep timing randomization
- **Added**: Build signature generation
- **Added**: Interactive shell with full terminal emulation
- **Added**: Screen sharing capability (10 FPS with JPEG compression)
- **Added**: Enhanced file transfer system with visual progress
- **Added**: Console/Hidden mode selection
- **Added**: Static linking improvements for better portability
- **Added**: Persistence name randomization

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