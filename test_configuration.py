#!/usr/bin/env python3
"""
Tests for Configuration class
"""

import unittest
import sys
from chair_flying import Configuration


class TestConfiguration(unittest.TestCase):
    """Test cases for Configuration class."""
    
    def test_basic_configuration(self):
        """Test basic configuration with all parameters."""
        config_dict = {
            "maneuvers_file": "maneuvers.json",
            "interval_min_sec": 30,
            "interval_max_sec": 120,
            "show_next_maneuver_time": True,
            "show_maneuver_type": True,
            "show_maneuver_description": True,
            "emergency_probability": 25.0
        }
        
        config = Configuration(config_dict)
        
        self.assertEqual(config.maneuvers_file, "maneuvers.json")
        self.assertEqual(config.interval_min_sec, 30)
        self.assertEqual(config.interval_max_sec, 120)
        self.assertTrue(config.show_next_maneuver_time)
        self.assertTrue(config.show_maneuver_type)
        self.assertTrue(config.show_maneuver_description)
        self.assertEqual(config.emergency_probability, 25.0)
        self.assertFalse(config.is_manual_mode())
    
    def test_manual_mode_configuration(self):
        """Test configuration without intervals (manual mode)."""
        config_dict = {
            "maneuvers_file": "maneuvers.json",
            "show_next_maneuver_time": False,
            "show_maneuver_type": False,
            "show_maneuver_description": False
        }
        
        config = Configuration(config_dict)
        
        self.assertEqual(config.maneuvers_file, "maneuvers.json")
        self.assertIsNone(config.interval_min_sec)
        self.assertIsNone(config.interval_max_sec)
        self.assertFalse(config.show_next_maneuver_time)
        self.assertFalse(config.show_maneuver_type)
        self.assertFalse(config.show_maneuver_description)
        self.assertIsNone(config.emergency_probability)
        self.assertTrue(config.is_manual_mode())
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config_dict = {
            "maneuvers_file": "test.json"
        }
        
        config = Configuration(config_dict)
        
        self.assertEqual(config.maneuvers_file, "test.json")
        self.assertTrue(config.show_next_maneuver_time)
        self.assertTrue(config.show_maneuver_type)
        self.assertTrue(config.show_maneuver_description)
        self.assertIsNone(config.emergency_probability)
    
    def test_missing_maneuvers_file(self):
        """Test that missing maneuvers_file raises ValueError."""
        config_dict = {
            "interval_min_sec": 30,
            "interval_max_sec": 120
        }
        
        with self.assertRaises(ValueError) as context:
            Configuration(config_dict)
        
        self.assertIn("maneuvers_file", str(context.exception))
    
    def test_invalid_interval_configuration(self):
        """Test that providing only one interval parameter raises ValueError."""
        config_dict = {
            "maneuvers_file": "maneuvers.json",
            "interval_min_sec": 30
            # Missing interval_max_sec
        }
        
        with self.assertRaises(ValueError) as context:
            Configuration(config_dict)
        
        self.assertIn("together", str(context.exception))
    
    def test_invalid_interval_range(self):
        """Test that min > max raises ValueError."""
        config_dict = {
            "maneuvers_file": "maneuvers.json",
            "interval_min_sec": 120,
            "interval_max_sec": 30
        }
        
        with self.assertRaises(ValueError) as context:
            Configuration(config_dict)
        
        self.assertIn("less than or equal to", str(context.exception))
    
    def test_invalid_emergency_probability_type(self):
        """Test that non-numeric emergency_probability raises ValueError."""
        config_dict = {
            "maneuvers_file": "maneuvers.json",
            "emergency_probability": "invalid"
        }
        
        with self.assertRaises(ValueError) as context:
            Configuration(config_dict)
        
        self.assertIn("must be a number", str(context.exception))
    
    def test_invalid_emergency_probability_range(self):
        """Test that out-of-range emergency_probability raises ValueError."""
        config_dict = {
            "maneuvers_file": "maneuvers.json",
            "emergency_probability": 150.0
        }
        
        with self.assertRaises(ValueError) as context:
            Configuration(config_dict)
        
        self.assertIn("between 0 and 100", str(context.exception))
        
        config_dict["emergency_probability"] = -10.0
        
        with self.assertRaises(ValueError) as context:
            Configuration(config_dict)
        
        self.assertIn("between 0 and 100", str(context.exception))


if __name__ == "__main__":
    unittest.main()
