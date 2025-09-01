import re
import sys

def validate_and_normalize(equation: str):
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
    term_pattern = re.compile(r"""
        ^\s*
        (?:
            [+-]?\s*\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\s*
            |
            [+-]?\s*\d*(?:\.\d+)?(?:[eE][+-]?\d+)?\s*\*?\s*
            {var}
            (?:\^\s*[-]?\d+)?
        )
        \s*$
    """.format(var=re.escape(variable)), re.VERBOSE)
    def normalize_term(term):
        term = term.strip().replace(" ", "")

        # 1. Pure constant (e.g. 5, -3.2, +2e4)
        if re.fullmatch(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", term):
            return f"{term}*{variable}^0"

        # 2. Pure variable (x, -x, +x)
        if re.fullmatch(r"[+-]?{v}".format(v=re.escape(variable)), term):
            sign = "-" if term.startswith("-") else ""
            return f"{sign}1*{variable}^1"

        # 3. Variable with exponent but no coefficient (x^2, -x^3)
        if re.fullmatch(r"[+-]?{v}\^-?\d+".format(v=re.escape(variable)), term):
            sign = "-" if term.startswith("-") else ""
            power = term.split("^")[1]
            return f"{sign}1*{variable}^{power}"

        # 4. Coefficient * variable (e.g. 3*x, -2.5*x, +4e2*x)
        if re.fullmatch(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\*{v}".format(v=re.escape(variable)), term):
            coeff = term.replace(f"*{variable}", "")
            return f"{coeff}*{variable}^1"

        # 5. Coefficient * variable^power (e.g. 2*x^3, -0.5*x^-2)
        if re.fullmatch(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\*{v}\^-?\d+".format(v=re.escape(variable)), term):
            return term

        # 6. Fallback: insert missing pieces
        if f"*{variable}" not in term:
            term = term.replace(variable, f"*{variable}")
        if "^" not in term:
            term += "^1"
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

    normalized_eq = f"{norm_left} = {norm_right}"
    return True, "Equation is valid", normalized_eq, variable


def gcd(a, b):
    """Calculate greatest common divisor"""
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a


class SimpleFraction:
    """Simple fraction class for exact arithmetic"""
    def __init__(self, numerator, denominator=1):
        if denominator == 0:
            raise ValueError("Denominator cannot be zero")
        if isinstance(numerator, float):
            num_str = str(numerator)
            if 'e' in num_str.lower():
                numerator = float(numerator)
                decimal_places = 10
                multiplier = 10 ** decimal_places
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
        g = gcd(numerator, denominator)
        self.numerator = numerator // g
        self.denominator = denominator // g
        if self.denominator < 0:
            self.numerator *= -1
            self.denominator *= -1
    
    def __add__(self, other):
        if isinstance(other, (int, float)):
            other = SimpleFraction(other)
        num = self.numerator * other.denominator + other.numerator * self.denominator
        den = self.denominator * other.denominator
        return SimpleFraction(num, den)
    
    def __sub__(self, other):
        if isinstance(other, (int, float)):
            other = SimpleFraction(other)
        num = self.numerator * other.denominator - other.numerator * self.denominator
        den = self.denominator * other.denominator
        return SimpleFraction(num, den)
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            other = SimpleFraction(other)
        return SimpleFraction(self.numerator * other.numerator, self.denominator * other.denominator)
    
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            other = SimpleFraction(other)
        return SimpleFraction(self.numerator * other.denominator, self.denominator * other.numerator)
    
    def __neg__(self):
        return SimpleFraction(-self.numerator, self.denominator)


def display_solution_enhanced(numerator, denominator, show_steps=True):
    """Enhanced solution display with detailed steps and smart fraction logic"""
    
    if show_steps:
        print(f"\nSimplifying the solution:")
        print(f"  Original fraction: {numerator}/{denominator}")
    
    if denominator == 0:
        if numerator == 0:
            print("Infinite solutions")
        else:
            print("No solution")
        return
    g = gcd(numerator, denominator)
    if show_steps and g > 1:
        print(f"  GCD({abs(numerator)}, {abs(denominator)}) = {g}")
    
    orig_num, orig_den = numerator, denominator
    numerator //= g
    denominator //= g
    
    if show_steps and g > 1:
        print(f"  Simplified: {numerator}/{denominator}")
    if denominator < 0:
        numerator *= -1
        denominator *= -1
        if show_steps:
            print(f"  Moving negative to numerator: {numerator}/{denominator}")
    solution_decimal = numerator / denominator
    is_integer = denominator == 1
    is_simple_fraction = (denominator <= 20 and abs(numerator) <= 100)
    is_very_long_decimal = len(f"{solution_decimal:.10f}".rstrip('0')) > 8
    if is_integer:
        print(f"The solution is: {numerator}")
    elif is_simple_fraction or is_very_long_decimal:
        print(f"The solution is: {numerator}/{denominator} (irreducible fraction)")
        if abs(solution_decimal) > 0.0001:
            print(f"Decimal form: {solution_decimal:.6g}")
    else:
        print(f"The solution is: {solution_decimal:.6g}")
        if denominator <= 1000:
            print(f"Exact fraction: {numerator}/{denominator}")


def is_perfect_square(n):
    """Check if a number is a perfect square"""
    if n < 0:
        return False
    if isinstance(n, float):
        sqrt_n = n ** 0.5
        int_sqrt = int(round(sqrt_n))
        return abs(int_sqrt * int_sqrt - n) < 1e-10
    sqrt_n = int(n ** 0.5)
    return sqrt_n * sqrt_n == n


def parse_and_solve_real(normalized_eq: str, variable: str):
    print(f"Normalized equation: {normalized_eq}")
    
    left, right = normalized_eq.split("=")
    term_pattern = re.compile(r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\*{var}\^([-]?\d+)".format(var=re.escape(variable)))
    
    def extract_terms(side):
        terms = {}
        print(f"\nExtracting terms from: {side}")
        for match in term_pattern.finditer(side.replace(" ", "")):
            coeff, power = float(match.group(1)), int(match.group(2))
            terms[power] = terms.get(power, 0) + coeff
            print(f"  Found term: {coeff} * {variable}^{power}")
        return terms
    
    left_terms = extract_terms(left)
    right_terms = extract_terms(right)
    print(f"\nMoving all terms to left side (Left - Right = 0):")
    coeffs = {}
    for p in set(left_terms) | set(right_terms):
        left_coeff = left_terms.get(p, 0)
        right_coeff = right_terms.get(p, 0)
        coeffs[p] = left_coeff - right_coeff
        if left_coeff != 0 or right_coeff != 0:
            print(f"  {variable}^{p}: {left_coeff} - ({right_coeff}) = {coeffs[p]}")
    coeffs = {p: c for p, c in coeffs.items() if c != 0}
    parts = []
    sorted_powers = sorted(coeffs.keys(), reverse=True)
    if not sorted_powers:
        reduced_form = "0"
    else:
        for i, power in enumerate(sorted_powers):
            coeff = coeffs[power]
            coeff_rep = int(coeff) if coeff == int(coeff) else coeff
            abs_coeff = abs(coeff_rep)
            if i == 0:
                sign = "-" if coeff < 0 else ""
            else:
                sign = " - " if coeff < 0 else " + "
            if power == 0:
                term = str(abs_coeff)
            else:
                var_part = variable
                if power != 1:
                    var_part += f"^{power}"
                
                if abs_coeff == 1:
                    term = var_part
                else:
                    term = f"{abs_coeff} * {var_part}"
            parts.append(f"{sign}{term}")
        reduced_form = "".join(parts)
    
    print(f"\nReduced form: {reduced_form} = 0")
    degree = max(coeffs.keys()) if coeffs else 0
    print(f"Polynomial degree: {degree}")
    
    if any(p < 0 for p in coeffs.keys()):
        print("Error: The equation involves negative powers, which is not a polynomial.")
        return
    
    if degree > 2:
        print("The polynomial degree is strictly greater than 2, I can't solve.")
        return

    if degree == 0:
        if not coeffs:
            print("\nAll real numbers are solutions (infinite solutions).")
        else:
            print("\nThe equation is false, there is no solution.")
        return

    if degree == 1:
        print("\nThis is a linear equation.")
        a = coeffs.get(1, 0)
        b = coeffs.get(0, 0)
        print(f"Standard form: {a} * {variable} + {b} = 0")
        print(f"\nStep-by-step solution:")
        print(f"  {a} * {variable} + {b} = 0")
        print(f"  {a} * {variable} = -{b}")
        print(f"  {variable} = -{b}/{a}")
        b_frac = SimpleFraction(b)
        a_frac = SimpleFraction(a)
        solution = -b_frac / a_frac
        
        display_solution_enhanced(solution.numerator, solution.denominator)

    if degree == 2:
        a = coeffs.get(2, 0)
        b = coeffs.get(1, 0)
        c = coeffs.get(0, 0)
        print("\nThis is a quadratic equation.")
        print(f"Standard form: {a} * {variable}^2 + {b} * {variable} + {c} = 0")
        print(f"Coefficients: a = {a}, b = {b}, c = {c}")
        
        print(f"\nUsing the quadratic formula:")
        print(f"  {variable} = (-b ± √(b² - 4ac)) / (2a)")
        print(f"  {variable} = (-({b}) ± √(({b})² - 4*({a})*({c}))) / (2*{a})")
        
        print(f"\nStep 1: Calculate the discriminant (Δ = b² - 4ac)")
        print(f"  Δ = ({b})² - 4*({a})*({c})")
        print(f"  Δ = {b**2} - {4*a*c}")
        disc = b**2 - 4*a*c
        print(f"  Δ = {disc}")

        if disc < 0:
            print("\nStep 2: Analyze the discriminant")
            print("Result: Discriminant is strictly negative.")
            print("There are no real solutions (solutions are complex).")
        elif disc == 0:
            print("\nStep 2: Analyze the discriminant")
            print("Result: Discriminant is zero, there is one real solution (repeated root).")
            print(f"\nStep 3: Apply the formula")
            print(f"  {variable} = -b / (2*a)")
            print(f"  {variable} = -({b}) / (2*{a})")
            print(f"  {variable} = {-b} / {2*a}")
            b_frac = SimpleFraction(b)
            a_frac = SimpleFraction(a)
            solution = -b_frac / (SimpleFraction(2) * a_frac)
            
            display_solution_enhanced(solution.numerator, solution.denominator)
        else:
            print("\nStep 2: Analyze the discriminant")
            print("Result: Discriminant is strictly positive, there are two real solutions.")
            
            sqrt_disc = disc ** 0.5
            is_perfect_square_disc = is_perfect_square(disc)
            
            print(f"\nStep 3: Calculate √Δ")
            if is_perfect_square_disc:
                sqrt_disc_int = int(sqrt_disc)
                print(f"  √{disc} = {sqrt_disc_int} (perfect square)")
                print("The solutions will be rational numbers.")
                
                print(f"\nStep 4: Apply the quadratic formula")
                b_frac = SimpleFraction(b)
                a_frac = SimpleFraction(a)
                
                print(f"\nSolution 1: {variable} = (-b - √Δ) / (2a)")
                print(f"  = (-({b}) - {sqrt_disc_int}) / (2*{a})")
                print(f"  = ({-b} - {sqrt_disc_int}) / {2*a}")
                print(f"  = {-b - sqrt_disc_int} / {2*a}")
                
                sol1 = (-b_frac - SimpleFraction(sqrt_disc_int)) / (SimpleFraction(2) * a_frac)
                display_solution_enhanced(sol1.numerator, sol1.denominator, show_steps=False)
                
                print(f"\nSolution 2: {variable} = (-b + √Δ) / (2a)")
                print(f"  = (-({b}) + {sqrt_disc_int}) / (2*{a})")
                print(f"  = ({-b} + {sqrt_disc_int}) / {2*a}")
                print(f"  = {-b + sqrt_disc_int} / {2*a}")
                
                sol2 = (-b_frac + SimpleFraction(sqrt_disc_int)) / (SimpleFraction(2) * a_frac)
                display_solution_enhanced(sol2.numerator, sol2.denominator, show_steps=False)
            else:
                print(f"  √{disc} ≈ {sqrt_disc:.6g} (not a perfect square)")
                print("The solutions will be irrational numbers.")
                
                print(f"\nStep 4: Apply the quadratic formula")
                print(f"Solution 1: {variable} = (-{b} - √{disc}) / {2*a}")
                sol1 = (-b - sqrt_disc) / (2*a)
                print(f"  ≈ {sol1:.8g}")
                
                print(f"\nSolution 2: {variable} = (-{b} + √{disc}) / {2*a}")
                sol2 = (-b + sqrt_disc) / (2*a)
                print(f"  ≈ {sol2:.8g}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python computor.py \"<equation>\"")
        sys.exit(1)
    
    eq = sys.argv[1]
    print("="*60)
    print("POLYNOMIAL EQUATION SOLVER")
    print("="*60)
    
    valid, msg, norm, variable = validate_and_normalize(eq)
    
    if not valid:
        print(f"Error parsing equation: {msg}")
        sys.exit(1)
    
    print(f"Input equation: \"{eq}\"")
    print(f"Variable detected: {variable}")
    print("-" * 60)
    parse_and_solve_real(norm, variable)
    print("=" * 60)


if __name__ == "__main__":
    main()