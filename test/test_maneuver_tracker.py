#!/usr/bin/env python3
"""
Tests for ManeuverTracker class
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from chair_flying import ManeuverTracker


class TestManeuverTracker(unittest.TestCase):
    """Test cases for ManeuverTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for each test
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.temp_filename = self.temp_file.name
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.temp_filename):
            os.unlink(self.temp_filename)
    
    def test_initialization_no_existing_file(self):
        """Test tracker initialization with no existing history file."""
        tracker = ManeuverTracker(self.temp_filename)
        self.assertEqual(len(tracker.history), 0)
        self.assertEqual(tracker.history_file, Path(self.temp_filename))
    
    def test_initialization_with_existing_file(self):
        """Test tracker initialization with existing history file."""
        # Create a history file with some data
        history_data = [
            {
                "timestamp": "2024-01-01T12:00:00",
                "maneuver": "Test Maneuver",
                "type": "maneuver",
                "status": "completed"
            }
        ]
        with open(self.temp_filename, 'w') as f:
            json.dump(history_data, f)
        
        tracker = ManeuverTracker(self.temp_filename)
        self.assertEqual(len(tracker.history), 1)
        self.assertEqual(tracker.history[0]["maneuver"], "Test Maneuver")
    
    def test_record_maneuver_completed(self):
        """Test recording a completed maneuver."""
        tracker = ManeuverTracker(self.temp_filename)
        
        maneuver = {
            "name": "Power-Off Stall",
            "type": "maneuver"
        }
        
        tracker.record_maneuver(maneuver, "completed")
        
        self.assertEqual(len(tracker.history), 1)
        self.assertEqual(tracker.history[0]["maneuver"], "Power-Off Stall")
        self.assertEqual(tracker.history[0]["type"], "maneuver")
        self.assertEqual(tracker.history[0]["status"], "completed")
        self.assertIn("timestamp", tracker.history[0])
    
    def test_record_maneuver_review(self):
        """Test recording a maneuver marked for review."""
        tracker = ManeuverTracker(self.temp_filename)
        
        maneuver = {
            "name": "Engine Failure",
            "type": "emergency"
        }
        
        tracker.record_maneuver(maneuver, "review")
        
        self.assertEqual(len(tracker.history), 1)
        self.assertEqual(tracker.history[0]["status"], "review")
    
    def test_record_maneuver_with_phase(self):
        """Test recording a maneuver with a phase."""
        tracker = ManeuverTracker(self.temp_filename)
        
        maneuver = {
            "name": "Engine Fire During Startup",
            "type": "emergency"
        }
        
        phase = {
            "name": "Engine Starts",
            "description": "Engine successfully starts despite the fire"
        }
        
        tracker.record_maneuver(maneuver, "completed", phase)
        
        self.assertEqual(len(tracker.history), 1)
        self.assertEqual(tracker.history[0]["phase"], "Engine Starts")
    
    def test_get_follow_ups_empty(self):
        """Test getting follow-ups when none exist."""
        tracker = ManeuverTracker(self.temp_filename)
        follow_ups = tracker.get_follow_ups()
        self.assertEqual(len(follow_ups), 0)
    
    def test_get_follow_ups_with_reviews(self):
        """Test getting follow-ups with review items."""
        tracker = ManeuverTracker(self.temp_filename)
        
        maneuver1 = {"name": "Stall", "type": "maneuver"}
        maneuver2 = {"name": "Engine Failure", "type": "emergency"}
        maneuver3 = {"name": "Chandelles", "type": "maneuver"}
        
        tracker.record_maneuver(maneuver1, "completed")
        tracker.record_maneuver(maneuver2, "review")
        tracker.record_maneuver(maneuver3, "review")
        
        follow_ups = tracker.get_follow_ups()
        self.assertEqual(len(follow_ups), 2)
        self.assertEqual(follow_ups[0]["maneuver"], "Engine Failure")
        self.assertEqual(follow_ups[1]["maneuver"], "Chandelles")
    
    def test_save_and_load_history(self):
        """Test that history persists across instances."""
        # Create first tracker and add data
        tracker1 = ManeuverTracker(self.temp_filename)
        maneuver = {"name": "Test Maneuver", "type": "maneuver"}
        tracker1.record_maneuver(maneuver, "completed")
        
        # Create second tracker with same file
        tracker2 = ManeuverTracker(self.temp_filename)
        
        # Verify data persisted
        self.assertEqual(len(tracker2.history), 1)
        self.assertEqual(tracker2.history[0]["maneuver"], "Test Maneuver")
    
    def test_load_history_invalid_json(self):
        """Test handling of invalid JSON in history file."""
        # Write invalid JSON to file
        with open(self.temp_filename, 'w') as f:
            f.write("{ invalid json }")
        
        # Should not raise exception, just start with empty history
        tracker = ManeuverTracker(self.temp_filename)
        self.assertEqual(len(tracker.history), 0)
    
    def test_record_maneuver_missing_type(self):
        """Test recording a maneuver without type field."""
        tracker = ManeuverTracker(self.temp_filename)
        
        maneuver = {
            "name": "Basic Maneuver"
            # type field is missing
        }
        
        tracker.record_maneuver(maneuver, "completed")
        
        self.assertEqual(len(tracker.history), 1)
        self.assertEqual(tracker.history[0]["type"], "normal")


if __name__ == "__main__":
    unittest.main()
