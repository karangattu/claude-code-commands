import unittest
from math_utils import divide, is_prime, calculate_factorial

class TestMathUtils(unittest.TestCase):
    def test_divide(self):
        self.assertEqual(divide(6, 2), 3)
        self.assertIsNone(divide(6, 0))

    def test_is_prime(self):
        self.assertTrue(is_prime(2))
        self.assertTrue(is_prime(7))
        self.assertFalse(is_prime(4))

    def test_factorial_bug(self):
        self.assertEqual(calculate_factorial(3), 6)
        with self.assertRaises(ValueError):
            calculate_factorial(-1)
