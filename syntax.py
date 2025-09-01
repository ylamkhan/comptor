# ==============================================================================
# SECTION 2: INPUT VALIDATION AND NORMALIZATION (Unchanged)
# ==============================================================================

def validate_and_normalize(equation: str):
    """
    Validates the input equation and normalizes all terms to the form 'c*v^p'.
    """
    if equation.count("=") != 1:
        return False, "Equation must contain exactly one '=' sign", None, None
    left, right = equation.split("=")
    variables = re.findall(r"[a-zA-Z]", equation)
    unique_vars = set(variables)
    if not unique_vars:
        return False, "Equation must contain at least one variable", None, None
    if len(unique_vars) > 1:
        return False, f"Equation must contain only ONE variable, found {unique_vars}", None, None
    variable = unique_vars.pop()
    
    
    term_pattern = re.compile(r"^\s*([+-]?\s*\d*(?:\.\d+)?(?:[eE][+-]?\d+)?\s*\*?\s*{var}(?:\^\s*[-]?\d+)? | [+-]?\s*\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*$".format(var=re.escape(variable)), re.VERBOSE)
    
    def normalize_term(term):
        term = term.strip().replace(" ", "")
        if re.fullmatch(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", term):
            return f"{term}*{variable}^0"
        if re.fullmatch(r"[+-]?{v}".format(v=re.escape(variable)), term):
            return f"{term.replace(variable, '1*')} {variable}^1"
        if f'*{variable}' not in term:
             term = term.replace(variable, f'*{variable}')
        if '^' not in term:
            term += '^1'
        return term

    def check_and_normalize_side(side):
        side = side.replace("-", "+-").replace(" ", "")
        tokens = [token for token in side.split('+') if token]
        normalized = []
        for token in tokens:
            if not term_pattern.match(token):
                return False, f"Invalid term: '{token}'", None
            normalized.append(normalize_term(token))
        return True, None, " + ".join(normalized)

    ok_left, err_left, norm_left = check_and_normalize_side(left)
    ok_right, err_right, norm_right = check_and_normalize_side(right)

    if not ok_left: return False, err_left, None, None
    if not ok_right: return False, err_right, None, None

    return True, "Equation is valid", f"{norm_left} = {norm_right}", variable