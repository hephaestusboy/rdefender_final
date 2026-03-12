# 🛡️ R-Defender - Linux Setup & Build Guide

Complete guide for setting up and running R-Defender on Linux.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Running R-Defender](#running-r-defender)
4. [Building Windows Installer on Linux](#building-windows-installer-on-linux)
5. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Supported Distributions
- Ubuntu 18.04 LTS or later
- Debian 10 or later
- CentOS 7 or later
- Fedora 30 or later
- Any systemd-based distribution

### Hardware
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 500MB
- **CPU**: 2 cores minimum
- **Network**: Internet access (for package downloads)

### Software
- Python 3.8 or later
- pip (Python package manager)
- git (optional, for cloning)

---

## Installation

### Step 1: Update System

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get upgrade

# CentOS/Fedora
sudo dnf update
```

### Step 2: Install Python and Dependencies

**Debian/Ubuntu:**
```bash
sudo apt-get install -y \
    python3 python3-pip python3-dev python3-venv \
    build-essential libssl-dev libffi-dev \
    git wget curl
```

**CentOS/Fedora:**
```bash
sudo dnf install -y \
    python3 python3-pip python3-devel \
    gcc gcc-c++ openssl-devel libffi-devel \
    git wget curl
```

**Verify installation:**
```bash
python3 --version
pip3 --version
```

### Step 3: Clone/Download Project

```bash
# Option 1: Clone from repository
git clone <repository-url>
cd rdefender_final

# Option 2: Download ZIP
# Extract the archive and navigate to folder
cd rdefender_final
```

### Step 4: Create Virtual Environment

```bash
# Create isolated Python environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
```

### Step 5: Install Dependencies

```bash
# Ensure venv is activated
source venv/bin/activate

# Install required packages
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python3 -c "import rdefender_ui_clr_copy; print('✓ Installation successful')"
```

---

## Running R-Defender

### First Time Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python3 rdefender_ui_clr_copy.py
```

### Daily Usage

```bash
# Quick start
source venv/bin/activate
python3 rdefender_ui_clr_copy.py
```

### Create Desktop Shortcut (Optional)

```bash
# Create launcher script
cat > ~/.local/bin/rdefender << 'EOF'
#!/bin/bash
cd ~/rdefender_final
source venv/bin/activate
python3 rdefender_ui_clr_copy.py
EOF

# Make executable
chmod +x ~/.local/bin/rdefender

# Create .desktop file
cat > ~/.local/share/applications/rdefender.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=R-Defender
Exec=~/.local/bin/rdefender
Icon=security
Terminal=false
Categories=System;Security;
EOF
```

### Command Line Options

```bash
# Run with specific watch directory
WATCH_DIR=/home python3 rdefender_ui_clr_copy.py

# Enable debug output
PYTHONDEBUG=1 python3 rdefender_ui_clr_copy.py

# Run in background (with nohup)
nohup python3 rdefender_ui_clr_copy.py &
```

---

## Building Windows Installer on Linux

### Note
R-Defender GUI requires X11 (graphical interface). To build for Windows, you have two options:

### Option 1: Build Executable on Linux (Recommended)

```bash
# Activate venv
source venv/bin/activate

# Install build dependencies
pip install -r build_requirements.txt

# Build Linux executable
pyinstaller build_config.spec --clean

# Output: dist/RDefender/RDefender (Linux binary)
# Copy this to Windows to create final installer
```

### Option 2: Build Complete Installer on Windows

1. Transfer entire project to Windows machine
2. Follow [SETUP_WINDOWS.md](SETUP_WINDOWS.md)
3. Get Windows installer

### Option 3: Use Docker (Advanced)

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt build_requirements.txt ./
RUN pip install -r requirements.txt -r build_requirements.txt
COPY . .
RUN pyinstaller build_config.spec --clean
EOF

# Build Docker image
docker build -t rdefender-builder .

# Run build
docker run -v $(pwd)/dist:/app/dist rdefender-builder

# Extract Windows binary
# Result: dist/RDefender/RDefender.exe (Windows executable)
```

---

## Development Setup

### For Contributors

```bash
# Clone repository
git clone <repo-url>
cd rdefender_final

# Create development environment
python3 -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
pip install -r build_requirements.txt

# Install development tools (optional)
pip install pytest black flake8 mypy

# Run tests
pytest tests/
```

### Project Structure
```
rdefender_final/
├── rdefender_ui_clr_copy.py          # Main GUI application
├── rdefender_agent.py                 # ML scanning engine
├── static_feature_extractor.py        # Binary feature extraction
├── feature_vectorizer.py              # Feature encoding
├── model_feature_groups.py            # Feature group definitions
├── feature_schema.py                  # Feature schema
├── *.joblib                           # ML models (5 files)
├── requirements.txt                   # Runtime dependencies
├── build_requirements.txt             # Build dependencies
├── build_config.spec                  # PyInstaller config
├── installer.nsi                      # Windows installer
├── build.py                           # Build script
└── README.md                          # Documentation
```

---

## Troubleshooting

### Python Version Issues

```bash
# Error: Python 3.8+ required

# Solution 1: Check Python version
python3 --version

# Solution 2: Install Python 3.10
sudo apt-get install python3.10

# Solution 3: Use alternatives
sudo update-alternatives --install /usr/bin/python3 \
    python3 /usr/bin/python3.10 1
```

### Virtual Environment Issues

```bash
# Error: venv module not found

# Solution: Install venv
sudo apt-get install python3-venv

# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Dependency Installation Fails

```bash
# Error: Failed building wheel for X

# Solution 1: Install build tools
sudo apt-get install build-essential python3-dev

# Solution 2: Upgrade pip
pip install --upgrade pip setuptools wheel

# Solution 3: Install development headers
sudo apt-get install python3.10-dev

# Retry installation
pip install -r requirements.txt
```

### tkinter Not Found

```bash
# Error: ImportError: No module named 'tkinter'

# Solution:
# Debian/Ubuntu
sudo apt-get install python3-tk

# CentOS/Fedora
sudo dnf install python3-tkinter

# macOS
brew install python-tk@3.10
```

### GUI Won't Display

```bash
# Error: No display found / Can't connect to X

# Solution 1: Check DISPLAY variable
echo $DISPLAY
# Should show something like :0 or :1

# Solution 2: Use SSH with X forwarding
ssh -X user@host
python3 rdefender_ui_clr_copy.py

# Solution 3: Use VNC
# Install vncserver first, then:
python3 rdefender_ui_clr_copy.py
```

### Models Not Loading

```bash
# Error: Cannot find .joblib files

# Solution 1: Verify files exist
ls -la *.joblib

# Solution 2: Check permissions
chmod 644 *.joblib

# Solution 3: Reinstall from source
git clone <repo-url>
```

### Permission Denied

```bash
# Error: Permission denied for /home, /root, etc.

# Solution: Run with appropriate permissions
sudo python3 rdefender_ui_clr_copy.py

# Note: Continuous monitoring requires elevated privileges
sudo bash
source venv/bin/activate
python3 rdefender_ui_clr_copy.py
```

### High CPU Usage

```bash
# Solution 1: Reduce watch directory scope
# Edit rdefender_agent.py:
TARGET_WATCH_DIR = "/home/user"  # Instead of "/"

# Solution 2: Exclude directories
# Edit rdefender_agent.py to add exclusions

# Solution 3: Increase model inference threads
# Adjust ML engine parameters

# Solution 4: Monitor with top
top -p $(pgrep -f rdefender_ui_clr_copy.py)
```

### Memory Issues

```bash
# If application uses too much memory:

# Solution 1: Monitor memory
watch -n 1 'free -h'

# Solution 2: Check ml engine
# Edit rdefender_agent.py to reduce model count

# Solution 3: Restart application
pkill -f rdefender_ui_clr_copy.py
sleep 2
python3 rdefender_ui_clr_copy.py
```

### File System Monitoring Fails

```bash
# Error: Cannot watch directory

# Solution 1: Check inotify limits
cat /proc/sys/fs/inotify/max_user_watches

# Solution 2: Increase limits temporarily
sudo sysctl fs.inotify.max_user_watches=524288

# Solution 3: Make permanent
echo "fs.inotify.max_user_watches=524288" | \
    sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Logging Issues

```bash
# Check application logs
cat rdefender_events.log

# Real-time log monitoring
tail -f rdefender_events.log

# Filter by severity
grep "ERROR" rdefender_events.log
grep "WARNING" rdefender_events.log
```

---

## System Integration

### Run as Service (Optional)

```bash
# Create systemd service
sudo tee /etc/systemd/system/rdefender.service > /dev/null << 'EOF'
[Unit]
Description=R-Defender Antimalware
After=network.target

[Service]
Type=simple
User=<your-username>
WorkingDirectory=/home/<your-username>/rdefender_final
ExecStart=/home/<your-username>/rdefender_final/venv/bin/python3 \
          /home/<your-username>/rdefender_final/rdefender_ui_clr_copy.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable rdefender
sudo systemctl start rdefender

# Check status
sudo systemctl status rdefender
```

### Automatic Startup

```bash
# Add to crontab
crontab -e

# Add this line (runs on boot)
@reboot ~/rdefender_final/venv/bin/python3 ~/rdefender_final/rdefender_ui_clr_copy.py

# Or add to ~/.bashrc for user session
# Add to ~/.bashrc:
# [ -z "$DISPLAY" ] || ~/rdefender_final/venv/bin/python3 ~/rdefender_final/rdefender_ui_clr_copy.py &
```

---

## Performance Tuning

### Monitor Resource Usage

```bash
# CPU and Memory
top -p $(pgrep -f rdefender_ui_clr_copy.py)

# Real-time network (if applicable)
nethogs

# Disk I/O
iotop
```

### Optimize for Low-End Hardware

```bash
# Reduce scanning frequency
# Edit rdefender_agent.py to adjust sweeper interval

# Exclude large directories
# Point TARGET_WATCH_DIR to specific folders only

# Disable graphics effects
# Edit rdefender_ui_clr_copy.py
```

---

## Support & Resources

- **Main Documentation**: [README.md](README.md)
- **Windows Setup**: [SETUP_WINDOWS.md](SETUP_WINDOWS.md)
- **Log File**: `rdefender_events.log`
- **Config**: Edit `rdefender_agent.py` for settings

---

## Next Steps

- Run R-Defender: `python3 rdefender_ui_clr_copy.py`
- Read [README.md](README.md) for feature overview
- Configure for your needs
- Consider system service integration for 24/7 protection
