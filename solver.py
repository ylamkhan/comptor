from fractions import Fraction

def manual_sqrt(n, eps=1e-10):
    """Compute the square root of n using the Babylonian method (Newton-Raphson)."""
    if n < 0:
        raise ValueError("Cannot compute the square root of a negative number.")
    if n == 0:
        return 0
    x = n
    while True:
        root = 0.5 * (x + n / x)
        if abs(root - x) < eps:
            return root
        x = root

def solve(coeffs):
    max_deg = max((k for k, v in coeffs.items() if v != 0), default=0)
    print(f"Polynomial degree: {max_deg}")

    if max_deg > 2:
        print("The polynomial degree is strictly greater than 2, I can't solve.")
        return

    a = coeffs.get(2, 0)
    b = coeffs.get(1, 0)
    c = coeffs.get(0, 0)

    if max_deg == 0:
        if c == 0:
            print("Every real number is a solution.")
        else:
            print("No solution.")
    elif max_deg == 1:
        x = -c / b
        print("The solution is:")
        try:
            print(f"{x} or {Fraction(str(-c)) / Fraction(str(b))}")
        except:
            print(f"{x} (approximate)")
    elif max_deg == 2:
        d = b ** 2 - 4 * a * c
        print(f"Discriminant: {d:.2f}")
        if d > 0:
            print("Discriminant is strictly positive, the two solutions are:")
            sqrt_d = manual_sqrt(d)
            r1 = (-b + sqrt_d) / (2 * a)
            r2 = (-b - sqrt_d) / (2 * a)
            try:
                print(f"{r1} or {Fraction(str(-b + sqrt_d)) / Fraction(str(2 * a))}")
                print(f"{r2} or {Fraction(str(-b - sqrt_d)) / Fraction(str(2 * a))}")
            except:
                print(f"{r1} and {r2} (approximate)")
        elif d == 0:
            x = -b / (2 * a)
            print("Discriminant is zero, the solution is:")
            try:
                print(f"{x} or {Fraction(str(-b)) / Fraction(str(2 * a))}")
            except:
                print(f"{x} (approximate)")
        else:
            print("Discriminant is strictly negative, complex solutions:")
            real = -b / (2 * a)
            imag = manual_sqrt(-d) / (2 * a)
            print(f"{real} + {imag}i")
            print(f"{real} - {imag}i")
