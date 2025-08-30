#!/usr/bin/env python3
import re
import sys
import math
from fractions import Fraction
from typing import Dict, Tuple, Optional, List

class PolynomialSolver:
    def __init__(self, show_steps=False, use_fractions=False):
        self.coefficients = {}
        self.show_steps = show_steps
        self.use_fractions = use_fractions
        self.steps = []
    
    def log_step(self, step):
        """Log a step for intermediate display"""
        if self.show_steps:
            self.steps.append(step)
    
    def parse_free_form_term(self, term):
        """Parse free-form terms like '5', 'X', '3X', 'X^2', '-2X^3'"""
        term = term.strip()
        if not term:
            return None, None
        
        # Handle sign
        sign = 1
        if term.startswith('-'):
            sign = -1
            term = term[1:]
        elif term.startswith('+'):
            term = term[1:]
        
        # Remove spaces
        term = re.sub(r'\s+', '', term)
        
        # Case 1: Just a number (constant term)
        if re.match(r'^\d*\.?\d+$', term):
            return sign * float(term), 0
        
        # Case 2: Just X (degree 1, coefficient 1)
        if term == 'X':
            return sign * 1.0, 1
        
        # Case 3: X^n (degree n, coefficient 1)
        match = re.match(r'^X\^(\d+)$', term)
        if match:
            return sign * 1.0, int(match.group(1))
        
        # Case 4: number*X or numberX (degree 1)
        match = re.match(r'^(\d*\.?\d+)\*?X$', term)
        if match:
            return sign * float(match.group(1)), 1
        
        # Case 5: number*X^n or numberX^n
        match = re.match(r'^(\d*\.?\d+)\*?X\^(\d+)$', term)
        if match:
            return sign * float(match.group(1)), int(match.group(2))
        
        # Case 6: Standard format a * X^n
        match = re.match(r'^(\d*\.?\d+)\*X\^(\d+)$', term)
        if match:
            return sign * float(match.group(1)), int(match.group(2))
        
        return None, None
    
    def parse_standard_term(self, term):
        """Parse standard format terms like '5 * X^2'"""
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
        pattern = r'^([+-]?\d*\.?\d*)\*X\^(\d+)$'
        match = re.match(pattern, term)
        
        if match:
            coeff_str = match.group(1)
            power = int(match.group(2))
            
            if coeff_str == '' or coeff_str == '+':
                coefficient = 1.0
            elif coeff_str == '-':
                coefficient = -1.0
            else:
                coefficient = float(coeff_str)
            
            return coefficient, power
        
        # Handle constant terms
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
        
        # Handle pure numbers
        pattern_num = r'^([+-]?\d*\.?\d*)$'
        match_num = re.match(pattern_num, term)
        if match_num and match_num.group(1):
            return float(match_num.group(1)), 0
            
        return None, None
    
    def normalize_equation(self, equation_str):
        """Normalize equation format and handle free-form input"""
        # Remove extra spaces
        equation_str = re.sub(r'\s+', ' ', equation_str.strip())
        
        # Check if it's already in standard format
        if '*' in equation_str and 'X^' in equation_str:
            return equation_str, False
        
        # Convert free-form to standard format
        self.log_step(f"Converting free-form equation: {equation_str}")
        
        # Handle free-form input
        if '=' not in equation_str:
            raise ValueError("Equation must contain '=' sign")
        
        left, right = equation_str.split('=', 1)
        
        def convert_side(side):
            # Add explicit + for first term if no sign
            side = side.strip()
            if not side.startswith(('+', '-')):
                side = '+' + side
            
            # Split into terms while preserving signs
            terms = re.findall(r'[+-][^+-]+', side)
            converted_terms = []
            
            for term in terms:
                term = term.strip()
                if not term:
                    continue
                
                # Try free-form parsing first
                coeff, power = self.parse_free_form_term(term)
                if coeff is not None:
                    if power == 0:
                        converted_terms.append(f"{coeff} * X^0")
                    else:
                        converted_terms.append(f"{coeff} * X^{power}")
            
            return ' '.join(converted_terms) if converted_terms else "0 * X^0"
        
        left_converted = convert_side(left)
        right_converted = convert_side(right)
        normalized = f"{left_converted} = {right_converted}"
        
        self.log_step(f"Normalized to: {normalized}")
        return normalized, True
    
    def parse_equation(self, equation_str):
        """Parse equation with enhanced error handling"""
        try:
            # Validate basic format
            if not equation_str or equation_str.isspace():
                raise ValueError("Empty equation provided")
            
            if equation_str.count('=') != 1:
                raise ValueError("Equation must contain exactly one '=' sign")
            
            # Normalize the equation
            normalized_eq, was_converted = self.normalize_equation(equation_str)
            
            # Split by '='
            left_side, right_side = normalized_eq.split('=', 1)
            
            self.log_step(f"Parsing left side: {left_side}")
            left_coeffs = self.parse_side(left_side)
            
            self.log_step(f"Parsing right side: {right_side}")
            right_coeffs = self.parse_side(right_side)
            
            # Combine coefficients (left - right = 0)
            all_coeffs = {}
            
            for power, coeff in left_coeffs.items():
                all_coeffs[power] = all_coeffs.get(power, 0) + coeff
            
            for power, coeff in right_coeffs.items():
                all_coeffs[power] = all_coeffs.get(power, 0) - coeff
            
            # Remove near-zero coefficients
            self.coefficients = {k: v for k, v in all_coeffs.items() if abs(v) > 1e-10}
            
            if self.show_steps:
                self.log_step(f"Combined coefficients: {self.coefficients}")
            
            return self.coefficients
            
        except Exception as e:
            raise ValueError(f"Parsing error: {str(e)}")
    
    def parse_side(self, side_str):
        """Parse one side with better error handling"""
        coeffs = {}
        side_str = side_str.strip()
        
        if not side_str:
            return coeffs
        
        # Add explicit + at the beginning if needed
        if not side_str.startswith(('+', '-')):
            side_str = '+' + side_str
        
        # Split by + and - while keeping signs
        terms = re.split(r'(?=[+-])', side_str)
        terms = [term.strip() for term in terms if term.strip()]
        
        for term in terms:
            if not term:
                continue
            
            # Try standard format first
            result = self.parse_standard_term(term)
            if result[0] is not None:
                coeff, power = result
                coeffs[power] = coeffs.get(power, 0) + coeff
                continue
            
            # Try free-form format
            result = self.parse_free_form_term(term)
            if result[0] is not None:
                coeff, power = result
                coeffs[power] = coeffs.get(power, 0) + coeff
                continue
            
            raise ValueError(f"Cannot parse term: '{term}'")
        
        return coeffs
    
    def get_reduced_form(self):
        """Return the reduced form string"""
        if not self.coefficients:
            return "0 = 0"
        
        terms = []
        
        # Sort powers in ascending order for display
        for power in sorted(self.coefficients.keys()):
            coeff = self.coefficients[power]
            
            if abs(coeff) < 1e-10:
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
            else:
                if coeff_str in ["", " + "]:
                    coeff_str += "1"
                elif coeff_str == " - ":
                    coeff_str += "1"
                power_str = f" * X^{power}"
            
            terms.append(coeff_str + power_str)
        
        return ("".join(terms) + " = 0") if terms else "0 = 0"
    
    def get_degree(self):
        """Return the degree of the polynomial"""
        if not self.coefficients:
            return 0
        return max(self.coefficients.keys())
    
    def format_number(self, num):
        """Format number as fraction if beneficial, otherwise as decimal"""
        if not self.use_fractions:
            return f"{num:g}"
        
        try:
            frac = Fraction(num).limit_denominator(1000)
            if abs(float(frac) - num) < 1e-10 and frac.denominator > 1:
                if frac.denominator <= 20:  # Only show "nice" fractions
                    return str(frac)
            return f"{num:g}"
        except:
            return f"{num:g}"
    
    def format_complex_number(self, real, imag):
        """Format complex number nicely"""
        if abs(real) < 1e-10:
            real = 0
        if abs(imag) < 1e-10:
            imag = 0
        
        if real == 0 and imag == 0:
            return "0"
        elif real == 0:
            if imag == 1:
                return "i"
            elif imag == -1:
                return "-i"
            else:
                return f"{self.format_number(imag)}i"
        elif imag == 0:
            return self.format_number(real)
        else:
            imag_str = ""
            if imag == 1:
                imag_str = " + i"
            elif imag == -1:
                imag_str = " - i"
            elif imag > 0:
                imag_str = f" + {self.format_number(imag)}i"
            else:
                imag_str = f" - {self.format_number(abs(imag))}i"
            
            return f"{self.format_number(real)}{imag_str}"
    
    def solve(self):
        """Solve the polynomial equation with detailed steps"""
        degree = self.get_degree()
        
        if self.show_steps:
            self.log_step(f"\nSolving polynomial of degree {degree}")
        
        if degree == 0:
            # Constant equation
            const = self.coefficients.get(0, 0)
            
            if self.show_steps:
                self.log_step(f"Constant equation: {const} = 0")
            
            if abs(const) < 1e-10:
                return "Any real number is a solution."
            else:
                return "No solution."
        
        elif degree == 1:
            # Linear equation: ax + b = 0
            a = self.coefficients.get(1, 0)
            b = self.coefficients.get(0, 0)
            
            if self.show_steps:
                self.log_step(f"Linear equation: {a}x + {b} = 0")
                self.log_step(f"Solving for x: x = -{b}/{a}")
            
            if abs(a) < 1e-10:
                return "No solution." if abs(b) > 1e-10 else "Any real number is a solution."
            
            solution = -b / a
            
            if self.show_steps:
                self.log_step(f"Solution: x = {self.format_number(solution)}")
            
            return f"The solution is:\n{self.format_number(solution)}"
        
        elif degree == 2:
            # Quadratic equation: ax² + bx + c = 0
            a = self.coefficients.get(2, 0)
            b = self.coefficients.get(1, 0)
            c = self.coefficients.get(0, 0)
            
            if self.show_steps:
                self.log_step(f"Quadratic equation: {a}x² + {b}x + {c} = 0")
            
            if abs(a) < 1e-10:
                # Actually linear
                if abs(b) < 1e-10:
                    return "No solution." if abs(c) > 1e-10 else "Any real number is a solution."
                solution = -c / b
                return f"The solution is:\n{self.format_number(solution)}"
            
            # Calculate discriminant
            discriminant = b*b - 4*a*c
            
            if self.show_steps:
                self.log_step(f"Using quadratic formula: x = (-b ± √(b² - 4ac)) / 2a")
                self.log_step(f"Discriminant: Δ = b² - 4ac = {b}² - 4×{a}×{c} = {discriminant}")
            
            if discriminant > 1e-10:
                # Two real solutions
                sqrt_d = math.sqrt(discriminant)
                x1 = (-b + sqrt_d) / (2*a)
                x2 = (-b - sqrt_d) / (2*a)
                
                if self.show_steps:
                    self.log_step(f"√Δ = {sqrt_d}")
                    self.log_step(f"x₁ = ({-b} + {sqrt_d}) / {2*a} = {self.format_number(x1)}")
                    self.log_step(f"x₂ = ({-b} - {sqrt_d}) / {2*a} = {self.format_number(x2)}")
                
                return f"Discriminant is strictly positive, the two solutions are:\n{self.format_number(x1)}\n{self.format_number(x2)}"
            
            elif abs(discriminant) <= 1e-10:
                # One real solution
                x = -b / (2*a)
                
                if self.show_steps:
                    self.log_step(f"x = {-b} / {2*a} = {self.format_number(x)}")
                
                return f"Discriminant is zero, the solution is:\n{self.format_number(x)}"
            
            else:
                # Complex solutions
                sqrt_d = math.sqrt(abs(discriminant))
                real_part = -b / (2*a)
                imag_part = sqrt_d / (2*a)
                
                if self.show_steps:
                    self.log_step(f"√|Δ| = {sqrt_d}")
                    self.log_step(f"Real part: {-b} / {2*a} = {self.format_number(real_part)}")
                    self.log_step(f"Imaginary part: ±{sqrt_d} / {2*a} = ±{self.format_number(imag_part)}")
                
                x1 = self.format_complex_number(real_part, imag_part)
                x2 = self.format_complex_number(real_part, -imag_part)
                
                return f"Discriminant is strictly negative, the two complex solutions are:\n{x1}\n{x2}"
        
        else:
            return f"The polynomial degree is strictly greater than 2, I can't solve."
    
    def validate_input(self, equation_str):
        """Validate input with helpful error messages"""
        if not equation_str:
            raise ValueError("Empty equation provided")
        
        if equation_str.count('=') == 0:
            raise ValueError("Equation must contain '=' sign")
        
        if equation_str.count('=') > 1:
            raise ValueError("Equation must contain exactly one '=' sign")
        
        # Check for invalid characters
        valid_chars = set('0123456789+-*/=.XxEe^ ()')
        invalid_chars = set(equation_str) - valid_chars
        if invalid_chars:
            raise ValueError(f"Invalid characters found: {', '.join(invalid_chars)}")
        
        # Check for basic X variable format
        if 'X' not in equation_str.upper():
            if any(char.isalpha() for char in equation_str):
                raise ValueError("Only 'X' is allowed as variable name")
        
        return True

