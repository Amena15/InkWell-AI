def add(a, b):
    """
    Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The sum of a and b
    """
    return a + b

class Calculator:
    """A simple calculator class."""
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b

if __name__ == "__main__":
    # Test the functions
    print(f"2 + 3 = {add(2, 3)}")
    calc = Calculator()
    print(f"2 * 3 = {calc.multiply(2, 3)}")
