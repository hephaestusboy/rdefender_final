# 🛡️ R-Defender - Advanced Malware Detection System

A powerful machine learning-powered antimalware solution that combines behavioral analysis, artifact inspection, and advanced threat detection using Random Forest, XGBoost, and ensemble learning models.

## Features

- **Real-time File Monitoring** - Continuous surveillance of file system activities
- **ML-Powered Detection** - 4 independent ML models (RF Behavior, RF Artifact, XGB Behavior, XGB Artifact) + Fusion model for maximum accuracy
- **Automatic Quarantine** - Suspicious/malicious files automatically isolated
- **Recovery Management** - Easy file recovery with automatic path restoration
- **Whitelist System** - Exclude trusted files from scanning
- **System Metrics** - Real-time CPU, RAM, and engine status monitoring
- **User-Friendly GUI** - Built with Tkinter, dark theme interface

## System Requirements

### Windows
- **OS**: Windows 10 or later
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 500MB for installation
- **Python**: 3.8+ (automatically bundled in installer)

### Linux
- **OS**: Ubuntu 18.04+, Debian 10+, or equivalent
- **RAM**: 4GB minimum
- **Disk Space**: 500MB
- **Python**: 3.8 or later

## Quick Start

### Windows Users
1. **Download** `RDefender-Setup.exe`
2. **Run** the installer
3. **Launch** R-Defender from Start Menu
4. **Enable** "START MONITORING" button

See [SETUP_WINDOWS.md](SETUP_WINDOWS.md) for detailed instructions.

### Linux Users
1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python rdefender_ui_clr_copy.py`
3. Enable "START MONITORING" button

See [SETUP_LINUX.md](SETUP_LINUX.md) for detailed instructions.

## Building from Source

### For Windows Installers
```bash
python build.py
```
Creates `RDefender-Setup.exe` ready for distribution.

### For Linux
```bash
python rdefender_ui_clr_copy.py
```
Runs directly without installation.

See platform-specific guides for detailed build instructions with troubleshooting.

## Project Structure

```
rdefender_final/
├── rdefender_ui_clr_copy.py          # Main UI application
├── rdefender_agent.py                 # ML scanning engine
├── static_feature_extractor.py        # Binary analysis features
├── feature_vectorizer.py              # Feature encoding
├── build_config.spec                  # PyInstaller configuration
├── installer.nsi                      # Windows installer script
├── build.py                           # Build automation script
├── *.joblib                           # ML models (5 files)
├── requirements.txt                   # Python dependencies
├── build_requirements.txt             # Build dependencies
├── README.md                          # This file
├── SETUP_WINDOWS.md                   # Windows setup guide
├── SETUP_LINUX.md                     # Linux setup guide
└── LICENSE                            # License file
```

## Features in Detail

### Real-Time Monitoring
- Watches entire file system (configurable)
- Detects new files, modifications, and access attempts
- Custom folder scanning available

### File Recovery
- **Multi-file Support** - Recover multiple files at once
- **Bulk Selection** - Use Shift+Click for ranges, Ctrl+Click for individual files
- **Auto-Restore** - Files restore to original locations
- **Original Location Override** - Choose custom locations if needed

### Whitelist Management
- Add detected-clean files to whitelist
- Bulk remove files from whitelist
- Persistent across restarts

### Advanced Detection
- **Behavior Analysis** - Detects suspicious execution patterns
- **Artifact Analysis** - Identifies suspicious file signatures
- **Entropy Detection** - Recognizes packed/encrypted malware
- **Signature Validation** - Checks digital signatures
- **Consensus Model** - Fusion of multiple models for accuracy

## Key Metrics

| Metric | Value |
|--------|-------|
| ML Models | 5 (4 base + 1 fusion) |
| Features Analyzed | 80+ per file |
| Supported Formats | .exe, .dll, .sys |
| Detection Categories | Malware, Suspicious, Clean |
| Quarantine Path | C:\RDefender_Quarantine |

## Default Settings

| Setting | Value |
|---------|-------|
| Malware Threshold | 0.65 |
| Suspicious Threshold | 0.30 |
| Watch Directory | C:\ (entire drive) |
| Quarantine Cleanup | Manual only |

## Architecture

### ML Engine
```
Binary File
    ↓
Feature Extraction (80+ features)
    ↓
Behavior Model (RF + XGB)    Artifact Model (RF + XGB)
    ↓                              ↓
    └─────→ Fusion Model ←─────┘
            ↓
    Confidence Score
    ↓
MALWARE / SUSPICIOUS / CLEAN
```

### Components
- **Static Feature Extractor**: Analyzes binary headers, imports, entropy
- **Feature Vectorizer**: Encodes features for ML models
- **ML Scanner Engine**: Loads and runs all 5 models
- **Quarantine System**: File isolation with metadata storage
- **Whitelist Manager**: Hash-based file exemption system

## Troubleshooting

### Windows
See [SETUP_WINDOWS.md - Troubleshooting](SETUP_WINDOWS.md#troubleshooting)

### Linux
See [SETUP_LINUX.md - Troubleshooting](SETUP_LINUX.md#troubleshooting)

## Contributing

To contribute improvements:
1. Test changes thoroughly
2. Follow existing code style
3. Update documentation
4. Submit pull requests

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

If you encounter issues:
1. Check the platform-specific setup guide
2. Review logs in `rdefender_events.log`
3. Verify all dependencies are installed
4. Check system requirements

## Development Notes

### Building Installers
- **Windows**: Requires NSIS installer builder
- **Linux**: Creates executable without installer
- **macOS**: Not currently supported

### ML Models
- **rf_behavior_model.joblib** - Random Forest behavior classifier
- **rf_artifact_model.joblib** - Random Forest artifact classifier
- **xgb_behavior_model.joblib** - XGBoost behavior classifier
- **xgb_artifact_model.joblib** - XGBoost artifact classifier
- **fusion_model.joblib** - Ensemble fusion model

### Performance
- First run: ~5 seconds for ML engine initialization
- Per-file scan: 50-200ms depending on file size
- Monitoring: <1% CPU at idle

## Version History
- **v2.0.0** - Updated UI
- Migrated from ktinker to HTML/CSS based UI.

- **v1.0.0** - Initial release with ML-powered detection
- Dual behavior/artifact analysis
- Multi-file recovery system
- Enhanced whitelist management
- Separated quarantine categories

## Disclaimer

R-Defender is a protective tool and should be used responsibly. It may occasionally flag legitimate files (false positives). The whitelist feature allows you to add trusted applications. Always maintain updated antivirus software alongside this tool.
