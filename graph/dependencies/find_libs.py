#!/usr/bin/env python3
import sys
import json
import subprocess
import re
import os
from pathlib import Path

def debug(msg):
    """Print debug information."""
    print(f"DEBUG: {msg}", file=sys.stderr)

def parse_ldflags(flags_str):
    """Extract library names from LD flags string."""
    libs = [lib[2:] for lib in flags_str.split() if lib.startswith('-l')]
    debug(f"Parsed library flags: {libs}")
    return libs

def get_ldconfig_cache():
    """Get the ldconfig cache mapping."""
    debug("Fetching ldconfig cache...")
    try:
        result = subprocess.run(['ldconfig', '-p'], capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()[1:]  # Skip header line
        cache = {}
        for line in lines:
            # Parse lines like: "libz.so.1 (libc6,x86-64) => /lib/x86_64-linux-gnu/libz.so.1"
            match = re.match(r'\s*(\S+)\s+\([^)]+\)\s+=>\s+(\S+)', line)
            if match:
                lib_name, lib_path = match.groups()
                if lib_name not in cache:
                    cache[lib_name] = []
                cache[lib_name].append(lib_path)
                debug(f"Found library mapping: {lib_name} => {lib_path}")

        debug(f"Loaded {len(cache)} library entries from ldconfig")
        return cache
    except subprocess.CalledProcessError as e:
        debug(f"Error running ldconfig: {e}")
        return {}

def find_library_files(lib_name, ldconfig_cache):
    """Find all potential files for a given library name."""
    debug(f"\nSearching for library: {lib_name}")
    files = []
    patterns = [
        f'lib{lib_name}.so',
        f'lib{lib_name}.',
        f'lib{lib_name}',
    ]

    debug(f"Looking for patterns: {patterns}")

    for pattern in patterns:
        matching_libs = [
            path for name, paths in ldconfig_cache.items()
            for path in paths
            if name.startswith(pattern)
        ]
        if matching_libs:
            debug(f"Found matches for {pattern}: {matching_libs}")
        files.extend(matching_libs)

    if not files:
        debug(f"No files found for library {lib_name}")

    return files

def resolve_package_for_file(file_path):
    """Find debian package for a file, trying both direct path and realpath."""
    debug(f"\nResolving package for file: {file_path}")
    paths_to_try = [file_path]

    # Add realpath if different
    real_path = os.path.realpath(file_path)
    if real_path != file_path:
        debug(f"Adding realpath: {real_path}")
        paths_to_try.append(real_path)

    for path in paths_to_try:
        debug(f"Trying path: {path}")
        try:
            # Run dpkg -S to find package
            debug(f"Running: dpkg -S {path}")
            result = subprocess.run(
                ['dpkg', '-S', path],
                capture_output=True,
                text=True,
                check=True
            )
            # Parse output like "libz1:arm64: /lib/aarch64-linux-gnu/libz.so.1"
            debug(f"dpkg -S output: {result.stdout.strip()}")
            package = result.stdout.split(':')[0]
            debug(f"Found package: {package}")

            # Get version information
            debug(f"Getting version for package: {package}")
            version_result = subprocess.run(
                ['dpkg-query', '-W', '-f=${Version}', package],
                capture_output=True,
                text=True,
                check=True
            )
            version = version_result.stdout.strip()
            debug(f"Found version: {version}")

            return {
                'package': package,
                'version': version,
                'path': path
            }
        except subprocess.CalledProcessError as e:
            debug(f"Error resolving {path}: {e}")
            debug(f"stderr: {e.stderr}")
            continue

    debug(f"Failed to resolve package for {file_path}")
    return None

def analyze_libs(flags_str):
    """Analyze libraries from LD flags."""
    debug("\nStarting library analysis...")
    debug(f"Input flags: {flags_str}")

    result = []

    # Special cases that are part of libc
    special_libs = {'m', 'pthread', 'dl', 'rt'}
    debug(f"Special libraries (built-in): {special_libs}")

    # Get library names from flags
    libs = parse_ldflags(flags_str)

    # Get ldconfig cache
    ldconfig_cache = get_ldconfig_cache()

    for ldflag in libs:
        debug(f"\nProcessing ldflag: {ldflag}")
        if ldflag in special_libs:
            debug(f"{ldflag} is a special (built-in) library")
            lib = "c"
        else:
            lib = ldflag

        # Find all potential library files
        lib_files = find_library_files(lib, ldconfig_cache)

        # Try to find package for each file until we get a hit
        pkg_info = None
        for file in lib_files:
            pkg_info = resolve_package_for_file(file)
            if pkg_info:
                debug(f"Successfully resolved {lib} to {pkg_info}")
                result.append({
                    'name': pkg_info['package'],
                    'version': pkg_info['version'],
                    'path': pkg_info['path'],
                    'type': 'deb',
                    'ldconfig': lib,
                    'ldflag': [ldflag]
                })
                break

        if not pkg_info:
            debug(f"Failed to resolve package for {lib}")
            result.append({
                'name': "lib"+lib,
                'version': 'unknown',
                'path': 'not found',
                'type': 'deb',
                'ldconfig': lib,
                'ldflag': [ldflag]
            })

    debug("\nAnalysis complete.")
    return merge(result)

def merge(result):
    merged = {}

    for entry in result:
        key = (entry['name'], entry['version'], entry['path'], entry['type'])
        if key not in merged:
            merged[key] = entry
        else:
            x = set(merged[key]['ldflag'])
            x.add(*entry['ldflag'])
            merged[key]['ldflag'] = sorted(list(x))

    return sorted(list(merged.values()), key=lambda x: x['name'])

def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_libs.py <LDFLAGS>", file=sys.stderr)
        sys.exit(1)

    debug("Starting library analysis script...")
    debug(f"Arguments: {sys.argv}")

    ldflags = sys.argv[1]
    result = analyze_libs(ldflags)

    # Write to JSON file
    debug("\nWriting results to lib.json")
    with open('libs.json', 'w') as f:
        json.dump(result, f, indent=2)

    # Also print to stdout
    print(json.dumps(result, indent=2))
    debug("Script complete.")

if __name__ == "__main__":
    main()
