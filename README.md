# PSD to CoNLL-U Converter

## psd2conll.py

The script converts Penn Treebank-formatted files (`.psd`) into CoNLL-U format, capturing the hierarchical tree relations.  
It is a **graph converter** and does not perform grammar conversion. The tool extracts the tree structure and terminal nodes, preserving the tree hierarchy.

## Features

- Converts `.psd` files to CoNLL-U format.
- Includes all tree structure information by default, including `CODE` elements.
- Compatible with tools like:
  - **[Grew](https://grew.fr/match/)**: For querying or modifying CoNLL-U files.
  - **Python Grewpy**: For further processing.
  - **CoNLL-U Viewer**: [Universal Dependencies Viewer](https://universaldependencies.org/conllu_viewer.html).
- Offers options for customizing the output, including metadata adjustments.

---

## Usage

### Command-line Arguments

```bash
python script_name.py [OPTIONS] <input_psd_file> <output_conllu_file>
```
