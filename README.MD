# Text Summarizer using Lexical Chains 

The program reads sentences from a file and creates lexical chains to summarize the text.
The output is stored in 'summary.txt' along with a graphical representation of lexical chains in 'lexicalChains.png'.

## Usage
python3 textSummarizer.py sentences.txt

## How it works?

The sentences are read from the file and networkx is used to make undirected graph of the words based on synsets, hyponyms and hypernyms. Later the connected components of the graph are used to build lexical chains and the longest chain is used to summarize text. The sentences that have words from the longest lexical chain are used in the text summary.

## Orphan Pronouns
To avoid the problem of orphan pronouns, every sentence that is followed by a sentence that has a pronoun is added in the text summary. The underlying assumption is that the every pronoun has its corresponding noun present in the sentence that precedes it.

## Libraries
* [networkx](https://networkx.github.io/):
A Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks.
* [wordnet](https://wordnet.princeton.edu/): A large lexical database of English. Nouns, verbs, adjectives and adverbs are grouped into sets of cognitive synonyms (synsets), each expressing a distinct concept.
