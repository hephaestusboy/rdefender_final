#!/usr/bin/env python3
"""
Build script for packaging R-Defender into a Windows installer.
This script works on Linux, macOS, and Windows.

On Linux/macOS: Builds the executable only (requires Windows + NSIS for final installer)
On Windows: Builds both executable and installer
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_requirements():
    """Check if required tools are installed."""
    print_header("Checking Requirements")
    
    system = platform.system()
    print(f"System: {system}\n")
    
    # Always need PyInstaller
    try:
        subprocess.run(['pyinstaller', '--version'], capture_output=True, check=True)
        print("✅ PyInstaller is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller is NOT installed")
        print("Install with: pip install pyinstaller")
        return False
    
    # NSIS only needed on Windows
    if system == "Windows":
        try:
            subprocess.run(['makensis', '/version'], capture_output=True, check=True)
            print("✅ NSIS is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ NSIS is NOT installed")
            print("Download from: https://nsis.sourceforge.io/Download")
            return False
    else:
        print(f"⚠️  NSIS not needed on {system} (only for final installer)")
        print("   Build executable here, then create installer on Windows")
    
    return True

def clean_build_dirs():
    """Remove old build artifacts."""
    print_header("Cleaning Old Build Artifacts")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}/")
            shutil.rmtree(dir_name)
    
    for file in os.listdir('.'):
        if file.endswith('.spec') and file != 'build_config.spec':
            print(f"Removing {file}")
            os.remove(file)

def build_executable():
    """Build the executable using PyInstaller."""
    print_header("Building Executable with PyInstaller")
    
    cmd = [
        'pyinstaller',
        'build_config.spec',
        '--clean'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Executable built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def build_installer():
    """Build the installer using NSIS (Windows only)."""
    print_header("Building Installer with NSIS")
    
    system = platform.system()
    
    if system != "Windows":
        print(f"⚠️  NSIS installer cannot be built on {system}")
        print("\nTo create the Windows installer:")
        print("1. Copy the 'dist/RDefender' folder to Windows")
        print("2. Copy 'installer.nsi' to Windows")
        print("3. Install NSIS: https://nsis.sourceforge.io/Download")
        print("4. Right-click 'installer.nsi' → 'Compile NSIS Script'")
        print("   OR run: makensis installer.nsi")
        return True  # Not a failure, just a limitation
    
    if not os.path.exists('dist/RDefender'):
        print("❌ Build folder not found. Run PyInstaller first!")
        return False
    
    cmd = ['makensis', 'installer.nsi']
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Installer created successfully!")
        print("\n📦 Output: RDefender-Setup.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installer build failed: {e}")
        return False

def create_portable_zip():
    """Create a portable ZIP version of the executable."""
    print_header("Creating Portable ZIP Package")
    
    if not os.path.exists('dist/RDefender'):
        print("❌ Build folder not found!")
        return False
    
    try:
        import zipfile
        
        zip_name = 'RDefender-Portable.zip'
        print(f"Creating {zip_name}...")
        
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk('dist/RDefender'):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, 'dist')
                    zipf.write(file_path, arcname)
        
        print(f"✅ Portable package created: {zip_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to create ZIP: {e}")
        return False

def main():
    """Main build process."""
    print("\n" + "🛡️  " * 15)
    print("      R-DEFENDER WINDOWS PACKAGE BUILD SYSTEM")
    print("🛡️  " * 15 + "\n")
    
    system = platform.system()
    
    # Step 1: Check requirements
    if not check_requirements():
        return False
    
    # Step 2: Clean old builds
    clean_build_dirs()
    
    # Step 3: Build executable
    if not build_executable():
        return False
    
    # Step 4: Build installer (Windows only)
    if system == "Windows":
        if not build_installer():
            return False
        print_header("Build Complete!")
        print("✅ Your installer is ready: RDefender-Setup.exe")
    else:
        # On Linux/macOS, create a portable ZIP
        print_header("Non-Windows System Detected")
        print("Created executable package at: dist/RDefender/")
        create_portable_zip()
        print("\n📋 Next steps for Windows installer:")
        print("1. Transfer 'dist/RDefender' folder to a Windows machine")
        print("2. Transfer 'installer.nsi' file to the same Windows machine")
        print("3. Install NSIS on Windows: https://nsis.sourceforge.io/Download")
        print("4. Run: makensis installer.nsi")
        print("5. This creates: RDefender-Setup.exe")
        return True
    
    print("\nNext steps:")
    print("1. Test the installer on a Windows machine")
    print("2. Distribute RDefender-Setup.exe to users")
    print("3. Users can run the installer to install R-Defender")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
