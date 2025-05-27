import re
from collections import defaultdict

def preprocess(expr):
    expr = expr.replace("−", "-").replace("–", "-")
    expr = expr.replace("x", "X")
    expr = re.sub(r'(?<!\*)\bX\^(\d+)', r'1 * X^\1', expr)
    expr = re.sub(r'(?<!\*)\bX\b', r'1 * X^1', expr)
    expr = re.sub(r'\b(?<!X\^)(\d+)(?!\s*\*)', r'\1 * X^0', expr)
    return expr

def parse_side(expr):
    terms = defaultdict(float)
    pattern = r'([+-]?\s*\d*\.?\d*)\s*\*\s*X\^(\d+)'
    for match in re.finditer(pattern, expr):
        coeff = match.group(1).replace(' ', '')
        coeff = float(coeff) if coeff not in ('', '+', '-') else float(f'{coeff}1')
        power = int(match.group(2))
        terms[power] += coeff
    return terms

def parse_equation(expr):
    if "=" not in expr:
        raise ValueError("Equation must contain '='.")
    lhs, rhs = map(preprocess, expr.split("="))
    left_terms = parse_side(lhs)
    right_terms = parse_side(rhs)
    result = defaultdict(float)

    for power in set(left_terms.keys()).union(right_terms.keys()):
        result[power] = left_terms[power] - right_terms[power]
    
    # Print reduced form
    reduced = " + ".join(f"{v:+.2f} * X^{k}" for k, v in sorted(result.items()) if v != 0)
    print(f"Reduced form: {reduced if reduced else '0 * X^0'} = 0")

    return result
