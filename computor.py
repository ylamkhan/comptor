import re
import sys

# ==============================================================================
# SECTION 1: UTILITY AND HELPER FUNCTIONS (Largely Unchanged)
# ==============================================================================

def gcd(a, b):
    """Calculate the greatest common divisor of two integers."""
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a

class SimpleFraction:
    """A simple class to handle fraction arithmetic for exact calculations."""
    def __init__(self, numerator, denominator=1):
        if denominator == 0:
            raise ValueError("Denominator cannot be zero")
        if isinstance(numerator, float):
            num_str = str(numerator)
            if 'e' in num_str.lower():
                numerator = float(numerator)
                multiplier = 10 ** 10
                numerator = int(numerator * multiplier)
                denominator *= multiplier
            elif '.' in num_str:
                decimal_places = len(num_str.split('.')[1])
                multiplier = 10 ** decimal_places
                numerator = int(numerator * multiplier)
                denominator *= multiplier
            else:
                numerator = int(numerator)
        
        if isinstance(denominator, float):
            den_str = str(denominator)
            if '.' in den_str:
                decimal_places = len(den_str.split('.')[1])
                multiplier = 10 ** decimal_places
                numerator *= multiplier
                denominator = int(denominator * multiplier)
            else:
                denominator = int(denominator)
        
        common_divisor = gcd(numerator, denominator)
        self.numerator = numerator // common_divisor
        self.denominator = denominator // common_divisor
        
        if self.denominator < 0:
            self.numerator *= -1
            self.denominator *= -1
    
    def __add__(self, other):
        if isinstance(other, (int, float)): other = SimpleFraction(other)
        num = self.numerator * other.denominator + other.numerator * self.denominator
        den = self.denominator * other.denominator
        return SimpleFraction(num, den)
    
    def __sub__(self, other):
        if isinstance(other, (int, float)): other = SimpleFraction(other)
        num = self.numerator * other.denominator - other.numerator * self.denominator
        den = self.denominator * other.denominator
        return SimpleFraction(num, den)
    
    def __mul__(self, other):
        if isinstance(other, (int, float)): other = SimpleFraction(other)
        return SimpleFraction(self.numerator * other.numerator, self.denominator * other.denominator)
    
    def __truediv__(self, other):
        if isinstance(other, (int, float)): other = SimpleFraction(other)
        return SimpleFraction(self.numerator * other.denominator, self.denominator * other.numerator)
    
    def __neg__(self):
        return SimpleFraction(-self.numerator, self.denominator)

