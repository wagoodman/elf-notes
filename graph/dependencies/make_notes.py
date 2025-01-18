#!/usr/bin/env python3
import json
import argparse
import sys
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description='Generate dependency notes from library information')

    # Required arguments
    parser.add_argument('input_file', type=str, help='Input JSON file with library information')
    parser.add_argument('--name', required=True, help='Name of the main package')
    parser.add_argument('--version', required=True, help='Version of the main package')

    # Optional arguments
    parser.add_argument('--type', help='Type of the main package')
    parser.add_argument('--cpe', help='CPE identifier')
    parser.add_argument('--purl', help='Package URL')
    parser.add_argument('--license', help='License information')

    return parser.parse_args()

def read_input_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Input file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

def generate_notes(args, libs_data):
    # Build the base notes structure
    notes = {
        "name": args.name,
        "version": args.version,
        "dependencies": []
    }

    # Add optional fields if provided
    if args.type:
        notes["type"] = args.type
    if args.cpe:
        notes["cpe"] = args.cpe
    if args.purl:
        notes["purl"] = args.purl
    if args.license:
        notes["license"] = args.license

    # Add dependencies
    for lib in libs_data:
        dep = {
            "name": lib["name"],
            "version": lib["version"],
            "type": lib["type"]
        }
        notes["dependencies"].append(dep)

    return notes

def write_output(notes):
    try:
        with open('notes.json', 'w') as f:
            json.dump(notes, f)
        print(f"Successfully wrote notes.json", file=sys.stderr)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    # Parse command line arguments
    args = parse_args()

    # Read and parse input file
    libs_data = read_input_file(args.input_file)

    # Generate notes structure
    notes = generate_notes(args, libs_data)

    # Write output
    write_output(notes)

if __name__ == "__main__":
    main()
