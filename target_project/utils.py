"""Target project utility functions."""

def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

def format_greeting(greeting: str) -> str:
    """Format greeting with decorative banner."""
    return f"=== {greeting} ==="
