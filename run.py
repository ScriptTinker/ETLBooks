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
    try:
        from pyngrok import ngrok
        http_tunnel = ngrok.connect(5000)
        public_url = http_tunnel.public_url
        print("Public URL:", public_url)
    except:
        print("Couldn't load the public url! Perhaps app is running locally? Please check your Authtoken!")    
    
    app.run(host="0.0.0.0", debug=True, use_reloader=False)