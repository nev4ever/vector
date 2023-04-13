import re

PLUS = "+"
MINUS = "-"
MULTIPLY = "*"
DIVIDE = "/"
VECTOR_MULTIPLY = "x"

NUMBER = "number"
VECTOR = "vector"
SCALAR = "scalar"

OPERATORS = [
    PLUS,
    MINUS,
    MULTIPLY,
    DIVIDE,
    VECTOR_MULTIPLY,
]

def scalar_multiply(t1, t2):
    s = t1 if is_number(t1) else t2
    v = t1 if is_vector(t1) else t2
    return [s * i for i in v]

def scalar_vector_multiply(v1, v2): 
    s = 0
    for i in range(len(v1)):
        s += v1[i] * v2[i]
    return s

def scalar_divide(v, s):
    if not is_vector(v):
        raise ValueError("division: left operand must be a vector", v)
    if not is_number(s):
        raise ValueError("division: right operand must be a number", s)
    return [i / s for i in v]

# scalar vector addition, not a real operation
def scalar_add(v, s):
    return [i + s for i in v]

#scalar vector subtraction, not a real operation
def scalar_subtract(v, s):
    return [i - s for i in v]

def vector_add(v1, v2):
    return [v1[i] + v2[i] for i in range(len(v1))]

def vector_subtract(v1, v2):
    return [v1[i] - v2[i] for i in range(len(v1))]

#  vector product, only in 3D
def vector_multiply(a, b):
    if len(a) != len(b):
        raise ValueError("multiply: vectors must have the same length")
    if len(a) != 3:
        raise ValueError("multiply: vector cross product is only defined in 3D")
    return [
        a[1] * b[2] - a[2] * b[1], 
        a[2] * b[0] - a[0] * b[2], 
        a[0] * b[1] - a[1] * b[0]
    ]

# not defined
def vector_divide(v1, v2):
    return [v1[i] / v2[i] for i in range(len(v1))]

def plus(a, b):
    return a + b

