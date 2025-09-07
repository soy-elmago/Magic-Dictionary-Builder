# 🔍 Magic Dictionary Builder

> **Custom wordlist generator for Bug Bounty and Penetration Testing**

A powerful Python tool that automatically generates custom dictionaries by extracting directories and files from web assets discovered through **GAU** and **URLFinder**. Perfect for targeted directory brute-forcing and asset discovery during security assessments.

## ✨ Features

- 🚀 **Dual Source Integration**: Combines results from both GAU and URLFinder for comprehensive coverage
- 🎯 **Smart Filtering**: Automatically excludes static assets (images, stylesheets, etc.) to focus on actionable paths
- 🔄 **Subdomain Discovery**: Leverages `--subs` flag in GAU for extensive subdomain enumeration
- 📝 **Clean Output**: Removes duplicates and sorts results alphabetically
- ⚡ **Optimized for Large Domains**: No timeout limits by default, handles enterprise-scale targets
- 🛡️ **Robust Error Handling**: Comprehensive error handling and informative status messages
- 🔧 **Flexible Tool Selection**: Run both tools or choose specific ones
- ⏱️ **Timeout Control**: Optional custom timeouts for time-sensitive operations
- 🎮 **Interactive Control**: Interrupt operations with Ctrl+C when needed

## 🛠️ Installation

### Prerequisites

Make sure you have Python 3.6+ installed, then install the required tools:

```bash
# Install GAU
go install github.com/lc/gau/v2/cmd/gau@latest

# Install URLFinder from Project Discovery
go install -v github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest
```

### Download the Script

```bash
# Clone the repository
git clone https://github.com/your-username/dictionary-builder.git
cd dictionary-builder

# Make it executable
chmod +x dictionary_builder.py

# Test tools installation
python3 dictionary_builder.py --test-tools
```

## 🚀 Usage

### Basic Usage

```bash
# Standard usage (recommended for most cases)
python3 dictionary_builder.py -i target.com -o wordlist.txt

# Test tools before running
python3 dictionary_builder.py --test-tools
```

### Advanced Examples

```bash
# Large enterprise domains (no timeout - let it finish)
python3 dictionary_builder.py -i deere.com -o enterprise_wordlist.txt

# With custom timeout (30 minutes per tool)
python3 dictionary_builder.py -i target.com -o wordlist.txt -t 1800

# Only GAU (faster for quick reconnaissance)
python3 dictionary_builder.py -i target.com -o gau_wordlist.txt --no-urlfinder

# Only URLFinder (comprehensive passive discovery)
python3 dictionary_builder.py -i target.com -o url_wordlist.txt --no-gau

# Bug bounty workflow
python3 dictionary_builder.py -i bugcrowd-target.com -o comprehensive_dict.txt
```

### Command Line Options

```
-i, --input         Target domain (required)
-o, --output        Output file for the dictionary (required)
-t, --timeout       Timeout in seconds for each tool (default: no timeout)
--no-gau           Skip GAU and only use URLFinder
--no-urlfinder     Skip URLFinder and only use GAU
--test-tools       Test if GAU and URLFinder are properly installed
-h, --help         Show help message
```

## 📊 Example Output

Given the domain `example.com`, the tool might extract:

**Input URLs:**
```
http://example.com/img/logo.png
http://example.com/admin/login.php
http://example.com/api/v1/users
http://example.com/js/main.js
http://example.com/css/style.css
http://example.com/beta/dashboard
```

**Generated Dictionary:**
```
admin
api
beta
dashboard
login.php
users
v1
```

**Filtered Out:** `img`, `logo.png`, `main.js`, `style.css` (static assets)

## 🎯 What Gets Included

### ✅ Included in Dictionary
- Directory names (`admin`, `api`, `dashboard`, `beta`)
- Dynamic files (`.php`, `.asp`, `.jsp`, `.py`, `.html`, etc.)
- API endpoints and versioned paths (`v1`, `v2`, `api`)
- Unique path components and subdirectories
- Configuration and admin paths

### ❌ Filtered Out
- Static assets: `.js`, `.css`, `.png`, `.jpg`, `.gif`
- Font files: `.ttf`, `.woff`, `.woff2`, `.eot`
- Flash files: `.swf`
- Documents: `.pdf`, `.doc`, `.xls`
- Media files: `.mp4`, `.mp3`, `.avi`
- Archives: `.zip`, `.rar`, `.tar`
- Binary files: `.exe`, `.dmg`, `.iso`

