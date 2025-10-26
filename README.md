# Chair Flying - Aviation Training Practice

A Python application that helps pilots practice "chair flying" by presenting random maneuvers and emergency scenarios at configurable intervals. Perfect for memorizing flows and procedures for aviation training.

## Features

- **Configurable Maneuvers**: Define your own list of maneuvers and emergency scenarios
- **Separate Configuration**: Application settings separate from maneuver list
- **Random Intervals**: Presents maneuvers at random time intervals (configurable)
- **Type Classification**: Categorize maneuvers by type (emergency, maneuver, etc.)
- **Display Options**: Control what information is shown during practice
- **Progress Tracking**: Mark maneuvers as completed or for follow-up
- **Session History**: Maintains a history of all practiced maneuvers
- **Follow-up List**: Automatically tracks maneuvers that need more practice

## Installation

This application requires Python 3.7 or higher and uses only the standard library.

```bash
# Clone the repository
git clone https://github.com/corygehr/chair-flying.git
cd chair-flying

# No additional dependencies needed!
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

Create a `maneuvers.json` file with your maneuvers. You can use the provided `example_maneuvers.json` as a template:

```bash
cp example_maneuvers.json maneuvers.json
```

The maneuvers file is a JSON array:

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
    "description": "Demonstrate recognition and recovery from power-off stall"
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
- `description`: Description of the maneuver (optional)

## Usage

### Basic Usage

```bash
python chair_flying.py
```

### Custom Configuration File

```bash
python chair_flying.py my_custom_config.json
```

### During a Session

1. The application will wait for a random interval (between your configured min/max)
2. A maneuver will be displayed
3. Perform the maneuver mentally ("chair fly" it)
4. Choose an option:
   - **[c]** Completed - Mark as successfully completed
   - **[f]** Follow-up needed - Mark for additional practice
   - **[s]** Skip - Don't record this attempt
   - **[q]** Quit - End the session

### Example Session

```
============================================================
Chair Flying - Aviation Training Practice
============================================================

Loaded 20 maneuvers
Interval: 30-120 seconds

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
  [f] Follow-up needed
  [s] Skip (no recording)
  [q] Quit

Your response: c
✓ Marked as completed
```

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
- Create emergency-only or maneuver-only configurations

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