def print_help():
    """Print usage help"""
    print("Polynomial Equation Solver - Enhanced Version")
    print("=" * 50)
    print("Usage:")
    print("  python computor.py \"equation\" [options]")
    print("\nOptions:")
    print("  --steps, -s     Show step-by-step solution")
    print("  --fractions, -f Show solutions as fractions when beneficial")
    print("  --help, -h      Show this help message")
    print("\nSupported formats:")
    print("  Standard:  5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0")
    print("  Free-form: 5 + 4*X - 9.3*X^2 = 1")
    print("  Mixed:     5 + 4X - 9.3X² = 1")
    print("\nExamples:")
    print("  python computor.py \"X^2 - 4 = 0\"")
    print("  python computor.py \"2X + 6 = 0\" --steps")
    print("  python computor.py \"X^2 + X + 1 = 0\" --fractions")

def main():
    # Parse command line arguments
    if len(sys.argv) < 2:
        print_help()
        return
    
    equation = ""
    show_steps = False
    use_fractions = False
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ['--help', '-h']:
            print_help()
            return
        elif arg in ['--steps', '-s']:
            show_steps = True
        elif arg in ['--fractions', '-f']:
            use_fractions = True
        elif arg.startswith('-'):
            print(f"Unknown option: {arg}")
            print("Use --help for usage information")
            return
        else:
            equation = arg
        i += 1
    
    if not equation:
        print("Error: No equation provided")
        print_help()
        return
    
    solver = PolynomialSolver(show_steps=show_steps, use_fractions=use_fractions)
    
    try:
        # Validate input
        solver.validate_input(equation)
        
        if show_steps:
            print("STEP-BY-STEP SOLUTION")
            print("=" * 40)
            print(f"Original equation: {equation}")
        
        # Parse the equation
        solver.parse_equation(equation)
        
        # Display intermediate steps if requested
        if show_steps and solver.steps:
            print("\nParsing steps:")
            for step in solver.steps:
                print(f"  {step}")
        
        # Display reduced form
        reduced_form = solver.get_reduced_form()
        print(f"\nReduced form: {reduced_form}")
        
        # Display degree
        degree = solver.get_degree()
        print(f"Polynomial degree: {degree}")
        
        # Solve and display solution
        solution = solver.solve()
        
        # Display solution steps if requested
        if show_steps and hasattr(solver, 'steps') and len(solver.steps) > len([s for s in solver.steps if 'Parsing' in s or 'Converting' in s or 'Combined' in s]):
            print("\nSolution steps:")
            for step in solver.steps:
                if not any(keyword in step for keyword in ['Parsing', 'Converting', 'Combined']):
                    print(f"  {step}")
        
        print(solution)
        
    except ValueError as e:
        print(f"Input Error: {e}")
        print("\nPlease check your equation format. Examples:")
        print("  Standard: \"5 * X^0 + 4 * X^1 - 9.3 * X^2 = 1 * X^0\"")
        print("  Free-form: \"5 + 4*X - 9.3*X^2 = 1\"")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()