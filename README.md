# Polynomial Equation Solver (computor.py)

A comprehensive Python program that solves polynomial equations of degree 0, 1, and 2 with detailed step-by-step solutions and intelligent fraction display.

## Features

- ✅ **Linear and Quadratic Equation Solving**: Handles polynomials up to degree 2
- ✅ **Step-by-Step Solutions**: Shows complete mathematical reasoning process
- ✅ **Smart Fraction Display**: Automatically determines when fraction representation is beneficial
- ✅ **Exact Arithmetic**: Uses custom fraction implementation for precise rational calculations
- ✅ **Input Validation**: Comprehensive equation parsing and error handling
- ✅ **Multiple Solution Types**: Handles no solution, infinite solutions, and complex discriminants

## Installation

No external dependencies required! The program uses only Python's built-in libraries.

```bash
# Clone or download the computor.py file
# No pip install needed!
```

## Usage

```bash
python computor.py "<equation>"
```

### Examples

#### Linear Equations
```bash
python computor.py "2*x + 5 = 3*x - 7"
python computor.py "5*x - 3 = 12"
python computor.py "x = 42"
```

#### Quadratic Equations
```bash
python computor.py "x^2 - 5*x + 6 = 0"
python computor.py "2*x^2 + 3*x - 2 = 5*x^2 + x - 1"
python computor.py "x^2 + 2*x + 1 = 0"
```

#### Edge Cases
```bash
python computor.py "x^2 + x + 1 = 0"  # No real solutions
python computor.py "5 = 5"             # Infinite solutions
python computor.py "3 = 7"             # No solution
```

## Output Format

The program provides detailed output including:

1. **Input Validation**: Confirms the equation format and variable detection
2. **Equation Normalization**: Shows the standardized form
3. **Term Extraction**: Details how terms are identified and processed
4. **Reduced Form**: Displays the canonical polynomial form
5. **Solution Steps**: Complete mathematical derivation
6. **Final Answer**: Solutions in both fraction and decimal form when appropriate

### Sample Output

```
============================================================
POLYNOMIAL EQUATION SOLVER
============================================================
Input equation: "x^2 - 5*x + 6 = 0"
Variable detected: x
------------------------------------------------------------
Normalized equation: 1.0*x^2 + -5.0*x^1 + 6.0*x^0 = 0.0*x^0

Extracting terms from: 1.0*x^2 + -5.0*x^1 + 6.0*x^0
  Found term: 1.0 * x^2
  Found term: -5.0 * x^1
  Found term: 6.0 * x^0

Moving all terms to left side (Left - Right = 0):
  x^2: 1.0 - (0.0) = 1.0
  x^1: -5.0 - (0.0) = -5.0
  x^0: 6.0 - (0.0) = 6.0

Reduced form: 1 * x^2 - 5 * x + 6 = 0
Polynomial degree: 2

This is a quadratic equation.
Standard form: 1.0 * x^2 + -5.0 * x + 6.0 = 0
Coefficients: a = 1.0, b = -5.0, c = 6.0

Using the quadratic formula:
  x = (-b ± √(b² - 4ac)) / (2a)
  x = (-(-5.0) ± √((-5.0)² - 4*(1.0)*(6.0))) / (2*1.0)

Step 1: Calculate the discriminant (Δ = b² - 4ac)
  Δ = (-5.0)² - 4*(1.0)*(6.0)
  Δ = 25.0 - 24.0
  Δ = 1.0

Step 2: Analyze the discriminant
Result: Discriminant is strictly positive, there are two real solutions.

Step 3: Calculate √Δ
  √1.0 = 1 (perfect square)
The solutions will be rational numbers.

Step 4: Apply the quadratic formula

Solution 1: x = (-b - √Δ) / (2a)
  = (-(-5.0) - 1) / (2*1.0)
  = (5 - 1) / 2
  = 4 / 2
The solution is: 2

Solution 2: x = (-b + √Δ) / (2a)
  = (-(-5.0) + 1) / (2*1.0)
  = (5 + 1) / 2
  = 6 / 2
The solution is: 3
============================================================
```

