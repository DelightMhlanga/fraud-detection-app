# run.py

from app import create_app

from dotenv import load_dotenv
load_dotenv()

app = create_app()

if __name__ == '__main__':
    app.secret_key = 'your-secret-key'
    app.run(host='0.0.0.0', port=5000, debug=True)