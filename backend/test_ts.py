import tree_sitter_python
from tree_sitter import Language, Parser
print(tree_sitter_python.__version__)
lang = Language(tree_sitter_python.language())
parser = Parser(lang)
print(parser)
