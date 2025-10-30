#!/usr/bin/env python3
"""
Tests for ChairFlying class
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from chair_flying import ChairFlying, Configuration


class TestChairFlying(unittest.TestCase):
    """Test cases for ChairFlying class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_maneuvers = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        
        # Create test maneuvers
        self.test_maneuvers = [
            {
                "name": "Power-Off Stall",
                "type": "maneuver",
                "kind": "private",
                "description": "Practice stall recovery"
            },
            {
                "name": "Chandelles",
                "type": "maneuver",
                "kind": "commercial",
                "description": "Maximum performance climbing turn"
            },
            {
                "name": "Engine Failure",
                "type": "emergency",
                "description": "Engine failure emergency"
            }
        ]
        
        json.dump(self.test_maneuvers, self.temp_maneuvers)
        self.temp_maneuvers.close()
        
        # Create test config
        self.test_config = {
            "maneuvers_file": self.temp_maneuvers.name,
            "interval_min_sec": 30,
            "interval_max_sec": 120,
            "show_next_maneuver_time": True,
            "show_maneuver_type": True,
            "show_maneuver_description": True
        }
        
        json.dump(self.test_config, self.temp_config)
        self.temp_config.close()
        
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
        if os.path.exists(self.temp_maneuvers.name):
            os.unlink(self.temp_maneuvers.name)
    
    def test_load_config_valid(self):
        """Test loading valid configuration."""
        app = ChairFlying(self.temp_config.name)
        self.assertIsNotNone(app.config)
        self.assertEqual(app.config.interval_min_sec, 30)
        self.assertEqual(app.config.interval_max_sec, 120)
    
    def test_load_config_missing_file(self):
        """Test loading configuration from non-existent file."""
        with self.assertRaises(FileNotFoundError):
            ChairFlying("nonexistent_config.json")
    
    def test_load_maneuvers_valid(self):
        """Test loading valid maneuvers."""
        app = ChairFlying(self.temp_config.name)
        self.assertEqual(len(app.all_maneuvers), 3)
        self.assertEqual(app.all_maneuvers[0]["name"], "Power-Off Stall")
    
    def test_load_maneuvers_invalid_json(self):
        """Test loading maneuvers with invalid JSON."""
        # Create config pointing to invalid maneuvers file
        temp_invalid = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_invalid.write("{ invalid json }")
        temp_invalid.close()
        
        temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        config_data = {
            "maneuvers_file": temp_invalid.name,
            "interval_min_sec": 30,
            "interval_max_sec": 120
        }
        json.dump(config_data, temp_config)
        temp_config.close()
        
        try:
            with self.assertRaises(ValueError) as context:
                ChairFlying(temp_config.name)
            self.assertIn("invalid JSON", str(context.exception))
        finally:
            os.unlink(temp_invalid.name)
            os.unlink(temp_config.name)
    
    def test_load_maneuvers_empty_array(self):
        """Test loading maneuvers with empty array."""
        # Create empty maneuvers file
        temp_empty = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump([], temp_empty)
        temp_empty.close()
        
        temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        config_data = {
            "maneuvers_file": temp_empty.name,
            "interval_min_sec": 30,
            "interval_max_sec": 120
        }
        json.dump(config_data, temp_config)
        temp_config.close()
        
        try:
            with self.assertRaises(ValueError) as context:
                ChairFlying(temp_config.name)
            self.assertIn("at least one maneuver", str(context.exception))
        finally:
            os.unlink(temp_empty.name)
            os.unlink(temp_config.name)
    
    def test_is_manual_mode_automatic(self):
        """Test manual mode detection for automatic mode."""
        app = ChairFlying(self.temp_config.name)
        self.assertFalse(app.is_manual_mode())
    
    def test_is_manual_mode_manual(self):
        """Test manual mode detection for manual mode."""
        # Create config without intervals
        temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        config_data = {
            "maneuvers_file": self.temp_maneuvers.name
        }
        json.dump(config_data, temp_config)
        temp_config.close()
        
        try:
            app = ChairFlying(temp_config.name)
            self.assertTrue(app.is_manual_mode())
        finally:
            os.unlink(temp_config.name)
    
    def test_get_random_interval(self):
        """Test random interval generation."""
        app = ChairFlying(self.temp_config.name)
        interval = app.get_random_interval()
        self.assertGreaterEqual(interval, 30)
        self.assertLessEqual(interval, 120)
    
    def test_filter_maneuvers_all(self):
        """Test filtering maneuvers with 'all' selection."""
        app = ChairFlying(self.temp_config.name)
        app.maneuver_kind = 'all'
        app.include_emergencies = True
        app.filter_maneuvers()
        self.assertEqual(len(app.maneuvers), 3)
    
    def test_filter_maneuvers_private_only(self):
        """Test filtering maneuvers with 'private' selection."""
        app = ChairFlying(self.temp_config.name)
        app.maneuver_kind = 'private'
        app.include_emergencies = True
        app.filter_maneuvers()
        # Should include private maneuvers and emergencies
        self.assertEqual(len(app.maneuvers), 2)
        names = [m["name"] for m in app.maneuvers]
        self.assertIn("Power-Off Stall", names)
        self.assertIn("Engine Failure", names)
    
    def test_filter_maneuvers_commercial_only(self):
        """Test filtering maneuvers with 'commercial' selection."""
        app = ChairFlying(self.temp_config.name)
        app.maneuver_kind = 'commercial'
        app.include_emergencies = True
        app.filter_maneuvers()
        # Should include commercial maneuvers and emergencies
        self.assertEqual(len(app.maneuvers), 2)
        names = [m["name"] for m in app.maneuvers]
        self.assertIn("Chandelles", names)
        self.assertIn("Engine Failure", names)
    
    def test_filter_maneuvers_emergency_only(self):
        """Test filtering maneuvers with 'emergency' selection."""
        app = ChairFlying(self.temp_config.name)
        app.maneuver_kind = 'emergency'
        app.include_emergencies = True  # Implied when emergency-only
        app.filter_maneuvers()
        self.assertEqual(len(app.maneuvers), 1)
        self.assertEqual(app.maneuvers[0]["name"], "Engine Failure")
    
    def test_filter_maneuvers_exclude_emergencies(self):
        """Test filtering maneuvers excluding emergencies."""
        app = ChairFlying(self.temp_config.name)
        app.maneuver_kind = 'all'
        app.include_emergencies = False
        app.filter_maneuvers()
        # Should only include non-emergency maneuvers
        self.assertEqual(len(app.maneuvers), 2)
        for maneuver in app.maneuvers:
            self.assertNotEqual(maneuver.get("type", "").lower(), "emergency")
    
    def test_select_maneuver_basic(self):
        """Test basic maneuver selection."""
        app = ChairFlying(self.temp_config.name)
        app.maneuver_kind = 'all'
        app.include_emergencies = True
        app.filter_maneuvers()
        
        maneuver = app.select_maneuver()
        self.assertIsNotNone(maneuver)
        self.assertIn("name", maneuver)
    
    def test_select_maneuver_with_probability(self):
        """Test maneuver selection with emergency probability."""
        # Create config with emergency probability
        temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        config_data = {
            "maneuvers_file": self.temp_maneuvers.name,
            "interval_min_sec": 30,
            "interval_max_sec": 120,
            "emergency_probability": 50.0
        }
        json.dump(config_data, temp_config)
        temp_config.close()
        
        try:
            app = ChairFlying(temp_config.name)
            app.maneuver_kind = 'all'
            app.include_emergencies = True
            app.filter_maneuvers()
            
            # Test multiple selections to ensure probability works
            selections = []
            for _ in range(20):
                maneuver = app.select_maneuver()
                selections.append(maneuver.get("type", "").lower())
            
            # Should have mix of emergency and non-emergency
            self.assertIn("emergency", selections)
            self.assertTrue(any(t != "emergency" for t in selections))
        finally:
            os.unlink(temp_config.name)
    
    def test_select_phase_no_phases(self):
        """Test phase selection for maneuver without phases."""
        app = ChairFlying(self.temp_config.name)
        maneuver = {"name": "Test", "type": "maneuver"}
        phase = app.select_phase(maneuver)
        self.assertIsNone(phase)
    
    def test_select_phase_with_phases(self):
        """Test phase selection for maneuver with phases."""
        app = ChairFlying(self.temp_config.name)
        maneuver = {
            "name": "Engine Fire",
            "type": "emergency",
            "phases": [
                {"name": "Phase 1", "description": "First phase"},
                {"name": "Phase 2", "description": "Second phase"}
            ]
        }
        phase = app.select_phase(maneuver)
        self.assertIsNotNone(phase)
        self.assertIn("name", phase)
        self.assertIn(phase["name"], ["Phase 1", "Phase 2"])
    
    def test_permanently_skip_maneuver(self):
        """Test permanently skipping a maneuver."""
        app = ChairFlying(self.temp_config.name)
        app.maneuver_kind = 'all'
        app.include_emergencies = True
        app.filter_maneuvers()
        
        initial_count = len(app.maneuvers)
        maneuver_to_skip = app.maneuvers[0]
        
        has_maneuvers = app.permanently_skip_maneuver(maneuver_to_skip)
        
        self.assertTrue(has_maneuvers)
        self.assertEqual(len(app.maneuvers), initial_count - 1)
        self.assertIn(maneuver_to_skip, app.skipped_maneuvers)
        self.assertNotIn(maneuver_to_skip, app.maneuvers)
    
    def test_permanently_skip_last_maneuver(self):
        """Test permanently skipping the last remaining maneuver."""
        app = ChairFlying(self.temp_config.name)
        app.maneuver_kind = 'emergency'
        app.include_emergencies = True
        app.filter_maneuvers()
        
        # Should have only one emergency maneuver
        self.assertEqual(len(app.maneuvers), 1)
        
        maneuver_to_skip = app.maneuvers[0]
        has_maneuvers = app.permanently_skip_maneuver(maneuver_to_skip)
        
        self.assertFalse(has_maneuvers)
        self.assertEqual(len(app.maneuvers), 0)
    
    def test_fixed_length_session_maneuver_count(self):
        """Test that fixed-length session with random emergencies counts correctly."""
        # Create a setup with multiple commercial and emergency maneuvers
        temp_maneuvers = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        maneuvers = [
            {"name": "Chandelles", "type": "maneuver", "kind": "commercial"},
            {"name": "Lazy Eights", "type": "maneuver", "kind": "commercial"},
            {"name": "Steep Turns", "type": "maneuver", "kind": "commercial"},
            {"name": "Engine Failure", "type": "emergency"},
            {"name": "Electrical Fire", "type": "emergency"},
        ]
        json.dump(maneuvers, temp_maneuvers)
        temp_maneuvers.close()
        
        temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        config_data = {
            "maneuvers_file": temp_maneuvers.name,
            "interval_min_sec": 5,
            "interval_max_sec": 20
        }
        json.dump(config_data, temp_config)
        temp_config.close()
        
        try:
            app = ChairFlying(temp_config.name)
            app.session_mode = 'fixed'
            app.maneuver_kind = 'commercial'
            app.include_emergencies = True
            app.emergency_mode = 'random'
            app.filter_maneuvers()
            
            # Should have 3 commercial + 2 emergency = 5 total
            self.assertEqual(len(app.maneuvers), 5)
            
            # Count non-emergency and emergency maneuvers in a single pass
            emergency_count = 0
            non_emergency_count = 0
            for m in app.maneuvers:
                if m.get("type", "").lower() == "emergency":
                    emergency_count += 1
                else:
                    non_emergency_count += 1
            
            self.assertEqual(non_emergency_count, 3)
            self.assertEqual(emergency_count, 2)
        finally:
            os.unlink(temp_maneuvers.name)
            os.unlink(temp_config.name)
    
    def test_show_remaining_count_fixed_random_emergencies(self):
        """Test that remaining count excludes emergencies in fixed mode with random emergencies."""
        # Create a setup with multiple commercial and emergency maneuvers
        temp_maneuvers = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        maneuvers = [
            {"name": "Chandelles", "type": "maneuver", "kind": "commercial"},
            {"name": "Lazy Eights", "type": "maneuver", "kind": "commercial"},
            {"name": "Steep Turns", "type": "maneuver", "kind": "commercial"},
            {"name": "Engine Failure", "type": "emergency"},
            {"name": "Electrical Fire", "type": "emergency"},
        ]
        json.dump(maneuvers, temp_maneuvers)
        temp_maneuvers.close()
        
        temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        config_data = {
            "maneuvers_file": temp_maneuvers.name,
            "interval_min_sec": 5,
            "interval_max_sec": 20
        }
        json.dump(config_data, temp_config)
        temp_config.close()
        
        try:
            app = ChairFlying(temp_config.name)
            app.session_mode = 'fixed'
            app.maneuver_kind = 'commercial'
            app.include_emergencies = True
            app.emergency_mode = 'random'
            app.filter_maneuvers()
            
            # Mark one non-emergency maneuver as completed
            app.completed_maneuvers.append(app.maneuvers[0])  # Chandelles
            
            # Capture the output
            import io
            import sys
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            app.show_remaining_count()
            
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            
            # Should show 2 remaining (3 commercial - 1 completed), not 4 (5 total - 1 completed)
            self.assertIn("2 maneuver(s) remaining", output)
            self.assertNotIn("4 maneuver(s) remaining", output)
        finally:
            os.unlink(temp_maneuvers.name)
            os.unlink(temp_config.name)
    
    def test_show_remaining_count_fixed_all_emergencies(self):
        """Test that remaining count includes emergencies in fixed mode with all emergencies."""
        # Create a setup with multiple commercial and emergency maneuvers
        temp_maneuvers = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        maneuvers = [
            {"name": "Chandelles", "type": "maneuver", "kind": "commercial"},
            {"name": "Lazy Eights", "type": "maneuver", "kind": "commercial"},
            {"name": "Steep Turns", "type": "maneuver", "kind": "commercial"},
            {"name": "Engine Failure", "type": "emergency"},
            {"name": "Electrical Fire", "type": "emergency"},
        ]
        json.dump(maneuvers, temp_maneuvers)
        temp_maneuvers.close()
        
        temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        config_data = {
            "maneuvers_file": temp_maneuvers.name,
            "interval_min_sec": 5,
            "interval_max_sec": 20
        }
        json.dump(config_data, temp_config)
        temp_config.close()
        
        try:
            app = ChairFlying(temp_config.name)
            app.session_mode = 'fixed'
            app.maneuver_kind = 'commercial'
            app.include_emergencies = True
            app.emergency_mode = 'all'
            app.filter_maneuvers()
            
            # Mark one non-emergency maneuver as completed
            app.completed_maneuvers.append(app.maneuvers[0])  # Chandelles
            
            # Capture the output
            import io
            import sys
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            app.show_remaining_count()
            
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            
            # Should show 4 remaining (5 total - 1 completed) when all emergencies mode
            self.assertIn("4 maneuver(s) remaining", output)
        finally:
            os.unlink(temp_maneuvers.name)
            os.unlink(temp_config.name)


if __name__ == "__main__":
    unittest.main()
