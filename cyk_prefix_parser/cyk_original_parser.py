class Dictlist(dict):
    
    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)



class Grammar(object):
    grammar_rules = Dictlist()
    grammar_origins = set()
    parse_table = None
    length = 0
    tokens = []
    
    #Parameters:
    #   Filename: file containing a grammar
    
    def __init__(self, filename):
        self.grammar_rules = Dictlist()
        self.parse_table = None
        self.length = 0
        for line in open(filename):
            a, b = line.split("->")
            self.grammar_rules[b.rstrip().strip()] = a.rstrip().strip()
            self.grammar_origins.add(a.rstrip().strip())
        
        if len(self.grammar_rules) == 0:
            raise ValueError("No rules found in the grammar file")
        # print('')
        # print('Grammar file readed succesfully. Rules readed:')
        # self.print_rules()
        # print('')
    
    #Print the production rules in the grammar
    
    def print_rules(self):
        for r in self.grammar_rules:
            for p in self.grammar_rules[r]:
                print(str(p) + ' --> ' + str(r))
        
    def apply_rules(self,t):
        try:
            return self.grammar_rules[t]
        except KeyError as r:
            return None
            
    #Parse a sentence (string) with the CYK algorithm
    def parse(self, sentence):
        self.tokens = sentence.split()
        self.length = len(self.tokens)
        if self.length < 1:
            raise ValueError("The sentence could no be read")
        self.parse_table = [[set() for x in range(self.length - y)] for y in range(self.length)]

        # Process the first line
        for x, t in enumerate(self.tokens):
            r = self.apply_rules(t)
            if r is None:
                raise ValueError("The word " + str(t) + " is not in the grammar")
            else:
                for w in r: 
                    self.parse_table[0][x].add(w)

        # Run CYK-Parser
        for l in range(2,self.length+1):
            for s in range(1,self.length-l+2):
                for p in range(1,l-1+1):
                    
                    t1 = self.parse_table[p-1][s-1]
                    t2 = self.parse_table[l-p-1][s+p-1]
                            
                    for a in t1:
                        for b in t2:
                            r = self.apply_rules(str(a) + " " + str(b))
                                    
                            if r is not None:
                                for w in r:
                                    self.parse_table[l-1][s-1].add(w)


        if str('S') in self.parse_table[self.length-1][0]:
            return True
        else:
            return False
  
