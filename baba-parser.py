from terminal_symbols import TERMINAL_SYMBOLS

token_stream = []
token_index = 0

root_node = None    # root node of the parse tree; each node is a dictionary, must have a 'children' field

def lex(string):
    word_list = string.split(' ')
    for word in word_list:
        token = tokenize(word)
        token_stream.append(token)

def tokenize(token_str):
    for terminal, lexeme_list in TERMINAL_SYMBOLS.items():
        if token_str in lexeme_list:
            return (terminal, token_str)
    
    raise ValueError("{} is not a valid token".format(token_str))

def parse():
    global root_node
    
    success, root_node = S()
    return success

def S():
    success, nodes = grammar_rule(T_Noun, T_Verb, T_Property)
    print(nodes)
    node = {
        'children': nodes,
        'value': {
            'object': nodes[0]['value'],
            'verb': nodes[1]['value'],
            'property': nodes[2]['value']
        }
    }

    return success, node

def T_Noun():
    return is_token("T_Noun")

def T_Verb():
    return is_token("T_Verb")

def T_Property():
    return is_token("T_Property")

# Evaluate LHS with RHS composed of a variable number of symbols. Returns success, nodes.
def grammar_rule(*symbols):
    global token_index
    
    saved_index = token_index
    nodes = []
    for symbol in symbols:
        print(symbol)
        success, node = symbol()
        if success:
            nodes.append(node)
        else:
            token_index = saved_index
            return False, None
    
    return True, nodes

def is_token(token_str):
    global token_index
    
    token, lexeme = token_stream[token_index]
    if token == token_str:
        token_index += 1
        return True, {
            'children': None,
            'value': lexeme
        }
    else:
        return False, None
        
    

if __name__ == "__main__":
    lex("BABA IS YOU")
    print(token_stream)

    print("Try parsing...")
    if parse():
        print(root_node["value"])