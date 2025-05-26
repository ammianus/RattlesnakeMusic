# Music Library Metadata Validator

A simple command-line tool for scanning music libraries and identifying files with missing or incomplete metadata. Perfect for organizing large music collections and ensuring consistent metadata across your library.

## 🎵 Features

- **Multi-format support**: MP3, MP4, and M4A files
- **Comprehensive validation**: Checks for album artwork, album name, artist, and track numbers
- **Flexible output**: Human-readable text reports or JSON for programmatic processing
- **Recursive scanning**: Deep directory traversal with optional depth control
- **Error handling**: Graceful handling of corrupted or unreadable files
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/music-metadata-validator.git
   cd music-metadata-validator
   ```

2. **Install dependencies**:
   ```bash
   pip install mutagen
   ```

3. **Run the validator**:
   ```bash
   python rattlesnake.py /path/to/your/music/library
   ```

## 📖 Usage

### Basic Commands

**Scan a music directory:**
```bash
python rattlesnake.py "C:\Users\YourName\Music"
```

**Save report to file:**
```bash
python rattlesnake.py "C:\Users\YourName\Music" --output validation_report.txt
```

**Generate JSON report:**
```bash
python rattlesnake.py "C:\Users\YourName\Music" --format json --output report.json
```

**Scan only current directory (no subdirectories):**
```bash
python rattlesnake.py "C:\Users\YourName\Music" --no-recursive
```

**Quiet mode (minimal console output):**
```bash
python rattlesnake.py "C:\Users\YourName\Music" --quiet --output report.txt
```

### Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--recursive` | `-r` | Scan subdirectories recursively (default: enabled) |
| `--no-recursive` | | Disable recursive scanning |
| `--output` | `-o` | Save report to specified file |
| `--format` | `-f` | Output format: `text` or `json` (default: text) |
| `--quiet` | `-q` | Suppress progress messages |
| `--help` | `-h` | Show help message |
| `--condensed` | `-c` | include only files missing artwork metadata |

## 📊 What Gets Validated

The tool checks for the following metadata in your music files:

### ✅ Required Metadata
- **Album Artwork**: Embedded cover art/images
- **Album Name**: The album or collection name
- **Artist Name**: The performing artist or band
- **Track Number**: Position of the track within the album

### 📁 Supported File Types
- **MP3** (`.mp3`) - ID3 tag validation
- **MP4** (`.mp4`, `.m4a`) - iTunes-style metadata validation

## 📈 Sample Output

### Text Report
```
============================================================
MUSIC LIBRARY METADATA VALIDATION REPORT
============================================================
Generated: 2024-12-15 14:30:22
Total files scanned: 1,247
Files with metadata issues: 83
Files with read errors: 2

FILES WITH MISSING METADATA:
----------------------------------------

File: C:\Music\Unknown Album\track01.mp3
Type: MP3
Missing: Album Artwork, Album, Track Number

File: C:\Music\Various Artists\song.mp4
Type: MP4
Missing: Artist

SUMMARY BY ISSUE TYPE:
----------------------------------------
Album Artwork: 45 files
Album: 23 files
Artist: 8 files
Track Number: 31 files
```

### JSON Report
```json
{
  "generated": "2024-12-15T14:30:22",
  "total_files": 1247,
  "files_with_issues": 83,
  "summary": {
    "missing_album_art": 45,
    "missing_album": 23,
    "missing_artist": 8,
    "missing_track_number": 31
  },
  "files": [
    {
      "filepath": "C:\\Music\\Unknown Album\\track01.mp3",
      "file_type": ".mp3",
      "missing_metadata": ["Album Artwork", "Album", "Track Number"],
      "error": null
    }
  ]
}
```

## 🔧 Advanced Usage

### Integration with Other Tools

**Use with music taggers:**
```bash
# Generate JSON report for programmatic processing
python rattlesnake.py /music/library --format json --output issues.json

# Process the JSON with other tools
jq '.files[] | select(.missing_metadata | length > 0)' issues.json
```

**Batch processing:**
```bash
# Windows batch file example
for /d %%i in ("C:\Music\*") do (
    python rattlesnake.py "%%i" --output "reports\%%~ni_report.txt"
)
```

### Custom Filtering

The JSON output makes it easy to filter results:

```python
import json

# Load validation results
with open('report.json', 'r') as f:
    data = json.load(f)

# Find files missing only album artwork
artwork_only = [
    f for f in data['files'] 
    if f['missing_metadata'] == ['Album Artwork']
]

print(f"Files missing only artwork: {len(artwork_only)}")
```

## 🛠️ Development

### Project Structure
```
music-metadata-validator/
├── rattlesnake.py      # Main application
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── examples/             # Example reports and scripts
└── tests/               # Unit tests (coming soon)
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone the repo
git clone https://github.com/ammianus/RattlesnakeMusic.git
cd RattlesnakeMusic

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install mutagen

```

## 📋 Requirements

- **Python**: 3.7 or higher
- **Dependencies**: 
  - `mutagen` (audio metadata handling)

## 🐛 Troubleshooting

### Common Issues

**"mutagen not found" error:**
```bash
pip install mutagen
```

**Permission denied on Windows:**
- Run Command Prompt/PowerShell as Administrator
- Or use `--user` flag: `pip install --user mutagen`

**Unicode errors with file paths:**
- Ensure your terminal supports UTF-8 encoding
- Use raw strings or escape backslashes in paths

**Large libraries taking too long:**
- Use `--quiet` mode to reduce output
- Consider scanning subdirectories individually
- Save to file instead of console output

### Performance Tips

- **For large libraries (10,000+ files)**: Use `--quiet --output report.txt` to avoid console bottlenecks
- **Network drives**: Local scanning is significantly faster than network-mounted directories
- **SSD vs HDD**: Scanning is I/O intensive; SSDs provide much better performance

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Acknowledgments

- [Mutagen](https://mutagen.readthedocs.io/) - Excellent Python library for audio metadata
- The Python community for great libraries and documentation
- Music enthusiasts who provided feedback and testing
- [Claude](https://claude.ai) Sonnet 4

## 🏷️ Version History

- **v1.0.0** - Initial release with MP3/MP4 support

---

**Star this repo if you find it useful!** 🌟

For questions, issues, or feature requests, please [open an issue](https://github.com/ammianus/RattlesnakeMusic/issues).