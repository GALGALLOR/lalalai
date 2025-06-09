from src import create_app
import os

app = create_app()

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    os.makedirs('acapellas', exist_ok=True)
    app.run(debug=True)
