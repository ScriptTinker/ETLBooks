import subprocess
import sys
import os

def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_versions.txt"])

if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    try:
        from ETLBooks_flask import app, models
    except ImportError:
        print("Installing missing packages...")
        install_requirements()
        from ETLBooks_flask import app

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)