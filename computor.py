import sys
from parser import parse_equation
from solver import solve

def main():
    if len(sys.argv) != 2:
        print("Usage: ./computor \"equation\"")
        return
    expression = sys.argv[1]
    try:
        coefficients = parse_equation(expression)
        solve(coefficients)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
