"""Target project utility functions."""

def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

def format_greeting(greeting: str) -> str:
    """Format greeting with decorative banner."""
    return f"=== {greeting} ==="

def search_users(users: list, query: str) -> list:
    """Search and filter users by name or role matching the query."""
    q = query.lower()
    return [u for u in users if q in u.name.lower() or q in u.role.lower()]
