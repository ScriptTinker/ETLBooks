import subprocess
import sys

def install_requirements():
    """Install dependencies from the requirements_versions.txt file."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_versions.txt"])

try:
    # Try importing the app
    from ETLBooks_flask import app

except ImportError:
    # If some packages are missing, install them
    print("Some packages are missing! Installing now...")
    install_requirements()

    from ETLBooks_flask import app


if __name__ == "__main__":
    app.run(debug=True)