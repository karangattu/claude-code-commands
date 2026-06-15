def divide(a, b):
    if b == 0:
        return None
    return a / b

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

def calculate_factorial(n):
    if n == 0:
        return 1
    return n * calculate_factorial(n - 1)
