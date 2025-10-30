# Chair Flying - Unit Tests

This directory contains unit tests for the Chair Flying application.

## Running Tests

### Run All Tests

```bash
python -m unittest discover -s test -p "test_*.py"
```

### Run Tests with Verbose Output

```bash
python -m unittest discover -s test -p "test_*.py" -v
```

### Run a Specific Test File

```bash
python -m unittest test.test_configuration
python -m unittest test.test_maneuver_tracker
python -m unittest test.test_chair_flying
```

### Run a Specific Test Case

```bash
python -m unittest test.test_configuration.TestConfiguration.test_basic_configuration
```

## Test Structure

- `test_configuration.py` - Tests for the Configuration class
- `test_maneuver_tracker.py` - Tests for the ManeuverTracker class  
- `test_chair_flying.py` - Tests for the ChairFlying class and core application logic

## Requirements

- Python 3.8 or higher
- No external dependencies required (uses Python's built-in `unittest` module)

## Continuous Integration

Tests are automatically run on every pull request via GitHub Actions. The workflow tests against multiple Python versions (3.8-3.12) to ensure compatibility.

## Adding New Tests

When adding new features or fixing bugs:

1. Add corresponding test cases to the appropriate test file
2. Ensure all tests pass locally before submitting a PR
3. Follow the existing test structure and naming conventions
4. Use descriptive test method names that explain what is being tested

## Code Coverage

While no specific coverage tool is required, aim for comprehensive test coverage:
- Test both success and failure cases
- Test edge cases and boundary conditions
- Test error handling and validation logic
