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