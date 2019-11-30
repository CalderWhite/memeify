import ast
import symtable
import sys

import astunparse

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

    def get_new_sym(self, sym):
        if sym not in self.excludes:
            if sym not in self.new_sym_table:
                self.new_sym_table[sym] = self.next_sym()

            return self.new_sym_table[sym]

        return sym

    def visit_Name(self, node: ast.Name):
        node.id = self.get_new_sym(node.id)
        return node

    def visit_Attribute(self, node: ast.Attribute):
        if type(node.value) == ast.Name:
            _id = node.value.id
            if _id == "self":
                node.attr = self.get_new_sym(node.attr)
            elif node.value.id not in self.excludes:
                node.value.id = self.get_new_sym(node.value.id)
        elif type(node.value) == ast.Attribute:
            if type(node.value.value) == ast.Name and node.value.value.id == "self":
                self.visit(node.value)
        elif type(node.value) == ast.Subscript:
            self.visit(node.value)

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for i in range(len(node.args.args)):
            name = node.args.args[i].arg

            node.args.args[i].arg = self.get_new_sym(name)
        node.name = self.get_new_sym(node.name)

        # recursively change the symbols within the function
        for i in node.body:
            self.generic_visit(i)

        return node

    def visit_Lambda(self, node: ast.Lambda):
        for i in range(len(node.args.args)):
            name = node.args.args[i].arg

            node.args.args[i].arg = self.get_new_sym(name)

        self.visit(node.body)
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


def main(args):
    r = open(args[1]).read()
    imported = get_imports(r)
    parsed = ast.parse(r)

    if len(args) < 4:
        args.append([])

    swapper = SymbolSwapper(args[2], imported, excludes=["__init__", "self"] + args[3].split(","))
    tree = swapper.visit(parsed)

    swapper.print_stats()
    open("out.py", 'w').write(astunparse.unparse(tree))


if __name__ == "__main__":
    main(sys.argv)
