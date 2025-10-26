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
        self.maneuvers = self.load_maneuvers()
        self.tracker = ManeuverTracker()
    
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
    
    def select_maneuver(self) -> Dict:
        """Select a random maneuver from the maneuvers list."""
        if not self.maneuvers:
            raise ValueError("No maneuvers configured!")
        return random.choice(self.maneuvers)
    
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
            print("  [q] Quit")
            
            response = input("\nYour response: ").strip().lower()
            
            valid_responses = ['f', 's', 'q']
            if show_next:
                valid_responses.append('n')
            elif show_complete:
                valid_responses.append('c')
            
            if response in valid_responses:
                return response
            else:
                options = ", ".join(valid_responses)
                print(f"Invalid input. Please choose {options}.")
    
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
    
    def run(self):
        """Run the main chair flying loop."""
        print("=" * 60)
        print("Chair Flying - Aviation Training Practice")
        print("=" * 60)
        print(f"\nLoaded {len(self.maneuvers)} maneuvers")
        min_interval = self.config.get("interval_min", self.DEFAULT_INTERVAL_MIN)
        max_interval = self.config.get("interval_max", self.DEFAULT_INTERVAL_MAX)
        print(f"Interval: {min_interval}-{max_interval} seconds")
        print("\nStarting practice session...")
        print("Press Ctrl+C to stop at any time.\n")
        
        try:
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
                        print("\nEnding practice session. Good work!")
                        return  # Exit both loops
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
        
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Good work!")
        
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
            print("\nNo maneuvers marked for review. Great job!")
        
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
