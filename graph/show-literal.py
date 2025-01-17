#!/usr/bin/env python3
import json
import sys
import webbrowser
import os
from graphviz import Digraph

def load_sbom(filepath):
    """Load and parse SBOM JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def create_node_id(prefix, item):
    """Create a unique node ID based on the item type and properties."""
    if prefix == 'pkg':
        # For packages, use name and version to create unique ID
        name = item.get('name', '')
        version = item.get('version', '')
        node_id = f"{prefix}_{name}_{version}".replace('.', '_').replace('-', '_')
        print(f"Creating package node ID: {node_id}")
        print(f"  From name: {name}, version: {version}")
        return node_id
    else:
        # For files, use the path to create unique ID
        path = item.get('location', {}).get('path', '')
        node_id = f"{prefix}_{path}".replace('/', '_').replace('.', '_').replace('-', '_')
        print(f"Creating file node ID: {node_id}")
        print(f"  From path: {path}")
        return node_id

def create_graph(sbom_data):
    """Create a directed graph from SBOM data."""
    print("\n=== Starting Graph Creation ===")

    dot = Digraph(comment='SBOM Visualization')
    dot.attr(rankdir='LR')
    dot.attr('node', fontname='Arial')

    # Create a mapping of IDs to node_ids
    id_to_node = {}

    print("\n--- Creating Package Nodes ---")
    # Create nodes for artifacts (packages)
    for artifact in sbom_data.get('artifacts', []):
        print(f"\nProcessing artifact:")
        print(f"  ID: {artifact.get('id', '')}")
        print(f"  Name: {artifact.get('name', '')}")
        print(f"  Version: {artifact.get('version', '')}")
        print(f"  Type: {artifact.get('type', '')}")

        node_id = create_node_id('pkg', artifact)
        id_to_node[artifact.get('id', '')] = node_id

        label = f"{artifact.get('name', '')}\n{artifact.get('version', '')}"
        dot.node(node_id, label,
                shape='box',
                style='filled',
                fillcolor='lightblue',
                tooltip=f"Type: {artifact.get('type', '')}")

        print(f"  Created node: {node_id}")
        print(f"  Label: {label}")

    print("\n--- Creating File Nodes ---")
    # Create nodes for files
    for file in sbom_data.get('files', []):
        print(f"\nProcessing file:")
        print(f"  ID: {file.get('id', '')}")
        print(f"  Path: {file.get('location', {}).get('path', '')}")
        print(f"  Type: {file.get('type', '')}")

        node_id = create_node_id('file', file)
        id_to_node[file.get('id', '')] = node_id

        label = file.get('location', {}).get('path', '')
        dot.node(node_id, label,
                shape='ellipse',
                style='filled',
                fillcolor='lightgreen',
                tooltip=f"Type: {file.get('type', '')}")

        print(f"  Created node: {node_id}")
        print(f"  Label: {label}")

    print("\n--- Creating Edges ---")
    # Add relationships as edges
    for rel in sbom_data.get('artifactRelationships', []):
        print(f"\nProcessing relationship:")
        print(f"  Parent ID: {rel.get('parent', '')}")
        print(f"  Child ID: {rel.get('child', '')}")
        print(f"  Type: {rel.get('type', '')}")

        parent_id = rel.get('parent', '')
        child_id = rel.get('child', '')
        rel_type = rel.get('type', '')

        if parent_id in id_to_node and child_id in id_to_node:
            parent_node = id_to_node[parent_id]
            child_node = id_to_node[child_id]

            print(f"  Creating edge:")
            print(f"    From parent node: {parent_node}")
            print(f"    To child node: {child_node}")
            print(f"    Relationship: {rel_type}")

            dot.edge(parent_node, child_node,
                    label=rel_type,
                    tooltip=rel_type,
                    color='gray')
        else:
            print(f"  WARNING: Missing node mapping for relationship:")
            if parent_id not in id_to_node:
                print(f"    Missing parent node: {parent_id}")
            if child_id not in id_to_node:
                print(f"    Missing child node: {child_id}")

    print("\n=== Graph Creation Complete ===")
    return dot

def main():
    if len(sys.argv) != 2:
        print("Usage: python sbom_visualizer.py <sbom_json_file>")
        sys.exit(1)

    sbom_file = sys.argv[1]
    try:
        print(f"\nProcessing SBOM file: {sbom_file}")

        # Load SBOM data
        sbom_data = load_sbom(sbom_file)
        print("SBOM file loaded successfully")

        # Create visualization
        dot = create_graph(sbom_data)

        # Generate output file with absolute path
        output_base = os.path.splitext(os.path.abspath(sbom_file))[0]
        png_path = output_base + '_sbom_viz.png'

        print(f"\nGenerating visualization...")
        # Generate only PNG output
        dot.render(output_base + '_sbom_viz', format='png', cleanup=True)

        print(f"\nGenerated visualization file:")
        print(f"- {png_path}")

        # Open the PNG file in the default web browser using absolute path
        webbrowser.open('file://' + png_path)

    except Exception as e:
        print(f"\nError processing SBOM file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
