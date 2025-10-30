# Chair Flying - Aviation Training Practice

A Python application that helps pilots practice "chair flying" by presenting random maneuvers and emergency scenarios at configurable intervals. Perfect for memorizing flows and procedures for aviation training.

## Features

- **Configurable Maneuvers**: Define your own list of maneuvers and emergency scenarios
- **Separate Configuration**: Application settings separate from maneuver list
- **Interactive Selection**: Choose at startup which maneuvers to practice (Private, Commercial, or All) and whether to include emergencies
- **Maneuver Classification**: Categorize maneuvers by pilot certification level (Private, Commercial)
- **Random Intervals**: Presents maneuvers at random time intervals (configurable)
- **Type Classification**: Categorize maneuvers by type (emergency, maneuver, etc.)
- **Display Options**: Control what information is shown during practice
- **Progress Tracking**: Mark maneuvers as completed or for follow-up
- **Session History**: Maintains a history of all practiced maneuvers
- **Follow-up List**: Automatically tracks maneuvers that need more practice

## Quick Start for Non-Developers

**New to Python?** We've made it easy for you! 

👉 **[Read the Quick Start Guide (QUICK_START.md)](QUICK_START.md)** for step-by-step instructions with screenshots and troubleshooting tips.

### Easy Launch Options

#### Windows
Just **double-click** `run_chair_flying.bat` in the chair-flying folder!

#### macOS / Linux
**Double-click** `run_chair_flying.sh` or run it from Terminal: `./run_chair_flying.sh`

These launcher scripts will:
- Check if Python is installed
- Verify your configuration files exist
- Display helpful error messages if something is wrong
- Start the application automatically

### Verify Your Setup

Run the setup verification script to check if everything is configured correctly:

```bash
# Windows
python verify_setup.py

# macOS/Linux
python3 verify_setup.py
```

This checks Python version, configuration files, and maneuvers list validity.

## Installation for Developers

This application requires Python 3.7 or higher and uses only the standard library.

```bash
# Clone the repository
git clone https://github.com/corygehr/chair-flying.git
cd chair-flying

# No additional dependencies needed!

# Run directly with Python
python chair_flying.py
# or
python3 chair_flying.py

# Or use the launcher scripts
# Windows: run_chair_flying.bat
# macOS/Linux: ./run_chair_flying.sh
```

## Configuration

The application uses two separate configuration files:

### 1. Application Configuration (`config.json`)

Create a `config.json` file with your application settings:

```json
{
  "maneuvers_file": "maneuvers.json",
  "interval_min": 30,
  "interval_max": 120,
  "show_next_maneuver_time": true,
  "show_maneuver_type": true,
  "show_maneuver_description": true
}
```

### 2. Maneuvers List (`maneuvers.json`)

Create a `maneuvers.json` file with your maneuvers. The maneuvers file is a JSON array:

```json
[
  {
    "name": "Engine Failure on Takeoff",
    "type": "emergency",
    "description": "Engine fails during takeoff roll or initial climb"
  },
  {
    "name": "Power-Off Stall",
    "type": "maneuver",
    "kind": "private",
    "description": "Demonstrate recognition and recovery from power-off stall"
  },
  {
    "name": "Chandelles",
    "type": "maneuver",
    "kind": "commercial",
    "description": "Maximum performance climbing turn"
  }
]
```

### Configuration Options

#### Application Configuration (`config.json`)

- `maneuvers_file`: Path to the maneuvers JSON file (required)
- `interval_min`: Minimum seconds between maneuvers (optional, default: 30)
- `interval_max`: Maximum seconds between maneuvers (optional, default: 120)
- `show_next_maneuver_time`: Display "Next maneuver in X seconds" message (optional, default: true)
- `show_maneuver_type`: Display the type of maneuver (optional, default: true)
- `show_maneuver_description`: Display the maneuver description (optional, default: true)

#### Maneuvers Configuration (`maneuvers.json`)

Each maneuver object in the array can have:
- `name`: Name of the maneuver (required)
- `type`: Category of maneuver (e.g., "emergency", "maneuver", "normal") (optional)
- `kind`: Pilot certification level for the maneuver ("private", "commercial") (optional, not used for emergencies)
- `description`: Description of the maneuver (optional)
- `phases`: Array of phase objects for multi-phase maneuvers (optional)

##### Multi-Phase Maneuvers

Some maneuvers have multiple phases or variants. For example, an engine fire during startup may have different outcomes depending on whether the engine starts or not. Multi-phase maneuvers allow you to practice different scenarios within a single maneuver.

To create a multi-phase maneuver, add a `phases` array:

```json
{
  "name": "Engine Fire During Startup",
  "type": "emergency",
  "description": "Engine fire occurs during startup procedure",
  "phases": [
    {
      "name": "Engine Starts",
      "description": "Engine successfully starts despite the fire"
    },
    {
      "name": "Engine Fails to Start",
      "description": "Engine does not start"
    }
  ]
}
```

Each phase object can have:
- `name`: Name of the phase (required)
- `description`: Description of the phase (optional)

When practicing a multi-phase maneuver:
1. The initial maneuver is displayed first
2. Instead of `[c] Completed`, you'll see `[n] Next` to proceed to a random phase
3. Selecting `[n]` randomly chooses and displays one of the available phases
4. Once in a phase, the `[c] Completed` option appears
5. After completing, skipping, or marking a phase for review, the application proceeds to wait for the next maneuver (you cannot go back to see other phases of the same maneuver in the same iteration)

