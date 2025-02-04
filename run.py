import subprocess
import sys
import os

def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_versions.txt"])

def is_colab():
    """Check if the code is running on Google Colab"""
    try:
        import google.colab
        return True
    except ImportError:
        return False

if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    try:
        from ETLBooks_flask import app, models
    except ImportError:
        print("Installing missing packages...")
        install_requirements()
        from ETLBooks_flask import app

if __name__ == "__main__":
    if is_colab():
        print("Running on Google Colab - Setting up public URL...")
        # Fix IPython/traitlets version conflict first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "traitlets==4.1.0"])
        
        # Install pyngrok for Colab
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok"])
        
        from pyngrok import ngrok
        from threading import Thread
        
        # Start Flask server in a thread
        Thread(target=lambda: app.run(
            host='0.0.0.0', 
            port=5000, 
            debug=True, 
            use_reloader=False)
        ).start()
        
        # Set up ngrok tunnel
        public_url = ngrok.connect(5000, bind_tls=True).public_url
        print(f"\nPublic URL: {public_url}\n")
    else:
        # Normal execution for local environment
        app.run(debug=True, use_reloader=False)