# ==============================================================================
# SECTION 3: CORE LOGIC - PARSING AND SOLVING (Newly Structured Functions)
# ==============================================================================

def get_reduced_coefficients(normalized_eq: str, variable: str) -> dict:
    """
    Parses terms from the normalized equation, shows the process, and
    returns a dictionary of the reduced form's coefficients.
    """
    left, right = normalized_eq.split("=")
    term_pattern = re.compile(r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\*{var}\^([-]?\d+)".format(var=re.escape(variable)))
    
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