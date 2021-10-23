import regex

def search_open_square_bracket(word):
    """Search for open square bracket in a string

    Args:
        word (str): String to search.

    Returns:
        bool: True if the string contains open square bracket, False otherwise.
    """
    return (word.count("[") - word.count("]")) != 0


def search_open_parenthesis(word):
    """Search for open square bracket in a string

    Args:
        word (str): String to search.

    Returns:
        bool: True if the string contains open square bracket, False otherwise.
    """
    return (word.count("(") - word.count(")")) != 0


def search_before(position, text, pattern):
    """
    Search for the parameter before the given position in the given text.
    """
    # Find the first open parenthesis before the given position.
    seed_search = position - 2 # because of the parenthesis ")"
    par_count = 1
    get_paranthesis_body = ""
    while True:
        if text[seed_search] == pattern[0]:
            par_count -= 1
        elif text[seed_search] == pattern[1]:
            par_count += 1
        if seed_search == 0 or par_count == 0:
            # if is the first character of the line.
            if seed_search == 0:
                break
            # if the next character is a space.
            elif text[seed_search -1] == " ":
                get_paranthesis_body += text[seed_search]
                break                                
        get_paranthesis_body += text[seed_search]
        seed_search -= 1
    return ''.join(reversed(get_paranthesis_body))


def search_after(position, text):
    """
    Search for the parameter before the given position in the given text.
    """
    # Find the first open parenthesis before the given position.
    seed_search = position + 1
    par_count = 0
    activate_counter = 0        
    get_paranthesis_body = ""
    
    # we have two cases:
    # xxx.method(param1, param2, param3)
    # [xxx.length, xxx.length, ] or xxx.length + 1 or ...    
    while True:        
        if text[seed_search] == "(":
            activate_counter = 1
            par_count += 1
        elif text[seed_search] == ")":
            par_count -= 1
        get_paranthesis_body += text[seed_search]
        seed_search += 1
        if  (seed_search == len(text) or par_count == 0) & activate_counter == 1:
            break 
    return ''.join(get_paranthesis_body)
    
def search_after_attribute(position, text):
    """
    Search for the parameter before the given position in the given text.
    """
    # Find the first open parenthesis before the given position.
    seed_search = position + 1
    get_paranthesis_body = ""
    
    # we have two cases:
    # xxx.method(param1, param2, param3)
    # [xxx.length, xxx.length, ] or xxx.length + 1 or ...    
    while True:       
        if seed_search == len(text) or text[seed_search] == " ":
            break 
        get_paranthesis_body += text[seed_search]
        seed_search += 1
        
    toexport = ''.join(get_paranthesis_body)
    toexport = regex.sub(";|,|", "", toexport)
    return toexport

# -----------------------------------------------------------------------------
### Great solution obtained from zwer: 
# https://stackoverflow.com/questions/49641089/
def replace_multiple(source, replacements):  # a convenience multi-replacement function
    if not source:  # no need to process empty strings
        return ""
    for r in replacements:
        source = source.replace(r[0], r[1])
    return source

def replace_non_quoted(source, replacements):
    QUOTE_STRINGS = ("'", "\\'", '"', '\\"') 
    result = []  # a store for the result pieces
    head = 0  # a search head reference
    eos = len(source)  # a convenience string length reference
    quote = None  # last quote match literal
    quote_len = 0  # a convenience reference to the current quote substring length
    while True:
        if quote:  # we already have a matching quote stored
            index = source.find(quote, head + quote_len)  # find the closing quote
            if index == -1:  # EOS reached
                break
            result.append(source[head:index + quote_len])  # add the quoted string verbatim
            head = index + quote_len  # move the search head after the quoted match
            quote = None  # blank out the quote literal
        else:  # the current position is not in a quoted substring
            index = eos
            # find the first quoted substring from the current head position
            for entry in QUOTE_STRINGS:  # loop through all quote substrings
                candidate = source.find(entry, head)
                if head < candidate < index:
                    index = candidate
                    quote = entry
                    quote_len = len(entry)
            if not quote:  # EOS reached, no quote found
                break
            result.append(replace_multiple(source[head:index], replacements))
            head = index  # move the search head to the start of the quoted match
    if head < eos:  # if the search head is not at the end of the string
        result.append(replace_multiple(source[head:], replacements))
    return "".join(result)  # join back the result pieces and return them
# -----------------------------------------------------------------------------