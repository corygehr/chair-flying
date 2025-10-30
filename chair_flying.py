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


class Configuration:
    """Configuration class for Chair Flying application.
    
    Encapsulates all configuration parameters with validation and type safety.
    """
    
    def __init__(self, config_dict: Dict):
        """Initialize configuration from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration parameters
            
        Raises:
            ValueError: If configuration is invalid
        """
        self._validate_and_set(config_dict)
    
    def _validate_and_set(self, config: Dict):
        """Validate and set configuration parameters.
        
        Args:
            config: Dictionary containing configuration parameters
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate required fields
        if "maneuvers_file" not in config:
            raise ValueError("Configuration missing required key: maneuvers_file")
        
        self._maneuvers_file = config["maneuvers_file"]
        
        # Validate interval configuration - both or neither should be provided
        has_min = "interval_min_sec" in config
        has_max = "interval_max_sec" in config
        
        if has_min != has_max:
            raise ValueError(
                "Both interval_min_sec and interval_max_sec must be provided together, "
                "or neither (for manual mode)"
            )
        
        if has_min and has_max:
            if config["interval_min_sec"] > config["interval_max_sec"]:
                raise ValueError("interval_min_sec must be less than or equal to interval_max_sec")
            self._interval_min_sec = config["interval_min_sec"]
            self._interval_max_sec = config["interval_max_sec"]
        else:
            self._interval_min_sec = None
            self._interval_max_sec = None
        
        # Set default values for display options
        self._show_next_maneuver_time = config.get("show_next_maneuver_time", True)
        self._show_maneuver_type = config.get("show_maneuver_type", True)
        self._show_maneuver_description = config.get("show_maneuver_description", True)
        
        # Validate and set emergency_probability if provided
        self._emergency_probability = None
        if "emergency_probability" in config:
            prob = config["emergency_probability"]
            if not isinstance(prob, (int, float)):
                raise ValueError("emergency_probability must be a number")
            if prob < 0 or prob > 100:
                raise ValueError("emergency_probability must be between 0 and 100")
            self._emergency_probability = prob
    
    @property
    def maneuvers_file(self) -> str:
        """Get the maneuvers file path."""
        return self._maneuvers_file
    
    @property
    def interval_min_sec(self) -> Optional[int]:
        """Get the minimum interval in seconds."""
        return self._interval_min_sec
    
    @property
    def interval_max_sec(self) -> Optional[int]:
        """Get the maximum interval in seconds."""
        return self._interval_max_sec
    
    @property
    def show_next_maneuver_time(self) -> bool:
        """Get whether to show next maneuver time."""
        return self._show_next_maneuver_time
    
    @property
    def show_maneuver_type(self) -> bool:
        """Get whether to show maneuver type."""
        return self._show_maneuver_type
    
    @property
    def show_maneuver_description(self) -> bool:
        """Get whether to show maneuver description."""
        return self._show_maneuver_description
    
    @property
    def emergency_probability(self) -> Optional[float]:
        """Get the emergency probability."""
        return self._emergency_probability
    
    def is_manual_mode(self) -> bool:
        """Check if manual mode is enabled (no interval configuration)."""
        return self._interval_min_sec is None and self._interval_max_sec is None


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
            except (json.JSONDecodeError, IOError) as e:
                # Log warning but don't fail - start with empty history
                print(f"Warning: Could not load history file: {e}")
                self.history = []
    
    def save_history(self):
        """Save history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save history file: {e}")
    
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
        self.session_mode = None  # 'indefinite' or 'fixed'
        self.emergency_mode = None  # 'all' or 'random' (only for fixed-length sessions)
        self.completed_maneuvers = []  # Track completed maneuvers in fixed-length mode
    
    def load_config(self) -> Configuration:
        """Load application configuration from JSON file."""
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Configuration file '{self.config_file}' not found. "
                "Please create it with your settings."
            )
        
        try:
            with open(self.config_file, 'r') as f:
                config_dict = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Configuration file '{self.config_file}' contains invalid JSON: {e}"
            )
        except IOError as e:
            raise IOError(
                f"Error reading configuration file '{self.config_file}': {e}"
            )
        
        # Create and return Configuration object (validation happens in constructor)
        return Configuration(config_dict)
    
    def load_maneuvers(self) -> List[Dict]:
        """Load maneuvers from separate JSON file."""
        maneuvers_file = Path(self.config.maneuvers_file)
        
        if not maneuvers_file.exists():
            raise FileNotFoundError(
                f"Maneuvers file '{maneuvers_file}' not found. "
                "Please create it with your maneuvers."
            )
        
        if not maneuvers_file.is_file():
            raise ValueError(
                f"Maneuvers file path '{maneuvers_file}' is not a file. "
                "Please provide a valid file path."
            )
        
        try:
            with open(maneuvers_file, 'r') as f:
                maneuvers = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Maneuvers file '{maneuvers_file}' contains invalid JSON: {e}"
            )
        except IOError as e:
            raise IOError(
                f"Error reading maneuvers file '{maneuvers_file}': {e}"
            )
        
        if not isinstance(maneuvers, list):
            raise ValueError("Maneuvers file must contain a JSON array of maneuvers")
        
        if not maneuvers:
            raise ValueError("Maneuvers file must contain at least one maneuver")
        
        return maneuvers
    
    def is_manual_mode(self) -> bool:
        """Check if manual mode is enabled (no interval configuration)."""
        return self.config.is_manual_mode()
    
    def get_random_interval(self) -> int:
        """Get random interval between min and max from config."""
        min_interval = self.config.interval_min_sec if self.config.interval_min_sec is not None else self.DEFAULT_INTERVAL_MIN
        max_interval = self.config.interval_max_sec if self.config.interval_max_sec is not None else self.DEFAULT_INTERVAL_MAX
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
    
    def prompt_session_mode(self) -> str:
        """Prompt user to select session mode.
        
        Returns:
            str: 'indefinite' or 'fixed'
        """
        print("\nHow would you like to structure your session?")
        print("  [i] Indefinite - Practice maneuvers randomly (default)")
        print("  [f] Fixed-length - Practice each maneuver once")
        
        while True:
            response = input("\nYour choice (i/f or Enter for indefinite): ").strip().lower()
            
            if response == '' or response == 'i' or response == 'indefinite':
                return 'indefinite'
            elif response == 'f' or response == 'fixed':
                return 'fixed'
            else:
                print("Invalid choice. Please select i, f, or press Enter for indefinite.")
    
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
    
    def prompt_emergency_mode(self) -> str:
        """Prompt user how emergencies should appear in fixed-length sessions.
        
        Returns:
            str: 'all' to include all emergencies, 'random' for probability-based
        """
        print("\nHow should emergencies appear in the session?")
        print("  [a] All emergencies - Every emergency will appear (default)")
        print("  [r] Random emergencies - Based on configured probability")
        
        while True:
            response = input("\nYour choice (a/r or Enter for all): ").strip().lower()
            
            if response == '' or response == 'a' or response == 'all':
                return 'all'
            elif response == 'r' or response == 'random':
                return 'random'
            else:
                print("Invalid choice. Please select a, r, or press Enter for all.")
    
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
        
        For indefinite sessions or fixed sessions with random emergencies:
        - If emergency_probability is configured, uses weighted selection
        - Otherwise, uses pure random selection
        
        For fixed-length sessions with all emergencies:
        - Selects from maneuvers not yet completed
        """
        if not self.maneuvers:
            raise ValueError("No maneuvers configured!")
        
        # Determine available maneuvers based on session mode
        if self.session_mode == 'fixed':
            available = [m for m in self.maneuvers if m not in self.completed_maneuvers]
            if not available:
                return None  # All maneuvers completed
        else:
            available = self.maneuvers
        
        # For fixed sessions with all emergencies mode, or no probability configured
        if (self.session_mode == 'fixed' and self.emergency_mode == 'all') or \
           self.config.emergency_probability is None:
            return random.choice(available)
        
        # Use weighted selection based on emergency_probability
        return self._select_with_probability(available, self.config.emergency_probability)
    
    def _select_with_probability(self, maneuvers: List[Dict], emergency_prob: float) -> Dict:
        """Select a maneuver using weighted probability for emergencies.
        
        Args:
            maneuvers: List of maneuvers to select from
            emergency_prob: Probability (0-100) of selecting an emergency
            
        Returns:
            Selected maneuver
        """
        emergencies = [m for m in maneuvers if m.get("type", "").lower() == "emergency"]
        non_emergencies = [m for m in maneuvers if m.get("type", "").lower() != "emergency"]
        
        # If only one type available, select from that type
        if not emergencies or not non_emergencies:
            return random.choice(maneuvers)
        
        # Use probability to determine maneuver type
        if random.random() < emergency_prob / 100:
            return random.choice(emergencies)
        else:
            return random.choice(non_emergencies)
    
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
        if self.config.show_maneuver_type:
            print(f"Type: {maneuver.get('type', 'normal').upper()}")
        
        # Show description if configured and available
        if self.config.show_maneuver_description and "description" in maneuver:
            print(f"Description: {maneuver['description']}")
        
        # Show phase information if provided
        if phase:
            print(f"\nPHASE: {phase['name']}")
            if self.config.show_maneuver_description and "description" in phase:
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
    
    def wait_for_user_ready(self):
        """Wait for user to indicate they're ready for the next maneuver."""
        print("\nPress Enter when ready for the next maneuver...")
        input()
    
    def wait_with_countdown(self, interval: int):
        """Wait for the specified interval with a countdown or progress indicator."""
        show_countdown = self.config.show_next_maneuver_time
        
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
    
    def mark_maneuver_completed(self, maneuver: Dict):
        """Mark a maneuver as completed in fixed-length mode.
        
        Args:
            maneuver: The maneuver to mark as completed
        """
        if self.session_mode == 'fixed' and maneuver not in self.completed_maneuvers:
            self.completed_maneuvers.append(maneuver)
    
    def show_remaining_count(self):
        """Display remaining maneuvers count in fixed-length mode."""
        if self.session_mode == 'fixed':
            remaining = len(self.maneuvers) - len(self.completed_maneuvers)
            if remaining > 0:
                print(f"({remaining} maneuver(s) remaining)")
    
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
        
        # Session mode
        session_display = "Indefinite (random)" if self.session_mode == 'indefinite' else "Fixed-length (each once)"
        print(f"Session mode: {session_display}")
        if self.session_mode == 'fixed' and self.include_emergencies:
            emergency_mode_display = "All will appear" if self.emergency_mode == 'all' else "Random (probability-based)"
            print(f"  Emergency behavior: {emergency_mode_display}")
        
        # Interval settings
        if self.is_manual_mode():
            print(f"Timing mode: Manual (user-prompted)")
        else:
            min_interval = self.config.interval_min_sec if self.config.interval_min_sec is not None else self.DEFAULT_INTERVAL_MIN
            max_interval = self.config.interval_max_sec if self.config.interval_max_sec is not None else self.DEFAULT_INTERVAL_MAX
            print(f"Timing mode: Automatic")
            print(f"Interval range: {min_interval}-{max_interval} seconds")
        
        # Emergency probability setting
        if self.config.emergency_probability is not None:
            print(f"Emergency probability: {self.config.emergency_probability}%")
        
        # Display options
        print(f"Display options:")
        print(f"  - Show countdown timer: {'Yes' if self.config.show_next_maneuver_time else 'No'}")
        print(f"  - Show maneuver type: {'Yes' if self.config.show_maneuver_type else 'No'}")
        print(f"  - Show descriptions: {'Yes' if self.config.show_maneuver_description else 'No'}")
        
        print("-" * 60)
    
    def run(self):
        """Run the main chair flying loop."""
        print("=" * 60)
        print("Chair Flying -  Checklist Memorization Aid")
        print("=" * 60)
        
        # Prompt user for session mode
        self.session_mode = self.prompt_session_mode()
        
        # Prompt user for preferences
        self.maneuver_kind = self.prompt_maneuver_kind()
        
        # Only ask about emergencies if not in emergency-only mode
        if self.maneuver_kind == 'emergency':
            self.include_emergencies = True  # Implied when emergency-only is selected
        else:
            self.include_emergencies = self.prompt_include_emergencies()
        
        # For fixed-length sessions with emergencies, ask about emergency mode
        if self.session_mode == 'fixed' and self.include_emergencies:
            self.emergency_mode = self.prompt_emergency_mode()
        else:
            # For indefinite sessions or no emergencies, emergency_mode is not applicable
            self.emergency_mode = None
        
        # Filter maneuvers based on user preferences
        try:
            self.filter_maneuvers()
        except ValueError as e:
            print(f"\nError: {e}")
            return
        
        # Display configuration summary
        self.show_config_summary()
        
        print("\nStarting practice session...")
        if self.session_mode == 'fixed':
            # Count maneuvers that will definitely appear once
            if self.emergency_mode == 'random':
                # Only count non-emergency maneuvers for fixed-length sessions with random emergencies
                non_emergency_count = sum(1 for m in self.maneuvers if m.get("type", "").lower() != "emergency")
                emergency_count = sum(1 for m in self.maneuvers if m.get("type", "").lower() == "emergency")
                print(f"You will practice {non_emergency_count} maneuver(s) once each.")
                if emergency_count > 0:
                    print(f"(with the potential for any of the {emergency_count} emergency maneuver(s) to appear at random)")
            else:
                # All maneuvers (including emergencies) will appear once
                print(f"You will practice {len(self.maneuvers)} maneuver(s) once each.")
        print("Press Ctrl+C to stop at any time.\n")
        
        try:
            quit_requested = False
            while True:
                # Wait for next maneuver - either with timer or user prompt
                if self.is_manual_mode():
                    self.wait_for_user_ready()
                else:
                    interval = self.get_random_interval()
                    self.wait_with_countdown(interval)
                
                # Select and display maneuver
                maneuver = self.select_maneuver()
                
                # Check if all maneuvers are completed in fixed-length mode
                if maneuver is None:
                    print("\n✓ All maneuvers completed!")
                    break  # Exit outer loop
                
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
                        self.mark_maneuver_completed(maneuver)
                        self.show_remaining_count()
                        break
                    elif response == 'f':
                        self.tracker.record_maneuver(maneuver, "review", current_phase)
                        print("⚠ Marked for review")
                        self.mark_maneuver_completed(maneuver)
                        self.show_remaining_count()
                        break
                    elif response == 's':
                        print("Skipped (not recorded)")
                        self.mark_maneuver_completed(maneuver)
                        self.show_remaining_count()
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
