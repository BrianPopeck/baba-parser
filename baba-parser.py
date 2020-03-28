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
    old_token_index = token_index
    success, root_node = S()
    return success


if __name__ == "__main__":
    lex("LONELY BABA IS YOU")
    print(token_stream)