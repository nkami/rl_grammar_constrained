This is a CYK Prefix Parser implemented in Python 3.

Based on a basic CYK parser from https://github.com/ikergarcia1996/Basic-CYK-Parser.git - by ikergarcia1996, Iker García Ferrero
# Files in the repository

1. CYK_Parser.py: Prefix Parser in .py format
2. example.py: a possible examples of use (usage: python3 example.py)
3. example_grammar*.txt: Some example grammars



# Example Of Use
 
```
# Initialize the grammar and read the rules from a file
g = Grammar('example_grammar1.txt')

# Parse a sentence
g.parse('astronomers saw stars with ears')

# Print the table used for parsing the sentence
g.print_parse_table()

```

 ## Expected output

```
#For the Grammer file read
Grammar file readed succesfully. Rules readed:
S --> NP VP
PP --> P NP
VP --> V NP
VP --> VP PP
NP --> NP PP
NP --> astronomers
NP --> ears
NP --> saw
V --> saw
NP --> telescope
NP --> stars
P --> with


# For the parsing table
-----------  ------------  ------  ------  ------
['S', 'S']
[]           ['VP', 'VP']
['S']        []            ['NP']
[]           ['VP']        []      ['PP']
['NP']       ['NP', 'V']   ['NP']  ['P']   ['NP']
astronomers  saw           stars   with    ears
-----------  ------------  ------  ------  ------
```

# Example of grammar file
The program assumes that the grammar is a valid context-free grammar in CNF form. Rules must be separated by lines. 
```
S -> NP VP
PP -> P NP
VP -> V NP
VP -> VP PP
NP-> NP PP
NP -> astronomers
NP -> ears
NP -> saw
NP-> telescope
NP -> stars
P -> with
V -> saw

Non-Terminal rules with multiple outcome options should be written in different lines
Each outcome should be a terminal symbol or 2 Non-Terminal Symbols divided by space. 
```




