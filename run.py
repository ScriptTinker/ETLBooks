import subprocess
import sys
import os

def install_requirements():
    # First install Colab-compatible base versions
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "traitlets==4.1.0",
        "ipython==7.34.0",
        "jupyter-client==6.1.12",
        "jupyter-core==4.9.2",
        "numpy==1.21.6"
    ])
    
    # Then install other requirements
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_versions.txt"])

def is_colab():
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
        print("Configuring Colab environment...")
        # Additional Colab-specific setup
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok==5.0.5"])
        
        # Fix IPython display compatibility
        from IPython.display import clear_output
        clear_output()
        
        from pyngrok import ngrok
        from threading import Thread
        
        # Configure Flask for Colab
        Thread(target=lambda: app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Debug mode can cause issues in Colab
            use_reloader=False
        )).start()
        
        # Set up ngrok tunnel
        public_url = ngrok.connect(5000, bind_tls=True).public_url
        print(f"\nPublic URL: {public_url}\n")
    else:
        # Local development configuration
        app.run(debug=True, use_reloader=False)