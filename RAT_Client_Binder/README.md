# RAT Client Binder v1.6

## Overview

The RAT Client Binder allows you to bind the RAT client (v1.6) with legitimate applications to create stealthy executables. This version supports the latest RAT client features including:

- **Screen sharing capabilities** (10 FPS JPEG streaming)
- **Interactive shell sessions**
- **Advanced system information gathering**
- **Process management and control**
- **Network monitoring**
- **Browser data extraction**
- **Persistence mechanisms**

## Quick Start Guide

### Prerequisites

- **RAT Client v1.6** (generated using RAT_Client_Generator)
- **Legitimate application** (.exe file to bind with)
- **MinGW-w64** or **GCC** compiler for Windows
- **Python 3.x** with required dependencies

### Using Binder.bat

1. **Run the Binder.bat file**

   - Double-click on `Binder.bat` in the RAT_Client_Binder directory
   - Or open Command Prompt and navigate to the directory, then type `Binder.bat`

2. **Follow the prompts**

   - Enter the path to the executable you want to extract an icon from
   - Enter the output path for the icon (e.g., `output.ico`)

3. **Automatic binding process**

   - After successful icon extraction, the script will automatically run `binder.py`
   - Follow the additional prompts to complete the binding process:
     - Enter the **RAT client v1.6 executable path** (from RAT_Client_Generator)
     - Enter the legitimate application path
     - Enter the desired output filename

4. **Verify the output**
   - Check that the bound executable was created successfully
   - Test the bound executable to ensure it works as expected
   - Verify screen sharing and other v1.6 features work correctly

## Version Compatibility

### RAT Client v1.6 Features Supported:
- ✅ **Screen Sharing**: Real-time desktop streaming with JPEG compression
- ✅ **Interactive Shell**: Full command-line access with real-time I/O
- ✅ **Process Control**: Start, stop, and monitor processes
- ✅ **System Information**: Detailed hardware and software inventory
- ✅ **Network Monitoring**: Active connections and adapter information
- ✅ **Browser Data**: History and cookie extraction capabilities
- ✅ **Persistence**: Registry and file system persistence mechanisms

### Recommended Workflow:
1. Generate RAT client v1.6 using `RAT_Client_Generator`
2. Use this binder to combine with legitimate application
3. Deploy the bound executable
4. Connect using the RAT server to access all v1.6 features

## Changelog

### v1.6 (Current)
- **Added**: Support for RAT client v1.6 with screen sharing capabilities
- **Added**: Improved resource extraction with efficient 16KB chunking
- **Added**: Enhanced icon extraction utility
- **Added**: Static linking for better portability (no DLL dependencies)
- **Added**: Polymorphic code compatibility
- **Fixed**: Compilation issues with MinGW-w64 toolchain
- **Fixed**: Memory management for large v1.6 clients (2-5MB+)
- **Fixed**: Socket handling in interactive shell
- **Improved**: Error handling and user feedback

### v1.5
- **Added**: Support for RAT client v1.5 with persistence features
- **Added**: Automatic icon extraction from legitimate applications
- **Added**: Registry-based persistence support
- **Fixed**: Resource size limitations
- **Fixed**: Path handling issues

### v1.0
- Initial release
- Basic binding functionality
- Limited to smaller client sizes
- Manual icon replacement
