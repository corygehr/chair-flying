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
    
    def record_maneuver(self, maneuver: Dict, status: str):
        """Record a maneuver attempt with timestamp and status."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "maneuver": maneuver["name"],
            "type": maneuver.get("type", "normal"),
            "status": status
        }
        self.history.append(entry)
        self.save_history()
    
    def get_follow_ups(self) -> List[Dict]:
        """Get list of maneuvers marked for follow-up."""
        return [entry for entry in self.history if entry["status"] == "follow-up"]


class ChairFlying:
    """Main application for chair flying practice."""
    
    def __init__(self, config_file: str = "maneuvers.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.tracker = ManeuverTracker()
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file."""
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Configuration file '{self.config_file}' not found. "
                "Please create it with your maneuvers."
            )
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        # Validate configuration
        required_keys = ["maneuvers", "interval_min", "interval_max"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Configuration missing required key: {key}")
        
        return config
    
    def get_random_interval(self) -> int:
        """Get random interval between min and max from config."""
        min_interval = self.config.get("interval_min", 30)
        max_interval = self.config.get("interval_max", 120)
        return random.randint(min_interval, max_interval)
    
    def select_maneuver(self) -> Dict:
        """Select a random maneuver from the configuration."""
        maneuvers = self.config["maneuvers"]
        if not maneuvers:
            raise ValueError("No maneuvers configured!")
        return random.choice(maneuvers)
    
    def display_maneuver(self, maneuver: Dict):
        """Display maneuver information to the user."""
        print("\n" + "=" * 60)
        print(f"MANEUVER: {maneuver['name']}")
        print(f"Type: {maneuver.get('type', 'normal').upper()}")
        if "description" in maneuver:
            print(f"Description: {maneuver['description']}")
        print("=" * 60)
    
    def get_user_response(self) -> str:
        """Get user response for maneuver completion."""
        while True:
            print("\nOptions:")
            print("  [c] Completed")
            print("  [f] Follow-up needed")
            print("  [s] Skip (no recording)")
            print("  [q] Quit")
            
            response = input("\nYour response: ").strip().lower()
            
            if response in ['c', 'f', 's', 'q']:
                return response
            else:
                print("Invalid input. Please choose c, f, s, or q.")
    
    def run(self):
        """Run the main chair flying loop."""
        print("=" * 60)
        print("Chair Flying - Aviation Training Practice")
        print("=" * 60)
        print(f"\nLoaded {len(self.config['maneuvers'])} maneuvers")
        print(f"Interval: {self.config['interval_min']}-{self.config['interval_max']} seconds")
        print("\nStarting practice session...")
        print("Press Ctrl+C to stop at any time.\n")
        
        try:
            while True:
                # Wait for random interval
                interval = self.get_random_interval()
                print(f"\nNext maneuver in {interval} seconds...")
                time.sleep(interval)
                
                # Select and display maneuver
                maneuver = self.select_maneuver()
                self.display_maneuver(maneuver)
                
                # Get user response
                response = self.get_user_response()
                
                if response == 'q':
                    print("\nEnding practice session. Good work!")
                    break
                elif response == 'c':
                    self.tracker.record_maneuver(maneuver, "completed")
                    print("✓ Marked as completed")
                elif response == 'f':
                    self.tracker.record_maneuver(maneuver, "follow-up")
                    print("⚠ Marked for follow-up")
                elif response == 's':
                    print("Skipped (not recorded)")
        
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
            print(f"\nManeuvers marked for follow-up ({len(follow_ups)}):")
            for entry in follow_ups:
                print(f"  - {entry['maneuver']} ({entry['type']})")
        else:
            print("\nNo maneuvers marked for follow-up. Great job!")
        
        print(f"\nTotal history entries: {len(self.tracker.history)}")


def main():
    """Entry point for the application."""
    import sys
    
    config_file = "maneuvers.json"
    
    # Allow custom config file as command line argument
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    try:
        app = ChairFlying(config_file)
        app.run()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease create a maneuvers.json file with your configuration.")
        print("See example_maneuvers.json for the format.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
