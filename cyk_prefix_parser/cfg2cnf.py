# -*- coding: utf-8 -*-
# IT's assumed that starting variable is the first typed
import sys
from cyk_prefix_parser import helper
# import helper

left, right = 0, 1

K, V, Productions = [], [], []

original_vaiableJar = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
                        "W", "X", "Y", "Z"]

variablesJar = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
                "W", "X", "Y", "Z"]

emptyJar_index = 1



def isUnitary(rule, variables):
    if rule[left] in variables and rule[right][0] in variables and len(rule[right]) == 1:
        return True
    return False


def isSimple(rule):
    if rule[left] in V and rule[right][0] in K and len(rule[right]) == 1:
        return True
    return False

def EmptyCheck(variables):
    global variablesJar, emptyJar_index
    # print(variablesJar)
    while len(variablesJar) == 0:
        variablesJar = [(symbol + str(emptyJar_index)) for symbol in original_vaiableJar if (symbol + str(emptyJar_index)) not in variables and (symbol + str(emptyJar_index)) not in V]
        emptyJar_index = emptyJar_index + 1

# Add S0->S rule––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––START
def START(productions, variables):
    variables.append('S0')
    return [('S0', [variables[0]])] + productions


# Remove rules containing both terms and variables, like A->Bc, replacing by A->BZ and Z->c–––––––––––TERM
def TERM(productions, variables):
    newProductions = []
    # create a dictionari for all base production, like A->a, in the form dic['a'] = 'A'
    dictionary = helper.setupDict(productions, variables, terms=K)
    for production in productions:
        # check if the production is simple
        if isSimple(production):
            # in that case there is nothing to change
            newProductions.append(production)
        else:
            for term in K:
                for index, value in enumerate(production[right]):
                    if term == value and not term in dictionary:
                        # it's created a new production vaiable->term and added to it
                        dictionary[term] = variablesJar.pop()
                        # Variables set it's updated adding new variable
                        V.append(dictionary[term])
                        newProductions.append((dictionary[term], [term]))
                        EmptyCheck(variables)
                        production[right][index] = dictionary[term]
                    elif term == value:
                        production[right][index] = dictionary[term]
            newProductions.append((production[left], production[right]))

    # merge created set and the introduced rules
    return newProductions


# Eliminate non unitry rules––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––BIN
def BIN(productions, variables):
    result = []
    for production in productions:
        k = len(production[right])
        # newVar = production[left]
        if k <= 2:
            result.append(production)
        else:
            newVar = variablesJar.pop(0)
            variables.append(newVar + '1')
            EmptyCheck(variables)
            result.append((production[left], [production[right][0]] + [newVar + '1']))
            i = 1
            # TODO
            for i in range(1, k - 2):
                var, var2 = newVar + str(i), newVar + str(i + 1)
                assert var2 not in variables,"var2 already used"
                variables.append(var2)
                if var in variablesJar:
                    variablesJar.remove(var)
                if var2 in variablesJar:
                    variablesJar.remove(var2)
                EmptyCheck(variables)
                result.append((var, [production[right][i], var2]))
            result.append((newVar + str(k - 2), production[right][k - 2:k]))
    return result


# Delete non terminal rules–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––DEL
def DEL(productions):
    newSet = []
    # seekAndDestroy throw back in:
    #        – outlaws all left side of productions such that right side is equal to the outlaw
    #        – productions the productions without outlaws
    outlaws, productions = helper.seekAndDestroy(target='e', productions=productions)
    # add new reformulation of old rules
    for outlaw in outlaws:
        # consider every production: old + new resulting important when more than one outlaws are in the same prod.
        for production in productions + [e for e in newSet if e not in productions]:
            # if outlaw is present in the right side of a rule
            if outlaw in production[right]:
                # the rule is rewrited in all combination of it, rewriting "e" rather than outlaw
                # this cycle prevent to insert duplicate rules
                newSet = newSet + [e for e in helper.rewrite(outlaw, production) if e not in newSet]

    # add unchanged rules and return
    return newSet + ([productions[i] for i in range(len(productions))
                      if productions[i] not in newSet])


def unit_routine(rules, variables):
    unitaries, result = [], []
    # controllo se una regola è unaria
    for aRule in rules:
        if isUnitary(aRule, variables):
            unitaries.append((aRule[left], aRule[right][0]))
        else:
            result.append(aRule)
    # altrimenti controllo se posso sostituirla in tutte le altre
    for uni in unitaries:
        for rule in rules:
            if uni[right] == rule[left] and uni[left] != rule[left]:
                result.append((uni[left], rule[right]))

    return result


def UNIT(productions, variables):
    i = 0
    result = unit_routine(productions, variables)
    tmp = unit_routine(result, variables)
    while result != tmp and i < 1000:
        result = unit_routine(tmp, variables)
        tmp = unit_routine(result, variables)
        i += 1
    return result


def converter(modelPath):
    k, v, productions = helper.loadModel(modelPath)
    
    for nonTerminal in v:
        if nonTerminal in variablesJar:
            variablesJar.remove(nonTerminal)
    for nonTerminal in V:
        if nonTerminal in variablesJar:
            variablesJar.remove(nonTerminal)
    EmptyCheck(variables=v)

    # productions = START(productions, variables=V)
    productions = TERM(productions, variables=v)
    productions = BIN(productions, variables=v)
    productions = DEL(productions)
    productions = UNIT(productions, variables=v)

    # print(helper.prettyForm(productions))
    # print(len(productions))
    open('grammar_cnf.txt', 'w').write(helper.prettyForm(productions))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        modelPath = str(sys.argv[1])
    else:
        modelPath = 'model.txt'

    converter(modelPath)