## Supported Equation Formats

### Variable Names
- Any single letter: `x`, `y`, `z`, `a`, `b`, etc.
- Case sensitive: `X` and `x` are different variables

### Term Formats
- **Constants**: `5`, `-3`, `42`
- **Linear terms**: `x`, `-x`, `3*x`, `5x`, `-2*x`
- **Quadratic terms**: `x^2`, `-x^2`, `3*x^2`, `5x^2`
- **Mixed**: `2*x^2 - 3*x + 1`

### Operators
- Addition: `+`
- Subtraction: `-`
- Multiplication: `*` (optional for coefficient-variable)
- Exponentiation: `^`

## Algorithm Details

### Equation Processing
1. **Validation**: Checks for exactly one `=` sign and single variable
2. **Normalization**: Converts all terms to standard `coeff*var^power` format
3. **Term Extraction**: Uses regex to identify coefficients and powers
4. **Reduction**: Moves all terms to left side and combines like terms

### Solution Methods

#### Linear Equations (ax + b = 0)
- Direct algebraic solution: `x = -b/a`
- Handles edge cases (a = 0)

#### Quadratic Equations (ax² + bx + c = 0)
- Uses quadratic formula: `x = (-b ± √(b² - 4ac)) / (2a)`
- Calculates discriminant to determine solution types:
  - **Δ < 0**: No real solutions
  - **Δ = 0**: One real solution (repeated root)
  - **Δ > 0**: Two real solutions
- Detects perfect square discriminants for exact rational solutions

### Fraction Display Logic

The program intelligently decides when to display fractions:

- **Always as fractions**: Simple fractions (small denominators), very long decimals
- **Prefer decimals**: Complex fractions that don't add clarity
- **Both formats**: Shows both when helpful for understanding

## Error Handling

The program handles various error cases:

- Invalid equation format
- Multiple variables
- No variables
- Invalid terms or syntax
- Negative powers (non-polynomial)
- High-degree polynomials (> 2)

## Technical Implementation

### Custom Fraction Class
Since external libraries are restricted, the program includes a custom `SimpleFraction` class that:
- Performs exact rational arithmetic
- Automatically reduces fractions to lowest terms
- Handles float-to-fraction conversion
- Maintains proper sign conventions

### Parsing Strategy
- Uses regex patterns to identify and validate terms
- Normalizes various input formats to standard form
- Extracts coefficients and powers systematically

## Limitations

- **Degree Restriction**: Only solves polynomials up to degree 2
- **Single Variable**: Equations must contain exactly one variable
- **Real Solutions Only**: Does not compute complex solutions
- **Polynomial Form**: Does not handle rational functions or transcendental equations

## Examples by Category

### Basic Linear
```bash
python computor.py "x + 5 = 0"          # x = -5
python computor.py "2*x = 8"            # x = 4
python computor.py "3*x + 1 = 7"        # x = 2
```

### Linear with Fractions
```bash
python computor.py "2*x + 1 = 0"        # x = -1/2
python computor.py "3*x = 2"            # x = 2/3
```

### Simple Quadratic
```bash
python computor.py "x^2 = 4"            # x = ±2
python computor.py "x^2 - x = 0"        # x = 0, x = 1
```

### Complex Quadratic
```bash
python computor.py "x^2 + x + 1 = 0"    # No real solutions
python computor.py "x^2 - 2*x + 1 = 0"  # x = 1 (repeated)
```

## Development

The code is structured with clear separation of concerns:
- `validate_and_normalize()`: Input processing and validation
- `parse_and_solve_real()`: Main solving algorithm
- `display_solution_enhanced()`: Output formatting
- `SimpleFraction`: Exact arithmetic operations

## License

This project is available for educational and personal use. 