"""Entry point for the fixture project."""
import models
import utils

def main() -> None:
    """Run sample workflow."""
    item = models.Item("Sample", 42)
    formatted = utils.format_item(item.name, item.value)
    print(formatted)

if __name__ == "__main__":
    main()
