#!/usr/bin/env python3
"""
Script to merge all herb JSON files from py/json/final/ directory into a single file.
"""

import glob
import json
import os
from typing import Any, Dict, List


def load_json_file(filepath: str) -> List[Dict[Any, Any]]:
    """Load a JSON file and return its contents."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure we always return a list
            if isinstance(data, list):
                return data
            else:
                return [data]
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []


def merge_herb_files(input_dir: str, output_file: str) -> None:
    """
    Merge all JSON files in the input directory into a single JSON file.

    Args:
        input_dir: Directory containing the JSON files to merge
        output_file: Path for the output merged JSON file
    """

    # Find all JSON files in the directory
    json_pattern = os.path.join(input_dir, "*.json")
    json_files = glob.glob(json_pattern)

    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return

    print(f"Found {len(json_files)} JSON files to merge")

    # Sort files to ensure consistent ordering
    json_files.sort()

    merged_data = []
    total_herbs = 0

    for filepath in json_files:
        print(f"Processing: {os.path.basename(filepath)}")
        herbs = load_json_file(filepath)
        merged_data.extend(herbs)
        total_herbs += len(herbs)
        print(f"  Added {len(herbs)} herbs")

    # Write merged data to output file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)

        print(f"\nSuccessfully merged {total_herbs} herbs into {output_file}")
        print(f"Output file size: {os.path.getsize(output_file)} bytes")

    except Exception as e:
        print(f"Error writing output file: {e}")


def main():
    """Main function to execute the merge process."""

    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "py", "json", "final")
    output_file = os.path.join(script_dir, "merged_herbs.json")

    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Input directory does not exist: {input_dir}")
        return

    print(f"Input directory: {input_dir}")
    print(f"Output file: {output_file}")
    print("-" * 50)

    # Perform the merge
    merge_herb_files(input_dir, output_file)

    print("-" * 50)
    print("Merge complete!")


if __name__ == "__main__":
    main()
