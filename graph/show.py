#!/usr/bin/env python3
import json
import sys
import webbrowser
import os
from graphviz import Digraph
from collections import defaultdict

def load_sbom(filepath):
    """Load and parse SBOM JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def get_node_key(prefix, item):
    """Generate a unique key for deduplication."""
    if prefix == 'pkg':
        return ('pkg', item.get('name', ''), item.get('version', ''))
    else:
        return ('file', item.get('location', {}).get('path', ''))

def create_node_id(prefix, item):
    """Create a unique node ID based on the item type and properties."""
    if prefix == 'pkg':
        name = item.get('name', '')
        version = item.get('version', '')
        node_id = f"{prefix}_{name}_{version}".replace('.', '_').replace('-', '_')
        print(f"Creating package node ID: {node_id}")
        print(f"  From name: {name}, version: {version}")
        return node_id
    else:
        path = item.get('location', {}).get('path', '')
        node_id = f"{prefix}_{path}".replace('/', '_').replace('.', '_').replace('-', '_')
        print(f"Creating file node ID: {node_id}")
        print(f"  From path: {path}")
        return node_id

def find_all_paths(graph, start, end, path=None):
    """Find all paths between two nodes in the graph."""
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths

def is_redundant_edge(graph, parent, child):
    """Check if there's already a path between parent and child without this edge."""
    if child in graph[parent]:
        graph[parent].remove(child)
    paths = find_all_paths(graph, parent, child)
    graph[parent].add(child)
    return len(paths) > 0

def create_graph(sbom_data):
    """Create a directed graph from SBOM data."""
    print("\n=== Starting Graph Creation ===")

    dot = Digraph(comment='SBOM Visualization')
    dot.attr(rankdir='LR')
    dot.attr('node', fontname='Arial')

    # Create mappings for deduplication
    node_keys = {}  # Maps original IDs to node keys
    unique_nodes = {}  # Maps node keys to node IDs
    id_to_node = {}  # Maps original IDs to final node IDs

    print("\n--- Processing Package Nodes ---")
    duplicate_count = 0
    for artifact in sbom_data.get('artifacts', []):
        orig_id = artifact.get('id', '')
        node_key = get_node_key('pkg', artifact)
        node_keys[orig_id] = node_key

        if node_key not in unique_nodes:
            node_id = create_node_id('pkg', artifact)
            unique_nodes[node_key] = node_id

            label = f"{artifact.get('name', '')}\n{artifact.get('version', '')}"
            dot.node(node_id, label,
                    shape='box',
                    style='filled',
                    fillcolor='lightblue',
                    tooltip=f"Type: {artifact.get('type', '')}")
            print(f"\nCreated new node:")
            print(f"  ID: {orig_id}")
            print(f"  Node ID: {node_id}")
        else:
            duplicate_count += 1
            print(f"\nFound duplicate package:")
            print(f"  ID: {orig_id}")
            print(f"  Using existing node: {unique_nodes[node_key]}")

        id_to_node[orig_id] = unique_nodes[node_key]

    print(f"\nPackage deduplication summary:")
    print(f"  Total packages: {len(sbom_data.get('artifacts', []))}")
    print(f"  Unique packages: {len([k for k in unique_nodes.keys() if k[0] == 'pkg'])}")
    print(f"  Duplicates removed: {duplicate_count}")

    print("\n--- Processing File Nodes ---")
    duplicate_count = 0
    for file in sbom_data.get('files', []):
        orig_id = file.get('id', '')
        node_key = get_node_key('file', file)
        node_keys[orig_id] = node_key

        if node_key not in unique_nodes:
            node_id = create_node_id('file', file)
            unique_nodes[node_key] = node_id

            label = file.get('location', {}).get('path', '')
            dot.node(node_id, label,
                    shape='ellipse',
                    style='filled',
                    fillcolor='lightgreen',
                    tooltip=f"Type: {file.get('type', '')}")
            print(f"\nCreated new node:")
            print(f"  ID: {orig_id}")
            print(f"  Node ID: {node_id}")
        else:
            duplicate_count += 1
            print(f"\nFound duplicate file:")
            print(f"  ID: {orig_id}")
            print(f"  Using existing node: {unique_nodes[node_key]}")

        id_to_node[orig_id] = unique_nodes[node_key]

    print(f"\nFile deduplication summary:")
    print(f"  Total files: {len(sbom_data.get('files', []))}")
    print(f"  Unique files: {len([k for k in unique_nodes.keys() if k[0] == 'file'])}")
    print(f"  Duplicates removed: {duplicate_count}")

    print("\n--- Processing Relationships ---")
    graph = defaultdict(set)
    relationships = []

    for rel in sbom_data.get('artifactRelationships', []):
        parent_id = rel.get('parent', '')
        child_id = rel.get('child', '')
        rel_type = rel.get('type', '')

        if parent_id in id_to_node and child_id in id_to_node:
            parent_node = id_to_node[parent_id]
            child_node = id_to_node[child_id]
            relationships.append((parent_node, child_node, rel_type))
            graph[parent_node].add(child_node)

    print("\n--- Creating Non-redundant Edges ---")
    added_edges = set()
    for parent_node, child_node, rel_type in relationships:
        edge = (parent_node, child_node)
        if edge not in added_edges:
            if not is_redundant_edge(graph, parent_node, child_node):
                print(f"\nAdding edge:")
                print(f"  From: {parent_node}")
                print(f"  To: {child_node}")
                print(f"  Type: {rel_type}")

                dot.edge(parent_node, child_node,
                        label=rel_type,
                        tooltip=rel_type,
                        color='gray')
                added_edges.add(edge)
            else:
                print(f"\nSkipping redundant edge:")
                print(f"  From: {parent_node}")
                print(f"  To: {child_node}")
                print(f"  Type: {rel_type}")

    print(f"\nRelationship summary:")
    print(f"  Total relationships: {len(relationships)}")
    print(f"  Non-redundant edges: {len(added_edges)}")
    print("\n=== Graph Creation Complete ===")
    return dot

def main():
    if len(sys.argv) != 2:
        print("Usage: python sbom_visualizer.py <sbom_json_file>")
        sys.exit(1)

    sbom_file = sys.argv[1]
    try:
        print(f"\nProcessing SBOM file: {sbom_file}")

        sbom_data = load_sbom(sbom_file)
        print("SBOM file loaded successfully")

        dot = create_graph(sbom_data)

        output_base = os.path.splitext(os.path.abspath(sbom_file))[0]
        png_path = output_base + '_sbom_viz.png'

        print(f"\nGenerating visualization...")
        dot.render(output_base + '_sbom_viz', format='png', cleanup=True)

        print(f"\nGenerated visualization file:")
        print(f"- {png_path}")

        webbrowser.open('file://' + png_path)

    except Exception as e:
        print(f"\nError processing SBOM file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
