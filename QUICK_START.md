# Quick Start Guide for Non-Developers

This guide will help you get started with Chair Flying even if you've never used Python before.

## What You'll Need

1. **A Computer** - Windows, macOS, or Linux
2. **Python 3.7 or higher** - Free programming language (we'll show you how to install it)
3. **5-10 minutes** - For setup

## Step-by-Step Installation

### Step 1: Install Python

#### Windows

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow "Download Python" button
3. Run the downloaded installer
4. **IMPORTANT:** Check the box that says "Add Python to PATH" at the bottom of the installer
5. Click "Install Now"
6. Wait for installation to complete
7. Click "Close"

#### macOS

**Option 1: Official Installer (Recommended for beginners)**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow "Download Python" button
3. Open the downloaded .pkg file
4. Follow the installation wizard
5. Click "Continue" and "Install"

**Option 2: Using Homebrew (if you have it installed)**
1. Open Terminal
2. Type: `brew install python3`
3. Press Enter

#### Linux

Open your terminal and run:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3
```

**Fedora:**
```bash
sudo dnf install python3
```

**Arch Linux:**
```bash
sudo pacman -S python
```

### Step 2: Download Chair Flying

1. Go to [github.com/corygehr/chair-flying](https://github.com/corygehr/chair-flying)
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file to a folder on your computer (e.g., `Documents/chair-flying`)

**Alternative (if you have git):**
```bash
git clone https://github.com/corygehr/chair-flying.git
cd chair-flying
```

### Step 3: Verify Your Files

Make sure your folder contains these files:
- `chair_flying.py` - The main program
- `config.json` - Configuration file
- `maneuvers.json` - List of maneuvers
- `run_chair_flying.bat` (Windows) or `run_chair_flying.sh` (macOS/Linux) - Launcher script
- `README.md` - Full documentation

## Running Chair Flying

### Windows

1. Open the `chair-flying` folder
2. **Double-click** `run_chair_flying.bat`
3. A black window will open and the program will start!

### macOS

1. Open the `chair-flying` folder
2. **Right-click** on `run_chair_flying.sh`
3. Select "Open With" → "Terminal" (or "Other..." → "Terminal")
4. If you see a security warning, go to System Preferences → Security & Privacy and click "Open Anyway"

**Alternative method:**
1. Open Terminal
2. Type `cd ` (with a space after cd)
3. Drag the chair-flying folder into the Terminal window
4. Press Enter
5. Type `./run_chair_flying.sh` and press Enter

### Linux

1. Open your file manager and navigate to the `chair-flying` folder
2. **Double-click** `run_chair_flying.sh`
   - If it asks, choose "Run in Terminal" or "Execute"

**Alternative method:**
1. Open Terminal
2. Navigate to the folder: `cd /path/to/chair-flying`
3. Run: `./run_chair_flying.sh`

## What to Expect

When you run the program, you'll see:

1. **Maneuver Selection** - Choose which types of maneuvers to practice
2. **Emergency Scenarios** - Choose whether to include emergencies
3. **Configuration Summary** - Review your settings
4. **Practice Session** - Maneuvers will be displayed at random intervals

### During Practice

When a maneuver appears, you have these options:
- **[c]** Completed - You successfully chair-flew the maneuver
- **[f]** Mark for review - This maneuver needs more practice
- **[s]** Skip - Don't record this one
- **[p]** Permanently skip - Remove from this session
- **[q]** Quit - End your practice session

## Customizing Your Practice

### Changing Time Intervals

Edit `config.json` in any text editor (Notepad, TextEdit, etc.):

```json
{
  "maneuvers_file": "maneuvers.json",
  "interval_min": 30,    ← Change this to your minimum seconds
  "interval_max": 120,   ← Change this to your maximum seconds
  "show_next_maneuver_time": true,
  "show_maneuver_type": true,
  "show_maneuver_description": true
}
```

### Adding Your Own Maneuvers

Edit `maneuvers.json` in any text editor:

```json
[
  {
    "name": "Your Maneuver Name",
    "type": "maneuver",
    "kind": "private",
    "description": "Description of what to do"
  }
]
```

- `type` can be: "maneuver" or "emergency"
- `kind` can be: "private" or "commercial" (for maneuvers only)

## Troubleshooting

### "Python is not installed or not in PATH"

**Problem:** Python isn't installed or wasn't added to PATH during installation.

**Solution:**
1. Reinstall Python following Step 1 above
2. On Windows, make sure to check "Add Python to PATH"
3. On macOS/Linux, Python is usually in PATH automatically

### "config.json not found"

**Problem:** You're running the script from the wrong folder.

**Solution:**
1. Make sure you're in the chair-flying folder
2. The launcher script must be in the same folder as `config.json`

### "Permission Denied" (macOS/Linux)

**Problem:** The script doesn't have permission to run.

**Solution:**
Open Terminal and run:
```bash
chmod +x run_chair_flying.sh
```

### "Python 3.7 or higher is required"

**Problem:** Your Python version is too old.

**Solution:**
1. Update Python using the installation instructions in Step 1
2. On Linux, you might need to use `python3` instead of `python`

### Program Crashes or Shows Errors

**Problem:** Something went wrong with the program.

**Solution:**
1. Check that your `config.json` is valid JSON (no missing commas or brackets)
2. Check that your `maneuvers.json` is valid JSON
3. Make sure `maneuvers.json` has at least one maneuver
4. Try running the program from the command line to see detailed error messages

### Can't Double-Click to Run (macOS)

**Problem:** macOS security settings prevent running downloaded scripts.

**Solution:**
1. Right-click the script → "Open With" → "Terminal"
2. Or: System Preferences → Security & Privacy → Allow the script to run
3. Or: Use the Terminal method described above

## Getting Help

If you're still having trouble:

1. **Read the Full Documentation** - Check `README.md` for more details
2. **Check for Updates** - Download the latest version from GitHub
3. **Ask for Help** - Open an issue on the GitHub repository with:
   - Your operating system (Windows, macOS, Linux)
   - Your Python version (run `python --version` or `python3 --version`)
   - The exact error message you're seeing
   - What you were doing when the error occurred

## Tips for New Users

- **Start with default settings** - The included config.json works great for beginners
- **Practice in short sessions** - 10-15 minutes is often enough
- **Use the review feature** - Mark maneuvers you struggle with for focused practice
- **Adjust intervals** - Start with longer intervals (60-120 seconds) if you need more time
- **Create custom configurations** - Make different config files for different training focuses

## Next Steps

Once you're comfortable with the basics:

1. Create custom maneuver lists for specific training phases
2. Adjust intervals to challenge yourself
3. Experiment with different display options
4. Track your progress using the history file

Happy chair flying! ✈️
