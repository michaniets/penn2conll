import re
import sys
from pathlib import Path
import argparse

"""
Convert a Penn Treebank formatted file (.psd) into CoNLL-U format, capturing hierarchical tree relations.
This is not a grammar converter: it only extracts the tree structure and the terminal nodes, preserving the tree hierarchy.
Output CoNLL-U files can be queried using Grew Match (https://grew.fr/match/), grewpy or other tools that support CoNLL-U format.

This is a first version of the script. It will certainly not cover all the idiosyncracies of the .psd files.
version 0.1 AS 13.1.2025
"""

def parse_psd_to_conllu(psd_file, output_file):
    """
    Convert a Penn Treebank formatted file (.psd) into CoNLL-U format, capturing hierarchical tree relations.

    Args:
        psd_file (str): Path to the input .psd file.
        output_file (str): Path to the output .conllu file.
    """
    with open(psd_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split the input into graphs using empty lines as separators
    graphs = [graph.strip() for graph in content.split('\n\n') if graph.strip()]

    sentences = []

    for graph in graphs:
        # Check if metadata is adjoined to the whole graph
        metadata = {}
        if re.search(r'^\(\s*\(', graph):
            match = re.search(r'\(ID\s+(.*?)\)', graph)
            if match:
                metadata['id'] = match.group(1)
                graph = re.sub(r'\(ID\s+.*?\)', '', graph)  # Exclude the metadata line for the tree
            # Delete the outer pair of brackets and the metadata from the graph
            graph = graph[1:-1].strip()

        # Reconstruct the graph from the lines
        lines = graph.splitlines()

        # Extract metadata from the last line if it's within the graph (not adjoined)
        if re.search(r'\(ID\s', lines[-1]):
            metadata['id'] = re.search(r'\(ID\s+(.*?)\)', lines[-1]).group(1)
            lines[-1] = re.sub(r'\(ID\s+.*?\)', '', lines[-1]) # Exclude the metadata line for the tree
    
        tree_str = '\n'.join(lines)  # Reconstructed graph

        tree_count = len(sentences) + 1
        (tree, add_to_metadata) = parse_tree(tree_str, tree_count)
        sentences.append((metadata, add_to_metadata, tree))

    # Write to CoNLL-U format
    with open(output_file, 'w', encoding='utf-8') as f:
        sent_nr = 0
        for metadata, add_to_metadata, tree in sentences:
            if args.add_sent_nr:
                sent_nr += 1
                f.write(f"# sent_nr = {sent_nr}\n")
            id_string = "NO_ID" if 'id' not in metadata else metadata['id']
            f.write(f"# sent_id = {id_string}\n")
            words = [node['form'] for node in tree if 'type=word' in node['feats']]
            sentence_text = ' '.join(words) #+ f" (metadata['id'])" if 'id' in metadata else ' '.join(words)
            if args.add_id_to_text:
#                sentence_text += f" ({id_string})"
                sentence_text = f"{sentence_text} ({id_string})"
            f.write(f"# text = {sentence_text}\n") if sentence_text else f.write("# text = EMPTY\n")
            for line in add_to_metadata:
                f.write(f"{line}\n")
            for i, node in enumerate(tree, start=1):
                f.write(
                    f"{i}\t{node['form']}\t{node['lemma']}\t{node['upostag']}\t{node['xpostag']}\t{node['feats']}\t{node['head']}\t{node['deprel']}\t{node['deps']}\t{node['misc']}\n"
                )
            f.write("\n")

def parse_tree(tree_str, tree_count):
    """
    Parse a tree structure in Penn Treebank format and return CoNLL-U-compatible rows.

    Args:
        tree_str (str): The tree structure in Penn Treebank format.
        tree_count (int): The current count of trees processed.

    Returns:
        list: List of dictionaries representing tokens and nodes in CoNLL-U format.
    """
    rows = []   # List of dicts holding conllu rows
    index = 0   # Index of the current node
    add_to_metadata = []  # List of metadata lines to add to the metadata section

    def add_node(form, lemma, upostag, xpostag, feats, head, deprel, deps, misc):
        nonlocal index
        index += 1
        rows.append({
            'form': form,
            'lemma': lemma,
            'upostag': upostag,
            'xpostag': xpostag,
            'feats': feats,
            'head': head,
            'deprel': deprel,
            'deps': deps,
            'misc': misc
        })

    def process_subtree(subtree, head_index):
        """ Recursively process subtrees to extract nodes and tokens. """
        nonlocal index
        feat_type = 'word' # Default feature type
        deps = '_' # Default deps field
        misc = '_' # Default misc field

        if isinstance(subtree, str):
            return

        if len(subtree) == 2 and isinstance(subtree[1], str):
            # Terminal node
            form, lemma = subtree[1], '_'
            if args.nodes_as_upos:
                upostag = subtree[0]
            else:
                upostag = '_'
            if re.search(r'^\*', form):
                feat_type = 'trace'
            if subtree[0] == 'CODE':  # for code nodes: store the code in the MISC field
                feat_type = 'code'
                misc = form  # store the code in the MISC field
                form = '_'  # empty form if code
            if args.codes_as_meta and subtree[0] == 'CODE':
                add_to_metadata.append(f"# code_after_{index} = {misc}")  # collect code nodes in metadata, not in the tree
                return
            add_node(form, lemma, upostag, '_', f"type={feat_type}", head_index, subtree[0], deps, misc)
        else:
            # Non-terminal node
            feat_type = 'node'
            node_type = subtree[0]
            node_index = index + 1
            add_node('_', '_', '_', '_', f"type={feat_type}", head_index, node_type, deps, misc)

            for child in subtree[1:]:
                process_subtree(child, node_index)

    # Parse the tree structure into a nested list
    tree = parse_bracketed_structure(tree_str)
    process_subtree(tree, 0)

    # Display progress count to stderr for every 50th tree
    if tree_count % 50 == 0:
        sys.stderr.write(f"\rProcessed tree count: {tree_count}")
        sys.stderr.flush()

    return (rows, add_to_metadata)

def parse_bracketed_structure(tree_str):
    """
    Convert a bracketed string into a nested list structure.
    Args:
        tree_str (str): The bracketed tree string.
    Returns:
        list: Nested list representing the tree structure.
    """
    stack = []
    current = []
    token = ''

    for char in tree_str:
        if char == '(':
            if token:
                current.append(token)
                token = ''
            stack.append(current)
            current = []
        elif char == ')':
            if token:
                current.append(token)
                token = ''
            completed = current
            current = stack.pop()
            current.append(completed)
        elif char.isspace():
            if token:
                current.append(token)
                token = ''
        else:
            token += char

    return current[0] if current else []

def main(args):
    parse_psd_to_conllu(args.input_psd_file, args.output_conllu_file)

    print(f"\nDone. Output written to {args.output_conllu_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
        """
            Convert PSD to CoNLL-U

            Convert a Penn Treebank formatted file (.psd) into CoNLL-U format, capturing the hierarchical tree relations.
            This is a graph converter, not a grammar converter! It only extracts the tree structure and the terminal nodes, preserving the tree hierarchy.
            Without any options, the script will include all the information in the CoNLL-U structure (including CODE elements).

            Output CoNLL-U files can be processed with any tool that supports CoNLL-U format, for example:
            - queried or modified using Grew (https://grew.fr/match/)
            - further processed using Python grewpy
            - inspected with CoNLL-U viewers like https://universaldependencies.org/conllu_viewer.html

            When the --codes_as_meta option is used, CODE elements are listed in metadata instead of including them in the tree.

        """)
    parser.add_argument("input_psd_file", help="Path to the input .psd file.")
    parser.add_argument("output_conllu_file", help="Path to the output .conllu file.")
    parser.add_argument("--codes_as_meta", action="store_true", help="List CODE elements in metadata instead of including them in the tree.")
    parser.add_argument("--nodes_as_upos", action="store_true", help="Take Penn nodes as upos of terminal nodes.")
    parser.add_argument("--add_sent_nr", action="store_true", help="Add sentence number to the metadata (# sent_nr =).")
    parser.add_argument("--add_id_to_text", action="store_true", help="Add ID string to text strint in the metadata.")
    args = parser.parse_args()
    main(args)
    