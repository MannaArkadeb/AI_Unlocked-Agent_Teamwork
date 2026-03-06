"""
Test the new realistic planner with simulated inputs
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test inputs for Study scenario
study_test_inputs = [
    "1",  # Choice: Study
    "Physics",  # Subject
    "Mechanics, Thermodynamics, Electromagnetism",  # Topics
    "1",  # Level: Beginner
    "5",  # Days
    "3",  # Hours per day
]

# Test inputs for Project scenario
project_test_inputs = [
    "2",  # Choice: Project
    "Employee Management System",  # Project name
    "1",  # Type: Software
    "",  # Components: use default
    "10",  # Days
    "4",  # Hours per day
]

def test_planner(inputs, test_name):
    """Test planner with simulated inputs."""
    print(f"\n{'='*70}")
    print(f"TESTING: {test_name}")
    print(f"{'='*70}\n")
    
    # Monkey patch input()
    input_iterator = iter(inputs)
    original_input = __builtins__.input
    
    def mock_input(prompt=""):
        try:
            value = next(input_iterator)
            print(f"{prompt}{value}")
            return value
        except StopIteration:
            return ""
    
    __builtins__.input = mock_input
    
    try:
        from examples.interactive_planner import DetailedPlanner
        planner = DetailedPlanner()
        planner.run()
        print(f"\n{'='*70}")
        print(f"TEST PASSED: {test_name}")
        print(f"{'='*70}\n")
        return True
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        __builtins__.input = original_input


if __name__ == "__main__":
    # Test Study scenario
    success1 = test_planner(study_test_inputs, "Study Physics for 5 Days")
    
    # Test Project scenario
    success2 = test_planner(project_test_inputs, "Software Project for 10 Days")
    
    if success1 and success2:
        print("\n" + "="*70)
        print("ALL TESTS PASSED!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("SOME TESTS FAILED")
        print("="*70)
