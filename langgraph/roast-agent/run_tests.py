#!/usr/bin/env python3
"""
Simple script to run the roast agent tests.
"""
from tests.roast_agent_test import run_roast_tests

if __name__ == "__main__":
    print("=== Running Roast Agent Tests ===")
    print("This will generate comedy roast questions for sample celebrities in English and Estonian")
    print("=" * 70)
    run_roast_tests()
    print("\n=== Tests completed! ===") 