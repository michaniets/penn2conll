# PSD to CoNLL-U Converter

This is work in progress, motivated by the desire of some Penn corpus users to use tools different from *CorpusSearch* to process the texts.
Before using these tools to reformat Penn corpora, verify if the license of the corpus allows you to do so.

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
  - There is a hands-on [Online Tutorial](https://universal.grew.fr/?tutorial=yes) for *Grew queries* 
- Offers options for customizing the output, including metadata adjustments and handling of 'CODE' strings.

See [ud-coding](https://github.com/michaniets/ud-coding) for a script providing a function similar to *CorpusSearch*'s coding queries.

### Usage

Without any options, the script will preserve the information of each node it encounters in the CoNLL-U structure (including CODE elements).

```bash
python script_name.py [OPTIONS] <input_psd_file> <output_conllu_file>
```
