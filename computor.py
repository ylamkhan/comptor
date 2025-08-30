#!/usr/bin/env python3
import re
import sys

class PolynomialSolver:
    def __init__(self):
        self.coefficients = {}
    
    def parse_term(self, term):
        """Parse a single term like '5 * X^2' or '-3.5 * X^1'"""
        # Remove spaces
        term = re.sub(r'\s+', '', term)
        
        # Handle cases like "X^2" (coefficient = 1)
        if term.startswith('X^'):
            return 1.0, int(term[2:])
        elif term.startswith('-X^'):
            return -1.0, int(term[3:])
        elif term == 'X':
            return 1.0, 1
        elif term == '-X':
            return -1.0, 1
        
        # Handle explicit coefficient cases
        # Pattern: optional sign, number, *, X^, power
        pattern = r'^([+-]?\d*\.?\d*)\*X\^(\d+)$'
        match = re.match(pattern, term)
        
        if match:
            coeff_str = match.group(1)
            power = int(match.group(2))
            
            # Handle empty coefficient (means 1)
            if coeff_str == '' or coeff_str == '+':
                coefficient = 1.0
            elif coeff_str == '-':
                coefficient = -1.0
            else:
                coefficient = float(coeff_str)
            
            return coefficient, power
        
        # Handle constant terms (X^0)
        pattern_const = r'^([+-]?\d*\.?\d*)\*X\^0$'
        match_const = re.match(pattern_const, term)
        if match_const:
            coeff_str = match_const.group(1)
            if coeff_str == '' or coeff_str == '+':
                coefficient = 1.0
            elif coeff_str == '-':
                coefficient = -1.0
            else:
                coefficient = float(coeff_str)
            return coefficient, 0
        
        # Handle pure numbers as X^0
        pattern_num = r'^([+-]?\d*\.?\d*)$'
        match_num = re.match(pattern_num, term)
        if match_num and match_num.group(1):
            return float(match_num.group(1)), 0
            
        raise ValueError(f"Invalid term format: {term}")
    
    def parse_equation(self, equation_str):
        """Parse the entire equation and return coefficients dictionary"""
        # Split by '='
        if '=' not in equation_str:
            raise ValueError("No '=' found in equation")
        
        left_side, right_side = equation_str.split('=', 1)
        
        # Parse both sides
        left_coeffs = self.parse_side(left_side)
        right_coeffs = self.parse_side(right_side)
        
        # Move everything to left side (subtract right side)
        all_coeffs = {}
        
        # Add left side coefficients
        for power, coeff in left_coeffs.items():
            all_coeffs[power] = all_coeffs.get(power, 0) + coeff
        
        # Subtract right side coefficients
        for power, coeff in right_coeffs.items():
            all_coeffs[power] = all_coeffs.get(power, 0) - coeff
        
        # Remove zero coefficients
        self.coefficients = {k: v for k, v in all_coeffs.items() if abs(v) > 1e-10}
        
        return self.coefficients
    
    def parse_side(self, side_str):
        """Parse one side of the equation"""
        coeffs = {}
        
        # Add explicit + at the beginning if the first term doesn't have a sign
        side_str = side_str.strip()
        if not side_str.startswith(('+', '-')):
            side_str = '+' + side_str
        
        # Split by + and - while keeping the signs
        terms = re.split(r'(?=[+-])', side_str)
        terms = [term.strip() for term in terms if term.strip()]
        
        for term in terms:
            if not term:
                continue
            try:
                coeff, power = self.parse_term(term)
                coeffs[power] = coeffs.get(power, 0) + coeff
            except ValueError as e:
                print(f"Error parsing term '{term}': {e}")
                raise
        
        return coeffs
    
    def get_reduced_form(self):
        """Return the reduced form string"""
        if not self.coefficients:
            return "0 = 0"
        
        terms = []
        max_power = max(self.coefficients.keys()) if self.coefficients else 0
        
        # Sort powers in ascending order for display
        for power in sorted(self.coefficients.keys()):
            coeff = self.coefficients[power]
            
            if abs(coeff) < 1e-10:  # Skip near-zero coefficients
                continue
                
            # Format coefficient
            if len(terms) == 0:  # First term
                if coeff == 1.0 and power > 0:
                    coeff_str = ""
                elif coeff == -1.0 and power > 0:
                    coeff_str = "-"
                elif coeff == int(coeff):
                    coeff_str = str(int(coeff))
                else:
                    coeff_str = str(coeff)
            else:  # Subsequent terms
                if coeff > 0:
                    if coeff == 1.0 and power > 0:
                        coeff_str = " + "
                    elif coeff == int(coeff):
                        coeff_str = f" + {int(coeff)}"
                    else:
                        coeff_str = f" + {coeff}"
                else:
                    if coeff == -1.0 and power > 0:
                        coeff_str = " - "
                    elif coeff == int(coeff):
                        coeff_str = f" - {int(abs(coeff))}"
                    else:
                        coeff_str = f" - {abs(coeff)}"
            
            # Add power part
            if power == 0:
                if coeff_str in ["", " + ", " - "]:
                    coeff_str += "1"
                power_str = " * X^0"
            elif power == 1:
                if coeff_str in ["", " + "]:
                    coeff_str += "1"
                elif coeff_str == " - ":
                    coeff_str += "1"
                power_str = " * X^1"
            else:
                if coeff_str in ["", " + "]:
                    coeff_str += "1"
                elif coeff_str == " - ":
                    coeff_str += "1"
                power_str = f" * X^{power}"
            
            terms.append(coeff_str + power_str)
        
        if not terms:
            return "0 = 0"
        
        return "".join(terms) + " = 0"
    
    def get_degree(self):
        """Return the degree of the polynomial"""
        if not self.coefficients:
            return 0
        return max(self.coefficients.keys())
    
    def solve(self):
        """Solve the polynomial equation"""
        degree = self.get_degree()
        
        if degree == 0:
            # Constant equation
            const = self.coefficients.get(0, 0)
            if abs(const) < 1e-10:
                return "Any real number is a solution."
            else:
                return "No solution."
        
        elif degree == 1:
            # Linear equation: ax + b = 0 -> x = -b/a
            a = self.coefficients.get(1, 0)
            b = self.coefficients.get(0, 0)
            
            if abs(a) < 1e-10:
                return "No solution." if abs(b) > 1e-10 else "Any real number is a solution."
            
            solution = -b / a
            return f"The solution is:\n{solution:g}"
        
        elif degree == 2:
            # Quadratic equation: ax² + bx + c = 0
            a = self.coefficients.get(2, 0)
            b = self.coefficients.get(1, 0)
            c = self.coefficients.get(0, 0)
            
            if abs(a) < 1e-10:
                # Actually a linear equation
                if abs(b) < 1e-10:
                    return "No solution." if abs(c) > 1e-10 else "Any real number is a solution."
                solution = -c / b
                return f"The solution is:\n{solution:g}"
            
            # Calculate discriminant
            discriminant = b*b - 4*a*c
            
            if discriminant > 1e-10:
                # Two real solutions
                sqrt_d = (discriminant)**(1/2)
                x1 = (-b + sqrt_d) / (2*a)
                x2 = (-b - sqrt_d) / (2*a)
                return f"Discriminant is strictly positive, the two solutions are:\n{x1:g}\n{x2:g}"
            
            elif abs(discriminant) <= 1e-10:
                # One real solution (repeated root)
                x = -b / (2*a)
                return f"Discriminant is zero, the solution is:\n{x:g}"
            
            else:
                # Complex solutions
                sqrt_d = (abs(discriminant))**0.5
                real_part = -b / (2*a)
                imag_part = sqrt_d / (2*a)
                
                if abs(real_part) < 1e-10:
                    real_part = 0
                if abs(imag_part) < 1e-10:
                    imag_part = 0
                
                # Format complex numbers nicely
                if real_part == 0:
                    if imag_part == 1:
                        return f"Discriminant is strictly negative, the two complex solutions are:\ni\n-i"
                    elif imag_part == -1:
                        return f"Discriminant is strictly negative, the two complex solutions are:\n-i\ni"
                    else:
                        return f"Discriminant is strictly negative, the two complex solutions are:\n{imag_part:g}i\n{-imag_part:g}i"
                else:
                    if imag_part == 1:
                        return f"Discriminant is strictly negative, the two complex solutions are:\n{real_part:g} + i\n{real_part:g} - i"
                    elif imag_part == -1:
                        return f"Discriminant is strictly negative, the two complex solutions are:\n{real_part:g} - i\n{real_part:g} + i"
                    else:
                        return f"Discriminant is strictly negative, the two complex solutions are:\n{real_part:g} + {imag_part:g}i\n{real_part:g} - {imag_part:g}i"
        
        else:
            return f"The polynomial degree is strictly greater than 2, I can't solve."

def main():
    if len(sys.argv) != 2:
        print("Usage: python computor.py \"equation\"")
        return
    
    equation = sys.argv[1]
    solver = PolynomialSolver()
    
    try:
        # Parse the equation
        solver.parse_equation(equation)
        
        # Display reduced form
        reduced_form = solver.get_reduced_form()
        print(f"Reduced form: {reduced_form}")
        
        # Display degree
        degree = solver.get_degree()
        print(f"Polynomial degree: {degree}")
        
        # Solve and display solution
        solution = solver.solve()
        print(solution)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()