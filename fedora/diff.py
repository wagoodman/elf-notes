#!/usr/bin/env python3

import difflib
from typing import List, Tuple, Dict
import re
from dataclasses import dataclass
from colorama import Fore, Back, Style, init
import argparse

similarity_threshold = 0.65
no_match = "---"

# Initialize colorama for cross-platform colored output
init()

@dataclass
class ComparisonResult:
    left: str
    right: str
    similarity: float
    colored_diff: str

def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def get_package_base(text: str) -> str:
    """Extract package base name (everything before the colon)."""
    return text.split(':')[0] if ':' in text else text

def color_diff(left: str, right: str) -> str:
    """Generate colored diff between two strings."""
    if not right or right == no_match:
        return Fore.RED + left + Style.RESET_ALL
    if not left or left == no_match:
        return Fore.GREEN + right + Style.RESET_ALL

    # Split package name and version
    left_parts = left.split(': ', 1)
    right_parts = right.split(': ', 1)

    if len(left_parts) != 2 or len(right_parts) != 2:
        return left  # Return unchanged if format is unexpected

    left_name, left_version = left_parts
    right_name, right_version = right_parts

    # Color the differences in name and version separately
    name_matcher = difflib.SequenceMatcher(None, left_name, right_name)
    version_matcher = difflib.SequenceMatcher(None, left_version, right_version)

    result = []

    # Handle package name differences
    for op, i1, i2, j1, j2 in name_matcher.get_opcodes():
        if op == 'equal':
            result.append(left_name[i1:i2])
        elif op == 'delete':
            result.append(Fore.RED + left_name[i1:i2] + Style.RESET_ALL)
        elif op == 'insert':
            result.append(Fore.GREEN + right_name[j1:j2] + Style.RESET_ALL)
        elif op == 'replace':
            result.append(Fore.RED + left_name[i1:i2] + Style.RESET_ALL)
            result.append(Fore.GREEN + right_name[j1:j2] + Style.RESET_ALL)

    result.append(': ')

    # Handle version differences
    for op, i1, i2, j1, j2 in version_matcher.get_opcodes():
        if op == 'equal':
            result.append(left_version[i1:i2])
        elif op == 'delete':
            result.append(Fore.RED + left_version[i1:i2] + Style.RESET_ALL)
        elif op == 'insert':
            result.append(Fore.GREEN + right_version[j1:j2] + Style.RESET_ALL)
        elif op == 'replace':
            result.append(Fore.RED + left_version[i1:i2] + Style.RESET_ALL)
            result.append(Fore.GREEN + right_version[j1:j2] + Style.RESET_ALL)

    return ''.join(result)

def calculate_similarity(left: str, right: str) -> float:
    """Calculate similarity between two package names (ignoring versions)."""
    if not left or not right or left == "(no match)" or right == "(no match)":
        return 0.0

    left_base = get_package_base(left)
    right_base = get_package_base(right)

    return difflib.SequenceMatcher(None, left_base, right_base).ratio()

def get_prefix(text: str) -> str:
    """Extract prefix (everything before the first hyphen)."""
    base = get_package_base(text)  # First get everything before the colon
    return base.split('-')[0] if '-' in base else base

def find_best_match(left: str, right_rows: List[str]) -> Tuple[str, float]:
    """Find the best matching right row for a given left row."""
    if not right_rows:
        return "", 0.0

    # Try exact match first
    if left in right_rows:
        return left, 1.0

    # Try matching by prefix before first hyphen
    left_prefix = get_prefix(left)
    prefix_matches = []
    for right in right_rows:
        right_prefix = get_prefix(right)
        if left_prefix == right_prefix:
            # Calculate similarity for sorting but don't filter by threshold
            similarity = max(calculate_similarity(left, right), similarity_threshold)
            prefix_matches.append((right, similarity))

    if prefix_matches:
        # Return the best matching prefix match
        return max(prefix_matches, key=lambda x: x[1])

    # If no prefix matches, fall back to similarity matching with threshold
    similarities = [(r, calculate_similarity(left, r)) for r in right_rows]
    similarities = [(r, s) for r, s in similarities if s >= similarity_threshold]

    if not similarities:
        return ("", 0.0)

    return max(similarities, key=lambda x: x[1])

def compare_files(left_rows: List[str], right_rows: List[str]) -> List[ComparisonResult]:
    """Compare rows from two files and generate comparison results."""
    results = []
    used_right_rows = set()

    # Sort left rows
    left_rows = sorted(left_rows)

    for left in left_rows:
        best_right, similarity = find_best_match(left, right_rows)
        if similarity >= similarity_threshold:
            used_right_rows.add(best_right)
            colored = color_diff(left, best_right)
            results.append(ComparisonResult(left, best_right, similarity, colored))
        else:
            results.append(ComparisonResult(left, no_match, 0.0, color_diff(left, "")))

    # Handle unmatched right rows
    for right in right_rows:
        if right not in used_right_rows:
            results.append(ComparisonResult(no_match, right, 0.0, color_diff("", right)))

    return results

def format_table(results: List[ComparisonResult]) -> str:
    """Format comparison results as a table."""
    # Calculate column widths (accounting for ANSI sequences)
    left_width = max(len(strip_ansi(r.left)) for r in results)
    right_width = max(len(strip_ansi(r.right)) for r in results)

    # Create header
    header = f"{'File 1':<{left_width}} | {'File 2':<{right_width}} | Similarity"
    separator = "-" * (left_width + right_width + 13)

    # Format rows
    rows = [header, separator]
    for result in results:
        # Use the colored diff for the left column
        left_content = result.colored_diff if result.left != no_match else result.left
        right_content = result.right

        # Pad the columns correctly (accounting for ANSI sequences)
        left_stripped = strip_ansi(left_content)
        left_padding = " " * (left_width - len(left_stripped))
        right_padding = " " * (right_width - len(strip_ansi(right_content)))

        similarity_str = f"{result.similarity:.2f}"
        rows.append(f"{left_content}{left_padding} | {right_content}{right_padding} | {similarity_str}")

    return "\n".join(rows)

def main():
    parser = argparse.ArgumentParser(description='Compare two files and show differences')
    parser.add_argument('file1', help='First file path')
    parser.add_argument('file2', help='Second file path')
    args = parser.parse_args()

    try:
        with open(args.file1, 'r') as f1, open(args.file2, 'r') as f2:
            left_rows = [line.strip() for line in f1 if line.strip()]
            right_rows = [line.strip() for line in f2 if line.strip()]
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    results = compare_files(left_rows, right_rows)
    print(format_table(results))

if __name__ == "__main__":
    main()
