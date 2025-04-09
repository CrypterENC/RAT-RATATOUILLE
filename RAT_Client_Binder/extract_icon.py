#!/usr/bin/env python3
import os
import sys
import subprocess
try:
    from PIL import Image # type: ignore
    import win32api # type: ignore
    import win32con # type: ignore
    import win32ui # type: ignore
    import win32gui # type: ignore
except ImportError:
    print("Required packages not found. Install with:")
    print("pip install pillow pywin32")
    sys.exit(1)

def extract_icon_with_win32(exe_path, output_path):
    """Extract icon using Win32 API directly"""
    try:
        # Get the large icon - ExtractIconEx takes 3 arguments in this context
        large_icons, small_icons = win32gui.ExtractIconEx(exe_path, 0, 1)
        if not large_icons:
            raise Exception("No icons found in executable")
        
        large_icon = large_icons[0]
        
        # Create a device context
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, 32, 32)
        
        # Create a memory device context
        hdc_mem = hdc.CreateCompatibleDC()
        hdc_mem.SelectObject(hbmp)
        
        # Draw the icon
        win32gui.DrawIconEx(hdc_mem.GetSafeHdc(), 0, 0, large_icon, 32, 32, 0, None, win32con.DI_NORMAL)
        
        # Convert to PIL Image
        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGBA',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRA', 0, 1
        )
        
        # Save as ICO
        img.save(output_path, format='ICO')
        
        # Clean up
        for icon in large_icons:
            win32gui.DestroyIcon(icon)
        for icon in small_icons:
            win32gui.DestroyIcon(icon)
        hdc_mem.DeleteDC()
        hdc.DeleteDC()
        win32gui.ReleaseDC(0, win32gui.GetDC(0))
        
        return os.path.exists(output_path) and os.path.getsize(output_path) > 100
    except Exception as e:
        print(f"Win32 icon extraction failed: {str(e)}")
        return False

def extract_icon_with_powershell(exe_path, output_path):
    """Extract icon using PowerShell as a fallback method"""
    try:
        # Method 1: Try using PowerShell's ExtractAssociatedIcon
        cmd = f'powershell -Command "$icon = [System.Drawing.Icon]::ExtractAssociatedIcon(\'{exe_path}\'); $icon.Save(\'{output_path}\')"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
            print(f"Successfully extracted icon using PowerShell method 1")
            return True
            
        # Method 2: Try using PowerShell's GetIconHandle
        cmd = f'powershell -Command "$handle = (Add-Type -MemberDefinition \'[DllImport(\\"Shell32.dll\\")] public static extern IntPtr ExtractIcon(IntPtr hInst, string lpszExeFileName, int nIconIndex);\' -Name ExtractIcon -Namespace Shell32 -PassThru)::ExtractIcon(0, \'{exe_path}\', 0); if ($handle -ne 0) {{ $icon = [System.Drawing.Icon]::FromHandle($handle); $icon.Save(\'{output_path}\'); }}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
            print(f"Successfully extracted icon using PowerShell method 2")
            return True
            
        return False
    except Exception as e:
        print(f"PowerShell icon extraction failed: {str(e)}")
        return False

def create_default_icon(output_path):
    """Create a default icon if extraction fails"""
    try:
        # Create a simple default icon using PIL
        img = Image.new('RGBA', (32, 32), color=(0, 0, 0, 0))
        
        # Save as ICO
        img.save(output_path, format='ICO')
        
        print(f"Created default icon at {output_path}")
        return os.path.exists(output_path)
    except Exception as e:
        print(f"Default icon creation failed: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_icon.py <exe_path> <output_ico>")
        sys.exit(1)
    
    exe_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Try Win32 method first
    if extract_icon_with_win32(exe_path, output_path):
        print(f"Successfully extracted icon to {output_path}")
    # Try PowerShell method as fallback
    elif extract_icon_with_powershell(exe_path, output_path):
        print(f"Successfully extracted icon to {output_path} using PowerShell")
    # Create a default icon as last resort
    elif create_default_icon(output_path):
        print(f"Created default icon at {output_path}")
    else:
        print(f"Failed to extract icon from {exe_path}")



