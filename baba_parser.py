import sys
from terminal_symbols import TERMINAL_SYMBOLS
from timeit import default_timer as timer

token_stream = []
token_index = 0

def lex(string):
    word_list = string.split(' ')
    for word in word_list:
        token = tokenize(word)
        token_stream.append(token)

def tokenize(token_str):
    for terminal, lexeme_list in TERMINAL_SYMBOLS.items():
        if token_str in lexeme_list:
            return (terminal, token_str)
    
    raise ValueError('{} is not a valid token'.format(token_str))

def parse():
    return S()

def parse_file(filename):
    global token_stream
    global token_index

    with open(filename, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            if not line.startswith('//'):   # ignore comments
                token_stream = []
                token_index = 0
                lex(line)
                success, root_node = parse()
                if success:
                    print('PASSED -- {} has rules {}'.format(line, root_node['value']))
                else:
                    print('FAILED -- {} could not be parsed'.format(line))
                    raise ValueError('failed to parse rule from file {}'.format(filename))

# Evaluate LHS with RHS composed of a variable number of symbols. Returns success, nodes.
def grammar_rule(*symbols):
    global token_index
    
    saved_index = token_index
    nodes = []
    for symbol in symbols:
        success, node = symbol()
        if success:
            nodes.append(node)
        else:
            token_index = saved_index
            return False, None
    
    return True, nodes

def is_token(token_str):
    global token_index

    if token_index >= len(token_stream):    # are at the end of the input
        return False, None
    
    token, lexeme = token_stream[token_index]
    if token == token_str:
        token_index += 1
        return True, {
            'children': None,
            'value': lexeme
        }  # return list of nodes similar to grammar_rule()
    else:
        return False, None

##### BEGIN GRAMMAR RULES #####
# S -> Rule If Noun Verb Preposition_phrase_list | Rule
def S():
    global token_index

    # lookahead to see if if-condition can be matched - avoid unnecessary backtracking
    if ('T_If', 'IF') in token_stream:
        success, nodes = grammar_rule(Rule, If, Noun, Verb, Preposition_phrase_list)
        if success:
            if_cond_rules = []
            for condition in nodes[4]['value']:
                if_cond_rule = {'noun': nodes[2]['value'], 'condition': condition, 'verb': nodes[3]['value']}
                if_cond_rules.append(if_cond_rule)
            rules = nodes[0]['value']
            for rule in rules:
                rule[nodes[1]['value']] = if_cond_rules
            return True, {'children': nodes, 'value': rules}

    success, nodes = grammar_rule(Rule)
    if success:    # note that it is ok if we have NOT matched the entire stream
        return True, {'children': nodes, 'value': nodes[0]['value']}

    return False, None

# Rule -> Noun_phrase_list Predicate_list
def Rule():
    success, nodes = grammar_rule(Noun_phrase_list, Predicate_list)
    if success:
        rules = []
        for noun_conditions_map in nodes[0]['value']:
            for noun, condition_list in noun_conditions_map.items():
                if len(condition_list) == 0:
                    # set condition to None
                    for verb_targets_map in nodes[1]['value']:
                        for verb, targets_list in verb_targets_map.items():
                            for target in targets_list:
                                rule = {'noun': noun, 'condition': None, 'verb': verb, 'target': target}
                                rules.append(rule)
                else:
                    for condition in condition_list:
                        # generate rule set per condition
                        for verb_targets_map in nodes[1]['value']:
                            for verb, targets_list in verb_targets_map.items():
                                for target in targets_list:
                                    rule = {'noun': noun, 'condition': condition, 'verb': verb, 'target': target}
                                    rules.append(rule)

        return True, {'children': nodes, 'value': rules}
    
    return False, None

# Noun_phrase_list -> Noun_phrase T_And Noun_phrase_list | Noun_phrase
def Noun_phrase_list():
    success, nodes = grammar_rule(Noun_phrase, T_And, Noun_phrase_list)
    if success:
        return True, {'children': nodes, 'value': [nodes[0]['value']] + nodes[2]['value']}    # list of nouns to conditions maps
    else:
        success, nodes = grammar_rule(Noun_phrase)

    if success:
        return True, {'children': nodes, 'value': [nodes[0]['value']]}  # list containing singular nouns to conditions map

    return False, None

# Noun_phrase -> Adjective Noun Preposition_phrase_list
def Noun_phrase():
    success, nodes = grammar_rule(Adjective, Noun, Preposition_phrase_list)
    if success:
        if nodes[0]['value'] is None:   # no adjective
            return True, {'children': nodes, 'value': {
                nodes[1]['value']: nodes[2]['value']    # noun mapped to list of conditions applying to that noun
            }}
        else:   # adjective present
            return True, {'children': nodes, 'value': {
                nodes[1]['value']: [nodes[0]['value']] + nodes[2]['value']    # noun mapped to list of conditions applying to that noun
            }}

    return False, None

# Preposition_phrase_list -> Preposition_phrase T_And Preposition_phrase_list | Preposition_phrase | epsilon
def Preposition_phrase_list():
    success, nodes = grammar_rule(Preposition_phrase, T_And, Preposition_phrase_list)
    if success:
        return True, {'children': nodes, 'value': [nodes[0]['value']] + nodes[2]['value']}  # list of conditions
    else:
        success, nodes = grammar_rule(Preposition_phrase)

    if success:
        return True, {'children': nodes, 'value': [nodes[0]['value']]}  # list containing singular condition
    else:
        return True, {'children': None, 'value': []}   # epsilon rule always matches

    return False, None

# Preposition_phrase -> Preposition Noun | Preposition Property
def Preposition_phrase():
    success, nodes = grammar_rule(Preposition, Noun)
    if success:
        return True, {'children': nodes, 'value': nodes[0]['value'] + ' ' + nodes[1]['value']}  # e.g. ON GRASS
    else:
        success, nodes = grammar_rule(Preposition, Property)

    if success:
        return True, {'children': nodes, 'value': nodes[0]['value'] + ' ' + nodes[1]['value']}  # e.g. FACING RIGHT -- note that this might require semantic analysis to rule out nonsense combinations like FACING PURPLE or NEAR MORE

    return False, None

# Predicate_list -> Predicate T_And Predicate_list | Predicate
def Predicate_list():
    success, nodes = grammar_rule(Predicate, T_And, Predicate_list)
    if success:
        return True, {'children': nodes, 'value': [nodes[0]['value']] + nodes[2]['value']}    # list containing multiple verb to properties mappings
    else:
        success, nodes = grammar_rule(Predicate)

    if success:
        return True, {'children': nodes, 'value': [nodes[0]['value']]}  # list containing singular verb to properties mapping
    
    return False, None

# Predicate -> Verb Property_list | Verb Noun
def Predicate():
    success, nodes = grammar_rule(Verb, Property_list)
    if success:
        return True, {'children': nodes, 'value': {
            nodes[0]['value']: nodes[1]['value']
        }}
    else:
        success, nodes = grammar_rule(Verb, Noun)

    if success:
        return True, {'children': nodes, 'value': {
            nodes[0]['value']: [nodes[1]['value']]
        }}

    return False, None

# Property_list -> Property T_And Property_list | Property
def Property_list():
    success, nodes = grammar_rule(Property, T_And, Property_list)
    if success:
        return True, {'children': nodes, 'value': [nodes[0]['value']] + nodes[2]['value']}
    else:
        success, nodes = grammar_rule(Property)

    if success:
        return True, {'children': nodes, 'value': [nodes[0]['value']]}

    return False, None

# Not_list -> T_Not Not_list | epsilon
def Not_list():
    success, nodes = grammar_rule(T_Not, Not_list)
    if success:
        return True, {'children': nodes, 'value': nodes[1]['value'] + 1}    # count consecutive NOTs

    # epsilon rule always matches
    return True, {'children': None, 'value': 0}

# Noun -> Not_list T_Noun
def Noun():
    success, nodes = grammar_rule(Not_list, T_Noun)
    if success:
        is_negated = nodes[0]['value'] % 2 == 1
        noun_str = '~' + nodes[1]['value'] if is_negated else nodes[1]['value']
        return True, {'children': nodes, 'value': noun_str}

    return False, None

# Verb -> Not_list T_Verb
def Verb():
    success, nodes = grammar_rule(Not_list, T_Verb)
    if success:
        is_negated = nodes[0]['value'] % 2 == 1
        verb_str = '~' + nodes[1]['value'] if is_negated else nodes[1]['value']
        return True, {'children': nodes, 'value': verb_str}

    return False, None

# Property -> Not_list T_Property
def Property():
    success, nodes = grammar_rule(Not_list, T_Property)
    if success:
        is_negated = nodes[0]['value'] % 2 == 1
        property_str = '~' + nodes[1]['value'] if is_negated else nodes[1]['value']
        return True, {'children': nodes, 'value': property_str}

    return False, None

# Adjective -> Not_list T_Adjective | epsilon
def Adjective():
    success, nodes = grammar_rule(Not_list, T_Adjective)
    if success:
        is_negated = nodes[0]['value'] % 2 == 1
        adjective_str = '~' + nodes[1]['value'] if is_negated else nodes[1]['value']
        return True, {'children': nodes, 'value': adjective_str}

    return True, {'children': None, 'value': None}   # epsilon rule always matches

# Preposition -> Not_list T_Preposition
def Preposition():
    success, nodes = grammar_rule(Not_list, T_Preposition)
    if success:
        is_negated = nodes[0]['value'] % 2 == 1
        preposition_str = '~' + nodes[1]['value'] if is_negated else nodes[1]['value']
        return True, {'children': nodes, 'value': preposition_str}

    return False, None

# Condition -> Not_list T_Condition
def Condition():
    success, nodes = grammar_rule(Not_list, T_Condition)
    if success:
        is_negated = nodes[0]['value'] % 2 == 1
        condition_str = '~' + nodes[1]['value'] if is_negated else nodes[1]['value']
        return True, {'children': nodes, 'value': condition_str}

    return False, None

# If -> Not_list T_if
def If():
    success, nodes = grammar_rule(Not_list, T_If)
    if success:
        is_negated = nodes[0]['value'] % 2 == 1
        if_str = '~' + nodes[1]['value'] if is_negated else nodes[1]['value']
        return True, {'children': nodes, 'value': if_str}

    return False, None

def T_Noun():
    return is_token('T_Noun')

def T_Verb():
    return is_token('T_Verb')

def T_Property():
    return is_token('T_Property')

def T_Adjective():
    return is_token('T_Adjective')

def T_Preposition():
    return is_token('T_Preposition')

def T_Condition():
    return is_token('T_Condition')

def T_And():
    return is_token('T_And')

def T_Not():
    return is_token('T_Not')

def T_If():
    return is_token('T_If')

##### END GRAMMAR RULES #####
 
def main(argv):
    if len(argv) == 2:
        # read strings from file
        filename = argv[1]
        start = timer()
        parse_file(filename)
        end = timer()
        print("Took {} seconds to parse the strings (and print results) in {}".format(end - start, filename))
    elif len(argv) == 1:
        # interactive mode
        while True:
            lex(input('Enter a phrase to parse: ').upper())
            success, root_node = parse()
            if success:
                print(root_node['value'])
            else:
                print("parsing FAILED")
    else:
        print('usage: python3 baba_parser.py [filename]\nor for interactive mode, python3 baba_parser.py')
        sys.exit(1)

if __name__ == '__main__':
    main(sys.argv)
