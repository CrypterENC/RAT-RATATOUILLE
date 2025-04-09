# RAT Client Generator

A utility for generating customized Remote Access Tool (RAT) client executables.

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

3. **Compilation process**

   The generator will:
   - Create a temporary modified version of the RAT client source code
   - Compile it with the specified settings
   - Output the executable to your specified filename

### Example

```
╔══════════════════════════════════════════════════╗
║ Enter the server details:                        ║
╚══════════════════════════════════════════════════╝

[+] Server IP ➤ 192.168.1.100
[+] Server Port [8888] ➤ 9999
[+] Output filename [rat_client.exe] ➤ my_client.exe

╔══════════════════════════════════════════════════╗
║ Generating client with the following settings:   ║
╠══════════════════════════════════════════════════╣
║  • Server IP:      192.168.1.100                 ║
║  • Server Port:    9999                          ║
║  • Output filename: my_client.exe                ║
╚══════════════════════════════════════════════════╝

Compiling...
Compilation successful!
Client executable saved to: my_client.exe
```

### Troubleshooting

If you encounter compilation errors:

1. Ensure g++ is properly installed and in your PATH
2. Verify all required libraries are available
3. Check that the source file exists and is readable

For Windows users, you may need to install MinGW-w64 if not already installed:
1. Download from [MSYS2](https://www.msys2.org/)
2. Follow installation instructions to set up the C++ compiler
3. Add the MinGW bin directory to your PATH

## Educational Use Only

This tool is intended for educational purposes and legitimate system administration only. Unauthorized access to computer systems is illegal and unethical.