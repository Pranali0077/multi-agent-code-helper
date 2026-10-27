"""Utility functions for the fixture project."""

def format_item(name: str, value: int) -> str:
    """Format an item's details as a readable string."""
    return f"Item({name}, value={value})"

def calculate_total(values: list[int]) -> int:
    """Calculate the sum of item values."""
    return sum(values)
