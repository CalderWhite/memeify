import sys
from antlr4 import *
from Python3.Python3Listener import Python3Listener
from Python3.Python3Lexer import Python3Lexer
from Python3.Python3Parser import Python3Parser

from WaveListener import WaveListener

def main(argv):
    input_stream = FileStream(argv[1])
    lexer = Python3Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = Python3Parser(stream)
    tree = parser.single_input()

    printer = WaveListener()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)

if __name__ == '__main__':
    main(sys.argv)