## Usage

### Basic Usage

```bash
python chair_flying.py
```

When you start the application, you'll be prompted to select:
1. **Maneuver kind**: Choose which type of maneuvers to practice
   - `[p]` Private pilot maneuvers
   - `[c]` Commercial pilot maneuvers
   - `[e]` Emergencies only
   - `[a]` All maneuvers (default - press Enter)
   
2. **Emergency scenarios**: Choose whether to include emergency scenarios (only asked if you didn't select "Emergencies only")
   - `[y]` Yes, include emergencies (default - press Enter)
   - `[n]` No, exclude emergencies

The application will then filter the maneuvers based on your selections and display a configuration summary before starting the practice session.

### Custom Configuration File

```bash
python chair_flying.py my_custom_config.json
```

### During a Session

1. The application will wait for a random interval (between your configured min/max)
2. A maneuver will be displayed
3. Perform the maneuver mentally ("chair fly" it)
4. Choose an option:
   - **[c]** Completed - Mark as successfully completed (shown for single-phase maneuvers or when in a phase)
   - **[n]** Next - Proceed to a randomly selected phase (shown for multi-phase maneuvers before selecting a phase)
   - **[f]** Mark for review - Mark for additional practice
   - **[s]** Skip - Don't record this attempt
   - **[p]** Permanently skip - Remove this maneuver from the session rotation (requires confirmation)
   - **[q]** Quit - End the session

### Example Session

```
============================================================
Chair Flying - Aviation Training Practice
============================================================

Which maneuvers would you like to practice?
  [p] Private pilot maneuvers
  [c] Commercial pilot maneuvers
  [e] Emergencies only
  [a] All maneuvers (default)

Your choice (p/c/e/a or Enter for all): 

Include emergency scenarios?
  [y] Yes (default)
  [n] No

Your choice (y/n or Enter for yes): 

Configuration Summary:
------------------------------------------------------------
Maneuvers loaded: 24
  - Emergency maneuvers: 11
  - Private pilot maneuvers: 11
  - Commercial pilot maneuvers: 2
Selected kind: All
Emergency scenarios: Included
Interval range: 30-120 seconds
Display options:
  - Show countdown timer: Yes
  - Show maneuver type: Yes
  - Show descriptions: Yes
------------------------------------------------------------

Starting practice session...
Press Ctrl+C to stop at any time.

Next maneuver in 45 seconds...

============================================================
MANEUVER: Engine Failure on Takeoff
Type: EMERGENCY
Description: Engine fails during takeoff roll or initial climb
============================================================

Options:
  [c] Completed
  [f] Mark for review
  [s] Skip (no recording)
  [p] Permanently skip (remove from session)
  [q] Quit

Your response: c
✓ Marked as completed
```

### Permanently Skipping Maneuvers

If you encounter a maneuver that you're not ready to practice or want to exclude from the current session, you can permanently skip it:

1. When a maneuver is displayed, select `[p]` for "Permanently skip"
2. You'll be prompted to confirm: "Are you sure you want to permanently skip '[maneuver name]' for this session?"
3. If you confirm with `y`, the maneuver will be removed from the rotation for the remainder of the session
4. If you cancel with `n`, the maneuver will be displayed again with all options available

**Note:** Permanently skipped maneuvers are only removed for the current session. When you restart the application, all maneuvers will be available again.

## Session History

The application maintains a `maneuver_history.json` file that tracks:
- Timestamp of each practice
- Maneuver name and type
- Completion status

This allows you to:
- Review what you've practiced
- Identify maneuvers that need more work
- Track your progress over time

## Customization Ideas

- Create different configuration files for different training phases
- Adjust intervals for longer or shorter practice sessions
- Add custom maneuver types relevant to your aircraft or training
- Create separate maneuvers files for different training focuses (e.g., emergency-only, private-only, commercial-only)
- Use the interactive prompts at startup to select which maneuvers to practice each session

## Example Configurations

### Quick Practice (Short Intervals)
```json
{
  "maneuvers_file": "maneuvers.json",
  "interval_min": 15,
  "interval_max": 30,
  "show_next_maneuver_time": true,
  "show_maneuver_type": true,
  "show_maneuver_description": true
}
```

### Minimalist Display (No Extra Info)
```json
{
  "maneuvers_file": "maneuvers.json",
  "interval_min": 30,
  "interval_max": 120,
  "show_next_maneuver_time": false,
  "show_maneuver_type": false,
  "show_maneuver_description": false
}
```

### Emergency Focus
Create a separate maneuvers file with only emergency maneuvers:
```json
[
  {
    "name": "Engine Failure on Takeoff",
    "type": "emergency",
    "description": "..."
  }
]
```

Then reference it in your config:
```json
{
  "maneuvers_file": "emergency_maneuvers.json",
  "interval_min": 30,
  "interval_max": 120
}
```

Alternatively, you can use the main maneuvers.json file and select to exclude emergencies when prompted at startup.

### Extended Practice
```json
{
  "maneuvers_file": "maneuvers.json",
  "interval_min": 60,
  "interval_max": 180,
  "show_next_maneuver_time": true,
  "show_maneuver_type": true,
  "show_maneuver_description": true
}
```

## License

See LICENSE file for details.