def minus(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b

OPERATOR_MAP = {
    PLUS: {
        "vector": vector_add,
        #"scalar": scalar_add,
        "number": plus,
        "priority": 2    
    },
    MINUS: {
        "vector": vector_subtract,
        #"scalar": scalar_subtract,
        "number": minus,
        "priority": 2
         
    },
    MULTIPLY: {
        "vector": scalar_vector_multiply,
        "scalar": scalar_multiply,
        "number": multiply,
        "priority": 1 
    },
    DIVIDE: {
        #"vector": vector_divide,
        "scalar": scalar_divide,
        "number": divide,
        "priority": 1 
    },
    VECTOR_MULTIPLY: {
        "vector": vector_multiply, # Kreuzprodukt
        #"scalar": vector_multiply,
        #"number": vector_multiply,  
        "priority": 0 
    },
}

def get_operation(token1, token2):
    if is_number(token1) and is_number(token2):
        return NUMBER
    if is_vector(token1) and is_vector(token2):
        return VECTOR
    if is_number(token1) and is_vector(token2) or is_vector(token1) and is_number(token2):
        return SCALAR
    raise ValueError("Invalid operation", token1, token2)


def calculate(token1, token2, op):
    try:
        return OPERATOR_MAP[op][get_operation(token1, token2)](token1, token2)
    except KeyError:
        raise ValueError("calculate: Invalid operation", token1, op, token2)

def contains_operator(v):
    for op in OPERATORS:
        if op in v:
            return True
    return False

def get_number(n):
    try:
        return int(n)
    except ValueError:
        try:
            return float(n)
        except ValueError:
            raise ValueError("get_number: Invalid value: {}".format(n))

def check_brackets(tokens):
    open_brackets = 0
    for t in tokens:
        if t == "(":
            open_brackets += 1
        if t == ")":
            open_brackets -= 1
    if open_brackets != 0:
        raise ValueError("Invalid brackets: open brackets", open_brackets)

def get_index_of_first_close_bracket(tokens, start_index=0):
    index = start_index
    for t in tokens[start_index::]:
        if t == ")" or t == "]":
            return index
        index += 1
    return None

#a= (1+3*(2+(3+4))+((2+3)*4))-1
def get_index_of_last_open_bracket(tokens, start_index):
    index = start_index
    for t in tokens[start_index::-1]:
        if t == "(" or t == "[":
            return index
        index -= 1
    return None

def get_index_of_lowest_priority_operator(tokens, start_index=0, end_index=None):
    if not end_index:
        end_index = len(tokens)

    lowest_priority_index = None
    for t in tokens[start_index:end_index]:
        if is_operator(t):
            if not lowest_priority_index or OPERATOR_MAP[t]["priority"] < OPERATOR_MAP[tokens[lowest_priority_index]]["priority"]:
                lowest_priority_index = tokens.index(t)
    return lowest_priority_index

def solve(tokens):
    #find first bracket to solve
    first_close_bracket_index = get_index_of_first_close_bracket(tokens)
    if first_close_bracket_index:
        #find last open bracket to solve
        last_open_bracket_index = get_index_of_last_open_bracket(tokens, first_close_bracket_index)
        #solve bracket
        bracket_result = solve(tokens[last_open_bracket_index + 1:first_close_bracket_index])
        tokens[last_open_bracket_index] = bracket_result
        del tokens[last_open_bracket_index + 1:first_close_bracket_index + 1]
        print(tokens)
        return solve(tokens)

    #find lowest priority operator
    lowest_priority_index = get_index_of_lowest_priority_operator(tokens)

    #solve
    if lowest_priority_index:
        op = tokens[lowest_priority_index]
        token1 = tokens[lowest_priority_index - 1]
        token2 = tokens[lowest_priority_index + 1]
        result = calculate(token1, token2, op)
        tokens[lowest_priority_index - 1] = result
        del tokens[lowest_priority_index:lowest_priority_index + 2]
        print(token1, op, token2, "=", result)
        return solve(tokens)

    return tokens[0]   

def check_if_token_strings_contains_vectors(token_strings, start_index=0, end_index=None):
    if not end_index:
        end_index = len(token_strings)
    contains_numbers = 0
    for i in range(start_index, end_index):
        if is_number(token_strings[i]):
            contains_numbers += 1
            continue
        if token_strings[i] in OPERATORS:
            return False
    return contains_numbers > 1

def fuse_tokens(token_strings, start_index, end_index):
    fused_token = ""
    for i in range(start_index, end_index):
        fused_token += token_strings[i]
    token_strings[start_index] = fused_token
    del token_strings[start_index + 1:end_index]
    return start_index

def find_vectors(token_strings, index=0):
    closing_bracket_index = get_index_of_first_close_bracket(token_strings, index)
    if closing_bracket_index:
        index = closing_bracket_index + 1
        opening_bracket_index = get_index_of_last_open_bracket(token_strings, closing_bracket_index)
        if check_if_token_strings_contains_vectors(token_strings, opening_bracket_index, closing_bracket_index + 1):
            index = fuse_tokens(token_strings, opening_bracket_index, closing_bracket_index + 1) + 1
        if index < len(token_strings):
            return find_vectors(token_strings, index)

def remove_whitespace(token_strings):
    for t in token_strings:
        if t == "" or t == " " or t == "\t" or t == "\n":
            token_strings.remove(t)
    return token_strings

def get_user_input():
    print("Welcome to the vector calculator!")
    print("Allowed operators: +, -, *, /, x")
    print("+ = add, - = subtract, * = multiply, / = divide, x = cross product")
    print("Allowed brackets: (, ), [, ]")
    print("Allowed vector notation: (1,2,3), [1,2,3], (1 2 3), [1 2 3]")
    print("Example: ((1,2,3) + (4,5,6)) - (7,8,9)")
    print("Normal calculator operators are also allowed: +, -, *, /")
    print("Example: 1 + 2 * (3 - 4) / 5")
    print("Enter a (vector) calculation, or 'exit' to quit.")
    while True:
        try:
            user_input = input("input (vector) calculation: ")
            # check if the v contains string "exit"
            if "exit" in user_input.lower():
                break
            tokens_strings = get_tokens(user_input)
            find_vectors(tokens_strings)
            remove_whitespace(tokens_strings)
            
            tokens = []
            for t_str in tokens_strings:
                tokens.append(parse_token(t_str))
            print(tokens)

            solve(tokens)
            print("result:", tokens[0])
        except Exception as e:
            print("Error:", e)

def get_tokens(v):
    pattern = r"\d+(?:\.\d+)?|."
    return re.findall(pattern, v)

def parse_vector(v):
    return [get_number(n) for n in re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", v)]

def parse_token(t):
    if is_vector(t):
        return parse_vector(t)
    if is_number(t):
        return get_number(t)
    if is_operator(t):
        return t
    if is_bracket(t):
        return t
    raise ValueError("parse_token: Invalid token", t)

def is_bracket(v):
    BRACKETS = ["(", ")", "[", "]"]
    return v in BRACKETS

def is_number(v):
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, str):
        return re.match(r"[-+]?\d*\.\d+|[-+]?\d+", v)
    return False

#funciton that checks if a value is list of numbers
def is_list_of_numbers(v):
    if not isinstance(v, list):
        return False
    for item in v:
        if not isinstance(item, (int, float)):
            return False
    return True

def is_vector(v):
    if is_list_of_numbers(v):
        return True
    if isinstance(v, str):
        return re.match(r"\(.*?\)|\[.*?\]", v)
    return False

def is_operator(v):
    return v in OPERATORS


if __name__ == "__main__":
    get_user_input()