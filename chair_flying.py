#!/usr/bin/env python3
"""
Chair Flying - Aviation Training Maneuver Memorization Tool

This application helps pilots practice chair flying by presenting random
maneuvers and scenarios at configurable intervals.
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ManeuverTracker:
    """Tracks maneuver completion status and follow-ups."""
    
    def __init__(self, history_file: str = "maneuver_history.json"):
        self.history_file = Path(history_file)
        self.history: List[Dict] = []
        self.load_history()
    
    def load_history(self):
        """Load history from file if it exists."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.history = []
    
    def save_history(self):
        """Save history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def record_maneuver(self, maneuver: Dict, status: str, phase: Optional[Dict] = None):
        """Record a maneuver attempt with timestamp and status."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "maneuver": maneuver["name"],
            "type": maneuver.get("type", "normal"),
            "status": status
        }
        if phase:
            entry["phase"] = phase["name"]
        self.history.append(entry)
        self.save_history()
    
    def get_follow_ups(self) -> List[Dict]:
        """Get list of maneuvers marked for review."""
        return [entry for entry in self.history if entry["status"] == "review"]


class ChairFlying:
    """Main application for chair flying practice."""
    
    # Default interval settings
    DEFAULT_INTERVAL_MIN = 30
    DEFAULT_INTERVAL_MAX = 120
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.all_maneuvers = self.load_maneuvers()
        self.maneuvers = []  # Will be set based on user selection
        self.tracker = ManeuverTracker()
        self.include_emergencies = None
        self.maneuver_kind = None
        self.skipped_maneuvers = []  # Track permanently skipped maneuvers for the session
    
    def load_config(self) -> Dict:
        """Load application configuration from JSON file."""
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Configuration file '{self.config_file}' not found. "
                "Please create it with your settings."
            )
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        # Validate configuration
        if "maneuvers_file" not in config:
            raise ValueError("Configuration missing required key: maneuvers_file")
        
        # Validate interval configuration - both or neither should be provided
        has_min = "interval_min" in config
        has_max = "interval_max" in config
        
        if has_min != has_max:
            raise ValueError(
                "Both interval_min and interval_max must be provided together, "
                "or neither (to use defaults)"
            )
        
        if has_min and has_max:
            if config["interval_min"] > config["interval_max"]:
                raise ValueError("interval_min must be less than or equal to interval_max")
        
        # Set default values for display options
        config.setdefault("show_next_maneuver_time", True)
        config.setdefault("show_maneuver_type", True)
        config.setdefault("show_maneuver_description", True)
        
        # Validate emergency_probability if provided
        if "emergency_probability" in config:
            prob = config["emergency_probability"]
            if not isinstance(prob, (int, float)):
                raise ValueError("emergency_probability must be a number")
            if prob < 0 or prob > 100:
                raise ValueError("emergency_probability must be between 0 and 100")
        
        return config
    
    def load_maneuvers(self) -> List[Dict]:
        """Load maneuvers from separate JSON file."""
        maneuvers_file = Path(self.config["maneuvers_file"])
        
        if not maneuvers_file.exists():
            raise FileNotFoundError(
                f"Maneuvers file '{maneuvers_file}' not found. "
                "Please create it with your maneuvers."
            )
        
        with open(maneuvers_file, 'r') as f:
            maneuvers = json.load(f)
        
        if not isinstance(maneuvers, list):
            raise ValueError("Maneuvers file must contain a JSON array of maneuvers")
        
        if not maneuvers:
            raise ValueError("Maneuvers file must contain at least one maneuver")
        
        return maneuvers
    
    def get_random_interval(self) -> int:
        """Get random interval between min and max from config."""
        min_interval = self.config.get("interval_min", self.DEFAULT_INTERVAL_MIN)
        max_interval = self.config.get("interval_max", self.DEFAULT_INTERVAL_MAX)
        return random.randint(min_interval, max_interval)
    
    def prompt_maneuver_kind(self) -> str:
        """Prompt user to select which kind of maneuvers to practice.
        
        Returns:
            str: 'private', 'commercial', 'emergency', or 'all'
        """
        print("\nWhich maneuvers would you like to practice?")
        print("  [p] Private pilot maneuvers")
        print("  [c] Commercial pilot maneuvers")
        print("  [e] Emergencies only")
        print("  [a] All maneuvers (default)")
        
        while True:
            response = input("\nYour choice (p/c/e/a or Enter for all): ").strip().lower()
            
            if response == '' or response == 'a' or response == 'all':
                return 'all'
            elif response == 'p' or response == 'private':
                return 'private'
            elif response == 'c' or response == 'commercial':
                return 'commercial'
            elif response == 'e' or response == 'emergency' or response == 'emergencies':
                return 'emergency'
            else:
                print("Invalid choice. Please select p, c, e, a, or press Enter for all.")
    
    def prompt_include_emergencies(self) -> bool:
        """Prompt user whether to include emergency scenarios.
        
        Returns:
            bool: True to include emergencies, False to exclude
        """
        print("\nInclude emergency scenarios?")
        print("  [y] Yes (default)")
        print("  [n] No")
        
        while True:
            response = input("\nYour choice (y/n or Enter for yes): ").strip().lower()
            
            if response == '' or response == 'y' or response == 'yes':
                return True
            elif response == 'n' or response == 'no':
                return False
            else:
                print("Invalid choice. Please select y, n, or press Enter for yes.")
    
    def filter_maneuvers(self):
        """Filter maneuvers based on user preferences."""
        filtered = self.all_maneuvers.copy()
        
        # Filter by kind
        if self.maneuver_kind == 'emergency':
            # Only emergencies
            filtered = [m for m in filtered if m.get("type", "").lower() == "emergency"]
        elif self.maneuver_kind != 'all':
            # Keep emergencies (they don't have a kind) and maneuvers matching the selected kind
            filtered = [
                m for m in filtered
                if m.get("type", "").lower() == "emergency" or 
                   m.get("kind", "").lower() == self.maneuver_kind
            ]
        
        # Filter out emergencies if user chose not to include them (only applicable when not emergency-only mode)
        if not self.include_emergencies and self.maneuver_kind != 'emergency':
            filtered = [m for m in filtered if m.get("type", "").lower() != "emergency"]
        
        # Ensure we have at least one maneuver
        if not filtered:
            raise ValueError(
                "No maneuvers match your selection criteria. "
                "Please adjust your preferences or add more maneuvers."
            )
        
        self.maneuvers = filtered
    
    def select_maneuver(self) -> Dict:
        """Select a random maneuver from the maneuvers list.
        
        If emergency_probability is configured, uses weighted selection to control
        how often emergency maneuvers appear. Otherwise, uses pure random selection.
        """
        if not self.maneuvers:
            raise ValueError("No maneuvers configured!")
        
        # Check if emergency_probability is configured
        emergency_prob = self.config.get("emergency_probability")
        
        # If no probability configured, use standard random selection
        if emergency_prob is None:
            return random.choice(self.maneuvers)
        
        # Separate emergency and non-emergency maneuvers
        emergency_maneuvers = [m for m in self.maneuvers if m.get("type", "").lower() == "emergency"]
        non_emergency_maneuvers = [m for m in self.maneuvers if m.get("type", "").lower() != "emergency"]
        
        # If no emergencies or no non-emergencies, fall back to random selection
        if not emergency_maneuvers or not non_emergency_maneuvers:
            return random.choice(self.maneuvers)
        
        # Use probability to determine whether to select an emergency
        if random.random() < emergency_prob / 100:
            return random.choice(emergency_maneuvers)
        else:
            return random.choice(non_emergency_maneuvers)
    
    def select_phase(self, maneuver: Dict) -> Optional[Dict]:
        """Select a random phase from the maneuver's phases."""
        if "phases" not in maneuver or not maneuver["phases"]:
            return None
        return random.choice(maneuver["phases"])
    
    def display_maneuver(self, maneuver: Dict, phase: Optional[Dict] = None):
        """Display maneuver information to the user."""
        print("\n" + "=" * 60)
        print(f"MANEUVER: {maneuver['name']}")
        
        # Show type if configured
        if self.config.get("show_maneuver_type", True):
            print(f"Type: {maneuver.get('type', 'normal').upper()}")
        
        # Show description if configured and available
        if self.config.get("show_maneuver_description", True) and "description" in maneuver:
            print(f"Description: {maneuver['description']}")
        
        # Show phase information if provided
        if phase:
            print(f"\nPHASE: {phase['name']}")
            if self.config.get("show_maneuver_description", True) and "description" in phase:
                print(f"Phase Description: {phase['description']}")
        
        print("=" * 60)
    
    def get_user_response(self, show_next: bool = False, show_complete: bool = True) -> str:
        """Get user response for maneuver completion.
        
        Args:
            show_next: If True, shows [n] Next instead of [c] Completed
            show_complete: If True, shows [c] Completed (only used when show_next is False)
        """
        while True:
            print("\nOptions:")
            if show_next:
                print("  [n] Next")
            elif show_complete:
                print("  [c] Completed")
            print("  [f] Mark for review")
            print("  [s] Skip (no recording)")
            print("  [p] Permanently skip (remove from session)")
            print("  [q] Quit")
            
            response = input("\nYour response: ").strip().lower()
            
            valid_responses = ['f', 's', 'p', 'q']
            if show_next:
                valid_responses.append('n')
            elif show_complete:
                valid_responses.append('c')
            
            if response in valid_responses:
                return response
            else:
                options = ", ".join(valid_responses)
                print(f"Invalid input. Please choose {options}.")
    
    def confirm_permanent_skip(self, maneuver: Dict) -> bool:
        """Prompt user to confirm permanent skip of a maneuver.
        
        Args:
            maneuver: The maneuver to confirm skipping
            
        Returns:
            bool: True if user confirms, False otherwise
        """
        print(f"\n⚠️  Are you sure you want to permanently skip '{maneuver['name']}' for this session?")
        print("This maneuver will not appear again until you restart the application.")
        
        while True:
            response = input("Confirm (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
    
    def permanently_skip_maneuver(self, maneuver: Dict):
        """Permanently skip a maneuver for the current session.
        
        Args:
            maneuver: The maneuver to permanently skip
        """
        # Add to skipped list
        self.skipped_maneuvers.append(maneuver)
        
        # Remove from active maneuvers list
        self.maneuvers = [m for m in self.maneuvers if m != maneuver]
        
        print(f"✗ '{maneuver['name']}' has been permanently removed from this session.")
        
        # Check if any maneuvers remain
        if not self.maneuvers:
            print("\n⚠️  No maneuvers remaining in the rotation!")
            return False
        else:
            print(f"({len(self.maneuvers)} maneuver(s) remaining)")
            return True
    
    def wait_with_countdown(self, interval: int):
        """Wait for the specified interval with a countdown or progress indicator."""
        show_countdown = self.config.get("show_next_maneuver_time", True)
        
        if show_countdown:
            # Show countdown timer
            import sys
            for remaining in range(interval, 0, -1):
                sys.stdout.write(f"\rNext maneuver in {remaining} seconds...  ")
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write("\r" + " " * 50 + "\r")  # Clear the line
            sys.stdout.flush()
        else:
            # Show progress indicator (dots) without countdown
            import sys
            sys.stdout.write("\nWaiting")
            sys.stdout.flush()
            for i in range(interval):
                time.sleep(1)
                sys.stdout.write(".")
                sys.stdout.flush()
            sys.stdout.write("\r" + " " * 50 + "\r")  # Clear the line
            sys.stdout.flush()
    
    def show_config_summary(self):
        """Display a summary of all configuration options."""
        print("\nConfiguration Summary:")
        print("-" * 60)
        
        # Maneuvers loaded
        total_maneuvers = len(self.maneuvers)
        emergency_count = sum(1 for m in self.maneuvers if m.get("type", "").lower() == "emergency")
        non_emergency_count = total_maneuvers - emergency_count
        
        # Count by kind
        private_count = sum(1 for m in self.maneuvers if m.get("kind", "").lower() == "private")
        commercial_count = sum(1 for m in self.maneuvers if m.get("kind", "").lower() == "commercial")
        
        print(f"Maneuvers loaded: {total_maneuvers}")
        print(f"  - Emergency maneuvers: {emergency_count}")
        print(f"  - Private pilot maneuvers: {private_count}")
        print(f"  - Commercial pilot maneuvers: {commercial_count}")
        
        # User selections
        if self.maneuver_kind == 'emergency':
            kind_display = "Emergencies only"
        else:
            kind_display = self.maneuver_kind.capitalize() if self.maneuver_kind else "All"
        emergencies_display = "Included" if self.include_emergencies else "Excluded"
        print(f"Selected kind: {kind_display}")
        if self.maneuver_kind != 'emergency':
            print(f"Emergency scenarios: {emergencies_display}")
        
        # Interval settings
        min_interval = self.config.get("interval_min", self.DEFAULT_INTERVAL_MIN)
        max_interval = self.config.get("interval_max", self.DEFAULT_INTERVAL_MAX)
        print(f"Interval range: {min_interval}-{max_interval} seconds")
        
        # Emergency probability setting
        emergency_prob = self.config.get("emergency_probability")
        if emergency_prob is not None:
            print(f"Emergency probability: {emergency_prob}%")
        
        # Display options
        show_time = self.config.get("show_next_maneuver_time", True)
        show_type = self.config.get("show_maneuver_type", True)
        show_desc = self.config.get("show_maneuver_description", True)
        
        print(f"Display options:")
        print(f"  - Show countdown timer: {'Yes' if show_time else 'No'}")
        print(f"  - Show maneuver type: {'Yes' if show_type else 'No'}")
        print(f"  - Show descriptions: {'Yes' if show_desc else 'No'}")
        
        print("-" * 60)
    
    def run(self):
        """Run the main chair flying loop."""
        print("=" * 60)
        print("Chair Flying -  Checklist Memorization Aid")
        print("=" * 60)
        
        # Prompt user for preferences
        self.maneuver_kind = self.prompt_maneuver_kind()
        
        # Only ask about emergencies if not in emergency-only mode
        if self.maneuver_kind == 'emergency':
            self.include_emergencies = True  # Implied when emergency-only is selected
        else:
            self.include_emergencies = self.prompt_include_emergencies()
        
        # Filter maneuvers based on user preferences
        try:
            self.filter_maneuvers()
        except ValueError as e:
            print(f"\nError: {e}")
            return
        
        # Display configuration summary
        self.show_config_summary()
        
        print("\nStarting practice session...")
        print("Press Ctrl+C to stop at any time.\n")
        
        try:
            quit_requested = False
            while True:
                # Wait for random interval with countdown or progress indicator
                interval = self.get_random_interval()
                self.wait_with_countdown(interval)
                
                # Select and display maneuver
                maneuver = self.select_maneuver()
                current_phase = None
                has_phases = "phases" in maneuver and maneuver["phases"]
                
                # Inner loop for handling phases
                while True:
                    self.display_maneuver(maneuver, current_phase)
                    
                    # Determine what options to show
                    # For multi-phase maneuvers without a phase selected, show "Next" instead of "Completed"
                    # For single-phase maneuvers or when already in a phase, show "Completed"
                    show_next = has_phases and current_phase is None
                    show_complete = not show_next
                    
                    # Get user response
                    response = self.get_user_response(show_next=show_next, show_complete=show_complete)
                    
                    if response == 'q':
                        print("\nEnding practice session.")
                        quit_requested = True
                        break  # Exit inner loop
                    elif response == 'n':
                        # Select a random phase (only reachable if maneuver has phases)
                        current_phase = self.select_phase(maneuver)
                        if current_phase:
                            print(f"\n→ Proceeding to next phase...")
                            continue  # Show the phase
                        else:
                            # This should never happen if has_phases check is working correctly
                            print("Error: No phases available. Proceeding to next maneuver.")
                            break
                    elif response == 'c':
                        self.tracker.record_maneuver(maneuver, "completed", current_phase)
                        print("✓ Marked as completed")
                        break
                    elif response == 'f':
                        self.tracker.record_maneuver(maneuver, "review", current_phase)
                        print("⚠ Marked for review")
                        break
                    elif response == 's':
                        print("Skipped (not recorded)")
                        break
                    elif response == 'p':
                        # Permanently skip this maneuver
                        if self.confirm_permanent_skip(maneuver):
                            has_maneuvers = self.permanently_skip_maneuver(maneuver)
                            if not has_maneuvers:
                                # No more maneuvers, end session
                                print("\nEnding practice session - no maneuvers remaining.")
                                quit_requested = True
                            break  # Exit inner loop
                        else:
                            # User cancelled, show the maneuver again
                            print("Permanent skip cancelled.")
                            continue
                
                # Check if user wants to quit
                if quit_requested:
                    break  # Exit outer loop
        
        except KeyboardInterrupt:
            print("\n\nSession interrupted.")
        
        # Show summary
        self.show_summary()
    
    def show_summary(self):
        """Show session summary and follow-ups."""
        print("\n" + "=" * 60)
        print("SESSION SUMMARY")
        print("=" * 60)
        
        follow_ups = self.tracker.get_follow_ups()
        if follow_ups:
            print(f"\nManeuvers marked for review ({len(follow_ups)}):")
            for entry in follow_ups:
                print(f"  - {entry['maneuver']} ({entry['type']})")
        else:
            print("\nNo maneuvers marked for review.")
        
        print(f"\nTotal history entries: {len(self.tracker.history)}")


def main():
    """Entry point for the application."""
    import sys
    
    config_file = "config.json"
    
    # Allow custom config file as command line argument
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    try:
        app = ChairFlying(config_file)
        app.run()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease create config.json and maneuvers.json files.")
        print("See config.json and example_maneuvers.json for the format.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
