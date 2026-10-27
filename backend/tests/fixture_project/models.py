"""Data models for the fixture project."""

class Item:
    """Represents a sample item."""
    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

    def to_dict(self) -> dict:
        """Serialize item to dictionary."""
        return {"name": self.name, "value": self.value}
