from flask import Flask, render_template
import json
import os

app = Flask(__name__)
DATA_FILE = 'sample_data.json'

def load_shipping_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, IOError):
            return []
    return []

@app.route('/')
def index():
    shipping_data = load_shipping_data()
    return render_template('index.html', shipping_data=shipping_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
