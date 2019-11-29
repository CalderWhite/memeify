import ast
import symtable
import sys

import astunparse
import astpretty

builtins = ["abs", "delattr", "hash", "memoryview", "set", "all", "dict", "help",
            "min", "setattr", "any", "dir", "hex", "next", "slice", "ascii", "divmod",
            "id", "object", "sorted", "bin", "enumerate", "input", "oct", "staticmethod",
            "bool", "eval", "int", "open", "str", "breakpoint", "exec", "isinstance", "ord",
            "sum", "bytearray", "filter", "issubclass", "pow", "super", "bytes", "float",
            "iter", "print", "tuple", "callable", "format", "len", "property", "type",
            "chr", "frozenset", "list", "range", "vars", "classmethod", "getattr",
            "locals", "repr", "zip", "compile", "globals", "map", "reversed", "__import__",
            "complex", "hasattr", "max", "round"]

class SymbolSwapper(ast.NodeTransformer):
    
    def __init__(self, original, imported, excludes=[]):
        self.imported = imported
        self.original = original
        self.new_sym_table = {}
        self.counter = 0

        self.excludes = excludes + imported + builtins

    def next_sym(self):
        # seperate shift from i to allow for non alpha characters
        sym = list(self.original)
        shift = 0
        for i in range(len(self.original)):
            if sym[i] == sym[i].upper():
                continue

            if self.counter & (1 << shift):
                sym[i] = sym[i].upper()
            shift += 1

        self.counter += 1

        return "".join(sym)

    def visit_Name(self, node: ast.Name):
        _id = node.id
        if _id not in self.excludes:
            if _id not in self.new_sym_table:
                self.new_sym_table[_id] = self.next_sym()

            node.id = self.new_sym_table[_id]

        return node

    def visit_Attribute(self, node: ast.Attribute):
        attr = node.attr

        if type(node.value) == ast.Name:
            _id = node.value.id
            if _id == "self":
                if attr not in self.excludes:
                    if attr not in self.new_sym_table:
                        self.new_sym_table[attr] = self.next_sym()

                    node.attr = self.new_sym_table[attr]
            elif node.value.id not in self.excludes:
                if _id not in self.new_sym_table:
                    self.new_sym_table[_id] = self.next_sym()

                node.value.id = self.new_sym_table[_id]
        elif type(node.value) == ast.Attribute:
            if type(node.value.value) == ast.Name and node.value.value.id == "self":
                attr = node.value.attr
                if attr not in self.excludes:
                    if attr not in self.new_sym_table:
                        self.new_sym_table[attr] = self.next_sym()

                    node.value.attr = self.new_sym_table[attr]

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for i in range(len(node.args.args)):
            name = node.args.args[i].arg
            if name not in self.excludes:
                if name not in self.new_sym_table:
                    self.new_sym_table[name] = self.next_sym()

                node.args.args[i].arg = self.new_sym_table[name]

        name = node.name
        if name not in self.excludes:
            if name not in self.new_sym_table:
                self.new_sym_table[name] = self.next_sym()

            node.name = self.new_sym_table[name]

        # recursively change the symbols within the function
        for i in node.body:
            self.generic_visit(i)

        return node

    def print_stats(self):
        c = 0
        for i in self.original:
            if i != i.upper():
                c += 1

        print(len(self.new_sym_table.keys()), "symbols used of max", 1 << c)

def get_imports(s):
    imported = []
    table = symtable.symtable(s, "string", "exec")
    for i in table.get_symbols():
        if i.is_imported():
            imported.append(i.get_name())

    return imported

r = open(sys.argv[1]).read()
imported = get_imports(r)
parsed = ast.parse(r)

#print(astpretty.pprint(parsed))

swapper = SymbolSwapper("bruh_moment", imported, excludes=["__init__", "self", "Test",
                        "get_next_move", "get_pos", "grid_width"])
tree = swapper.visit(parsed)

swapper.print_stats()

#print(astunparse.unparse(tree))
open("out.py", 'w').write(astunparse.unparse(tree))