## 🔧 How It Works

1. **URL Discovery**: Runs GAU with `--subs` and URLFinder in parallel
2. **URL Parsing**: Extracts paths and components from discovered URLs
3. **Smart Filtering**: Removes static assets based on file extensions
4. **Path Extraction**: Identifies directories and dynamic files
5. **Deduplication**: Merges results and removes duplicates
6. **Clean Output**: Sorts alphabetically and saves to specified file

## 📈 Sample Workflows

### Bug Bounty Reconnaissance
```bash
# Step 1: Generate comprehensive dictionary
python3 dictionary_builder.py -i target.com -o target_dict.txt

# Step 2: Use with ffuf
ffuf -w target_dict.txt -u https://target.com/FUZZ

# Step 3: Use with gobuster
gobuster dir -w target_dict.txt -u https://target.com
```

### Enterprise Assessment
```bash
# Step 1: Large enterprise domain (no timeout)
python3 dictionary_builder.py -i enterprise.com -o enterprise_dict.txt

# Step 2: Quick GAU-only scan for initial reconnaissance
python3 dictionary_builder.py -i enterprise.com -o quick_dict.txt --no-urlfinder

# Step 3: Use with dirsearch
dirsearch -w enterprise_dict.txt -u https://enterprise.com
```

### Time-Constrained Testing
```bash
# 15-minute limit per tool
python3 dictionary_builder.py -i target.com -o limited_dict.txt -t 900
```

## 🐛 Troubleshooting

### Common Issues

**GAU not found:**
```bash
go install github.com/lc/gau/v2/cmd/gau@latest
export PATH=$PATH:$(go env GOPATH)/bin
```

**URLFinder not found:**
```bash
go install -v github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest
export PATH=$PATH:$(go env GOPATH)/bin
```

**No URLs found:**
- Check your internet connection
- Verify the target domain is accessible
- Try running individual tools manually: `gau domain.com` and `urlfinder -d domain.com`
- Domain might be new or have limited web presence

**Tools taking too long:**
- Use `--no-urlfinder` for faster GAU-only results
- Set a timeout with `-t 1800` (30 minutes)
- Press `Ctrl+C` to interrupt and use partial results

**Large domains timing out:**
- Remove timeout completely (default behavior)
- Run tools separately with `--no-gau` or `--no-urlfinder`
- Be patient - enterprise domains can take 30+ minutes

## 🎯 Performance Tips

### For Large Domains (Fortune 500, Government)
```bash
# Let it run without timeout (recommended)
python3 dictionary_builder.py -i large-corp.com -o large_dict.txt

# Or run tools separately
python3 dictionary_builder.py -i large-corp.com -o gau_dict.txt --no-urlfinder
python3 dictionary_builder.py -i large-corp.com -o url_dict.txt --no-gau
```

### For Quick Reconnaissance
```bash
# GAU only (faster)
python3 dictionary_builder.py -i target.com -o quick_dict.txt --no-urlfinder

# With timeout
python3 dictionary_builder.py -i target.com -o quick_dict.txt -t 600
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/your-username/dictionary-builder.git
cd dictionary-builder
python3 dictionary_builder.py --test-tools
python3 dictionary_builder.py -i test.com -o test_output.txt
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⭐ Credits

- **GAU**: [github.com/lc/gau](https://github.com/lc/gau) - URL gathering from multiple sources
- **URLFinder**: [github.com/projectdiscovery/urlfinder](https://github.com/projectdiscovery/urlfinder) - Project Discovery: For their amazing security tool ecosystem

## 🎯 Use Cases

- **Bug Bounty Hunting**: Generate target-specific wordlists for directory brute-forcing
- **Penetration Testing**: Create custom dictionaries based on target's actual web assets
- **Red Team Operations**: Build reconnaissance wordlists for specific targets
- **Security Research**: Analyze web application structures and attack surfaces
- **Asset Discovery**: Map out organizational web presence and hidden endpoints

### Processing Time
- **GAU**: Usually 1-10 minutes for most domains
- **URLFinder**: Can take 5-30+ minutes for large domains
- **Combined**: Recommended for comprehensive coverage

---

**⚠️ Disclaimer**: This tool is for educational and authorized security testing purposes only. Always ensure you have proper authorization before testing any systems.

**📧 Contact**: Found a bug? Have a feature request? Open an issue on GitHub!
