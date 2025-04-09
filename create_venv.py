import os
import subprocess
import sys
import venv
from pathlib import Path

def create_windows_venv():
    """Create a Python virtual environment for Windows."""
    # Get current directory
    current_dir = os.getcwd()
    venv_folder = "venv_folder"  # New dedicated folder
    venv_name = ".venv"
    
    # Create the venv folder if it doesn't exist
    venv_folder_path = os.path.join(current_dir, venv_folder)
    if not os.path.exists(venv_folder_path):
        os.makedirs(venv_folder_path)
        print(f"Created dedicated folder for virtual environment: {venv_folder_path}")
    
    venv_path = os.path.join(venv_folder_path, venv_name)
    
    print(f"Creating virtual environment in: {venv_path}")
    
    try:
        # Create the virtual environment
        venv.create(venv_path, with_pip=True)
        print(f"✅ Virtual environment created successfully!")
        
        # Create activation batch file for easy activation
        activate_script = os.path.join(current_dir, "activate_venv.bat")
        with open(activate_script, "w") as f:
            f.write(f"@echo off\n")
            f.write(f"echo Activating virtual environment...\n")
            f.write(f"call {venv_folder}\\{venv_name}\\Scripts\\activate.bat\n")
            f.write(f"cmd /k\n")  # Keep the command window open
        
        print(f"✅ Created activation script: {activate_script}")
        
        # Install requirements automatically
        req_file = os.path.join(current_dir, "requirements.txt")
        if os.path.exists(req_file):
            print(f"\nRequirements file found: {req_file}")
            print("Installing requirements automatically...")
            pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
            subprocess.run([pip_path, "install", "-r", req_file])
            print("✅ Requirements installed!")
        
        # Remove the automatic activation of the virtual environment
        # which was opening an additional window
        print("\n✅ Virtual environment setup complete!")
        
        return True
    
    except Exception as e:
        print(f"❌ Error creating virtual environment: {e}")
        return False

if __name__ == "__main__":
    if sys.platform != "win32":
        print("This script is designed for Windows only.")
        sys.exit(1)
    
    create_windows_venv()




