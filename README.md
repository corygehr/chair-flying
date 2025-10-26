# Chair Flying - Aviation Training Practice

A Python application that helps pilots practice "chair flying" by presenting random maneuvers and emergency scenarios at configurable intervals. Perfect for memorizing flows and procedures for aviation training.

## Features

- **Configurable Maneuvers**: Define your own list of maneuvers and emergency scenarios
- **Random Intervals**: Presents maneuvers at random time intervals (configurable)
- **Type Classification**: Categorize maneuvers by type (emergency, maneuver, etc.)
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

Create a `maneuvers.json` file in the same directory as the application. You can use the provided `example_maneuvers.json` as a template:

```bash
cp example_maneuvers.json maneuvers.json
```

The configuration file has the following structure:

```json
{
  "interval_min": 30,
  "interval_max": 120,
  "maneuvers": [
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
}
```

### Configuration Options

- `interval_min`: Minimum seconds between maneuvers (default: 30)
- `interval_max`: Maximum seconds between maneuvers (default: 120)
- `maneuvers`: Array of maneuver objects
  - `name`: Name of the maneuver (required)
  - `type`: Category of maneuver (e.g., "emergency", "maneuver", "normal")
  - `description`: Optional description of the maneuver

## Usage

### Basic Usage

```bash
python chair_flying.py
```

### Custom Configuration File

```bash
python chair_flying.py my_custom_maneuvers.json
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
  "interval_min": 15,
  "interval_max": 30,
  "maneuvers": [...]
}
```

### Emergency Focus
Only include maneuvers with `"type": "emergency"`

### Extended Practice
```json
{
  "interval_min": 60,
  "interval_max": 180,
  "maneuvers": [...]
}
```

## License

See LICENSE file for details.
