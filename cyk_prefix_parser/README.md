This is a CYK Prefix Parser implemented in Python 3.

Based on a basic CYK parser from https://github.com/ikergarcia1996/Basic-CYK-Parser.git - by ikergarcia1996, Iker García Ferrero

CFG to CNF is based on https://github.com/adelmassimo/CFG2CNF.git - by adelmassimo

# Files in the repository
1. cfg2cnf.py: CFG to CNF converter in .py format
2. helper.py: implementation of auxiliary function for cfg2cnf
3. CYK_Parser.py: Prefix Parser in .py format
4. example.py: a possible examples of use (usage: python3 example.py)
5. example_grammar*.txt: Some example grammars



# Example Of Use
 
```
# convert to CNF format using the call 
python cfg2cnf.py <path to grammar file>
this will create grammar_cnf.txt

# Initialize the grammar and read the rules from a file
g = Grammar('grammar_cnf.txt')

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

# Example of grammar file - for CFG2CNF converter

```
Terminals:
all terminal symbols
Variables:
all non-terminal symbols
Productions:
all productions rules like: P -> A B C | A D | E C
with ; at the end of each line except the last one

For example:
Terminals:
she eats with fish fork a
Variables:
S NP VP V PP NP P N Det
Productions:
S -> NP VP;
VP -> VP PP | V NP | eats;
PP -> P NP;
NP -> Det N | she;
V -> eats;
P -> with;
N -> fish | fork;
Det -> a
```

# Example of grammar file - for parser
The program assumes that the grammar is a valid context-free grammar in CNF form. Rules must be separated by lines. 
```
S -> NP VP 
VP -> VP PP 
VP -> V NP 
VP -> eats 
PP -> P NP 
NP -> Det N 
NP -> she 
V -> eats 
P -> with 
N -> fish 
N -> fork 
Det -> a 

Non-Terminal rules with multiple outcome options should be written in different lines
Each outcome should be a terminal symbol or 2 Non-Terminal Symbols divided by space. 
```




