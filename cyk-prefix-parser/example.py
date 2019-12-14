#usage: pyhton3 example.py

import CYK_Paser as grammar

g = grammar.Grammar('example_grammar1.txt')
g.parse('a a')
g.print_parse_table()

print('')
print('')
print('')



