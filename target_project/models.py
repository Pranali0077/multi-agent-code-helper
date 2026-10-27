"""Target project data models."""

class User:
    """User entity definition."""
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def get_info(self) -> dict:
        """Return user info dictionary."""
        return {"name": self.name, "role": self.role}
