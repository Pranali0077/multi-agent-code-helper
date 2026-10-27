"""Target project entry point."""
import models
import utils

def run():
    """Main execution function."""
    user = models.User(name="Alice", role="Developer")
    print(utils.greet(user.name))

if __name__ == "__main__":
    run()