def is_perfect_square(n):
    """Checks if a number is a perfect square."""
    if n < 0: return False
    if isinstance(n, float):
        sqrt_n = n ** 0.5
        int_sqrt = int(round(sqrt_n))
        return abs(int_sqrt * int_sqrt - n) < 1e-10
    sqrt_n = int(n ** 0.5)
    return sqrt_n * sqrt_n == n

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
    
    term_pattern = re.compile(r"^\s*([+-]?\s*\d*(?:\.\d+)?(?:[eE][+-]?\d+)?\s*\*?\s*{var}(?:\^\s*\d+)?|[+-]?\s*\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*$".format(var=re.escape(variable)), re.VERBOSE)
    def normalize_term(term):
        if re.fullmatch(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", term):
            return f"{term}*{variable}^0"
        if re.fullmatch(r"[+-]?{v}".format(v=re.escape(variable)), term):
            sign = "-" if term.startswith("-") else ""
            return f"{sign}1*{variable}^1"
        if re.fullmatch(r"[+-]?\d*(?:\.\d+)?(?:[eE][+-]?\d+)?\*{v}".format(v=re.escape(variable)), term):
            coeff = term.replace(f"*{variable}", "")
            if coeff in ("", "+"): return f"1*{variable}^1"
            if coeff == "-": return f"-1*{variable}^1"
            return f"{coeff}*{variable}^1"
        if f'*{variable}' not in term:
             term = term.replace(variable, f'*{variable}')
        if '^' not in term:
            term += '^1'
        return term

    def check_and_normalize_side(side):
        side = side.replace("-", "+-").replace(" ", "").replace("\t","")
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

# ==============================================================================
# SECTION 3: CORE LOGIC - PARSING AND SOLVING (Newly Structured Functions)
# ==============================================================================

def get_reduced_coefficients(normalized_eq: str, variable: str) -> dict:
    """
    Parses terms from the normalized equation, shows the process, and
    returns a dictionary of the reduced form's coefficients.
    """
    left, right = normalized_eq.split("=")
    term_pattern = re.compile(r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\*{var}\^(\d+)".format(var=re.escape(variable)))
    
    def extract_terms(side, side_name):
        terms = {}
        print(f"\nExtracting terms from {side_name} side: {side}")
        for match in term_pattern.finditer(side.replace(" ", "")):
            coeff, power = float(match.group(1)), int(match.group(2))
            terms[power] = terms.get(power, 0) + coeff
            print(f"  Found term: {coeff} * {variable}^{power}")
        return terms
    
    left_terms = extract_terms(left, "Left")
    right_terms = extract_terms(right, "Right")
    
    print("\nMoving all terms to the left side (Left - Right = 0):")
    coeffs = {}
    all_powers = sorted(list(set(left_terms) | set(right_terms)), reverse=True)
    for p in all_powers:
        left_coeff = left_terms.get(p, 0)
        right_coeff = right_terms.get(p, 0)
        final_coeff = left_coeff - right_coeff
        if final_coeff != 0:
            coeffs[p] = final_coeff
            print(f"  For power {p} ({variable}^{p}): {left_coeff} - ({right_coeff}) = {final_coeff}")
            
    return coeffs

def display_reduced_form_and_degree(coeffs: dict, variable: str) -> int:
    """
    Displays the reduced form equation and its degree.
    Returns the polynomial degree.
    """
    parts = []
    sorted_powers = sorted(coeffs.keys(), reverse=True)
    if not sorted_powers:
        reduced_form = "0"
    else:
        for i, power in enumerate(sorted_powers):
            coeff = coeffs[power]
            coeff_rep = int(coeff) if coeff == int(coeff) else coeff
            abs_coeff = abs(coeff_rep)
            
            sign = " - " if coeff < 0 else " + "
            if i == 0:
                sign = "-" if coeff < 0 else ""
            
            if power == 0:
                term = str(abs_coeff)
            else:
                var_part = variable + (f"^{power}" if power != 1 else "")
                term = var_part if abs_coeff == 1 else f"{abs_coeff} * {var_part}"
            parts.append(sign + term)
        reduced_form = "".join(parts)
    
    degree = max(coeffs.keys()) if coeffs else 0
    print(f"\nReduced form: {reduced_form} = 0")
    print(f"Polynomial degree: {degree}")
    return degree

def solve_linear(coeffs: dict, variable: str):
    """Solves a degree 1 (linear) equation and displays the steps."""
    a = coeffs.get(1, 0)
    b = coeffs.get(0, 0)
    print("\nThis is a linear equation.")
    print(f"Standard form: {a}*{variable} + {b} = 0")
    
    print("\nSolving step-by-step:")
    print(f"  {a}*{variable} = {-b}")
    print(f"  {variable} = {-b}/{a}")
    
    solution = -SimpleFraction(b) / SimpleFraction(a)
    display_solution_enhanced(solution.numerator, solution.denominator)

def solve_quadratic(coeffs: dict, variable: str):
    """Solves a degree 2 (quadratic) equation for real and complex solutions."""
    a = coeffs.get(2, 0)
    b = coeffs.get(1, 0)
    c = coeffs.get(0, 0)
    print("\nThis is a quadratic equation.")
    print(f"Standard form: {a}*{variable}^2 + {b}*{variable} + {c} = 0")
    
    print("\nStep 1: Calculate the discriminant (Δ = b² - 4ac)")
    disc = b**2 - 4*a*c
    print(f"  Δ = ({b})² - 4*({a})*({c}) = {disc}")

    if disc < 0:
        print("\nResult: Discriminant is negative. There are two complex conjugate solutions.")
        
        real_part = -SimpleFraction(b) / (SimpleFraction(2) * SimpleFraction(a))
        imag_part_val = (-disc) ** 0.5
        imag_part = SimpleFraction(imag_part_val) / (SimpleFraction(2) * SimpleFraction(a))

        print(f"  Formula: {variable} = (-b ± i√(-Δ)) / 2a")
        rp_num, rp_den = real_part.numerator, real_part.denominator
        ip_num, ip_den = imag_part.numerator, imag_part.denominator

        real_str = f"{rp_num}" if rp_den == 1 else f"{rp_num}/{rp_den}"
        imag_str = ""
        sqrt_neg_disc_int = int(round((-disc)**0.5))
        if is_perfect_square(-disc):
             imag_part_simplified = SimpleFraction(sqrt_neg_disc_int) / (SimpleFraction(2) * SimpleFraction(a))
             ip_num, ip_den = imag_part_simplified.numerator, imag_part_simplified.denominator
             if ip_den == 1:
                 imag_str = f"{ip_num}" if ip_num != 1 else ""
             else:
                 imag_str = f"{ip_num}/{ip_den}"
        else:
             imag_str = f"√{abs(disc)}/{2*a}"

        print("\nThe two complex solutions are:")
        print(f"  Solution 1: {real_str} - {imag_str}i")
        print(f"  Solution 2: {real_str} + {imag_str}i")

    elif disc == 0:
        print("\nResult: Discriminant is zero. There is one real solution.")
        print(f"  Formula: {variable} = -b / (2a) = {-b}/{2*a}")
        solution = -SimpleFraction(b) / (SimpleFraction(2) * SimpleFraction(a))
        display_solution_enhanced(solution.numerator, solution.denominator)
    else:
        print("\nResult: Discriminant is positive. There are two real solutions.")
        if is_perfect_square(disc):
            sqrt_disc = int(disc ** 0.5)
            print(f"  √Δ = √{disc} = {sqrt_disc} (a perfect square, solutions are rational)")
            
            print("\nCalculating solutions:")
            sol1 = (-SimpleFraction(b) - sqrt_disc) / (SimpleFraction(2) * SimpleFraction(a))
            print(f"Solution 1 ({variable}₁ = (-b - √Δ)/2a):")
            display_solution_enhanced(sol1.numerator, sol1.denominator, show_steps=False)

            sol2 = (-SimpleFraction(b) + sqrt_disc) / (SimpleFraction(2) * SimpleFraction(a))
            print(f"\nSolution 2 ({variable}₂ = (-b + √Δ)/2a):")
            display_solution_enhanced(sol2.numerator, sol2.denominator, show_steps=False)
        else:
            sqrt_disc = disc ** 0.5
            print(f"  √Δ = √{disc} ≈ {sqrt_disc:.6g} (not a perfect square, solutions are irrational)")
            
            sol1 = (-b - sqrt_disc) / (2*a)
            sol2 = (-b + sqrt_disc) / (2*a)
            print(f"\nSolutions (approximate decimal form):")
            print(f"  {variable}₁ ≈ {sol1:.8g}")
            print(f"  {variable}₂ ≈ {sol2:.8g}")

# ==============================================================================
# SECTION 4: DISPLAY AND MAIN EXECUTION
# ==============================================================================

def display_solution_enhanced(numerator, denominator, show_steps=True):
    """
    Displays the final solution with smart formatting for fractions.
    """
    if show_steps:
        print(f"\nFinal simplification:")
        print(f"  Original fraction: {numerator}/{denominator}")
    
    g = gcd(numerator, denominator)
    num, den = numerator // g, denominator // g
    
    if den < 0:
        num, den = -num, -den

    if den == 1:
        print(f"The solution is: {num}")
    else:
        print(f"The solution is: {num}/{den} (irreducible fraction)")
        print(f"Decimal form: {num/den:.6g}")



def main():
    """Main entry point for the script."""
    if len(sys.argv) != 2:
        print("Usage: python computor.py \"<equation>\"")
        sys.exit(1)
    
    print("="*60 + "\nPOLYNOMIAL EQUATION SOLVER\n" + "="*60)
    
    eq_input = sys.argv[1]
    
    is_valid, msg, norm_eq, variable = validate_and_normalize(eq_input)
    
    if not is_valid:
        print(f"Error parsing equation: {msg}")
        sys.exit(1)
    
    print(f"Input equation: \"{eq_input}\"")
    print("-" * 60)
    coefficients = get_reduced_coefficients(norm_eq, variable)
    degree = display_reduced_form_and_degree(coefficients, variable)

    if any(p < 0 for p in coefficients.keys()):
        print("\nError: The equation involves negative powers, which is not a polynomial.")
    elif degree > 2:
        print("\nThe polynomial degree is strictly greater than 2, I can't solve.")
    elif degree == 0:
        print("\n" + ("All real numbers are solutions." if not coefficients else "The equation is false, there is no solution."))
    elif degree == 1:
        solve_linear(coefficients, variable)
    elif degree == 2:
        solve_quadratic(coefficients, variable)
        
    print("=" * 60)

if __name__ == "__main__":
    main()